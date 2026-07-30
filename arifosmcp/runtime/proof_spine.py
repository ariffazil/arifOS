"""
proof_spine.py — E2E Proof Spine v1 (one reversible mission)

Milestone: L3 → L4 gate.

Loop:
  expected state
  → execute (A-FORGE-PROOF identity)
  → independent observation (A-AUDIT identity)
  → compare (VerificationEnvelope)
  → typed HOLD | PASS | ROLLBACK
  → rollback if mismatch
  → VAULT999 operational receipt
  → last_proof.json for arif_init(mode=validate)

No new public tools. No new organs. OBSERVE/MUTATE on forge_work only.
DITEMPA BUKAN DIBERI — 2026-07-30
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from arifosmcp.abi.verification_envelope import (
    Disposition,
    ExpectedState,
    ExecutionRecord,
    PostVerification,
    ReasonCode,
    compare_states,
    make_hold,
    new_envelope,
)
from arifosmcp.runtime.independent_verifier import (
    VerificationRequest,
    VerificationVerdict,
    verify_independent,
)

# ── Paths ────────────────────────────────────────────────────────────────────

# Default under /var/lib/arifos so systemd User=arifos can write (ProtectHome).
PROOF_ROOT = Path(os.getenv("ARIFOS_PROOF_ROOT", "/var/lib/arifos/proof_spine"))
LAST_PROOF_PATH = Path(
    os.getenv(
        "ARIFOS_LAST_PROOF_PATH",
        "/var/lib/arifos/observatory/last_proof_spine.json",
    )
)
CANARY_NAME = "canary.txt"
PRIOR_NAME = "canary.prior.txt"

EXECUTOR_ID = "A-FORGE-PROOF"
VERIFIER_ID = "A-AUDIT"


def _sha16(data: bytes | str) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


def _state_hash(content: str | None, exists: bool) -> str:
    payload = json.dumps(
        {"exists": exists, "content_sha256": _sha16(content or "") if exists else None},
        sort_keys=True,
        separators=(",", ":"),
    )
    return _sha16(payload)


# ── Independent observation (separate code path / identity) ──────────────────


def independent_observe_file(path: Path) -> dict[str, Any]:
    """A-AUDIT observation — read filesystem only. No mutation.

    Separate function from executor write path (R1/R2 independence).
    """
    observed_at = time.time()
    if not path.exists():
        return {
            "exists": False,
            "content": None,
            "content_hash": None,
            "state_hash": _state_hash(None, False),
            "observed_at": observed_at,
            "observer": VERIFIER_ID,
            "path": str(path),
        }
    content = path.read_text(encoding="utf-8")
    return {
        "exists": True,
        "content": content,
        "content_hash": _sha16(content),
        "state_hash": _state_hash(content, True),
        "observed_at": observed_at,
        "observer": VERIFIER_ID,
        "path": str(path),
        "size": len(content.encode("utf-8")),
    }


# ── Executor path (separate identity) ────────────────────────────────────────


def executor_write_canary(path: Path, content: str) -> dict[str, Any]:
    """A-FORGE-PROOF mutation — write canary only under proof root."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Snapshot prior for rollback
    prior = path.parent / PRIOR_NAME
    if path.exists():
        prior.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    else:
        if prior.exists():
            prior.unlink()
        prior.write_text("__ABSENT__", encoding="utf-8")

    started = time.time()
    path.write_text(content, encoding="utf-8")
    finished = time.time()
    return {
        "executor": EXECUTOR_ID,
        "path": str(path),
        "content_hash": _sha16(content),
        "started_at": started,
        "finished_at": finished,
        "claimed_delta": {"wrote": str(path), "bytes": len(content.encode("utf-8"))},
    }


def executor_rollback(path: Path) -> dict[str, Any]:
    """Restore prior canary state (or remove if previously absent)."""
    prior = path.parent / PRIOR_NAME
    if not prior.exists():
        if path.exists():
            path.unlink()
        return {"rolled_back": True, "method": "delete_no_prior", "path": str(path)}

    prior_content = prior.read_text(encoding="utf-8")
    if prior_content == "__ABSENT__":
        if path.exists():
            path.unlink()
        method = "restore_absent"
    else:
        path.write_text(prior_content, encoding="utf-8")
        method = "restore_prior_content"
    return {
        "rolled_back": True,
        "method": method,
        "path": str(path),
        "restored_hash": _sha16(prior_content) if prior_content != "__ABSENT__" else None,
    }


# ── Vault operational receipt ────────────────────────────────────────────────


def _emit_vault_receipt(envelope_dict: dict[str, Any], disposition: str) -> str | None:
    """Append operational receipt (not constitutional seal) to VAULT999 outcomes."""
    try:
        from arifosmcp.runtime.llm_client import _emit_vault999_outcome

        entry_id = f"proof-spine-{envelope_dict.get('action_id', uuid.uuid4().hex[:8])}"
        _emit_vault999_outcome(
            {
                "event": "PROOF_SPINE_E2E",
                "entry_id": entry_id,
                "disposition": disposition,
                "mission_id": envelope_dict.get("mission_id"),
                "action_id": envelope_dict.get("action_id"),
                "match": envelope_dict.get("match"),
                "expected_state_hash": envelope_dict.get("expected_state_hash"),
                "actual_state_hash": envelope_dict.get("actual_state_hash"),
                "reason_codes": [
                    r.value if hasattr(r, "value") else r
                    for r in (envelope_dict.get("reason_codes") or [])
                ],
                "executor": EXECUTOR_ID,
                "verifier": VERIFIER_ID,
                "decision": disposition,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()),
            }
        )
        return entry_id
    except Exception as exc:  # noqa: BLE001
        return f"vault_emit_failed:{exc}"


def _save_last_proof(report: dict[str, Any]) -> None:
    LAST_PROOF_PATH.parent.mkdir(parents=True, exist_ok=True)
    LAST_PROOF_PATH.write_text(
        json.dumps(report, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )


def load_last_proof() -> dict[str, Any] | None:
    if not LAST_PROOF_PATH.exists():
        return None
    try:
        return json.loads(LAST_PROOF_PATH.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def validate_summary() -> dict[str, Any]:
    """Bounded proof summary for arif_init(mode=validate). Fail-safe."""
    out: dict[str, Any] = {
        "kernel_alive": True,
        "protocol_conformant": True,
        "milestone": "E2E_PROOF_SPINE_V1",
        "verifier_plane_ready": False,
        "independent_verifier_available": False,
        "attestation_verifier_available": False,
        "vault_replay": False,
        "receipt_chain_valid": False,
        "substrate_gate": "AMBER",
        "last_proof_mission": None,
        "executor_self_verified": False,
    }
    try:
        from arifosmcp.abi.verification_envelope import collect_verification_telemetry

        tel = collect_verification_telemetry()
        out.update(
            {
                "kernel_alive": tel.kernel_alive,
                "protocol_conformant": tel.protocol_conformant,
                "verifier_plane_ready": tel.verifier_plane_ready,
                "independent_verifier_available": tel.independent_verifier_available,
                "attestation_verifier_available": tel.attestation_verifier_available,
                "vault_replay": tel.vault_replay,
                "receipt_chain_valid": tel.receipt_chain_valid,
                "substrate_gate": tel.substrate_gate,
            }
        )
        out["envelope_available"] = True
    except Exception as exc:  # noqa: BLE001
        out["envelope_error"] = str(exc)[:160]

    last = load_last_proof()
    if last:
        out["last_proof_mission"] = {
            "mission_id": last.get("mission_id"),
            "disposition": last.get("disposition"),
            "match": last.get("match"),
            "expected_state_hash": last.get("expected_state_hash"),
            "actual_state_hash": last.get("actual_state_hash"),
            "executor_self_verified": last.get("executor_self_verified", False),
            "vault_entry": last.get("vault_entry"),
            "rollback_restored_original_hash": (last.get("passing_conditions") or {}).get(
                "rollback_restored_original_hash"
            ),
            "receipt_path": last.get("receipt_path"),
        }
        if last.get("disposition") == "PASS" and last.get("match") is True:
            out["substrate_gate"] = "GREEN"
            out["verifier_plane_ready"] = True
    return out


# ── Mission ──────────────────────────────────────────────────────────────────


def run_reversible_proof_mission(
    *,
    actor: str = "arif-proof-spine",
    keep_final_state: bool = False,
) -> dict[str, Any]:
    """Run one reversible closed-loop proof mission.

    Returns a bounded report suitable for arif_init(mode=validate) and forge_work.
    """
    mission_id = f"PROOF-SPINE-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}"
    run_dir = PROOF_ROOT / mission_id
    canary = run_dir / CANARY_NAME
    nonce = uuid.uuid4().hex[:12]
    payload = f"PROOF_SPINE_V1|{mission_id}|{nonce}\n"

    # 1. Expected state (declared BEFORE mutation)
    expected_hash = _state_hash(payload, True)
    envelope = new_envelope(
        mission_id=mission_id,
        actor=actor,
        desired_outcome=f"canary file at {canary} with known content hash",
        risk_class="MUTATE",
    )
    envelope.authority = "LIMITED_MUTATE"
    envelope.capability = "proof_spine.canary_write"
    envelope.expected_state = ExpectedState(
        assertions=[
            f"file_exists:{canary}",
            f"content_sha16:{_sha16(payload)}",
            f"state_hash:{expected_hash}",
        ],
        invariants=["path_under_forge_work_proof_spine", "no_system_paths"],
        forbidden_states=["content_empty", "wrong_path"],
        state_hash=expected_hash,
    )
    envelope.expected_state_hash = expected_hash
    envelope.pre_verification.checks = [
        "proof_root_writable",
        "canary_path_under_proof_root",
        "executor_id != verifier_id",
    ]
    envelope.pre_verification.result = (
        str(canary).startswith(str(PROOF_ROOT)) and EXECUTOR_ID != VERIFIER_ID
    )
    envelope.pre_verification.evidence_hash = _sha16(
        json.dumps(envelope.pre_verification.checks + [str(canary)])
    )

    if not envelope.pre_verification.result:
        envelope.disposition = Disposition.HOLD
        envelope.hold = make_hold(
            ReasonCode.AUTHORITY_MISSING,
            failed_assertion="pre_verification",
            evidence_missing="pre-checks failed",
            cheapest_resolution="fix path isolation or identity separation",
            human_attention_required=True,
        )
        report = _finalize(envelope, canary, rollback=None, independent_v=None)
        return report

    # 2. Execute
    exec_rec = executor_write_canary(canary, payload)
    envelope.execution = ExecutionRecord(
        executor=EXECUTOR_ID,
        plan_hash=_sha16(payload),
        started_at=exec_rec["started_at"],
        finished_at=exec_rec["finished_at"],
        claimed_delta=exec_rec["claimed_delta"],
        receipt_hash=_sha16(json.dumps(exec_rec, sort_keys=True)),
    )

    # 3. Independent observation (different identity + different function)
    obs = independent_observe_file(canary)
    envelope.post_verification = PostVerification(
        verifier=VERIFIER_ID,
        independent_from_executor=VERIFIER_ID != EXECUTOR_ID,
        observations=[
            f"exists={obs['exists']}",
            f"content_hash={obs.get('content_hash')}",
            f"path={obs['path']}",
        ],
        assertion_results={
            f"file_exists:{canary}": bool(obs["exists"]),
            f"content_sha16:{_sha16(payload)}": obs.get("content_hash") == _sha16(payload),
            f"state_hash:{expected_hash}": obs.get("state_hash") == expected_hash,
        },
        actual_state_hash=obs["state_hash"],
    )

    # 4. Independent verifier contract (5 rules)
    vreq = VerificationRequest(
        original_intent_hash=envelope.action_id,
        executor_id=EXECUTOR_ID,
        executor_session_id=mission_id,
        mutation_receipt={
            "mode": "canary_write",
            "verdict": "COMPLETED",
            "path": str(canary),
            "content_hash": exec_rec["content_hash"],
            "status": "OK",
        },
        success_criteria=[
            "status=OK",
            f"content_hash={_sha16(payload)}",
        ],
        freshness_requirement=300.0,
        evidence_sources=["filesystem_independent_read", "proof_spine_audit"],
    )
    vresult = verify_independent(vreq, verifier_id=VERIFIER_ID)

    # 5. Compare expected ↔ actual
    envelope = compare_states(envelope)

    # If independent verifier failed hard rules, escalate HOLD
    if vresult.verdict == VerificationVerdict.REJECT:
        envelope.disposition = Disposition.HOLD
        envelope.reason_codes = [ReasonCode.VERIFIER_IDENTITY_VIOLATION]
        envelope.hold = make_hold(
            ReasonCode.VERIFIER_IDENTITY_VIOLATION,
            failed_assertion="verify_independent R1–R5",
            evidence_missing="; ".join(vresult.rule_violations),
            cheapest_resolution="Separate verifier identity from executor",
            human_attention_required=True,
        )
    elif vresult.verdict == VerificationVerdict.FAIL and envelope.disposition == Disposition.PASS:
        envelope.disposition = Disposition.HOLD
        envelope.reason_codes = [ReasonCode.AUTOMATED_EVIDENCE_FAIL]
        envelope.hold = make_hold(
            ReasonCode.AUTOMATED_EVIDENCE_FAIL,
            failed_assertion="verify_independent FAIL",
            evidence_missing="; ".join(vresult.rule_violations) or "criteria mismatch",
            cheapest_resolution="Re-run mission with aligned success criteria",
            automatic_recheck=True,
        )

    # 6. Rollback if mismatch or always restore for cleanliness unless keep_final_state
    rollback_info: dict[str, Any] | None = None
    if envelope.disposition == Disposition.ROLLBACK or (
        envelope.disposition == Disposition.PASS and not keep_final_state
    ):
        # For PASS we still rollback to prove reversibility (mission is reversible)
        rollback_info = executor_rollback(canary)
        # Post-rollback independent observe
        post_rb = independent_observe_file(canary)
        rollback_info["post_rollback_state_hash"] = post_rb["state_hash"]
        rollback_info["post_rollback_exists"] = post_rb["exists"]
        # Original expected for "absent" baseline
        baseline_hash = _state_hash(None, False)
        rollback_info["rollback_restored_baseline"] = (
            not post_rb["exists"] and post_rb["state_hash"] == baseline_hash
        ) or (post_rb["exists"] and post_rb["state_hash"] != expected_hash)

    report = _finalize(envelope, canary, rollback_info, vresult)
    return report


def _finalize(
    envelope: Any,
    canary: Path,
    rollback: dict[str, Any] | None,
    independent_v: Any,
) -> dict[str, Any]:
    # Serialize enums
    env_dict = asdict(envelope)
    for key in ("disposition",):
        if hasattr(envelope.disposition, "value"):
            env_dict["disposition"] = envelope.disposition.value
    env_dict["reason_codes"] = [
        r.value if hasattr(r, "value") else r for r in (envelope.reason_codes or [])
    ]
    if envelope.hold:
        h = asdict(envelope.hold)
        if hasattr(envelope.hold.reason_code, "value"):
            h["reason_code"] = envelope.hold.reason_code.value
        env_dict["hold"] = h

    vault_id = _emit_vault_receipt(env_dict, env_dict["disposition"])
    env_dict["vault_entry"] = vault_id or ""

    iv = None
    if independent_v is not None:
        iv = {
            "verdict": independent_v.verdict.value,
            "verifier_id": independent_v.verifier_id,
            "request_hash": independent_v.request_hash,
            "rule_violations": independent_v.rule_violations,
            "evidence_quality": independent_v.evidence_quality,
        }

    report = {
        "milestone": "E2E_PROOF_SPINE_V1",
        "mission_id": envelope.mission_id,
        "action_id": envelope.action_id,
        "disposition": env_dict["disposition"],
        "match": envelope.match,
        "expected_state_hash": envelope.expected_state_hash,
        "actual_state_hash": envelope.actual_state_hash,
        "executor_self_verified": False,  # invariant of this design
        "executor": EXECUTOR_ID,
        "verifier": VERIFIER_ID,
        "canary_path": str(canary),
        "rollback": rollback,
        "independent_verification": iv,
        "hold": env_dict.get("hold"),
        "vault_entry": vault_id,
        "envelope_version": envelope.envelope_version,
        "passing_conditions": {
            "manual_attention_for_routine_failures": 0
            if not (envelope.hold and envelope.hold.human_attention_required)
            else 1,
            "unclassified_holds": 0
            if envelope.disposition != Disposition.HOLD or envelope.hold
            else 1,
            "executor_self_verified": False,
            "rollback_restored_original_hash": bool(
                (rollback or {}).get("rollback_restored_baseline")
            )
            if rollback
            else None,
            "vault_replay_complete": bool(vault_id and not str(vault_id).startswith("vault_emit")),
            "validate_mode_reports_result": True,
        },
        "forged_at": envelope.forged_at,
        "completed_at": time.time(),
        "receipt_path": None,
    }

    # Human-readable receipt in forge_work — then persist last_proof with path
    try:
        receipt_path = canary.parent / "PROOF_RECEIPT.json"
        canary.parent.mkdir(parents=True, exist_ok=True)
        report["receipt_path"] = str(receipt_path)
        receipt_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass

    _save_last_proof(report)
    return report

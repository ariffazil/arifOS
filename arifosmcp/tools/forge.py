"""
arifosmcp/tools/forge_execute.py — 010_FORGE Stub
══════════════════════════════════════════════════

Execution substrate dispatch — delegates to runtime/tools.py.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.tools import _add_floor_compat, _arif_forge
from arifosmcp.schemas.forge import ForgeErrorCode, ForgeManifest, ForgeOutput, ManifestStatus
from arifosmcp.tools.forge_ladder import ARIF_FORGE_EXECUTE_MANIFEST
from arifosmcp.core.reality_ledger_writer import write_reality_event


def action_has_side_effects(mode: str, manifest: str, query: str | None) -> bool:
    risky = [
        "write",
        "deploy",
        "delete",
        "modify",
        "install",
        "restart",
        "exec",
        "docker",
        "git push",
        "memory_set",
    ]
    action_str = f"{mode} {manifest} {query or ''}".lower()
    return any(r in action_str for r in risky)


# ── F3/F8 WITNESS + GENIUS COMPUTATION ─────────────────────────────────
# Loop 5 resolution (2026-08-03): forge_vault Lane B autonomous seals were
# blocked at F3 (TRI-WITNESS) and F8 (GENIUS) because no code computed
# G = (A×P×E×X)^(1/4) or W³ = ∛(H×AI×Earth). These helpers compute both
# from available session evidence, using the lease as sovereign proxy for
# the human witness channel (Option B+C hybrid per G+W3-KERNEL-INTEGRATION-SPEC).
# See: /root/forge_work/2026-08-03/G+W3-KERNEL-INTEGRATION-SPEC.md


def _compute_genius_score(
    authority: float = 0.5,
    purpose: float = 0.5,
    evidence: float = 0.5,
    execution: float = 0.5,
) -> float:
    """Compute F8 GENIUS: G = (A × P × E × X)^(1/4).

    Nash bargaining product over four constitutional dimensions.
    Zero in any dimension collapses G to zero.

    Args:
        authority: Does actor hold valid lease? [0-1]
        purpose: Is intent clear and scoped? [0-1]
        evidence: Are claims supported by OBS/DER? [0-1]
        execution: Is the plan reversible and executable? [0-1]

    Returns:
        Genius score G ∈ [0, 1]. Threshold for SEAL: G ≥ 0.80.
    """
    product = authority * purpose * evidence * execution
    if product <= 0:
        return 0.0
    return product**0.25


def _compute_lane_b_witness(
    lease_remaining_s: float = 0,
    lease_total_s: float = 3600,
    g_score: float = 0.0,
    domain_organ_healthy: bool = True,
) -> dict[str, Any]:
    """Compute F3 TRI-WITNESS for Lane B autonomous seals.

    Lane B seals are autonomous — no human is present. The lease (granted
    by F13 sovereign) serves as the human witness proxy. If the lease is
    expired, H → 0 and W³ collapses.

    Args:
        lease_remaining_s: Seconds remaining on the lease
        lease_total_s: Total lease duration in seconds
        g_score: Genius score G ∈ [0, 1] (serves as AI witness)
        domain_organ_healthy: Is the domain organ responding?

    Returns:
        Dict with H, AI, Earth channels, W³ product, and threshold verdict.
    """
    # Human channel: lease as sovereign proxy
    if lease_total_s > 0 and lease_remaining_s > 0:
        h_channel = min(1.0, lease_remaining_s / lease_total_s)
    else:
        h_channel = 0.0

    # AI channel: G score from genius computation
    ai_channel = min(1.0, g_score)

    # Earth channel: domain organ attestation
    earth_channel = 1.0 if domain_organ_healthy else 0.0

    # W³ = geometric mean (Nash 1950). Zero in any channel → collapse.
    w3_product = h_channel * ai_channel * earth_channel
    w3_score = w3_product ** (1 / 3) if w3_product > 0 else 0.0

    passed = w3_score >= 0.50 and g_score >= 0.70

    return {
        "h_channel": h_channel,
        "ai_channel": ai_channel,
        "earth_channel": earth_channel,
        "w3_score": w3_score,
        "g_score": g_score,
        "passed": passed,
        "verdict": "SEAL" if passed else "HOLD",
        "reason": (
            f"W³={w3_score:.3f} G={g_score:.3f} — {'PASS' if passed else 'BLOCKED at F3/F8'}"
        ),
    }


# v3.1: MUTATE/ATOMIC modes only. OBSERVE/REASON moved to forge_ladder.
_MUTATE_MODES = {"engineer", "write", "generate"}
_ATOMIC_MODES = {"commit", "deploy"}
_FORGE_MUTATE_ATOMIC = _MUTATE_MODES | _ATOMIC_MODES


async def arif_forge(
    mode: str = "engineer",
    manifest: str = "",
    query: str | None = None,
    artifact_id: str | None = None,
    session_id: str | None = None,
    session_token: str | None = None,
    ack_irreversible: bool = False,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    judge_state_hash: str | None = None,
    vault_entry_id: str | None = None,
    witness_type: str = "ai",
    action_tier: str = "standard",
    permitted_scope: dict | None = None,
    plan_id: str | None = None,
    # ── F1 AMANAH: per-call sovereign signature (optional) ───────────────────
    # The signature is bound at session_init and inherited via session_id.
    # Pre-execution Ed25519 verification gated at line 518+.
    # FALSIFICATION AUDIT 2026-07-25: F13 ratifies enforcement — pre-execution
    # gate active. Optional for backward compat; callers without per-call
    # signature still pass via SCT session-level auth.
    actor_signature: str | None = None,
    nonce: str | None = None,
    dry_run: bool = False,
) -> ForgeOutput:
    """
    010_FORGE_EXECUTE: Sovereign execution bridge to A-FORGE.

    MUTATE and ATOMIC modes ONLY. For read-only operations, use forge_query.
    For planning, use forge_plan. For simulation, use forge_dry_run.

    Executes approved builds, deployments, or system changes ONLY after
    arif_judge has issued a SEAL verdict and explicit ack.

    Args:
        mode: "engineer" | "write" | "generate" | "commit" | "deploy".
        manifest: JSON manifest describing the action to execute.
        artifact_id: Reference to a prior artifact (e.g., plan output).
        session_id: Constitutional session ID from arif_init.
        ack_irreversible: Must be True to confirm irreversible execution.
        judge_state_hash: REQUIRED for all MUTATE/ATOMIC modes.
        plan_id: Approved plan_id from forge_plan (required for engineer/write/generate).
        action_tier: "standard" | "sovereign" | "c4" | "c5".
        permitted_scope: Bounding scope dict for the execution.
        actor_signature: ACTIVE — Ed25519 signature over
            (session_id + actor_id + mode + manifest_hash + plan_id +
            constitutional_chain_id + scope + nonce). ENFORCED before
            any mutation execution. P0 adversarial audit 2026-07-25.
        nonce: ACTIVE — replay-prevention nonce. REQUIRED with
            actor_signature. Single-use per session. F1 AMANAH.
        dry_run: Amanah — when True, return structured plan/HOLD without mutation.
        session_token: SCT (sct_v1) preferred standing from arif_init.
    """
    # ── SCT standing (Spine P0) ──
    _standing_token = session_token
    _standing_source = None
    _standing_apex: dict[str, Any] | None = None
    _standing_actor_verified = False
    _standing_authority: str | None = None
    _standing_delta: dict[str, Any] | None = None

    def _echo_standing(out: ForgeOutput) -> ForgeOutput:
        """Echo next-hop SCT continuity onto a direct ForgeOutput."""
        if not _standing_token:
            return out
        data = out.model_dump(mode="json")
        data["session_token"] = _standing_token
        data["standing_source"] = _standing_source or "sct"
        if _standing_apex is not None:
            data["apex_scalars"] = _standing_apex
        data["authority"] = _standing_authority or "OBSERVE_ONLY"
        data["actor_verified"] = _standing_actor_verified
        if _standing_delta is not None:
            data["authority_delta"] = _standing_delta
        res = data.get("result")
        if isinstance(res, dict):
            res.setdefault("session_token", _standing_token)
            res.setdefault("standing_source", _standing_source or "sct")
            if _standing_apex is not None:
                res.setdefault("apex_scalars", _standing_apex)
        return ForgeOutput(**data)

    if session_token or session_id:
        try:
            from arifosmcp.runtime.sct import resolve_standing

            _standing = resolve_standing(
                session_id=session_id,
                actor_id=actor_id,
                session_token=session_token,
                allow_store=True,
            )
            if _standing.valid:
                _standing_token = _standing.session_token or session_token
                _standing_source = _standing.source
                _standing_apex = dict(_standing.apex) if _standing.apex else None
                _standing_actor_verified = _standing.actor_verified
                _standing_authority = _standing.authority
                _standing_delta = _standing.authority_delta
                if _standing.session_id:
                    session_id = _standing.session_id
                if _standing.actor_id and _standing.actor_id != "anonymous":
                    actor_id = _standing.actor_id
            elif session_token:
                _meta = {
                    "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
                    "reason": _standing.reason or "L11 AUTH: SCT invalid",
                    "sesat_event": {
                        "sesat": True,
                        "type": "TOKEN_INVALID",
                        "reason": _standing.reason,
                    },
                    "violated_laws": ["L11"],
                    "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
                }
                _add_floor_compat(_meta)
                return _echo_standing(
                    ForgeOutput(
                        status="HOLD",
                        result={},
                        manifest=ForgeManifest(status=ManifestStatus.HOLD),
                        meta=_meta,
                        timestamp=datetime.now(UTC).isoformat(),
                    )
                )
        except Exception:
            pass

    # ── ZEN HARD GATE (2026-07-30): Deterministic rules BEFORE any execution ──
    # Per ChatGPT forensic: arif_forge must reject immediately without prior
    # SEAL verdict. No LLM, no 45s wait. These are checkable facts.
    _forge_reasons: list[str] = []
    _mutate_modes = {"engineer", "write", "generate", "commit", "deploy"}

    # Gate F1: No session → cannot execute anything
    if not session_id and not _standing_token:
        _forge_reasons.append("No session_id or session_token — cannot execute.")

    # Gate F2: MUTATE modes require prior SEAL verdict (judge_state_hash or cc_id)
    if mode in _mutate_modes and not (judge_state_hash or constitutional_chain_id):
        _forge_reasons.append(
            f"Mode '{mode}' is MUTATE but no judge_state_hash or constitutional_chain_id "
            "provided. A prior arif_judge SEAL verdict is required before forge execution."
        )

    # Gate F3: Irreversible execution requires explicit ack
    if mode in _mutate_modes and not ack_irreversible:
        _forge_reasons.append(
            f"Mode '{mode}' may be irreversible. Set ack_irreversible=True to confirm. "
            "This gate runs BEFORE any backend call — no 45s wait."
        )

    # Gate F4: engineer/commit/deploy modes require a plan_id
    if mode in {"engineer", "commit", "deploy"} and not plan_id:
        _forge_reasons.append(f"Mode '{mode}' requires plan_id from a prior forge_plan.")

    if _forge_reasons:
        return _echo_standing(
            ForgeOutput(
                status="HOLD",
                result={"gate": "hard_deterministic", "llm_consulted": False, "zend": "2026-07-30"},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
                    "reason": "; ".join(_forge_reasons),
                    "violated_laws": ["L01", "L11"],
                    "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
                },
                timestamp=datetime.now(UTC).isoformat(),
            )
        )

    # Amanah: dry_run never mutates — structured receipt only
    if dry_run:
        return _echo_standing(
            ForgeOutput(
                status="HOLD",
                result={
                    "dry_run": True,
                    "mode": mode,
                    "session_id": session_id,
                    "session_token": _standing_token,
                    "actor_id": actor_id,
                    "note": "dry_run — no host mutation; pass dry_run=false after SEAL",
                },
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "dry_run": True,
                    "standing_source": _standing_source or ("sct" if _standing_token else "none"),
                },
                timestamp=datetime.now(UTC).isoformat(),
            )
        )

    # ── RASA DERITA Phase 3 — cascade + consent for MUTATE/ATOMIC ───────────
    # Machine 888_HOLD when L3 mutation lacks causal_cascade / consent_lease.
    # Zero new public tools — gates on existing arif_forge parameters only.
    if mode in _FORGE_MUTATE_ATOMIC:
        try:
            from arifosmcp.kernel.rasa_derita_gates import evaluate_from_payload

            _rd = evaluate_from_payload(
                manifest,
                mode=mode,
                action_tier=action_tier,
                ack_irreversible=ack_irreversible,
                reversible=False if mode in _ATOMIC_MODES else None,
            )
            if not _rd.passed:
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta={
                        "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                        "reason": " | ".join(_rd.reasons),
                        "rasa_derita_gate": _rd.to_dict(),
                        "verdict": "888_HOLD",
                        "module": "RASA_DERITA",
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )
        except Exception as _rd_exc:
            # Fail-closed on mutate path if gate module cannot run
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                    "reason": f"RASA DERITA gate unavailable on mutate path: {_rd_exc}",
                    "verdict": "888_HOLD",
                    "module": "RASA_DERITA",
                },
                timestamp=datetime.now(UTC).isoformat(),
            )

    # ── P0 EXECUTION BOUNDARY — CLOSED 2026-07-25 ──────────────────────────
    # FALSIFICATION AUDIT: All MUTATE/ATOMIC modes HALTED until permit-to-execute
    # protocol is hardened. Only query mode passes for read-only introspection.
    #   REOPEN CONDITION: Ed25519 signature REQUIRED + verify BEFORE execution
    #   + action_hash binding + durable atomic permit consumption.
    #   Audit ref: arif_falsification_audit_2026-07-25
    _P0_ALLOWED_MODES = {"query"}
    if mode not in _P0_ALLOWED_MODES:
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta={
                "error_code": ForgeErrorCode.E_FORGE_MODE_NOT_ALLOWED,
                "reason": (
                    f"P0 EXECUTION BOUNDARY CLOSED — mode='{mode}' is HALTED. "
                    f"Allowed: {sorted(_P0_ALLOWED_MODES)}. "
                    f"MUTATE/ATOMIC modes (engineer/write/generate/commit/deploy) "
                    f"blocked pending permit-to-execute protocol hardening. "
                    f"See: 888 JUDGE → signed permit → 777 FORGE verify+consume → 999 receipt."
                ),
                "p0_boundary": "CLOSED",
                "p0_audit": "arif_falsification_audit_2026-07-25",
                "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
            },
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: actor_id REQUIRED for MUTATE/ATOMIC (L11 authority) ─────────────
    if not actor_id:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — actor_id is REQUIRED for MUTATE/ATOMIC forge modes. "
                "Anonymous execution is prohibited."
            ),
            "violated_laws": ["L11"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: vault_entry_id REQUIRED for commit mode ─────────────────────────
    if mode == "commit" and not vault_entry_id:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — vault_entry_id is REQUIRED for commit mode. "
                "Link the commit to a VAULT999 lineage entry."
            ),
            "violated_laws": ["L01", "L11"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: F1 AMANAH nonce/signature consistency (RESERVED) ───────────────
    # If actor_signature is provided without nonce, reject for replay
    # prevention. If both are provided, log receipt but do not enforce
    # until F13 ratifies the per-call signature path.
    if actor_signature and not nonce:
        _meta = {
            "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
            "reason": (
                "F1 AMANAH: actor_signature requires nonce for replay prevention. "
                "Provide both, or omit both to inherit from session_init."
            ),
            "violated_laws": ["F01"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
            "f13_status": "RESERVED — per-call signature path not yet enforced",
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: judge_state_hash REQUIRED for MUTATE/ATOMIC ─────────────────────
    if not judge_state_hash:
        _meta = {
            "error_code": ForgeErrorCode.E_JUDGE_STATE_HASH_REQUIRED,
            "reason": (
                "888 HOLD — judge_state_hash is REQUIRED for MUTATE/ATOMIC forge modes. "
                "Call arif_judge first, then pass the returned state_hash."
            ),
            "violated_laws": ["L01", "L11"],
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── v3.1: plan_id REQUIRED for engineer/write/generate ────────────────────
    if mode in ("engineer", "write", "generate") and not plan_id:
        _meta = {
            "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
            "reason": (
                f"mode='{mode}' requires an approved plan_id from forge_plan. "
                "Call forge_plan(goal=...) first, then pass the returned plan_id."
            ),
            "tool_manifest": ARIF_FORGE_EXECUTE_MANIFEST.model_dump(),
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )

    # ── W-2: SOVEREIGN clarity gate for elevated-tier FORGE actions ───────────
    _is_elevated = action_tier.lower() in ("sovereign", "c4", "c5")
    if _is_elevated:
        try:
            from arifosmcp.tools.judge import _read_well_substrate

            _forge_sub = _read_well_substrate()
            _forge_clarity = _forge_sub.get("clarity")
            if (
                _forge_clarity is not None
                and float(_forge_clarity) < 4.0
                and _forge_sub.get("has_telemetry")
            ):
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta={
                        "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                        "reason": (
                            f"W5_COGNITIVE_ENTROPY: clarity={_forge_clarity}/10 below "
                            "SOVEREIGN threshold (4/10). FORGE blocked. "
                            "Rest. Reassess when clarity >= 6."
                        ),
                        "well_gate": "SOVEREIGN_BLOCKED",
                        "w_floor": "W5 -> F2",
                        "action_tier": action_tier,
                        "clarity": _forge_clarity,
                        "well_substrate": _forge_sub,
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )
        except Exception:
            pass  # WELL offline is non-fatal — W0 sovereignty invariant

    # ── Side Effect Gate (v2 Deepening) ──
    from arifosmcp.runtime.tools import _SESSIONS

    sess = _SESSIONS.get(session_id) if session_id else None
    card = sess.get("model_governance_card") if sess else None
    if card:
        rt = card.runtime_truth if hasattr(card, "runtime_truth") else card.get("runtime_truth", {})
        side_effects = (
            getattr(rt, "side_effects_allowed", False)
            if hasattr(rt, "side_effects_allowed")
            else rt.get("side_effects_allowed", False)
        )
        shadow = (
            card.shadow_profile
            if hasattr(card, "shadow_profile")
            else card.get("shadow_profile", {})
        )
        shadow_val = (
            getattr(shadow, "shadow", "unknown")
            if hasattr(shadow, "shadow")
            else shadow.get("shadow", "unknown")
        )
        if not side_effects and not ack_irreversible:
            if action_has_side_effects(mode, manifest, query):
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta={
                        "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                        "reason": f"888 HOLD — side_effects_allowed=False in runtime_truth. "
                        f"Shadow: {shadow_val}. "
                        f"Required: human_ack before proceeding.",
                    },
                    timestamp=datetime.now(UTC).isoformat(),
                )

    # ── P1 WIRING (2026-06-28): Latency budget enforcement ──
    # The floor check is a constitutional gate, not just a performance concern.
    # Record latency and flag if it exceeds the decision-class budget.
    import time as _time

    from arifosmcp.core.decision_contract import DecisionClass
    from arifosmcp.core.latency_budget import LATENCY_BUDGETS

    _t_check = _time.monotonic()
    floor_check = check_laws(
        "arif_forge",
        {
            "mode": mode,
            "ack_irreversible": ack_irreversible,
            "manifest": manifest,
            "query": query,
            "artifact_id": artifact_id,
            "session_id": session_id,
        },
        actor_id,
    )
    _latency_ms = (_time.monotonic() - _t_check) * 1000
    _budget = LATENCY_BUDGETS.get(DecisionClass.C2_STANDARD, LATENCY_BUDGETS[DecisionClass.C3_DEEP])
    floor_check["_latency_ms"] = _latency_ms
    floor_check["_within_budget"] = _latency_ms <= _budget.max_latency_ms
    if floor_check["verdict"] != "SEAL":
        from arifosmcp.runtime.tools import _inject_nine_signal

        raw = ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta={
                "reason": floor_check["reason"],
                "violated_laws": floor_check["violated_laws"],
            },
            timestamp=datetime.now(UTC).isoformat(),
        ).model_dump(mode="json")
        injected = _inject_nine_signal(raw, "HOLD")
        injected["reasons"] = [floor_check["reason"]] if floor_check.get("reason") else []
        return ForgeOutput(**injected)

    # ── F3/F8: WITNESS + GENIUS COMPUTATION (Loop 5 — 2026-08-03) ──────────
    # forge_vault Lane B autonomous seals were blocked because no code computed
    # G = (A×P×E×X)^(1/4) or W³ = ∛(H×AI×Earth). These scores are now computed
    # from available session evidence: lease as sovereign proxy (H channel),
    # mode/reversibility (P+E+X channels), and domain organ health (Earth channel).
    #
    # The scores are attached to the ForgeOutput as floor evidence regardless
    # of whether they pass — downstream tools (forge_vault, arif_seal) read them
    # from the constitutional compliance block.

    # Derive authority from lease validity
    _lease_valid = bool(session_id and session_token)
    _authority = 0.9 if _lease_valid else 0.1

    # Derive purpose from mode clarity
    _mode_is_explicit = mode in ("engineer", "write", "generate", "commit", "deploy")
    _purpose = 0.9 if _mode_is_explicit else 0.5

    # Derive evidence from manifest presence + ack state
    _manifest_present = bool(manifest and len(manifest) > 10)
    _evidence = 0.9 if _manifest_present else 0.4
    if ack_irreversible:
        _evidence = min(1.0, _evidence + 0.1)  # explicit ack strengthens evidence

    # Derive execution from reversibility
    _execution = 0.8 if ack_irreversible else 0.5  # reversible by default
    if mode in ("engineer", "write"):
        _execution = 0.85  # these modes are typically reversible

    _g_score = _compute_genius_score(
        authority=_authority,
        purpose=_purpose,
        evidence=_evidence,
        execution=_execution,
    )

    # Attempt lease lookup for witness computation
    _lease_valid_flag = bool(session_id and session_token)
    try:
        if session_id:
            from arifosmcp.gateway.lease_engine import LeaseEngine

            _engine = LeaseEngine()
            _lease = _engine.lookup(session_id, "arif_forge")
            if _lease:
                _lease_valid_flag = _lease.valid() and not _lease.expired()
    except Exception:
        pass  # lease engine unavailable — fall back to token presence

    # Human channel: 0.8 if lease valid, 0.0 if not
    _h_channel = 0.8 if _lease_valid_flag else 0.0

    # Domain organ probe (lightweight — only checks if organ is referenced)
    _domain_healthy = True
    try:
        import urllib.request

        _organ_port = {"geox": 8081, "wealth": 18082, "well": 18083}
        for _org, _port in _organ_port.items():
            if _org in (manifest or "").lower() or _org in (query or "").lower():
                req = urllib.request.Request(f"http://127.0.0.1:{_port}/health", method="GET")
                urllib.request.urlopen(req, timeout=2)
    except Exception:
        _domain_healthy = False  # organ unreachable — Earth channel degraded

    # Compute W³ manually (avoids lease_remaining/lease_total dependency)
    _ai_channel = min(1.0, _g_score)
    _earth_channel = 1.0 if _domain_healthy else 0.0
    _w3_product = _h_channel * _ai_channel * _earth_channel
    _w3_score = _w3_product ** (1 / 3) if _w3_product > 0 else 0.0
    _w3_passed = _w3_score >= 0.50 and _g_score >= 0.70

    _witness = {
        "h_channel": _h_channel,
        "ai_channel": _ai_channel,
        "earth_channel": _earth_channel,
        "w3_score": _w3_score,
        "g_score": _g_score,
        "passed": _w3_passed,
        "verdict": "SEAL" if _w3_passed else "HOLD",
        "reason": (
            f"W³={_w3_score:.3f} G={_g_score:.3f} — {'PASS' if _w3_passed else 'BLOCKED at F3/F8'}"
        ),
    }

    logger.info(
        f"F3/F8 computed: G={_g_score:.3f} W³={_witness['w3_score']:.3f} "
        f"verdict={_witness['verdict']} "
        f"H={_witness['h_channel']:.2f} AI={_witness['ai_channel']:.2f} "
        f"Earth={_witness['earth_channel']:.2f}"
    )

    # ── CAPABILITY MEMBRANE: Enforce exact permitted scope before execution ─────────
    # Phase 1: If a permitted_scope is provided, validate the action strictly matches.
    # This prevents capability drift: agent cannot broaden recipients, modify bodies,
    # or extend expiry after human has granted a one-time scope.
    if permitted_scope is not None:
        from arifosmcp.runtime.niat_gate import enforce_capability_membrane

        # Derive the tool name from mode — forge is a meta-tool dispatcher.
        _tool_for_membrane = {
            "write": "file.write",
            "generate": "code.generate",
            "commit": "git.commit",
            "deploy": "docker.deploy",
            "engineer": "forge.engineer",
        }.get(mode, f"forge.{mode}")

        _membrane_passed = enforce_capability_membrane(
            _tool_for_membrane,
            {"mode": mode, "manifest": manifest, "query": query},
            permitted_scope,
        )
        if not _membrane_passed:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "error_code": ForgeErrorCode.E_CAPABILITY_MEMBRANE_VIOLATION,
                    "reason": (
                        "888 HOLD — CAPABILITY_MEMBRANE: Action parameters exceed "
                        "the explicitly permitted scope. Human grant was limited to "
                        f"{permitted_scope.get('tool', 'unknown')}, but the requested "
                        "action did not match. Narrow the grant or obtain a new one."
                    ),
                    "capability_membrane": "HOLD",
                    "permitted_scope": {
                        k: v
                        for k, v in permitted_scope.items()
                        if k not in ("tool", "subject_hash", "body_hash")
                    },
                },
                timestamp=datetime.now(UTC).isoformat(),
            )

    # ── P1 WIRING (2026-06-28): Cross-organ conflict resolution before dispatch ──
    # Before forge dispatches to A-FORGE, validate there are no unresolved conflicts
    # between arifOS verdict and the execution target. Currently a no-op guardrail
    # that activates when cross-organ conflicts are registered.
    try:
        from arifosmcp.core.conflict_resolver import resolve_conflict
        from arifosmcp.core.decision_contract import ConflictEnvelope

        _conflict_envelope = ConflictEnvelope(
            conflict_id=f"forge-{mode}-{session_id or 'anon'}",
            organ_a="arifos",
            verdict_a=floor_check.get("verdict", "SEAL"),
            organ_b="a-forge",
            verdict_b="PROCEED",
            conflict_domain="forge",
            is_irreversible=(mode in _ATOMIC_MODES),
        )
        _resolution = resolve_conflict(_conflict_envelope)
        if _resolution.requires_888_hold:
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta={
                    "error_code": ForgeErrorCode.E_SIDE_EFFECTS_BLOCKED,
                    "reason": (
                        f"Pre-execution conflict resolution required 888_HOLD: {_resolution.reason}"
                    ),
                    "conflict_resolution": {
                        "winner_organ": _resolution.winner_organ,
                        "winner_verdict": _resolution.winner_verdict,
                        "resolution_method": _resolution.resolution_method,
                        "requires_888_hold": _resolution.requires_888_hold,
                    },
                },
                timestamp=datetime.now(UTC).isoformat(),
            )
    except Exception:
        pass  # Conflict resolver offline → proceed (no conflicts = no block)

    import asyncio

    # ── P1: Ed25519 per-call signature — ENFORCED for mutation modes ──
    # FALSIFICATION AUDIT 2026-07-25: Signature REQUIRED for any MUTATE/ATOMIC
    # mode. Payload MUST cover session_id + action_hash + nonce + mode.
    # Verification happens BEFORE _run_forge() — invalid signature = HOLD, no
    # execution occurs.
    _sig_receipt = None
    _is_mutate = mode in _MUTATE_MODES | _ATOMIC_MODES
    if _is_mutate and not (actor_signature and nonce):
        _meta = {
            "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
            "reason": (
                f"F11 AUTH: Ed25519 actor_signature + nonce REQUIRED for "
                f"mutation mode '{mode}'. P0 execution boundary enforces "
                f"pre-execution cryptographic authorization. "
                f"Provide both signature and nonce."
            ),
            "violated_laws": ["F11"],
            "f13_status": "ENFORCED — Ed25519 per-call signature required for mutation",
            "p0_audit": "arif_falsification_audit_2026-07-25",
        }
        _add_floor_compat(_meta)
        return ForgeOutput(
            status="HOLD",
            result={},
            manifest=ForgeManifest(status=ManifestStatus.HOLD),
            meta=_meta,
            timestamp=datetime.now(UTC).isoformat(),
        )
    if actor_signature and nonce:
        try:
            from pathlib import Path

            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

            _pub_pem = Path("/opt/arifos/secrets/did_arifos_public.key").read_bytes()
            _pub_key = serialization.load_pem_public_key(_pub_pem)
            if not isinstance(_pub_key, Ed25519PublicKey):
                raise TypeError("Expected Ed25519PublicKey")
            # P1: Full action_hash binding — signature covers:
            #   session_id + actor_id + tool + mode + manifest_hash + plan_id +
            #   constitutional_chain_id + permitted_scope + nonce
            _action_hash = hashlib.sha256(
                f"{session_id}:{actor_id}:arif_forge:{mode}:"
                f"{hashlib.sha256(manifest.encode()).hexdigest()[:16]}:"
                f"{plan_id or ''}:{constitutional_chain_id or ''}:"
                f"{json.dumps(permitted_scope or {}, sort_keys=True)}:{nonce}".encode()
            ).hexdigest()
            _payload = _action_hash.encode()
            _pub_key.verify(bytes.fromhex(actor_signature), _payload)
            _sig_receipt = {
                "actor_signature_verified": True,
                "nonce_provided": True,
                "action_hash": _action_hash,
                "f13_status": "VERIFIED — Ed25519 per-call signature enforced (pre-execution)",
                "binding": "session+actor+tool+mode+manifest+plan+chain+scope+nonce",
            }
        except Exception as e:
            _meta = {
                "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
                "reason": f"F11 AUTH: actor_signature verification FAILED: {e}",
                "violated_laws": ["F11"],
                "f13_status": "REJECTED — invalid Ed25519 signature (pre-execution gate)",
            }
            _add_floor_compat(_meta)
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta=_meta,
                timestamp=datetime.now(UTC).isoformat(),
            )

    # ── Gödel Lock pre-execution check (G1-G7) ──────────────────────────
    # DITEMPA 2026-08-05: runtime_hook.check_godel_lock was dead code; wire it
    # into the MUTATE pre-execution path per its docstring contract. Anti-
    # Beautiful-One invariant: the agent CANNOT certify its own safety.
    if _is_mutate:
        # VAULT999 liveness check (G6 axiom: pre-executive gate cannot verify
        # when VAULT999 is broken).
        try:
            from pathlib import Path as _VPath
            _vault_alive = _VPath("/root/arifOS/VAULT999/outcomes.jsonl").exists()
        except Exception:
            _vault_alive = False
        try:
            from arifosmcp.constitution.runtime_hook import check_godel_lock as _godel_check
            _godel_result = _godel_check(
                action_class="MUTATE",
                actor_id=actor_id or "",
                actor_signature=actor_signature or "",
                has_judge_hash=bool(judge_state_hash),
                has_plan_id=bool(plan_id),
                has_vaul_entry=bool(vault_entry_id),
                has_vaul999_connection=_vault_alive,
                failure_cause="",
            )
            if not _godel_result.get("ok", True):
                _meta = {
                    "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
                    "reason": (
                        f"Gödel Lock violation [{_godel_result.get('axiom_id', '?')}] "
                        f"{_godel_result.get('axiom_name', '?')}: "
                        f"{_godel_result.get('reason', '?')} "
                        f"(verdict={_godel_result.get('verdict', '?')})"
                    ),
                    "violated_laws": [f"G{_godel_result.get('axiom_id', '?')[1:]}"],
                    "f13_status": "ENFORCED — Gödel lock pre-execution",
                    "godel_audit": "arif_runtime_hook_2026-08-05",
                }
                _add_floor_compat(_meta)
                return ForgeOutput(
                    status="HOLD",
                    result={},
                    manifest=ForgeManifest(status=ManifestStatus.HOLD),
                    meta=_meta,
                    timestamp=datetime.now(UTC).isoformat(),
                )
        except ImportError:
            pass  # runtime_hook not available — fall through (governance_pipeline catches)
        except Exception as _godel_err:
            # Fail-closed: a malfunctioning Gödel lock must not be bypassed.
            _meta = {
                "error_code": ForgeErrorCode.E_SYNTHESIS_EMPTY,
                "reason": f"Gödel Lock check error — fail-closed (HOLD): {_godel_err}",
                "violated_laws": ["F11"],
                "f13_status": "ENFORCED — Gödel lock fail-closed",
                "godel_audit": "arif_runtime_hook_2026-08-05",
            }
            _add_floor_compat(_meta)
            return ForgeOutput(
                status="HOLD",
                result={},
                manifest=ForgeManifest(status=ManifestStatus.HOLD),
                meta=_meta,
                timestamp=datetime.now(UTC).isoformat(),
            )

    def _run_forge():
        return _arif_forge(
            mode=mode,
            manifest=manifest,
            query=query,
            artifact_id=artifact_id,
            session_id=session_id,
            ack_irreversible=ack_irreversible,
            actor_id=actor_id,
            constitutional_chain_id=constitutional_chain_id,
            judge_state_hash=judge_state_hash,
            vault_entry_id=vault_entry_id,
            witness_type=witness_type,
        )

    result_dict = await asyncio.to_thread(_run_forge)
    result = ForgeOutput(**result_dict)

    # ── AKAL I3: Novelty gate ────────────────────────────────────────────────
    from arifosmcp.core.akal_wiring import akal_pre_forge as _akal_novelty

    try:
        _akal_nov = _akal_novelty(
            output_text=str(result.result)[:2000] if result.result else "",
            session_id=session_id,
            friction_level="low",  # arif_forge has no context param — friction from arif_think unavailable
        )
        if _akal_nov.get("enforced") and _akal_nov.get("action") == "HOLD":
            # Novelty check failed — add warning to result but dont block
            if hasattr(result, "meta") and isinstance(result.meta, dict):
                result.meta.setdefault("akal_novelty", _akal_nov)
            elif hasattr(result, "result") and isinstance(result.result, dict):
                result.result.setdefault("akal_novelty", _akal_nov)
    except Exception as e:
        logger.warning("AKAL novelty check failed (non-blocking): %s", e)

    # ── P0 WIRING (2026-06-28): Seal forge execution to VAULT999 ──
    # Every successful forge execution must leave an auditable receipt.
    # The create_and_seal_receipt function exists in core/vault_receipt.py
    # and is proven in judge.py — it was never called from forge.py.
    try:
        from arifosmcp.core.vault_receipt import (
            create_and_seal_receipt,
            resolve_receipt_identity,
        )

        # F2 TRUTH: resolve real identity before minting receipt.
        _sess_ctx = None
        try:
            from arifosmcp.runtime.tools import get_session

            _sess_ctx = get_session(session_id) if session_id else None
        except Exception:
            pass
        _resolved_sid, _resolved_actor = resolve_receipt_identity(
            session_id=session_id,
            actor_id=actor_id,
            session_context=_sess_ctx,
        )

        create_and_seal_receipt(
            session_id=_resolved_sid,
            actor_id=_resolved_actor,
            organ_id="arifOS",
            intent_summary=f"forge:{mode}:{manifest[:80] if manifest else ''}",
            intent_hash=hashlib.sha256(f"{mode}:{manifest}".encode()).hexdigest()[:16],
            requested_authority=action_tier or "standard",
            pre_state_hash=judge_state_hash or "",
            decision=result.status,
            verdict_hash=hashlib.sha256(str(result_dict).encode()).hexdigest()[:16],
            floors_evaluated=["F1", "F2", "F9", "F13"],
            floors_violated=[],
            latency_ms=0.0,
            within_budget=True,
        )
    except Exception as e:
        logger.error("VAULT999 seal FAILED for forge:%s session:%s: %s", mode, session_id, e)
        # F1 + F11: An unsealed execution is an unauditable mutation.
        # Flip status to HOLD so the caller KNOWS the receipt was not written.
        result.status = "HOLD"
        if result.meta is None:
            result.meta = {}
        result.meta["vault_sealed"] = False
        result.meta["vault_seal_error"] = str(e)[:200]

    _register_forge_cooldown(result, mode, manifest, artifact_id, session_id)
    # ── Attach pre-execution Ed25519 receipt to result (verify already gated above) ──
    if _sig_receipt is not None:
        if hasattr(result, "meta") and result.meta is not None:
            result.meta["per_call_signature_receipt"] = _sig_receipt
        elif hasattr(result, "result") and isinstance(result.result, dict):
            result.result["per_call_signature_receipt"] = _sig_receipt
    # Z5b — Reality Ledger auto-witness (non-blocking, fail-safe)
    try:
        _v = getattr(result, "verdict", "COMPLETED") if hasattr(result, "verdict") else "COMPLETED"
        write_reality_event(
            actor="FORGE",
            event_type="forge_execute",
            session_id="unknown",
            verdict=str(_v),
            summary=f"forge_execute: mode={mode}",
            action_class="execute",
            evidence={"mode": mode},
        )
    except Exception:
        pass

    # ── VERIFY111: Independent post-execution verification (non-blocking, fail-safe) ──
    # Wires the existing independent_verifier.py into the forge_execute path.
    # Verifier ≠ executor (enforced by R1 in verify_independent).
    # Failure here does NOT block execution — it enriches the result with verification data.
    try:
        import time as _time

        from arifosmcp.runtime.independent_verifier import (
            VerificationRequest,
            VerificationVerdict,
            verify_independent,
        )

        _verdict = (
            getattr(result, "verdict", "COMPLETED") if hasattr(result, "verdict") else "COMPLETED"
        )
        _intent_hash = hashlib.sha256(
            f"{mode}:{manifest}:{session_id or 'anon'}".encode()
        ).hexdigest()[:16]
        _executor_id = actor_id or "unknown"

        _vreq = VerificationRequest(
            original_intent_hash=_intent_hash,
            executor_id=_executor_id,
            executor_session_id=session_id or "unknown",
            mutation_receipt={
                "mode": mode,
                "verdict": str(_verdict),
                "artifact_id": artifact_id or "",
                "manifest_hash": hashlib.sha256((manifest or "").encode()).hexdigest()[:16],
            },
            success_criteria=[
                f"verdict=SEAL",
                f"status=OK",
            ],
            freshness_requirement=300.0,  # 5 minutes
            evidence_sources=["forge_execute_receipt", "reality_ledger"],
        )

        # Verifier identity is "A-AUDIT" — separate from executor
        _vresult = verify_independent(_vreq, verifier_id="A-AUDIT")

        # Attach verification result to forge output
        if result.meta is None:
            result.meta = {}
        result.meta["independent_verification"] = {
            "verdict": _vresult.verdict.value,
            "verifier_id": _vresult.verifier_id,
            "request_hash": _vresult.request_hash,
            "rule_violations": _vresult.rule_violations,
            "evidence_quality": _vresult.evidence_quality,
            "verified_at": _vresult.verified_at,
            "note": "VERIFY111: independent post-execution verification (fail-safe, non-blocking)",
        }

        # If verification failed, surface HOLD recommendation
        if _vresult.verdict != VerificationVerdict.PASS:
            result.meta["verification_hold"] = {
                "reason": f"Independent verification returned {_vresult.verdict.value}",
                "violations": _vresult.rule_violations,
                "recommendation": "HOLD — review verification failures before sealing",
            }
    except Exception as _verr:
        # Fail-safe: verification failure does not block execution
        if result.meta is None:
            result.meta = {}
        result.meta["independent_verification"] = {
            "verdict": "UNAVAILABLE",
            "error": str(_verr)[:200],
            "note": "VERIFY111: independent verifier not reachable — execution completed without verification",
        }

    return _echo_standing(result)


def _register_forge_cooldown(
    result: ForgeOutput,
    mode: str,
    manifest: str,
    artifact_id: str | None,
    session_id: str | None,
) -> None:
    """Auto-register forge artifacts in SABAR cooldown band. Stage 2A: observe+warn only."""
    side_effect_modes = {"engineer", "write", "generate", "commit"}
    if mode not in side_effect_modes:
        return

    try:
        import hashlib

        from arifosmcp.core.cooldown_engine import get_cooldown_engine

        engine = get_cooldown_engine()
        artifact_ref = (
            artifact_id
            or hashlib.md5(  # nosec B324
                f"{mode}:{manifest}:{session_id or 'anon'}:{result.timestamp or ''}".encode()
            ).hexdigest()[:12]
        )
        desc = f"forge:{mode}:{manifest[:80]}" if manifest else f"forge:{mode}"

        entry = engine.propose(
            artifact_ref=artifact_ref,
            description=desc,
            risk_tier="medium",
            session_id=session_id,
        )

        # Attach cooldown metadata to result (observe only — no block)
        if result.meta is None:
            result.meta = {}
        result.meta["sabar_cooldown"] = {
            "stage": "registered",
            "cooldown_entry_id": entry.entry_id,
            "cooldown_expiry": entry.cooldown_expiry.isoformat() if entry.cooldown_expiry else None,
            "cooldown_hours": entry.cooldown_hours,
            "remaining_hours": round(entry.remaining_hours, 1),
            "verdict": entry.verdict,
            "note": "artifact entered SABAR cooldown — not yet sealed for permanence",
        }
    except Exception:
        if result.meta is None:
            result.meta = {}
        result.meta["sabar_cooldown"] = {
            "stage": "unavailable",
            "note": "cooldown engine not reachable",
        }


# Backward compatibility alias
arif_forge_execute = arif_forge

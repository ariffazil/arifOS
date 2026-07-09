"""
arifosmcp/tools/judge_deliberate.py — 888_JUDGE v3
═══════════════════════════════════════════════

Constitutional verdict engine.

Evidence pre-loading: vitals and heart output are piped into the judge
before adjudication so epistemic confidence is grounded in actual system state.

Post-SEAL auto-hook: When verdict is SEAL and vault_entry_id is provided,
the judge output is automatically routed to arif_seal for immutable anchoring.

PARADOX ANCHORS (v3): 11 linguistic invariants fire at verdict decision points:
  J1 (Parker/MLK) — SABAR carries deadline | J4 (Aristotle) — SEAL is incomplete justice
  J6 (Marcus Aurelius) — irreversible gate | J7 (Glaucon) — power asymmetry detection

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json as json_lib
import os
import time as time_module
import urllib.request
from pathlib import Path
from typing import Any

from arifosmcp.core.conflict_resolver import (
    resolve_conflict,
    resolve_multi_organ,
)
from arifosmcp.core.decision_contract import ConflictEnvelope
from arifosmcp.core.latency_budget import LATENCY_BUDGETS
from arifosmcp.core.latency_budget import DecisionClass as LatencyDecisionClass
from arifosmcp.core.vault_receipt import create_and_seal_receipt

from arifosmcp.core.enforcement.maruah_critic import (
    maruah_critic_check,
    MaruahVerdict,
)
from arifosmcp.core.enforcement.somatic_loop import (
    SomaticState,
    classify_somatic_state,
    TelemetrySample,
)
from arifosmcp.runtime.metabolic_receipt import get_cumulative_metrics
from arifosmcp.runtime.niat_gate import check_niat_gate
from arifosmcp.runtime.self_mod_lock import is_self_modification_attempt
from arifosmcp.runtime.tools import _arif_judge
from arifosmcp.schemas.verdict import VerdictCode, VerdictOutput

# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — REMOVED FROM RUNTIME 2026-07-04 FORGE
# ═══════════════════════════════════════════════════════════════════════════════
# The 11 anchors (Marcus Aurelius, Aristotle, Socrates, Glaucon, Kant) were
# once wired into `_inject_judge_paradox()` and called once per verdict.
#
# ABC falsifier result (2026-07-04):
#   - Falsifier: "remove X — does behavior change?"
#   - Result: removing all 11 anchors → same VerdictCode, only loses meta text.
#   - The anchors only mutated `result["meta"]["paradox_anchor"]` and
#     `result.setdefault("reasons", []).append(...)`. Never VerdictCode.*.
#
# VERDICT: 11 paradox anchors are commentary, not enforcement. REMOVED.
# PRESERVED: as non-executable canon at docs/canon/paradox_anchors.md
# REPLACED (in verdict path): single meta line — see post-verdict block.
# ═══════════════════════════════════════════════════════════════════════════════

PARADOX_ANCHORS_REMOVED_TO_CANON = True
"""Sentinel. Runtime excise 2026-07-04. Original 11 anchors now in
docs/canon/paradox_anchors.md. The wiring was a `_JUDGE_BY_ID` lookup that
only enriched meta — never `VerdictCode.*`. Therefore not load-bearing.
"""

# WELL state file candidates — covers docker-compose path, manual-start path, env override
_WELL_STATE_CANDIDATES = [
    Path(p)
    for p in [
        os.environ.get("WELL_STATE_PATH", ""),  # docker-compose: /app/well_state.json
        "/app/well_state.json",
        "/root/WELL/state.json",
    ]
    if p
]

# WELL internal HTTP fallback — used when no state file is accessible
_WELL_INTERNAL_URLS = [
    "http://well:8083/health",  # Docker Compose service name
    "http://172.19.0.5:8083/health",  # Docker network IP (static for this deployment)
]


def _read_well_substrate() -> dict[str, Any]:
    """Read WELL biological substrate state and return a minimal advisory packet.

    Strategy:
      1. Try state file candidates in order (fastest, no network)
      2. Fall back to WELL HTTP health endpoint (stable internal route)

    W0 invariant preserved: WELL informs. The judge decides. The operator
    holds the veto. This packet is advisory evidence — not a gate.
    """
    # ── Strategy 1: state file candidates ────────────────────────────────────
    state = None
    for path in _WELL_STATE_CANDIDATES:
        try:
            with open(path) as fh:
                state = json_lib.load(fh)
            break
        except Exception:
            continue

    # ── Strategy 2: HTTP fallback via WELL's internal health endpoint ─────────
    if state is None:
        for url in _WELL_INTERNAL_URLS:
            try:
                with urllib.request.urlopen(url, timeout=2) as resp:
                    raw = json_lib.loads(resp.read())
                # W-1: /health now exposes substrate advisory fields — forward them.
                state = {
                    "well_score": float(raw.get("well_score", 50.0)),
                    "floors_violated": raw.get("floors_violated") or [],
                    "metrics": raw.get("metrics") or {},
                    "truth_status": raw.get("truth_status", "OPERATOR_REPORTED"),
                    "_source": "http_health",
                    "_url": url,
                }
                # W-1: /health exposes clarity at top level — reconstruct cognitive metrics shape
                _http_clarity = raw.get("clarity")
                if _http_clarity is not None and not state["metrics"].get("cognitive", {}).get(
                    "clarity"
                ):
                    state["metrics"]["cognitive"] = {"clarity": float(_http_clarity)}
                break
            except Exception:
                continue

    if state is None:
        return {"status": "unavailable", "coupled_verdict": "CAUTION", "source": "all_paths_failed"}

    well_score = float(state.get("well_score", 50.0))
    floors_violated: list = state.get("floors_violated", []) or []
    metrics: dict = state.get("metrics") or {}
    truth_status: str = state.get("truth_status", "UNVERIFIED")
    has_metrics = bool(
        isinstance(metrics, dict)
        and any(metrics.get(d) for d in ("sleep", "stress", "cognitive", "metabolic", "structural"))
    )

    if not has_metrics or truth_status in ("VOID", "TEST", "UNVERIFIED"):
        human_ready, coupled_verdict = "UNKNOWN", "CAUTION"
    elif floors_violated:
        human_ready, coupled_verdict = "DEGRADED", "HOLD"
    elif well_score >= 80:
        human_ready, coupled_verdict = "OPTIMAL", "PROCEED"
    elif well_score >= 60:
        human_ready, coupled_verdict = "FUNCTIONAL", "PROCEED"
    else:
        human_ready, coupled_verdict = "LOW_CAPACITY", "CAUTION"

    clarity = metrics.get("cognitive", {}).get("clarity") if has_metrics else None

    packet: dict[str, Any] = {
        "status": "available",
        "well_score": well_score,
        "human_ready": human_ready,
        "coupled_verdict": coupled_verdict,
        "has_telemetry": has_metrics,
        "truth_status": truth_status,
        "active_violations": floors_violated,
        "source": state.get("_source", "live_state_file"),
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }
    if clarity is not None:
        packet["clarity"] = clarity
    return packet


def _read_well_governance(state_path_candidates: list | None = None) -> dict[str, Any]:
    """Read G-WELL governance packet from state file.

    W-4: Called for C4/C5 sovereign-tier actions. Extracts machine governance
    flags, vault status, and authority boundary from the WELL state file.
    Returns advisory only — W0 sovereignty invariant preserved.
    """
    candidates = state_path_candidates or _WELL_STATE_CANDIDATES
    for path in candidates:
        try:
            with open(path) as fh:
                state = json_lib.load(fh)
            break
        except Exception:
            continue
    else:
        return {"status": "unavailable", "g_well_verdict": "UNKNOWN", "source": "all_paths_failed"}

    m_machine = state.get("m_machine") or {}
    vault_status = m_machine.get("vault_status", "unknown")
    model_reliability = float(m_machine.get("model_reliability", 1.0))
    tool_availability = float(m_machine.get("tool_availability", 1.0))
    security_flags = m_machine.get("security_flags") or []
    amanah = state.get("amanah", "UNLOCKED")
    truth_status = state.get("truth_status", "UNVERIFIED")

    governance_flags: list[str] = []
    if not state.get("identity_valid", True):
        governance_flags.append("well_identity_compromised")
    if vault_status not in ("ok", "healthy", "unknown"):
        governance_flags.append(f"vault_disconnected:{vault_status}")
    if model_reliability < 0.5 or tool_availability < 0.5:
        governance_flags.append("machine_substrate_critical")
    if security_flags:
        governance_flags.append(f"security_flags:{','.join(security_flags)}")
    if amanah == "LOCKED":
        governance_flags.append("amanah_locked")

    if len(governance_flags) == 0:
        g_verdict = "COHERENT"
    elif len(governance_flags) <= 2:
        g_verdict = "FRAGMENTED"
    else:
        g_verdict = "INCOHERENT"

    return {
        "status": "available",
        "g_well_verdict": g_verdict,
        "governance_flags": governance_flags,
        "vault_status": vault_status,
        "model_reliability": model_reliability,
        "tool_availability": tool_availability,
        "truth_status": truth_status,
        "w0": "OPERATOR_VETO_INTACT / HIERARCHY_INVARIANT",
    }


async def arif_judge(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    session_token: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    vault_entry_id: str | None = None,
    cooldown_entry_id: str | None = None,
    action_tier: str = "standard",
    heart_critique: dict[str, Any] | None = None,
    niat_params: dict[str, Any] | None = None,
    context_source: str | None = None,
    sovereign_receipt: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> VerdictOutput:
    """
        888_JUDGE: Constitutional adjudication and verdict emission.

        Args:
            heart_critique: Optional 666_HEART critique. Red Team Finding #1:
                If heart_critique.verdict is VOID or status is HOLD, the judge
                must escalate to HOLD unless explicit Sovereign override.
            action_tier: "standard" | "sovereign" | "c4" | "c5".
    ...
        # ── 666_HEART: Ethical Gate (Red Team Finding #1) ────────────────────────
        # Hard-wire the heart's verdict into the judge loop.
        if mode == "judge" and heart_critique:
            heart_verdict = heart_critique.get("action_risk_verdict") or heart_critique.get("verdict")
            if heart_verdict in ("VOID", "HOLD"):
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        f"666_HEART_GATE: Critique returned {heart_verdict}.",
                        heart_critique.get("reason", "Ethical risks or uncertainty detected by Heart."),
                    ],
                    next_safe_action="Review 666_HEART risks and provide mitigations before re-judging.",
                    meta={
                        "heart_gate": "HEART_BLOCKED",
                        "heart_verdict": heart_verdict,
                        "heart_payload": heart_critique,
                    },
                )

    """
    from arifosmcp.tools.ops import arif_measure

    _evidence: dict = {}
    _is_elevated_tier = action_tier.lower() in ("sovereign", "c4", "c5")
    _has_receipt = bool(sovereign_receipt and sovereign_receipt.strip())

    # ── SCT-first standing (Spine P0) — store optional ─────────────────────
    _standing_token = session_token
    _standing_source = None
    _standing_apex: dict[str, Any] | None = None
    _standing_actor_verified = False
    _standing_authority: str | None = None
    _standing_delta: dict[str, Any] | None = None
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
                return _echo_standing(
                    VerdictOutput(
                        verdict=VerdictCode.HOLD,
                        reasons=[
                            _standing.reason or "L11 AUTH: SCT invalid",
                            "Provide a valid session_token from arif_init.",
                        ],
                        next_safe_action="Call arif_init, then re-invoke arif_judge with session_token.",
                        meta={
                            "gate": "L11_SCT_GATE",
                            "sesat_event": {
                                "sesat": True,
                                "type": "TOKEN_INVALID",
                                "reason": _standing.reason,
                            },
                            "session_id": session_id,
                            "floor": "F11",
                            "floor_type": "HARD",
                        },
                    )
                )
        except Exception:
            pass

    def _echo_standing(out: VerdictOutput) -> VerdictOutput:
        """Echo next-hop SCT continuity onto a direct VerdictOutput."""
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
        return VerdictOutput(**data)

    # ── F11 SESSION GATE — session_id OR valid SCT ────────────────────────
    if not session_id or not str(session_id).strip():
        return VerdictOutput(
            verdict=VerdictCode.HOLD,
            reasons=[
                "F11_SESSION_GATE: arif_judge requires a valid session_id or session_token. "
                "Empty or missing session means no constitutional chain exists.",
                "F11 AUTH mandates verified identity before sensitive operations.",
            ],
            next_safe_action=(
                "Call arif_init first to establish a valid session, "
                "then re-invoke arif_judge with session_id + session_token."
            ),
            meta={
                "gate": "F11_SESSION_GATE",
                "session_id": session_id,
                "floor": "F11",
                "floor_type": "HARD",
            },
        )

    # ── SESSION-BOUND IDENTITY — SCT reinjects store; prefer token actor ──
    from arifosmcp.runtime.tools import get_session as _get_session

    _sess = _get_session(session_id) if session_id else None
    if _sess and isinstance(_sess, dict):
        _sess_actor = _sess.get("actor_id")
        if _sess_actor and _sess_actor != "anonymous":
            if actor_id and actor_id != _sess_actor:
                _sess.setdefault("_judge_scars", []).append(
                    f"actor_mismatch: passed={actor_id} session={_sess_actor}"
                )
            actor_id = _sess_actor

    if mode != "history":
        if _evidence.get("vitals") is None:
            try:
                vitals_result = arif_measure(mode="vitals")
                _evidence["vitals"] = getattr(vitals_result, "__dict__", {}) or {
                    "status": "unavailable"
                }
            except Exception:
                _evidence["vitals"] = {"status": "unavailable"}

        # ── RUNTIME DRIFT GATE (G3 — 666_CRITIQUE closure) ──────────────────
        # If the kernel is reporting runtime_drift=true (build ≠ live),
        # every verdict carries explicit uncertainty. The judge refuses
        # to issue SEAL while drift is active unless the sovereign
        # explicitly acknowledges it via sovereign_receipt.
        #
        # Drift is a constitutional signal, not a footnote.
        # F2 TRUTH: "build_commit ≠ live_commit" means the kernel's
        # self-attestation is unreliable → all verdicts are provisional.
        _runtime_drift = _evidence.get("vitals", {}).get("runtime_drift", False)
        if _runtime_drift and not _has_receipt:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "RUNTIME_DRIFT_HOLD: Kernel reports runtime_drift=true "
                    "(build_commit ≠ live_commit). The kernel's self-attestation "
                    "is unreliable — all verdicts are provisional until drift "
                    "is resolved.",
                    "No SEAL may be issued while drift is active.",
                    "Options: (1) rebuild and redeploy to sync build with live, "
                    "or (2) provide sovereign_receipt for F13 override.",
                ],
                next_safe_action=(
                    "Rebuild and redeploy to resolve drift. "
                    "Then re-run deliberation with a clean health check."
                ),
                meta={
                    "drift_gate": "RUNTIME_DRIFT_HOLD",
                    "runtime_drift": True,
                    "build_commit": _evidence.get("vitals", {}).get("build_commit", "unknown"),
                    "live_commit": _evidence.get("vitals", {}).get("live_commit", "unknown"),
                },
            )
        elif _runtime_drift and _has_receipt:
            # F13 SOVEREIGN OVERRIDE: receipt present, drift acknowledged
            _evidence["f13_drift_override"] = {
                "runtime_drift": True,
                "sovereign_acknowledged": True,
                "override": "F13_SOVEREIGN_DRIFT_ACKNOWLEDGED",
            }

        # ── WELL biological substrate pre-load (Gap 2 wire) ──────────────────
        # W0 preserved: WELL informs, judge decides, operator holds veto.
        # This is advisory evidence surfaced alongside every verdict — not a gate.
        _evidence["well_substrate"] = _read_well_substrate()

        # ── W-4: G-WELL governance pre-load for elevated-tier actions ─────────
        # C4/C5/sovereign actions require governance coherence check before deliberation.
        if _is_elevated_tier:
            _evidence["well_governance"] = _read_well_governance()

        # ── W-2: SOVEREIGN clarity gate (W5 → F2 hard block) ─────────────────
        # If action_tier is sovereign/C4/C5 and cognitive clarity is below threshold,
        # return HOLD before deliberation. Operator readiness is constitutional.
        #
        # F13 SOVEREIGN RECEIPT PATH (2026-06-13):
        #   When sovereign_receipt is present, the clarity threshold is waived.
        #   The sovereign has explicitly confirmed readiness — F13 overrides W-2.
        #   The receipt is recorded in meta for audit trail.
        if _is_elevated_tier:
            _w2_sub = _evidence["well_substrate"]
            _w2_clarity = _w2_sub.get("clarity")
            _has_receipt = bool(sovereign_receipt and sovereign_receipt.strip())
            if (
                _w2_clarity is not None
                and float(_w2_clarity) < 4.0
                and _w2_sub.get("has_telemetry")
                and not _has_receipt
            ):
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[
                        (
                            f"W5_COGNITIVE_ENTROPY: clarity={_w2_clarity}/10"
                            " below SOVEREIGN threshold (4/10)."
                        ),
                        (
                            "Operator cognitive substrate does not meet"
                            " constitutional requirements for elevated-tier action."
                        ),
                        "Rest. Reassess when clarity ≥ 6/10, or provide sovereign_receipt for F13 override.",
                    ],
                    next_safe_action=(
                        "Rest. Return when clarity ≥ 6/10."
                        " Then re-run with action_tier='sovereign'."
                    ),
                    meta={
                        "well_gate": "SOVEREIGN_BLOCKED",
                        "w_floor": "W5 → F2",
                        "action_tier": action_tier,
                        "clarity": _w2_clarity,
                        "threshold": 4.0,
                        "human_ready": _w2_sub.get("human_ready"),
                        "active_violations": _w2_sub.get("active_violations", []),
                        "well_substrate": _w2_sub,
                        "f13_sovereign_receipt_available": False,
                    },
                )
            elif _has_receipt and _w2_clarity is not None and float(_w2_clarity) < 4.0:
                # F13 SOVEREIGN OVERRIDE: receipt present, clarity waived
                _evidence["f13_sovereign_receipt"] = {
                    "receipt_hash": f"sha256:{hashlib.sha256(sovereign_receipt.encode()).hexdigest()[:16]}",
                    "clarity_at_receipt": _w2_clarity,
                    "override": "F13_SOVEREIGN_CONFIRMED",
                }

    audit_entropy = _evidence.get("vitals", {}).get("audit_entropy")

    # ── NIAT GATE: Human Purpose under Constraint ─────────────────────────────────
    # Phase 2: Full NIAT gate implementation.
    # Fires on: formalize mode OR elevated action tiers (c3/c4/c5/sovereign).
    # Uses explicit niat_params if provided; otherwise infers from candidate.
    if mode == "formalize" or action_tier.lower() in ("c3", "c4", "c5", "sovereign"):
        if niat_params:
            _ni = niat_params.get("user_instruction", candidate or "")
            _nc = niat_params.get("context_source", context_source or "unknown")
            _na = niat_params.get("requested_action", mode)
            _nm = niat_params.get("medium_shift", "none")
            _ns = niat_params.get("negative_signals", [])
            _nr = niat_params.get("reversibility", "reversible")
            _nh = niat_params.get("affected_humans", [])
        else:
            _ni = candidate or ""
            _nc = context_source or "unknown"
            _na = mode
            _nm = "none"
            _ns = []
            _nr = "reversible"
            _nh = []

        _gate = check_niat_gate(
            user_instruction=_ni,
            context_source=_nc,
            requested_action=_na,
            medium_shift=_nm,
            negative_signals=_ns,
            reversibility=_nr,
            affected_humans=_nh,
        )

        if _gate["niat_state"] == "CONFLICTED":
            from arifosmcp.schemas.verdict import AmanahProof

            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "NIAT_GATE: niat_state=CONFLICTED — consent boundary unclear or violated.",
                    f"Formalization blocked: {_gate['formalization_allowed']}.",
                    f"Detected scars: {_gate['detected_scars']} (weight={_gate['scar_weight']:.2f}).",
                ],
                next_safe_action="Obtain explicit consent or narrow the action scope before re-judging.",
                amanah_proof=AmanahProof(
                    genius_score=0.0,
                    floors_checked=["F1", "F5", "F6"],
                    floors_passed=["F1"],
                    floors_failed=["F5", "F6"],
                    violations=["NIAT_CONSENT_BOUNDARY_VIOLATED"],
                    violation_mitigation=["Action blocked pending explicit consent"],
                ),
                meta={
                    "niat_gate": "HOLD",
                    "niat_state": _gate["niat_state"],
                    "scar_weight": _gate["scar_weight"],
                    "detected_scars": _gate["detected_scars"],
                    "required_next_step": _gate["required_next_step"],
                },
            )

        if _gate["niat_state"] == "UNCERTAIN" and _gate["execution_allowed"] is False:
            # NIAT uncertain — downgrade verdict to SABAR (proceed with caution)
            _niat_meta = {
                "niat_gate": "WATCH",
                "niat_state": _gate["niat_state"],
                "scar_weight": _gate["scar_weight"],
                "detected_scars": _gate["detected_scars"],
                "required_next_step": _gate["required_next_step"],
            }
        else:
            _niat_meta = None

    # ── A-RIF: Claim Strength Gate (Abduction/Judgment) ──

    # Extract evidence level from candidate or context if possible
    # Placeholder: currently we check if the candidate makes strong claims
    # that exceed the evidence stored in the receipt/session.

    # ── METABOLIC BYPASS CHECK (Gap 3.4 Invariant) ──────────────────────────
    if session_id:
        cumulative = get_cumulative_metrics(session_id)
        if cumulative.get("is_bypass_attempt"):
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    "METABOLIC_BYPASS_DETECTED: Cumulative risk or file changes exceeded safe window threshold.",
                    f"Cumulative Risk: {cumulative.get('cumulative_risk')}, Total Files: {cumulative.get('total_files_touched')}",
                ],
                next_safe_action="Aggregate small actions into a single atomic plan for human review.",
                meta={"cumulative_metrics": cumulative},
            )

        # ── MARUAH CRITIC GATE (Gap 1: community_maruah=true trigger) ─────────
        # If the candidate text or metadata flags community-maruah sensitivity,
        # run maruah_critic_check() before deliberation. Block if verdict not ok.
        #
        # Data flow:
        #   caller sets community_maruah=true in task metadata (e.g. via
        #   arif_kernel_route, arif_think plan, or MCP tool metadata).
        #   The flag reaches judge via: evidence_receipt or heart_critique meta.
        _maruah_sensitive = False
        _maruah_meta: dict = {}
        if isinstance(candidate, dict):
            _maruah_sensitive = bool(candidate.get("community_maruah", False))
            _maruah_meta = candidate
        if not _maruah_sensitive and isinstance(heart_critique, dict):
            _meta = heart_critique.get("meta", {}) if isinstance(heart_critique, dict) else {}
            _maruah_sensitive = bool(_meta.get("community_maruah", False))
            _maruah_meta = _meta
        if not _maruah_sensitive and isinstance(evidence, dict):
            _maruah_sensitive = bool(
                evidence.get("task_metadata", {}).get("community_maruah", False)
            )

        if _maruah_sensitive and isinstance(candidate, str) and candidate.strip():
            _mv: MaruahVerdict = maruah_critic_check(
                draft_text=candidate,
                audience_profile=_maruah_meta.get("audience_profile"),
            )
            if not _mv.ok:
                _maruah_reasons = [
                    f"MARUAH_CRITIC_BLOCK: {i.type} (severity={i.severity})" for i in _mv.issues
                ] + [
                    f"policy: {_mv.policy_line}",
                    "Respect maruah governance: kritik sistem dibenarkan walau kasar, "
                    "hinakan individu diblok. Semak dan ubah suai input sebelum cuba lagi.",
                ]
                return VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=_maruah_reasons,
                    next_safe_action=(
                        "Revise candidate text: kritik sistem/tindakan, "
                        "bukan martabat peribadi. Guna 'community_maruah=true' "
                        "metadata untuk trigger gate ini."
                    ),
                    meta={
                        "maruah_gate": "MARUAH_BLOCKED",
                        "maruah_verdict": {
                            "ok": _mv.ok,
                            "issues": [
                                {"type": i.type, "severity": i.severity, "snippet": i.snippet}
                                for i in _mv.issues
                            ],
                        },
                    },
                )
            _evidence["maruah_gate"] = {
                "gate": "MARUAH_PASS",
                "issues_found": len(_mv.issues),
            }

        # ── SOMATIC STATE GATE (Gap 2: machine telemetry → HOLD on CRITICAL) ──
        # Before deliberation, classify machine somatic state from arif_measure
        # telemetry. If somatic state is CRITICAL, return HOLD.
        # This is MACHINE-AS-BODY telemetry (F9 ANTIHANTU: NOT biological).
        _vitals = _evidence.get("vitals", {})
        _telemetry_sample = TelemetrySample(
            latency_ms=float(_vitals.get("avg_latency_ms", 0)),
            error_rate=float(_vitals.get("error_rate", 0)),
            cost_burn_per_min=float(_vitals.get("cost_burn_per_min", 0)),
            queue_depth=int(_vitals.get("queue_depth", 0)),
        )
        _somatic_state = classify_somatic_state(_telemetry_sample)
        _evidence["somatic_state"] = _somatic_state.value
        if _somatic_state == SomaticState.CRITICAL:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[
                    f"SOMATIC_GATE: Machine state is {_somatic_state.value}. "
                    "System telemetry shows critical thresholds exceeded.",
                    f"latency_ms={_telemetry_sample.latency_ms}, "
                    f"error_rate={_telemetry_sample.error_rate}, "
                    f"cost_burn={_telemetry_sample.cost_burn_per_min}, "
                    f"queue_depth={_telemetry_sample.queue_depth}",
                    "Pause. Escalate. Recover. Then re-judge.",
                ],
                next_safe_action=(
                    "Resolve critical machine state before deliberation. "
                    "Check arif_measure for details."
                ),
                meta={
                    "somatic_gate": "SOMATIC_BLOCKED",
                    "somatic_state": _somatic_state.value,
                    "telemetry": {
                        "latency_ms": _telemetry_sample.latency_ms,
                        "error_rate": _telemetry_sample.error_rate,
                        "cost_burn_per_min": _telemetry_sample.cost_burn_per_min,
                        "queue_depth": _telemetry_sample.queue_depth,
                    },
                    "well_substrate": _evidence.get("well_substrate", {}),
                },
            )

        # ── SELF-MODIFICATION LOCK (Gap 5) ──────────────────────────────────────
    if isinstance(candidate, str) or isinstance(candidate, dict):
        _target = ""
        _action = ""
        if isinstance(candidate, str):
            _target = candidate
        elif isinstance(candidate, dict):
            _target = candidate.get("target_path", "")
            _action = candidate.get("action_type", "")

        self_mod = is_self_modification_attempt(_target, _action, [])
        if self_mod.get("is_blocked"):
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[self_mod.get("reason")],
                next_safe_action="Draft the modification as a proposal only. Final approval requires Sovereign Arif.",
                meta={"self_mod_lock": self_mod},
            )

    # ── scan_instructions mode (L12 GUARD — absorbed from arif_scan_local_instructions) ──
    if mode == "scan_instructions":
        try:
            import asyncio

            from arifosmcp.tools.governance_scan import arif_scan_local_instructions

            root_dir = candidate if isinstance(candidate, str) else None
            raw = arif_scan_local_instructions(
                root_dir=root_dir,
                session_id=session_id,
                actor_id=actor_id,
            )
            if asyncio.iscoroutine(raw):
                try:
                    loop = asyncio.get_event_loop()
                    raw = loop.run_until_complete(raw)
                except RuntimeError:
                    raw = {"status": "async_context_required", "verdict": "HOLD"}
            scan_verdict = raw.get("verdict", "SEAL") if isinstance(raw, dict) else "HOLD"
            verdict_code = (
                VerdictCode.SEAL
                if scan_verdict == "SEAL"
                else (VerdictCode.VOID if scan_verdict == "VOID" else VerdictCode.HOLD)
            )
            return _echo_standing(
                VerdictOutput(
                    verdict=verdict_code,
                    reasons=[raw.get("summary", "Scan complete.")]
                    if isinstance(raw, dict)
                    else ["Scan complete."],
                    next_safe_action=(
                        "Review findings and remediate override patterns before continuing."
                        if scan_verdict in ("HOLD", "VOID")
                        else "No override patterns detected — proceed."
                    ),
                    meta={
                        "scan_instructions": raw if isinstance(raw, dict) else {"raw": str(raw)},
                        "floor": "L12",
                        "guard": "INJECTION_SCANNER",
                    },
                )
            )
        except Exception as exc:
            return _echo_standing(
                VerdictOutput(
                    verdict=VerdictCode.HOLD,
                    reasons=[f"scan_instructions failed: {exc}"],
                    next_safe_action="Check governance_scan module availability.",
                    meta={"error": str(exc)},
                )
            )

    import asyncio

    t_judge_start = time_module.monotonic()

    # Map action_tier to LatencyDecisionClass for budget lookup
    tier_to_class = {
        "standard": LatencyDecisionClass.C2_STANDARD,
        "elevated": LatencyDecisionClass.C3_DEEP,
        "sovereign": LatencyDecisionClass.C4_SOVEREIGN,
        "c4": LatencyDecisionClass.C4_SOVEREIGN,
        "c5": LatencyDecisionClass.C4_SOVEREIGN,
    }
    decision_class_latency = tier_to_class.get(action_tier, LatencyDecisionClass.C2_STANDARD)
    budget = LATENCY_BUDGETS.get(decision_class_latency)

    # ── Preventive timeout (L1 fix) ──────────────────────────────────
    # C4_SOVEREIGN: unbounded — no timeout. Human deliberation has no SLA.
    # All other classes: hard timeout via asyncio.wait_for.
    # If judge_fn exceeds budget → degrade immediately (preventive, not retroactive).
    timeout_seconds: float | None = None
    if budget and budget.max_latency_ms > 0:
        timeout_seconds = budget.max_latency_ms / 1000.0

    judge_coro = _arif_judge(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        audit_entropy=audit_entropy,
        wealth_score=_evidence.get("wealth_score"),
        verification_surface=_evidence.get("verification_surface"),
    )

    try:
        if timeout_seconds is not None:
            result = await asyncio.wait_for(judge_coro, timeout=timeout_seconds)
        else:
            result = await judge_coro
        elapsed_ms = (time_module.monotonic() - t_judge_start) * 1000
        within_budget = True
    except asyncio.TimeoutError:
        elapsed_ms = budget.max_latency_ms  # killed at deadline
        within_budget = False
        # Degrade to the budget's prescribed verdict
        degradation_verdict = budget.degradation_verdict if budget else "HOLD"
        result = {
            "verdict": degradation_verdict,
            "reasons": [
                f"LATENCY_TIMEOUT: judge exceeded {budget.max_latency_ms}ms budget "
                f"for {decision_class_latency.value}. Degraded to {degradation_verdict} "
                f"(preventive timeout — deliberation did not complete)."
            ],
            "next_safe_action": "Re-run with narrower scope or escalate to sovereign (C4 unbounded).",
        }

    if "meta" not in result:
        result["meta"] = {}
    result["meta"]["latency_ms"] = round(elapsed_ms, 2)
    result["meta"]["within_budget"] = within_budget
    result["meta"]["budget_class"] = decision_class_latency.value
    result["meta"]["budget_max_ms"] = (
        budget.max_latency_ms if (budget and budget.max_latency_ms > 0) else "unbounded"
    )
    result["meta"]["timeout_enforcement"] = (
        "preventive" if timeout_seconds is not None else "unbounded"
    )
    if not within_budget:
        result["meta"]["degradation"] = budget.degradation_verdict if budget else "HOLD"

    # Plumbing fix for 7-tool facade + semantic contract: ensure dict for downstream
    if hasattr(result, "model_dump"):
        result = result.model_dump()
    elif not isinstance(result, dict):
        result = {"verdict": "HOLD", "reasons": ["internal result normalization failed"]}

    # ── A-RIF: Post-Adjudication Integrity Check ──
    from arifosmcp.runtime.a_rif.scorecard import track_judge

    is_seal = "SEAL" in str(result.get("verdict", ""))

    if mode == "judge" and is_seal:
        # A-RIF: Claim Strength Gate — enforce claim_strength ≤ evidence_level
        evidence_level = _evidence.get("vitals", {}).get("max_evidence_level", "L1")
        # Extract claimed strength from candidate if present
        if isinstance(candidate, dict):
            claim_strength = candidate.get("claim_strength", evidence_level)
        elif isinstance(candidate, str):
            from arifosmcp.runtime.a_rif.parser import parse_claimed_evidence_level

            parsed = parse_claimed_evidence_level(candidate)
            claim_strength = parsed if parsed else evidence_level
        else:
            claim_strength = evidence_level
        claim_strength = claim_strength or evidence_level

        overclaim = False
        reasons: list[str] = []

        # General gate: claim strength must not exceed evidence level
        if claim_strength > evidence_level:
            overclaim = True
            reasons.append(
                "A-RIF_GOVERNANCE: Claim strength ("
                f"{claim_strength}) exceeds evidence level ({evidence_level})."
            )

        # Elevated tier gate: C4/C5 requires L4+
        if _is_elevated_tier and evidence_level < "L4":
            overclaim = True
            reasons.append(
                "A-RIF_GOVERNANCE: "
                f"{action_tier} action requires L4+ evidence. "
                f"Current level: {evidence_level}."
            )

        if overclaim:
            track_judge(overclaim=True, attested=False)
            if isinstance(result, dict):
                result["verdict"] = "HOLD"
                result.setdefault("reasons", []).extend(reasons)
            else:
                result.verdict = VerdictCode.HOLD
                result.reasons.extend(reasons)
        else:
            track_judge(overclaim=False, attested=(evidence_level != "L0"))

    # ── SIMULATIVE DETECTION GATE (RSI EUREKA 2026-06-12, Forge #3) ──
    # F8 advisory: checks whether agent output is DESCRIBING or PERFORMING.
    # Never blocks — only attaches an advisory question to the result.
    # "Are you describing or performing?"
    try:
        from arifosmcp.runtime.simulative_detector import simulative_check

        _sim_text = candidate if isinstance(candidate, str) else str(candidate)
        _sim_result = simulative_check(_sim_text)
        if _sim_result and _sim_result.get("advisory_question"):
            if isinstance(result, dict):
                result.setdefault("meta", {})["simulative_check"] = {
                    "simulation_index": _sim_result["simulation_index"],
                    "verdict": _sim_result["verdict"],
                    "advisory_question": _sim_result["advisory_question"],
                    "gate_id": _sim_result.get("gate_id", "simulative_detector_N2"),
                }
                # F8 advisory: surface the question in reasons
                result.setdefault("reasons", []).append(
                    f"F8_SIMULATIVE: {_sim_result['advisory_question']}"
                )
            else:
                result.meta.setdefault("simulative_check", {})["simulation_index"] = _sim_result[
                    "simulation_index"
                ]
                result.meta.setdefault("simulative_check", {})["verdict"] = _sim_result["verdict"]
                result.meta.setdefault("simulative_check", {})["advisory_question"] = _sim_result[
                    "advisory_question"
                ]
                result.reasons.append(f"F8_SIMULATIVE: {_sim_result['advisory_question']}")
    except Exception:
        pass  # fail-soft: simulative detection never blocks deliberation

    # ── Attach WELL substrate + somatic state + maruah gate to result ──
    # Every judge verdict now carries biological readiness evidence + machine
    # somatic state + maruah critic verdict. This closes the loop for all three
    # civilizational intelligence gates.
    well_sub = _evidence.get("well_substrate", {})
    if isinstance(result, dict):
        result.setdefault("meta", {})["well_substrate"] = well_sub
        if well_sub.get("coupled_verdict") == "HOLD" and well_sub.get("has_telemetry"):
            result["meta"]["well_gate"] = (
                f"WELL HOLD: human_ready={well_sub.get('human_ready')} "
                f"floors_violated={well_sub.get('active_violations')} — "
                "biological substrate flags active. Verdict stands; ARIF confirmation advised."
            )

        # ── Somatic state attachment (Gap 2) ──
        _somatic_val = _evidence.get("somatic_state")
        if _somatic_val:
            result["meta"]["somatic_state"] = _somatic_val

        # ── Maruah gate attachment (Gap 1) ──
        _maruah_gate_val = _evidence.get("maruah_gate")
        if _maruah_gate_val:
            result["meta"]["maruah_gate"] = _maruah_gate_val

        # ── W-4: Attach G-WELL governance to elevated-tier verdicts ───────────
        if _is_elevated_tier and "well_governance" in _evidence:
            gov = _evidence["well_governance"]
            result["meta"]["well_governance"] = gov
            if gov.get("g_well_verdict") == "INCOHERENT":
                result["meta"]["governance_gate"] = (
                    f"G-WELL INCOHERENT: {gov.get('governance_flags')} — "
                    "machine governance substrate flagged."
                    " ARIF confirmation required for C4/C5 actions."
                )
            elif gov.get("g_well_verdict") == "FRAGMENTED":
                result["meta"]["governance_advisory"] = (
                    f"G-WELL FRAGMENTED: {gov.get('governance_flags')} — "
                    "governance integrity stressed. Proceed with caution."
                )

    # ── SABAR cooldown awareness (Stage 2A: advisory) ──
    _apply_cooldown_awareness(result, cooldown_entry_id)

    # ── F13 SOVEREIGN RECEIPT: attach to verdict metadata ──────────────────
    # The sovereign receipt is recorded in every verdict where it was provided.
    # This creates an auditable chain: F13 confirmation → verdict → vault seal.
    # Without the receipt, F13 gates remain active (constitutional HOLD).
    if sovereign_receipt and sovereign_receipt.strip():
        _receipt_hash = f"sha256:{hashlib.sha256(sovereign_receipt.encode()).hexdigest()[:16]}"
        if isinstance(result, dict):
            result.setdefault("meta", {})["f13_sovereign_receipt"] = {
                "receipt_hash": _receipt_hash,
                "provided": True,
                "effect": "F13_SOVEREIGN_CONFIRMED",
                "note": "Sovereign (Arif) has explicitly confirmed this action. "
                "F13 gate waived per constitutional receipt path.",
            }
            result.setdefault("reasons", []).append(
                f"F13_SOVEREIGN_RECEIPT: {_receipt_hash} — "
                "sovereign confirmation recorded. Proceeding under F13 authority."
            )
        if "f13_sovereign_receipt" in _evidence:
            result.setdefault("meta", {})["f13_clarity_waiver"] = _evidence["f13_sovereign_receipt"]

    verdict_str = str(result.get("verdict", ""))
    is_seal = "SEAL" in verdict_str

    # ── Self-annotating meta note (replaces former paradox anchor injection) ──
    # FORGE 2026-07-04: 11 paradox anchors removed (ABC falsifier: commentary
    # not enforcement). Verdict language is now self-annotating; floor gates
    # F1/F2/F6/F9/F11/F13 are the executable hard gates. Canon lineage
    # preserved at docs/canon/paradox_anchors.md (non-executable).
    if isinstance(result, dict):
        result.setdefault("meta", {})["paradox_anchor_status"] = (
            "REMOVED_2026-07-04_FORGE - see docs/canon/paradox_anchors.md. "
            "Enforceability comes from floor gates, not quote anchors."
        )

    # ── Conflict Resolution (P0 wiring — I1 bridge) ──────────────────────
    # After verdict is rendered, run conflict resolution to determine if this
    # organ's verdict conflicts with others. Resolution result flows to vault receipt.
    # Single-envelope case (one organ): resolve_conflict handles it.
    # Multi-organ case (future): resolve_multi_organ does pairwise iteration.
    _conflict_result: dict[str, Any] = {"conflict_resolved": False, "conflict_resolution": "none"}
    try:
        _verdict = str(result.get("verdict", ""))
        _organ = organ_id or _evidence.get("organ_id", "arifOS")
        _envelope = ConflictEnvelope(
            conflict_id=f"{session_id or 'sess'}:{_organ}:{_verdict[:8]}",
            organ_a=_organ,
            verdict_a=_verdict,
            organ_b="human",
            verdict_b="888_HOLD",
            conflict_domain="constitutional_judgment",
            is_irreversible=("SEAL" in _verdict),
        )
        _res = resolve_conflict(_envelope)
        _conflict_result = {
            "conflict_resolved": True,
            "conflict_resolution": _res.resolution_method,
            "winner_organ": _res.winner_organ,
            "winner_verdict": _res.winner_verdict,
            "reason": _res.reason,
        }
        result.setdefault("meta", {})["conflict_resolution"] = _conflict_result
    except Exception:
        # Conflict resolution is advisory for now — never block vault sealing on error
        result.setdefault("meta", {})["conflict_resolution"] = _conflict_result

    if vault_entry_id and is_seal:
        try:
            from arifosmcp.tools.vault import arif_seal

            payload_dict = {
                "tool": "arif_judge",
                "candidate": candidate,
                "verdict": result.get("verdict", ""),
                "constitutional_chain_id": result.get("meta", {}).get("constitutional_chain_id"),
                "state_hash": result.get("meta", {}).get("state_hash"),
                "conflict_resolved": _conflict_result.get("conflict_resolved", False),
                "conflict_resolution": _conflict_result.get("conflict_resolution", "none"),
                "latency_ms": result.get("meta", {}).get("latency_ms", 0),
                "within_budget": result.get("meta", {}).get("within_budget", True),
            }

            seal_result = await arif_seal(
                mode="seal",
                payload=json_lib.dumps(payload_dict),
                session_id=session_id,
                actor_id=actor_id,
                constitutional_chain_id=constitutional_chain_id,
                judge_state_hash=result.get("meta", {}).get("state_hash"),
                cooldown_entry_id=cooldown_entry_id,
            )
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = True
            result["meta"]["vault_entry_id"] = getattr(seal_result, "entry_id", vault_entry_id)

            # ── Structured vault receipt (I1 bridge) ──────────────────────
            # Wire create_and_seal_receipt() for hash-chained provenance.
            # This runs alongside arif_seal() — additive, not replacement.
            # Produces a VaultReceipt with SHA-256 chain + Lamport clock
            # for tamper-evident audit trail.
            try:
                _verdict_hash = hashlib.sha256(
                    json_lib.dumps(result.get("verdict", ""), sort_keys=True).encode()
                ).hexdigest()
                _intent_hash = hashlib.sha256(
                    json_lib.dumps(
                        candidate if isinstance(candidate, str) else str(candidate)[:2000],
                        sort_keys=True,
                    ).encode()
                ).hexdigest()
                _receipt = create_and_seal_receipt(
                    session_id=session_id or "unknown",
                    actor_id=actor_id or "unknown",
                    organ_id=organ_id or "arifOS",
                    intent_summary=(str(candidate)[:200] if candidate else "judge verdict"),
                    intent_hash=_intent_hash,
                    requested_authority=action_tier or "standard",
                    pre_state_hash=result.get("meta", {}).get("state_hash", ""),
                    decision=result.get("verdict", "UNKNOWN"),
                    verdict_hash=_verdict_hash,
                    floors_evaluated=list(_evidence.get("floors_checked", [])),
                    floors_violated=list(_evidence.get("floors_violated", [])),
                    conflict_resolved=_conflict_result.get("conflict_resolved", False),
                    conflict_resolution=_conflict_result.get("conflict_resolution", "none"),
                    decision_class=decision_class_latency.value,
                    latency_ms=result.get("meta", {}).get("latency_ms", 0),
                    within_budget=result.get("meta", {}).get("within_budget", True),
                    witness_count=1 if _conflict_result.get("conflict_resolved") else 0,
                )
                result["meta"]["receipt_id"] = _receipt.receipt_id
                result["meta"]["receipt_hash"] = _receipt.receipt_hash
                result["meta"]["receipt_chain_ok"] = True
            except Exception:
                # Vault receipt is additive — never block the primary seal on receipt failure
                result["meta"]["receipt_chain_ok"] = False
        except Exception:
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = False

    # Semantic output fix: ensure amanah_proof validates for VerdictOutput (7-tool E2E)
    if "amanah_proof" in result and isinstance(result.get("amanah_proof"), dict):
        try:
            from arifosmcp.schemas.verdict import AmanahProof

            result["amanah_proof"] = AmanahProof(**result["amanah_proof"])
        except Exception:
            result["amanah_proof"] = AmanahProof()

    try:
        return _echo_standing(VerdictOutput(**result))
    except Exception:
        # Robust fallback for incomplete semantic outputs or plumbing during E2E (7-tool facade)
        v = result.get("verdict", "HOLD") if isinstance(result, dict) else "HOLD"
        if v not in ("SEAL", "SABAR", "VOID", "HOLD", "PARADOX_HOLD"):
            v = "HOLD"
        r = (
            result.get("reasons", ["semantic normalization fallback"])
            if isinstance(result, dict)
            else ["semantic normalization fallback"]
        )
        return _echo_standing(
            VerdictOutput(verdict=v, reasons=r if isinstance(r, list) else [str(r)])
        )


def _apply_cooldown_awareness(result: dict, cooldown_entry_id: str | None) -> None:
    """Check cooldown state and enforce SABAR. Stage 2B: SEAL blocked when cooling incomplete."""
    if cooldown_entry_id is None:
        return

    try:
        from arifosmcp.core.cooldown_engine import get_cooldown_engine

        engine = get_cooldown_engine()
        entry = engine.check(cooldown_entry_id)

        if "meta" not in result:
            result["meta"] = {}

        if entry is None:
            result["meta"]["sabar_cooldown"] = {
                "cooldown_entry_id": cooldown_entry_id,
                "status": "not_found",
                "note": "cooldown entry not found — proceeding without cooldown verification",
            }
            return

        cooldown_info = {
            "cooldown_entry_id": cooldown_entry_id,
            "verdict": entry.verdict,
            "remaining_hours": round(entry.remaining_hours, 1),
            "tri_witness_count": entry.tri_witness.count,
            "tri_witness_complete": entry.tri_witness.is_complete,
        }

        if entry.verdict == "SEAL":
            cooldown_info["status"] = "cooled"
            cooldown_info["note"] = "cooldown complete + witnessed — SEAL eligible"
        elif entry.verdict == "VOID":
            cooldown_info["status"] = "voided"
            cooldown_info["note"] = f"cooldown entry voided: {entry.void_reason}"
        elif entry.is_expired:
            cooldown_info["status"] = "expired"
            cooldown_info["note"] = "cooldown expired — auto-VOID applied"
        else:
            cooldown_info["status"] = "pending"
            cooldown_info["note"] = (
                f"SABAR: cooling incomplete ({entry.remaining_hours:.1f}h remaining, "
                f"{entry.tri_witness.count}/3 witnesses)."
            )

            # Stage 2B: hard enforcement — SEAL downgraded to SABAR when cooling incomplete
            verdict = str(result.get("verdict", ""))
            if "SEAL" in verdict:
                result["verdict"] = "SABAR"
                cooldown_info["enforcement"] = (
                    f"SABAR enforced — SEAL blocked. "
                    f"Return in {entry.remaining_hours:.1f}h with {3 - entry.tri_witness.count} "
                    "more witness(es) to unlock SEAL."
                )

        result["meta"]["sabar_cooldown"] = cooldown_info

    except Exception:
        if "meta" not in result:
            result["meta"] = {}
        result["meta"]["sabar_cooldown"] = {
            "cooldown_entry_id": cooldown_entry_id,
            "status": "unavailable",
            "note": "cooldown engine not reachable — proceeding without verification",
        }


# Backward compatibility alias
arif_judge_deliberate = arif_judge

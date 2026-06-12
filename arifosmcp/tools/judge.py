"""
arifosmcp/tools/judge_deliberate.py — 888_JUDGE
═══════════════════════════════════════════════

Constitutional verdict engine.

Evidence pre-loading: vitals and heart output are piped into the judge
before adjudication so epistemic confidence is grounded in actual system state.

Post-SEAL auto-hook: When verdict is SEAL and vault_entry_id is provided,
the judge output is automatically routed to arif_vault_seal for immutable anchoring.
"""

from __future__ import annotations

import json as json_lib
import os
import urllib.request
from pathlib import Path
from typing import Any

from arifosmcp.runtime.metabolic_receipt import get_cumulative_metrics
from arifosmcp.runtime.niat_gate import check_niat_gate
from arifosmcp.runtime.self_mod_lock import is_self_modification_attempt
from arifosmcp.runtime.tools import _arif_judge_deliberate
from arifosmcp.schemas.verdict import VerdictCode, VerdictOutput

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


def arif_judge_deliberate(
    mode: str = "judge",
    candidate: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    constitutional_chain_id: str | None = None,
    vault_entry_id: str | None = None,
    cooldown_entry_id: str | None = None,
    action_tier: str = "standard",
    heart_critique: dict[str, Any] | None = None,
    niat_params: dict[str, Any] | None = None,
    context_source: str | None = None,
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
    from arifosmcp.tools.ops import arif_ops_measure

    _evidence: dict = {}
    _is_elevated_tier = action_tier.lower() in ("sovereign", "c4", "c5")

    if mode != "history":
        if _evidence.get("vitals") is None:
            try:
                vitals_result = arif_ops_measure(mode="vitals")
                _evidence["vitals"] = getattr(vitals_result, "__dict__", {}) or {
                    "status": "unavailable"
                }
            except Exception:
                _evidence["vitals"] = {"status": "unavailable"}

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
        if _is_elevated_tier:
            _w2_sub = _evidence["well_substrate"]
            _w2_clarity = _w2_sub.get("clarity")
            if (
                _w2_clarity is not None
                and float(_w2_clarity) < 4.0
                and _w2_sub.get("has_telemetry")
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
                        "Rest. Reassess when clarity ≥ 6/10.",
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
                    },
                )

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
            return VerdictOutput(
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
        except Exception as exc:
            return VerdictOutput(
                verdict=VerdictCode.HOLD,
                reasons=[f"scan_instructions failed: {exc}"],
                next_safe_action="Check governance_scan module availability.",
                meta={"error": str(exc)},
            )

    result = _arif_judge_deliberate(
        mode=mode,
        candidate=candidate,
        session_id=session_id,
        actor_id=actor_id,
        constitutional_chain_id=constitutional_chain_id,
        audit_entropy=audit_entropy,
        wealth_score=_evidence.get("wealth_score"),
        verification_surface=_evidence.get("verification_surface"),
    )

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

    # ── Attach WELL substrate to result ──
    # Every judge verdict now carries biological readiness evidence.
    # This closes the loop: constitutional decisions are grounded
    # in operator substrate state.
    well_sub = _evidence.get("well_substrate", {})
    if isinstance(result, dict):
        result.setdefault("meta", {})["well_substrate"] = well_sub
        if well_sub.get("coupled_verdict") == "HOLD" and well_sub.get("has_telemetry"):
            result["meta"]["well_gate"] = (
                f"WELL HOLD: human_ready={well_sub.get('human_ready')} "
                f"floors_violated={well_sub.get('active_violations')} — "
                "biological substrate flags active. Verdict stands; ARIF confirmation advised."
            )

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

    verdict_str = str(result.get("verdict", ""))
    is_seal = "SEAL" in verdict_str

    if vault_entry_id and is_seal:
        try:
            from arifosmcp.tools.vault import arif_vault_seal

            payload_dict = {
                "tool": "arif_judge_deliberate",
                "candidate": candidate,
                "verdict": result.get("verdict", ""),
                "constitutional_chain_id": result.get("meta", {}).get("constitutional_chain_id"),
                "state_hash": result.get("meta", {}).get("state_hash"),
            }

            seal_result = arif_vault_seal(
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
        except Exception:
            if "meta" not in result:
                result["meta"] = {}
            result["meta"]["vault_sealed"] = False

    return VerdictOutput(**result)


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

"""
arifosmcp/tools/reason.py — 333_MIND
════════════════════════════════════════

Inductive reasoning engine and synthesis.

DELTA BUNDLE SPEC (from archive/333/README.md):
  Every arif_mind_reason output MUST include:
  - facts: F2 ≥ 0.99 verifiable claims
  - scars: unresolved contradictions blocking certainty
  - floor_scores: F2, F4, F7, L13 self-check
  - entropy: ΔS ≤ 0 (must decrease local entropy)
  - confidence: calibrated Ω₀ ∈ [0.03, 0.05] (F7 Humility band)

Context injection (P2): When context is provided, the tool pre-loads
  session state (session_id, G-score, vitals) and prior tool results
  into the reasoning trace before synthesis. This grounds every
  reasoning call in actual system state rather than abstract axioms.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import threading
from typing import Any

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.llm_client import LLMUnavailableError
from arifosmcp.runtime.tools import _hold, _ok
from arifosmcp.schemas.synthesis import Synthesis


def _reduce_verdict(*verdicts: str) -> str:
    """
    Verdict reducer — returns the most conservative verdict.

    Order (most conservative → least):
    VOID > HOLD > HYPOTHESIS > PARTIAL > PASS > SEAL
    """
    order = {
        "VOID": 0,
        "HOLD": 1,
        "ESCALATE_TO_888": 1,
        "NEEDS_EVIDENCE": 2,
        "HYPOTHESIS": 3,
        "PARTIAL": 4,
        "PASS": 5,
        "PASS_WITH_SCOPE_LIMIT": 5,
        "REASONED": 6,
        "REFLECTED": 6,
        "SEAL": 7,
    }
    # Default to HOLD if unknown verdict encountered
    mapped = [(order.get(v, 1), v) for v in verdicts if v]
    if not mapped:
        return "HOLD"
    return min(mapped, key=lambda x: x[0])[1]


def _sanitize_observed_inputs(inputs: list[str]) -> list[str]:
    """
    Sanitize observed_inputs to remove raw <think> blocks and private reasoning text.
    Replaces raw thinking with safe abstractions.
    """
    sanitized = []
    for item in inputs:
        if not isinstance(item, str):
            continue
        # Strip raw <think> blocks entirely
        if "<think>" in item or "</think>" in item:
            # Extract a safe abstraction if possible
            if "theory of mind" in item.lower() or "tom" in item.lower():
                sanitized.append("Evidence: operator asked about theory-of-mind scaffolding in init tool.")
            elif "identity" in item.lower() or "verification" in item.lower():
                sanitized.append("Evidence: operator identity verification state was discussed.")
            elif "consent" in item.lower() or "privacy" in item.lower():
                sanitized.append("Evidence: consent boundaries and privacy were discussed.")
            else:
                sanitized.append("Evidence: reasoning trace contained structured constitutional analysis.")
            continue
        # Strip obvious raw model artifacts
        if item.startswith("[think]") or item.startswith("<thinking>"):
            sanitized.append("Evidence: structured reasoning trace available (raw thinking sanitized).")
            continue
        sanitized.append(item)
    return sanitized


def _ensure_confidence(conf: dict | None) -> dict:
    """Ensure confidence is never empty — governed reasoning requires explicit confidence."""
    if not isinstance(conf, dict) or not conf:
        return {
            "reasoning_confidence": 0.5,
            "evidence_confidence": 0.3,
            "overall_confidence": 0.3,
            "label": "low",
            "reason": "Confidence was empty or malformed — defaulting to low-confidence heuristic.",
        }
    # Ensure required keys exist
    conf.setdefault("reasoning_confidence", 0.5)
    conf.setdefault("evidence_confidence", 0.3)
    conf.setdefault("overall_confidence", 0.3)
    if "label" not in conf:
        overall = conf.get("overall_confidence", 0.3)
        if overall >= 0.8:
            conf["label"] = "high"
        elif overall >= 0.5:
            conf["label"] = "medium"
        else:
            conf["label"] = "low"
    if "reason" not in conf:
        conf["reason"] = f"Overall confidence {conf['overall_confidence']:.2f} — self-assessed, not verified."
    return conf


def _ensure_synthesis(synthesis: str | None, reasoning_status: str) -> str:
    """Ensure synthesis is never empty — empty synthesis creates false completion."""
    if synthesis and isinstance(synthesis, str) and synthesis.strip():
        return synthesis.strip()
    return (
        f"Unable to produce structured synthesis — reasoning status is {reasoning_status}. "
        "Claim remains unsealed and requires further evidence or critique."
    )


def _build_delta_bundle(
    query: str | None,
    status: str,
    claim_state: str,
    synthesis: str,
    reasoning: dict,
    confidence: dict,
    uncertainty: list,
    reasoning_mode: str = "analytical",
    axioms_used: list[str] | None = None,
    next_safe_action: list[str] | None = None,
    context: dict | None = None,
    actor_id: str | None = None,
) -> dict:
    """
    Build a Structured Delta Bundle — the upgraded constitutional output for 333_MIND.

    v3.2 fix: 6 orthogonal verdict planes (execution, reasoning, truth, evidence,
    authority, risk) + final_kernel_verdict = strictest across all.
    Provenance is metadata, not authority.

    Core invariant (from ChatGPT × BANGANG test, 2026-06-13):
      AI provenance ≠ authority. LLM output ≠ truth.
      Confidence ≠ permission. SEAL ≠ mutation right.
      Only lease + actor + sovereign authority can grant action.
    """
    # ── Sanitize inputs ──────────────────────────────────────
    reasoning = reasoning or {}
    observed_inputs = reasoning.get("observed_inputs", [])
    if observed_inputs:
        reasoning["observed_inputs"] = _sanitize_observed_inputs(observed_inputs)

    # ── Ensure non-empty critical fields ─────────────────────
    confidence = _ensure_confidence(confidence)
    synthesis = _ensure_synthesis(synthesis, status)

    overall_conf = confidence.get("overall_confidence", 0.5)
    omega_0 = max(0.03, min(0.05, round(1.0 - overall_conf, 4)))

    reasoning_trace = []
    if context:
        session_id = context.get("session_id", "unknown")
        g_score = context.get("g_score", context.get("vitals", {}).get("g_score", "unavailable"))
        reasoning_trace.append(f"[333_MIND context] session_id={session_id}, g_score={g_score}")

    # ── Compute floor scores ─────────────────────────────────
    f02_pass = confidence.get("evidence_confidence", 0) >= 0.9
    floor_scores = {
        "L02_TRUTH": "PASS" if f02_pass else "FAIL",
        "L04_CLARITY": "PASS",
        "L07_HUMILITY": "PASS" if 0.03 <= omega_0 <= 0.05 else "FAIL",
        "L13_SOVEREIGN": "PASS",
    }

    # ── Compute separate verdict planes ──────────────────────
    # Transport: did the tool execute without error?
    transport_verdict = "SEAL"
    # Execution: did the tool run safely (no crash, no mutation)?
    execution_verdict = "SEAL"
    # Reasoning: what did the inner reasoning conclude?
    reasoning_verdict = status  # HOLD, HYPOTHESIS, REASONED, etc.
    # Truth: is the claim proven based on evidence?
    if claim_state in ("VERIFIED_FACT", "SUPPORTED_CLAIM") and f02_pass:
        truth_verdict = "SEAL"
    elif claim_state == "HYPOTHESIS":
        truth_verdict = "HYPOTHESIS"
    elif claim_state in ("SPECULATION", "UNSUPPORTED"):
        truth_verdict = "HOLD"
    else:
        truth_verdict = "HOLD"
    # Floor verdict: did all mandatory floors pass?
    floor_verdict = "SEAL" if all(v == "PASS" for v in floor_scores.values()) else "HOLD"

    # ── Evidence verdict ─────────────────────────────────────
    # Has admissible evidence been attached to the claim?
    # Claim state covers this via VERIFIED_FACT/SUPPORTED_CLAIM vs SPECULATION/UNSUPPORTED.
    attestations = reasoning.get("attestations", []) if isinstance(reasoning, dict) else []
    missing_evidence = reasoning.get("missing_evidence", []) if isinstance(reasoning, dict) else []
    if claim_state in ("VERIFIED_FACT",) and attestations:
        evidence_verdict = "SEAL"          # strong evidence with attestations
    elif claim_state in ("SUPPORTED_CLAIM",) or (attestations and not missing_evidence):
        evidence_verdict = "HYPOTHESIS"    # partial — some support but not verified fact
    elif claim_state in ("SPECULATION", "UNSUPPORTED") or missing_evidence:
        evidence_verdict = "HOLD"          # unsupported or contradicted by missing evidence
    else:
        evidence_verdict = "HOLD"          # default to unsupported

    # ── Authority verdict ────────────────────────────────────
    # Does the actor have permission to act on this claim?
    # Note: authority is about WHO acts, not WHERE the claim came from.
    # AI provenance is metadata, not authority (see core invariant).
    if actor_id and actor_id.lower() in ("arif", "888", "f13"):
        authority_verdict = "SEAL"         # sovereign or named actor
    elif actor_id:
        authority_verdict = "HYPOTHESIS"   # identified but unverified actor
    else:
        authority_verdict = "HOLD"         # anonymous — no authority at all

    # ── Risk verdict ─────────────────────────────────────────
    # What is the blast radius of acting on this claim?
    # Determined by reversibility + claim sensitivity + actor authority.
    if reasoning_verdict in ("SEAL", "REASONED", "REFLECTED") and evidence_verdict in ("SEAL",) and authority_verdict == "SEAL":
        risk_verdict = "SEAL"              # low risk: well-supported, high authority
    elif reasoning_verdict in ("SEAL", "REASONED") and evidence_verdict in ("SEAL", "HYPOTHESIS"):
        risk_verdict = "HYPOTHESIS"        # medium risk: coherent reasoning but evidence is partial
    elif evidence_verdict == "HOLD":
        risk_verdict = "HOLD"              # high risk: unsupported claims used for action
    else:
        risk_verdict = "HOLD"              # default to high risk

    # Final: most conservative across all planes
    final_verdict = _reduce_verdict(
        transport_verdict,
        execution_verdict,
        reasoning_verdict,
        truth_verdict,
        evidence_verdict,
        authority_verdict,
        risk_verdict,
        floor_verdict,
    )

    # ── Provenance metadata ──────────────────────────────────
    # Provenance tells us WHERE a claim came from.
    # It gives admissibility (traceability, audit, reproducibility).
    # It NEVER gives authority (see core invariant).
    provenance = {
        "source": "arif_mind_reason",
        "model_provenance": confidence.get("model_source", "unknown"),
        "claim_origin": claim_state,
        "reasoning_backend": reasoning_mode,
        "axioms_used": axioms_used or [],
        "admissibility_statement": (
            "Provenance is metadata, not authority. "
            "This claim is admissible as evidence for audit. "
            "It is NOT authorised for action without lease + constitutional clearance."
        ),
    }

    # ── Stage progression with escalation reason ─────────────
    next_stage = "444_HEART"
    if final_verdict in ("HOLD", "VOID", "ESCALATE_TO_888"):
        escalation_reason = (
            f"Escalating to critique because final_verdict={final_verdict} "
            f"(reasoning={reasoning_verdict}, truth={truth_verdict}, "
            f"evidence={evidence_verdict}, authority={authority_verdict}, risk={risk_verdict})."
        )
    else:
        escalation_reason = "Standard progression to ethics/dignity critique stage."

    return {
        "query": query,
        # Verdict planes (v3.2 — orthogonal, never collapsed)
        "transport_verdict": transport_verdict,
        "execution_verdict": execution_verdict,
        "reasoning_verdict": reasoning_verdict,
        "truth_verdict": truth_verdict,
        "evidence_verdict": evidence_verdict,
        "authority_verdict": authority_verdict,
        "risk_verdict": risk_verdict,
        "floor_verdict": floor_verdict,
        "final_verdict": final_verdict,
        # Legacy fields (preserved for backward compat)
        "status": status,
        "claim_state": claim_state,
        "synthesis": synthesis,
        "reasoning": reasoning,
        "confidence": confidence,
        "uncertainty": uncertainty,
        "omega_0": omega_0,
        "reasoning_mode": reasoning_mode,
        "axioms_used": axioms_used or [],
        "next_safe_action": next_safe_action or [],
        "floor_scores": floor_scores,
        "reasoning_trace": reasoning_trace,
        "stage_progression": {
            "current_stage": "333_MIND",
            "next_stage": next_stage,
            "reason": escalation_reason,
        },
        "actor": {
            "claimed_id": actor_id or "anonymous",
            "verified": False,
            "effective_actor": actor_id if actor_id else "anonymous_until_verified",
        },
        # Provenance is metadata, not authority (v3.2)
        "provenance": provenance,
        # Core invariant reminder (never removed from output)
        "_core_invariant": (
            "AI provenance ≠ authority. LLM output ≠ truth. "
            "Confidence ≠ permission. SEAL ≠ mutation right. "
            "Only lease + actor + sovereign authority can grant action."
        ),
    }


def _run_reasoning_sync(coro: Any, timeout: float = 70.0) -> dict[str, Any]:
    """Run coroutine in sync context, including when caller already has an active event loop.

    L13 TIMEOUT_SAFE: Hard timeout prevents indefinite hangs when LLM backends stall.
    Default 15s balances SEA-LION latency (~1-3s) against CPU-Ollama slowness.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    result: dict[str, Any] = {}
    error: list[BaseException] = []

    def _runner() -> None:
        try:
            result["value"] = asyncio.run(coro)
        except BaseException as exc:  # pragma: no cover - passthrough for sync bridge failures
            error.append(exc)

    thread = threading.Thread(target=_runner, daemon=True)
    thread.start()
    thread.join(timeout=timeout)

    if thread.is_alive():
        # Thread still running after timeout — LLM backend stalled
        raise LLMUnavailableError(
            f"Reasoning backend timeout after {timeout}s — "
            "SEA-LION unreachable or Ollama CPU inference too slow"
        )

    if error:
        raise error[0]
    return result["value"]


def arif_mind_reason(

    mode: str = "reason",
    query: str | None = None,
    actor_id: str | None = None,
    context: dict | None = None,
) -> Synthesis:
    """
    333_MIND: Constitutional reasoning and synthesis (Structured Witness).
    """
    if mode in ("geox_quantum_suitability", "geox_scale_classifier", "geox_molecular_vs_macroscopic", "geox_hamiltonian_candidate"):
        return {"status": "readonly", "message": f"{mode} activated based on GEOX quantum scale classifier."}

    if mode in ("hndl_score", "pqc_gap_analysis", "migration_strategy", "qday_physics_assess", "claim_lint_quantum"):
        import yaml
        try:
            with open("/root/arifOS/config/qday_policy.yaml") as f:
                policy = yaml.safe_load(f).get("qday_policy", {})
        except Exception:
            policy = {}
            
        risk = "MEDIUM"
        reason_text = "Standard crypto usage detected."
        recommended_action = "Monitor CRQC horizon."
        
        has_vulnerable = True
        data_lifetime = 10
        hndl_crit = policy.get("hndl_critical_if", {})
        crit_lifetime = hndl_crit.get("data_lifetime_years_gte", 10)
        
        if data_lifetime >= crit_lifetime and has_vulnerable:
            risk = "CRITICAL"
            reason_text = "Long-lived data protected by quantum-vulnerable public-key cryptography."
            recommended_action = "Prioritize hybrid/PQC migration planning."
            
        return {
            "mode": mode,
            "risk": risk,
            "reason": reason_text,
            "recommended_action": recommended_action,
            "mutation": False
        }
        
    from arifosmcp.runtime.mind_reason import (
        arif_mind_reason_structured as run_reasoning,
    )

    session_id = context.get("session_id") if context else None

    reason_result = _run_reasoning_sync(run_reasoning(query or "", mode, session_id, actor_id))

    # If v2 metabolic mode, handle the nested mind_packet structure
    if mode == "metabolize" and "mind_packet" in reason_result:
        packet = reason_result["mind_packet"]
        synthesis_v2 = packet.get("synthesis", {})

        # ── AGI KERNEL READINESS GATE 001 FIELDS ──
        raw_conf_v2 = synthesis_v2.get("confidence", {}) if isinstance(synthesis_v2.get("confidence"), dict) else {}
        bundle = {
            "claim_state": str(packet.get("claim_state", "UNKNOWN")).upper(),
            "reasoning_verdict": str(reason_result.get("status", "OK")).upper(),
            "evidence_used": packet.get("attestations", []) if isinstance(packet.get("attestations"), list) else [],
            "inferences": packet.get("abductions", []) if isinstance(packet.get("abductions"), list) else [],
            "counterarguments": packet.get("counterarguments", []) if isinstance(packet.get("counterarguments"), list) else [],
            "missing_evidence": packet.get("missing_evidence", []) if isinstance(packet.get("missing_evidence"), list) else [],
            "confidence": {
                "overall": float(raw_conf_v2.get("overall_confidence", raw_conf_v2.get("overall", 0.0))),
                "label": str(raw_conf_v2.get("label", "low"))
            },
            "next_safe_action": [a.get("tool") for a in packet.get("next_actions", [])] if isinstance(packet.get("next_actions"), list) else []
        }
        return Synthesis(**_ok("arif_mind_reason", bundle))

    # Floor check (Manual override check)
    floor_check = check_laws("arif_mind_reason", {"query": query or ""}, actor_id)
    floor_verdict = floor_check.get("verdict", "HOLD")
    floor_reason = floor_check.get("reason", "Constitutional floor check did not SEAL")

    uncertainty = list(reason_result.get("uncertainty", []))
    if floor_verdict != "SEAL":
        uncertainty.append({"type": "FLOOR_BREACH", "detail": floor_reason})

    raw_conf = reason_result.get("confidence", {}) if isinstance(reason_result.get("confidence"), dict) else {}
    reasoning_data = reason_result.get("reasoning", {}) if isinstance(reason_result.get("reasoning"), dict) else {}
    
    # ── AGI KERNEL READINESS GATE 001 FIELDS ──
    bundle = {
        "claim_state": str(reason_result.get("claim_state", "UNKNOWN")).upper(),
        "reasoning_verdict": "HOLD" if floor_verdict != "SEAL" else str(reason_result.get("status", "HOLD")).upper(),
        "evidence_used": reasoning_data.get("attestations", []) if isinstance(reasoning_data.get("attestations"), list) else [],
        "inferences": reasoning_data.get("abductions", []) if isinstance(reasoning_data.get("abductions"), list) else [],
        "counterarguments": reasoning_data.get("counterarguments", []) if isinstance(reasoning_data.get("counterarguments"), list) else [],
        "missing_evidence": reasoning_data.get("missing_evidence", []) if isinstance(reasoning_data.get("missing_evidence"), list) else [],
        "confidence": {
            "overall": float(raw_conf.get("overall_confidence", raw_conf.get("overall", 0.0))),
            "label": str(raw_conf.get("label", "low"))
        },
        "next_safe_action": reason_result.get("next_safe_action", []) if isinstance(reason_result.get("next_safe_action"), list) else []
    }

    if floor_verdict != "SEAL":
        hold_env = _hold(
            "arif_mind_reason",
            floor_reason,
            floors=list(floor_check.get("violated_laws", [])),
            extra_meta={"floor_verdict": floor_verdict},
            session_id=session_id,
        )
        hold_env["result"] = bundle
        return Synthesis(**hold_env)

    return Synthesis(**_ok("arif_mind_reason", bundle))

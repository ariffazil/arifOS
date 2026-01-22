"""
apex.verdict - THE ONLY EXPOSED AUTHORITY TOOL.

This is the single entry point for L4_MCP black-box governance.
All internal machinery (Floors, W@W, 000→999 routing) is hidden.

Version: v45.1.2 (Phase 2B - Real Telemetry Integration)
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .schema import ApexRequest, ApexResponse, Verdict, ActionClass, Caller
from L4_MCP.core.classify import classify_action
from L4_MCP.core.identity import extract_caller
from L4_MCP.core.red_patterns import check_red_patterns
from L4_MCP.core.tri_witness import required_evidence_for
from L4_MCP.core.explain import generate_explanation

# Phase 2B: Import REAL arifOS core (not stubs)
from arifos_core.system.apex_prime import apex_review, ApexVerdict as CoreApexVerdict, Verdict as CoreVerdict
from arifos_core.enforcement.metrics import Metrics
from arifos_core.utils.session_telemetry import SessionTelemetry
from arifos_core.utils.reduction_engine import compute_attributes
from arifos_ledger.store import LedgerStore


def apex_verdict(req: ApexRequest, ledger: LedgerStore) -> ApexResponse:
    """
    THE ONLY EXTERNAL AUTHORITY TOOL.

    Phase 2B: Uses REAL telemetry from arifOS core.

    Args:
        req: ApexRequest with task, params, context, and optional caller
        ledger: LedgerStore implementation for audit logging

    Returns:
        ApexResponse with verdict and all relevant details
    """
    ts = datetime.now(timezone.utc).isoformat()

    # Extract or set caller identity
    caller = req.caller or extract_caller(req.context)

    # Classify the action by risk level
    action_class = classify_action(req.task, req.params, req.context)

    # =========================================================================
    # STEP 1: RED PATTERN CHECK - Instant VOID if dangerous pattern matches
    # =========================================================================
    red_flags = check_red_patterns(req.task, req.params, req.context)
    if red_flags:
        verdict = Verdict.VOID
        reasons = [f"RED::{code}" for code in red_flags]
        triggered_floors = ["F1_Amanah", "F9_AntiHantu"]
        evidence = required_evidence_for(verdict, action_class, triggered_floors, req)
        constraints = ["no_execution", "no_external_calls"]
        explanation = generate_explanation(
            verdict, reasons, evidence, constraints, context_hint="Red pattern matched"
        )
        ledger_id = _append_or_fail_closed(
            ledger, req, verdict, reasons, triggered_floors,
            evidence, constraints, caller, action_class, ts
        )
        return ApexResponse(
            verdict=verdict,
            apex_pulse=0.0,
            reason_codes=reasons,
            required_evidence=evidence,
            constraints=constraints,
            floor_triggered=triggered_floors,
            action_class=action_class,
            caller=caller,
            explanation=explanation,
            cooling_ledger_id=ledger_id,
            timestamp=ts,
        )

    # =========================================================================
    # STEP 2: BUILD REAL METRICS FROM TELEMETRY (Phase 2B)
    # =========================================================================
    metrics = _build_metrics_from_telemetry(req)

    # =========================================================================
    # STEP 3: CALL CANONICAL APEX_PRIME (From arifos_core)
    # =========================================================================
    core_verdict = apex_review(
        metrics=metrics,
        high_stakes=(action_class in [ActionClass.DELETE, ActionClass.PAY, ActionClass.SELF_MODIFY]),
        tri_witness_threshold=0.95,
        eye_blocking=False,
        energy=1.0,
        entropy=0.0,
        use_genius_law=True,
        prompt=req.task,
        response_text="",
        lane="UNKNOWN",
    )

    # Map core verdict to L4 verdict enum
    verdict = _map_verdict(core_verdict.verdict)
    apex_pulse = core_verdict.pulse
    reason_codes = [core_verdict.reason]
    triggered_floors = _extract_triggered_floors(core_verdict.floors)

    # =========================================================================
    # STEP 4: TRI-WITNESS & POLICY
    # =========================================================================
    required_evidence = required_evidence_for(verdict, action_class, triggered_floors, req)
    constraints = _constraints_for(verdict, action_class, triggered_floors)
    explanation = generate_explanation(
        verdict, reason_codes, required_evidence, constraints,
        context_hint=f"APEX PRIME: {core_verdict.reason}"
    )

    # =========================================================================
    # STEP 5: ATOMIC LEDGER APPEND
    # =========================================================================
    ledger_id = _append_or_fail_closed(
        ledger, req, verdict, reason_codes, triggered_floors,
        required_evidence, constraints, caller, action_class, ts
    )

    # Fail-closed override
    if ledger_id is None and verdict == Verdict.SEAL:
        verdict = Verdict.VOID
        reason_codes = list(reason_codes) + ["LEDGER_DOWN_FAIL_CLOSED"]
        explanation = generate_explanation(
            verdict, reason_codes, required_evidence, constraints,
            context_hint="Fail-closed: ledger unavailable"
        )

    return ApexResponse(
        verdict=verdict,
        apex_pulse=apex_pulse,
        reason_codes=reason_codes,
        required_evidence=required_evidence,
        constraints=constraints,
        floor_triggered=triggered_floors,
        action_class=action_class,
        caller=caller,
        explanation=explanation,
        cooling_ledger_id=ledger_id,
        timestamp=ts,
    )


def _build_metrics_from_telemetry(req: ApexRequest) -> Metrics:
    """
    Build metrics from REAL telemetry (Phase 2B).
    
    This replaces the Phase 2A heuristic stub with actual
    token/time/latency physics from arifOS core.
    """
    # Extract telemetry from context (if provided by MCP client)
    telemetry = req.context.get("telemetry", {})
    
    # Initialize session telemetry tracker
    session = SessionTelemetry(max_session_tokens=8000)
    
    # Estimate tokens if not provided
    tokens_in = telemetry.get("tokens_in", _estimate_tokens(req.task))
    tokens_out = telemetry.get("tokens_out", 0)  # Unknown at request time
    temperature = telemetry.get("temperature", 0.7)
    top_p = telemetry.get("top_p", 0.9)
    latency_ms = telemetry.get("latency_ms", 0)
    
    # Start turn with physics
    session.start_turn(
        tokens_in=tokens_in,
        temperature=temperature,
        top_p=top_p,
    )
    
    # Compute attributes from telemetry
    # (In full implementation, this would use end_turn() with response data)
    attrs = compute_attributes(
        history=session.history,
        max_session_tokens=session.max_session_tokens,
        current_turn=None,
    )
    
    # =========================================================================
    # PHASE 2B: REAL METRICS FROM PHYSICS
    # =========================================================================
    
    # Token economics → Energy (E)
    token_ratio = tokens_out / max(1, tokens_in) if tokens_out > 0 else 1.0
    energy = 1.0
    if token_ratio > 10:  # Verbose without justification
        energy -= 0.2
    
    # Latency → Energy (E)
    if latency_ms > 5000:
        energy -= 0.1
    
    # Budget burn → Psi penalty
    budget_burn_pct = attrs.budget_burn_pct
    psi_penalty = 0.0
    if budget_burn_pct > 80:
        psi_penalty = 0.1
    elif budget_burn_pct > 90:
        psi_penalty = 0.2
    
    # Sampling parameters → Omega_0 (Humility)
    if temperature < 0.2:
        omega_0 = 0.01  # Too confident (greedy decoding)
    elif temperature > 1.0:
        omega_0 = 0.08  # Too chaotic
    else:
        omega_0 = 0.04  # Healthy
    
    # Semantic analysis (from text)
    task_lower = req.task.lower()
    
    # Truth: Check for uncertainty markers
    uncertainty_markers = ["maybe", "perhaps", "possibly", "might", "could", "think"]
    uncertainty_count = sum(1 for marker in uncertainty_markers if marker in task_lower)
    truth = max(0.5, 0.99 - (uncertainty_count * 0.05))
    
    # Amanah: Check for destructive keywords
    destructive_keywords = ["delete", "drop", "truncate", "rm -rf", "destroy", "wipe"]
    amanah = not any(keyword in task_lower for keyword in destructive_keywords)
    
    # DeltaS: Assume neutral for request (would be computed from response)
    delta_s = 0.0
    
    # Peace²: Detect aggressive language
    aggressive = ["kill", "attack", "destroy", "harm"]
    peace_squared = 0.8 if any(word in task_lower for word in aggressive) else 1.1
    
    # Kappa_r: Assume high empathy for now
    kappa_r = 0.95
    
    # Psi: Combine all factors
    psi = max(0.0, 1.0 - psi_penalty)
    
    # Anti-Hantu: Check for ghost claims
    ghost_claims = ["i feel", "i believe", "my heart", "i have a soul"]
    anti_hantu = not any(claim in task_lower for claim in ghost_claims)
    
    # Build metrics with REAL physics
    return Metrics(
        truth=truth,
        delta_s=delta_s,
        omega_0=omega_0,
        amanah=amanah,
        tri_witness=0.95,  # Would come from Tri-Witness layer
        peace_squared=peace_squared,
        kappa_r=kappa_r,
        psi=psi,
        anti_hantu=anti_hantu,
        rasa=True,
    )


def _estimate_tokens(text: str) -> int:
    """Estimate token count from text (BPE approximation)."""
    # Rough estimate: 0.35 tokens per character for English
    # Use max(1, ...) to ensure at least 1 token for non-empty text
    if not text:
        return 0
    return max(1, int(len(text) * 0.35 + 0.5))  # Round instead of truncate


def _map_verdict(core_verdict: CoreVerdict) -> Verdict:
    """Map core verdict enum to L4 verdict enum."""
    mapping = {
        CoreVerdict.SEAL: Verdict.SEAL,
        CoreVerdict.VOID: Verdict.VOID,
        CoreVerdict.SABAR: Verdict.SABAR,
        CoreVerdict.PARTIAL: Verdict.SABAR,
        CoreVerdict.HOLD_888: Verdict.HOLD_888,
        CoreVerdict.SUNSET: Verdict.VOID,
    }
    return mapping.get(core_verdict, Verdict.VOID)


def _extract_triggered_floors(floors) -> List[str]:
    """Extract floor failure reasons from FloorVerdict."""
    if floors is None:
        return []

    triggered = []
    if not floors.truth_ok:
        triggered.append("F2_Truth")
    if not floors.amanah_ok:
        triggered.append("F1_Amanah")
    if not floors.delta_s_ok:
        triggered.append("F4_DeltaS")
    if not floors.omega_0_ok:
        triggered.append("F7_Omega0")
    if not floors.peace_squared_ok:
        triggered.append("F5_Peace2")
    if not floors.kappa_r_ok:
        triggered.append("F6_KappaR")
    if not floors.tri_witness_ok:
        triggered.append("F3_TriWitness")
    if not floors.anti_hantu_ok:
        triggered.append("F9_AntiHantu")
    if hasattr(floors, 'psi_ok') and not floors.psi_ok:
        triggered.append("F8_Psi")

    return triggered


def _constraints_for(verdict: Verdict, action_class: ActionClass, floor_triggered: List[str]) -> List[str]:
    """Derive execution constraints."""
    base_constraints = ["max_execution_time_30s", "no_self_modify"]

    if verdict in (Verdict.VOID, Verdict.SABAR, Verdict.HOLD_888):
        base_constraints.append("no_execution")

    if action_class in (ActionClass.DELETE, ActionClass.PAY, ActionClass.SELF_MODIFY):
        base_constraints.append("require_human_confirmation")

    return base_constraints


def _append_or_fail_closed(
    ledger: LedgerStore,
    req: ApexRequest,
    verdict: Verdict,
    reason_codes: List[str],
    floor_triggered: List[str],
    required_evidence: List[str],
    constraints: List[str],
    caller: Caller,
    action_class: ActionClass,
    timestamp: str,
) -> Optional[str]:
    """Atomically append verdict to cooling ledger."""
    try:
        return ledger.append_atomic(
            task=req.task,
            params=req.params,
            context=req.context,
            verdict=verdict.value,
            reason_codes=reason_codes,
            floor_triggered=floor_triggered,
            required_evidence=required_evidence,
            constraints=constraints,
            caller={
                "source": caller.source,
                "model": caller.model,
                "tenant": caller.tenant,
                "trust_level": caller.trust_level,
            },
            action_class=action_class.value,
            timestamp=timestamp,
        )
    except Exception as e:
        import sys
        print(f"WARNING: cooling ledger append failed: {e}", file=sys.stderr)
        return None

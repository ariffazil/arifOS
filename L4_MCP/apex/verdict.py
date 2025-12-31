"""
apex.verdict - THE ONLY EXPOSED AUTHORITY TOOL.

This is the single entry point for L4_MCP black-box governance.
All internal machinery (Floors, W@W, 000→999 routing) is hidden.

Version: v45.1.0
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .schema import ApexRequest, ApexResponse, Verdict, ActionClass, Caller
from .pipeline import route_000_999
from L4_MCP.core.classify import classify_action
from L4_MCP.core.identity import extract_caller
from L4_MCP.core.red_patterns import check_red_patterns
from L4_MCP.core.tri_witness import required_evidence_for
from L4_MCP.core.explain import generate_explanation
from L4_MCP.floors.evaluate import evaluate_floors
from L4_MCP.waw.weights import compute_waw
from arifos_ledger.store import LedgerStore


def apex_verdict(req: ApexRequest, ledger: LedgerStore) -> ApexResponse:
    """
    THE ONLY EXTERNAL AUTHORITY TOOL.

    Evaluates a proposed task against constitutional rules and returns a verdict.

    Fail-closed: if the audit ledger append cannot complete atomically,
    the verdict will degrade to a safe state (VOID).

    Everything inside this function is internal (not directly callable by users):
    - AAA Floors F1–F9 (parallel constitutional checks)
    - W@W weighting (confidence metrics)
    - 000→999 routing pipeline (deterministic verdict logic)
    - Cooling ledger append (audit log, atomic)

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
        # Atomic ledger append (fail-safe returns None on failure)
        ledger_id = _append_or_fail_closed(
            ledger,
            req,
            verdict,
            reasons,
            triggered_floors,
            evidence,
            constraints,
            caller,
            action_class,
            ts,
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
    # STEP 2: EVALUATE FLOORS - Run all constitutional checks (F1-F9)
    # =========================================================================
    floor_result = evaluate_floors(req, caller, action_class)

    # =========================================================================
    # STEP 3: W@W WEIGHTING - Compute internal confidence metrics
    # =========================================================================
    waw = compute_waw(req, floor_result)

    # =========================================================================
    # STEP 4: ROUTING 000→999 - Decide verdict based on floors & W@W
    # =========================================================================
    verdict, apex_pulse, reason_codes = route_000_999(floor_result, waw)

    # =========================================================================
    # STEP 5: TRI-WITNESS & POLICY - Determine evidence and constraints
    # =========================================================================
    required_evidence = required_evidence_for(verdict, action_class, floor_result.triggered, req)
    constraints = _constraints_for(verdict, action_class, floor_result)
    explanation = generate_explanation(
        verdict,
        reason_codes,
        required_evidence,
        constraints,
        context_hint=f"Floors: {floor_result.triggered}",
    )

    # =========================================================================
    # STEP 6: ATOMIC LEDGER APPEND - Log the verdict
    # =========================================================================
    ledger_id = _append_or_fail_closed(
        ledger,
        req,
        verdict,
        reason_codes,
        floor_result.triggered,
        required_evidence,
        constraints,
        caller,
        action_class,
        ts,
    )

    # =========================================================================
    # FAIL-CLOSED OVERRIDE: If ledger down and verdict was SEAL, degrade to VOID
    # =========================================================================
    if ledger_id is None and verdict == Verdict.SEAL:
        verdict = Verdict.VOID
        reason_codes = list(reason_codes) + ["LEDGER_DOWN"]
        explanation = generate_explanation(
            verdict,
            reason_codes,
            required_evidence,
            constraints,
            context_hint="Fail-closed: ledger unavailable",
        )

    # =========================================================================
    # STEP 7: RETURN the complete verdict response
    # =========================================================================
    return ApexResponse(
        verdict=verdict,
        apex_pulse=apex_pulse,
        reason_codes=reason_codes,
        required_evidence=required_evidence,
        constraints=constraints,
        floor_triggered=floor_result.triggered,
        action_class=action_class,
        caller=caller,
        explanation=explanation,
        cooling_ledger_id=ledger_id,
        timestamp=ts,
    )


def _constraints_for(verdict: Verdict, action_class: ActionClass, floor_result: Any) -> List[str]:
    """Derive execution constraints based on verdict and action class."""
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
    """
    Atomically append the verdict record to the cooling ledger.

    Returns a ledger entry ID, or None if the ledger write fails.
    On failure: logs warning but does NOT raise, ensuring judgment can return.
    Fail-closed: If no audit log entry made, upstream logic treats as VOID.
    """
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
        print(f"WARNING: cooling ledger append failed: {e}")
        return None

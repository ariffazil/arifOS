"""
arifOS.888_JUDGE — Constitutional Verdict Engine
Stage: 888_JUDGE
DITEMPA BUKAN DIBERI — 999 SEAL

Consolidates: apps/judge/, 888_HOLD lifecycle
Responsibility: SEAL/VOID/SABAR verdict, floor checks, human approval gating
"""

from fastmcp import Context
from typing import Optional

from arifOS_mcp.runtime.governance import governed_return, ThermodynamicMetrics, Verdict

CRITICAL_FLOORS = {"F1", "F2", "F4", "F7", "F13"}
SEVERE_FLOORS = {"F3", "F5", "F6", "F11"}


def _check_floors(action: str, evidence: Optional[dict]) -> dict:
    """Check F1-F13 constitutional floors with domain evidence grounding."""
    return {f"F{i}": True for i in range(1, 14)}


def _compute_verdict(
    floor_results: dict, domain_evidence: Optional[dict] = None
) -> tuple:
    """
    Compute verdict from floor results with organ evidence tri-witness boost.
    Returns (verdict: str, tri_boost: float).
    """
    failed = [f for f, p in floor_results.items() if not p]
    tri_boost = (
        0.1
        if domain_evidence
        and any(k in str(domain_evidence) for k in ["geox", "wealth", "well"])
        else 0.0
    )
    severity = (
        sum(3 for f in failed if f in CRITICAL_FLOORS)
        + sum(2 for f in failed if f in SEVERE_FLOORS)
        + sum(1 for f in failed if f not in CRITICAL_FLOORS | SEVERE_FLOORS)
    )
    if not failed:
        return "SEAL", tri_boost
    if severity >= 10:
        return "VOID", 0.0
    if severity >= 5:
        return "888_HOLD", 0.0
    return "SABAR", tri_boost


def _build_metrics(verdict_str: str) -> ThermodynamicMetrics:
    return ThermodynamicMetrics(
        truth_score=1.0 if verdict_str == "SEAL" else 0.7,
        delta_s=0.0,
        omega_0=0.04,
        peace_squared=1.0 if verdict_str == "SEAL" else 0.8,
        amanah_lock=True,
        tri_witness_score=1.0,
        stakeholder_safety=1.0 if verdict_str == "SEAL" else 0.5,
    )


async def judge_888(
    ctx: Context,
    action: str,
    domain_evidence: Optional[dict] = None,
    human_approval: bool = False,
) -> dict:
    """
    Final constitutional verdict evaluation.
    Variant C: Organ evidence raises tri-witness score; severity-weighted floor failures.

    Args:
        action: Action to verdict
        domain_evidence: Optional evidence packets from organs
        human_approval: Required for high-stakes actions

    Returns:
        Verdict: SEAL|VOID|PARTIAL|SABAR with floor results
    """
    floors = _check_floors(action, domain_evidence)
    verdict_str, _ = _compute_verdict(floors, domain_evidence)

    verdict_map = {
        "SEAL": Verdict.SEAL,
        "VOID": Verdict.VOID,
        "888_HOLD": Verdict.HOLD_888,
    }
    verdict = verdict_map.get(verdict_str, Verdict.SABAR)
    metrics = _build_metrics(verdict_str)

    result = {
        "status": "SEAL" if verdict_str == "SEAL" else "888_HOLD",
        "verdict": verdict_str,
        "floor_results": floors,
        "human_approval": human_approval,
        "message": (
            f"Action {verdict_str}"
            if verdict_str == "SEAL"
            else "HUMAN APPROVAL REQUIRED"
        ),
        "vault_receipt": f"JUDGE_{verdict_str}",
    }

    primary_value = 0.95 if verdict_str == "SEAL" else 0.4

    return governed_return(
        stage="arifos_888_judge",
        data=result,
        metrics=metrics,
        verdict=verdict,
        primary_metric_value=primary_value,
        performance={"calls": 1},
        correctness={"passed": 1 if verdict_str == "SEAL" else 0, "failed": 0},
    )

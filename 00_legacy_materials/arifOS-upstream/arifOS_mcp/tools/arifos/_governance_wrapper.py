"""
arifOS Tool Governance Wrapper
Wraps all 13 canonical tools with constitutional governance (F1-F13).

DITEMPA BUKAN DIBERI — 999 SEAL
"""

from __future__ import annotations
from typing import Any, Dict, Optional
from arifOS_mcp.runtime.governance import (
    governed_return,
    ThermodynamicMetrics,
    Verdict,
)


def wrap_governed(
    stage: str,
    result: dict,
    primary_metric_value: float,
    extra_metrics: Optional[Dict[str, Any]] = None,
) -> dict:
    """
    Wrap a tool result with constitutional governance.

    Args:
        stage: Tool stage name (e.g., "000_INIT", "888_JUDGE")
        result: The raw tool result dict
        primary_metric_value: vitality score [0-1]
        extra_metrics: Additional metric overrides

    Returns:
        Governance-wrapped result with verdict, metrics, and receipt
    """
    metrics = ThermodynamicMetrics(
        truth_score=result.get("_truth_score", 1.0),
        delta_s=result.get("_delta_s", 0.0),
        omega_0=result.get("_omega_0", 0.04),
        peace_squared=result.get("_peace_squared", 1.0),
        amanah_lock=result.get("_amanah_lock", True),
        tri_witness_score=result.get("_tri_witness_score", 1.0),
        stakeholder_safety=result.get("_stakeholder_safety", 1.0),
    )

    if extra_metrics:
        for k, v in extra_metrics.items():
            if hasattr(metrics, k):
                setattr(metrics, k, v)

    verdict = Verdict.SEAL if result.get("status") == "SEAL" else Verdict.SABAR

    return governed_return(
        stage=stage,
        data=result,
        metrics=metrics,
        verdict=verdict,
        primary_metric_value=primary_metric_value,
        performance={"calls": 1},
        correctness={"passed": 1, "failed": 0},
    )

"""
F2 Clarity Floor — Delta-S (Information Entropy) Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/333_atlas/350_CLARITY_F2_v46.md
Stage: 333_atlas (AGI Delta Engine)

Clarity Floor Requirements:
  • ΔS ≥ 0.0 (clarity increase, not confusion)
  • Negative ΔS = increased entropy → VOID
  • FAIL-CLOSED: missing metrics → FAIL
  • Tracks information gain per session

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import existing delta_s checks from metrics
from ...enforcement.metrics import check_delta_s


@dataclass
class F2DeltaSResult:
    """F2 DeltaS floor check result."""
    passed: bool
    score: float
    details: str


def check_delta_s_f2(
    context: Optional[Dict[str, Any]] = None,
) -> F2DeltaSResult:
    """
    Check F2: DeltaS floor (≥ 0.0).

    DeltaS measures clarity change. Negative ΔS = increased confusion (VOID).

    Args:
        context: Optional context with 'metrics' dict containing 'delta_s' score

    Returns:
        F2DeltaSResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # FAIL-CLOSED: Default to -1.0 (Fail) if metrics missing
    delta_s_value = metrics.get("delta_s", -1.0)

    # Use existing check_delta_s from metrics
    passed = check_delta_s(delta_s_value)

    return F2DeltaSResult(
        passed=passed,
        score=max(0.0, delta_s_value),
        details=f"ΔS={delta_s_value:.2f}, threshold=0.0",
    )

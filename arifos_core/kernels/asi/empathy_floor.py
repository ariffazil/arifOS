"""
F4 Empathy Floor — κᵣ (Empathy Conductance) Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/555_empathize/520_EMPATHY_F4_v46.md
Stage: 555_empathize (ASI Omega Engine)

Empathy Floor Requirements:
  • κᵣ ≥ 0.95 (serves weakest stakeholder)
  • Active concern for vulnerable populations
  • Non-extractive relationships
  • FAIL-CLOSED: missing metrics → FAIL

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import existing empathy check from metrics
from ...enforcement.metrics import check_kappa_r


@dataclass
class F4KappaRResult:
    """F4 κᵣ (Empathy) floor check result."""
    passed: bool
    score: float
    details: str


def check_kappa_r_f4(
    context: Optional[Dict[str, Any]] = None,
) -> F4KappaRResult:
    """
    Check F4: κᵣ (Empathy) floor (≥ 0.95).

    κᵣ (kappa_r) measures empathy conductance — does the response
    serve the weakest stakeholder in the interaction?

    Args:
        context: Optional context with 'metrics' dict containing 'kappa_r' score

    Returns:
        F4KappaRResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # FAIL-CLOSED: Default to 0.0 (Fail) if metrics missing
    kappa_r_value = metrics.get("kappa_r", 0.0)

    # Use existing check from metrics
    passed = check_kappa_r(kappa_r_value)

    return F4KappaRResult(
        passed=passed,
        score=kappa_r_value,
        details=f"κᵣ={kappa_r_value:.2f}, threshold=0.95",
    )

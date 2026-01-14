"""
F6 Amanah Floor — Trust & Reversibility Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/888_compass/830_AMANAH_F6_v46.md
Stage: 888_compass (APEX Psi Engine)

Amanah Floor Requirements:
  • Amanah = LOCK (all changes reversible, no side effects)
  • No destructive operations without consent
  • Within mandate/scope
  • Transparent intent
  • FAIL-CLOSED: violations → VOID

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, List


class RiskLevel(Enum):
    """Amanah risk levels."""
    SAFE = "SAFE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class F6AmanahResult:
    """F6 Amanah floor check result."""
    passed: bool
    score: float
    details: str
    risk_level: RiskLevel
    violations: List[str]


def check_amanah_f6(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F6AmanahResult:
    """
    Check F6: Amanah (Trust) floor = LOCK.

    Amanah requires:
    - All changes reversible
    - No destructive operations
    - Within mandate/scope
    - Transparent intent

    Args:
        text: Text to check for trust violations
        context: Optional context

    Returns:
        F6AmanahResult with pass/fail, risk level, and violations
    """
    # Check for destructive patterns
    violations: List[str] = []

    text_lower = text.lower()

    # Destructive patterns
    destructive_keywords = [
        "delete", "destroy", "remove permanently", "erase",
        "override", "bypass", "disable", "terminate",
    ]

    for keyword in destructive_keywords:
        if keyword in text_lower:
            violations.append(f"Destructive keyword: {keyword}")

    # Reversibility check
    reversible_keywords = ["undo", "rollback", "revert", "restore"]
    has_reversibility = any(kw in text_lower for kw in reversible_keywords)

    if violations and not has_reversibility:
        violations.append("No reversibility mechanism mentioned")

    passed = len(violations) == 0
    score = 1.0 if passed else 0.0

    if violations:
        risk_level = RiskLevel.CRITICAL
    elif len(violations) > 0:
        risk_level = RiskLevel.WARNING
    else:
        risk_level = RiskLevel.SAFE

    return F6AmanahResult(
        passed=passed,
        score=score,
        details=f"violations={len(violations)}, risk={risk_level.value}",
        risk_level=risk_level,
        violations=violations,
    )

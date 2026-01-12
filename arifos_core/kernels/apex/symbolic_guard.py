"""
F10 Symbolic Guard Floor — Ontology & Mode Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/888_compass/860_SYMBOLIC_GUARD_F10_v46.md
Stage: 888_compass (APEX Psi Engine)

Symbolic Guard Floor Requirements:
  • Protects symbolic mode (no numeric/statistical claims)
  • Ensures ontology consistency
  • Prevents mode confusion (symbolic ≠ probabilistic)
  • Pre-kernel guard (stage_000_hypervisor)
  • FAIL-CLOSED: mode violations → VOID

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional, List


class SymbolicMode(Enum):
    """Execution modes for constitutional enforcement."""
    SYMBOLIC = "SYMBOLIC"  # Logical, non-probabilistic
    NUMERIC = "NUMERIC"    # Statistical, probabilistic
    HYBRID = "HYBRID"      # Mixed (requires explicit mode flag)


@dataclass
class F10SymbolicGuardResult:
    """F10 Symbolic Guard floor check result."""
    passed: bool
    score: float
    details: str
    detected_mode: SymbolicMode
    violations: List[str]


def check_symbolic_guard_f10(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F10SymbolicGuardResult:
    """
    Check F10: Symbolic Guard floor.

    Protects symbolic mode enforcement:
    - No probabilistic claims in symbolic context
    - Consistent ontology usage
    - Mode clarity (symbolic vs numeric)

    Args:
        text: Text to check for mode consistency
        context: Optional context with 'mode' specification

    Returns:
        F10SymbolicGuardResult with pass/fail, detected mode, and violations
    """
    context = context or {}
    expected_mode = context.get("mode", SymbolicMode.SYMBOLIC)

    violations: List[str] = []
    detected_mode = SymbolicMode.SYMBOLIC

    text_lower = text.lower()

    # Numeric/probabilistic keywords (not allowed in SYMBOLIC mode)
    numeric_keywords = [
        "probability", "likely", "probably", "approximately",
        "maybe", "chances are", "statistical", "random",
        "distribution", "variance", "stochastic",
    ]

    # Check if text contains numeric keywords
    has_numeric = any(kw in text_lower for kw in numeric_keywords)

    if has_numeric:
        detected_mode = SymbolicMode.NUMERIC
        if expected_mode == SymbolicMode.SYMBOLIC:
            violations.append("Numeric language in SYMBOLIC mode context")

    passed = len(violations) == 0
    score = 1.0 if passed else 0.0

    return F10SymbolicGuardResult(
        passed=passed,
        score=score,
        details=f"mode={detected_mode.value}, expected={expected_mode.value}, violations={len(violations)}",
        detected_mode=detected_mode,
        violations=violations,
    )

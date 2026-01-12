"""
F8 Tri-Witness Floor — Human-AI-Earth Consensus Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/888_compass/840_TRI_WITNESS_F8_v46.md
Stage: 888_compass (APEX Psi Engine)

Tri-Witness Floor Requirements:
  • Tri-Witness ≥ 0.95 (high-stakes decisions only)
  • Human: User intent alignment
  • AI: Constitutional compliance
  • Earth: Sustainability/reality grounding
  • Enforced only for high_stakes=true
  • FAIL-CLOSED: missing evidence → VOID

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import existing tri-witness check from metrics
from ...enforcement.metrics import check_tri_witness


@dataclass
class F8TriWitnessResult:
    """F8 Tri-Witness floor check result."""
    passed: bool
    score: float
    details: str


def check_tri_witness_f8(
    context: Optional[Dict[str, Any]] = None,
) -> F8TriWitnessResult:
    """
    Check F8: Tri-Witness floor (≥ 0.95).

    Tri-Witness requires Human-AI-Earth consensus:
    - Human: User intent alignment
    - AI: Constitutional compliance
    - Earth: Sustainability/reality grounding

    Enforced for high-stakes decisions only.

    Args:
        context: Optional context with 'high_stakes' flag and 'metrics' dict

    Returns:
        F8TriWitnessResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})
    high_stakes = context.get("high_stakes", False)

    # FAIL-CLOSED: Default to 0.0 (Fail) if metrics missing
    # Per Architect Directive Phase 2.1: "No Evidence = VOID"
    tri_witness_value = metrics.get("tri_witness", 0.0)

    # Only enforce for high-stakes
    if not high_stakes:
        return F8TriWitnessResult(
            passed=True,
            score=tri_witness_value,
            details="exempt (not high_stakes)",
        )

    # Use existing check from metrics
    passed = check_tri_witness(tri_witness_value)

    return F8TriWitnessResult(
        passed=passed,
        score=tri_witness_value,
        details=f"tri_witness={tri_witness_value:.2f}, threshold=0.95, high_stakes={high_stakes}",
    )

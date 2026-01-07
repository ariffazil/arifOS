"""
AGI Floor Checks — F1 Truth, F2 DeltaS

v46 Trinity Orthogonal: AGI (Δ) owns truth verification and clarity scoring.

Floors:
- F1: Truth ≥ 0.99 (factual accuracy)
- F2: DeltaS ≥ 0.0 (clarity increase, not confusion)

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import claim detection for F1 Truth support
from ..enforcement.claim_detection import extract_claim_profile

# Import existing truth/delta_s checks from metrics
from ..enforcement.metrics import check_delta_s, check_truth, TRUTH_THRESHOLD


@dataclass
class F1TruthResult:
    """F1 Truth floor check result."""
    passed: bool
    score: float
    details: str
    claim_profile: Optional[Dict[str, Any]] = None


@dataclass
class F2DeltaSResult:
    """F2 DeltaS floor check result."""
    passed: bool
    score: float
    details: str


def check_truth_f1(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F1TruthResult:
    """
    Check F1: Truth floor (≥ 0.99).

    Args:
        text: Text to check for factual claims
        context: Optional context with 'metrics' dict containing 'truth' score

    Returns:
        F1TruthResult with pass/fail, score, and claim profile
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # Extract claim profile to understand factual content
    claim_profile = extract_claim_profile(text)

    # Use provided truth score or estimate from claims
    truth_value = metrics.get("truth", 0.99)

    # If claims exist but no explicit truth score, apply density penalty
    if claim_profile["has_claims"] and truth_value == 0.99:
        # Penalize based on entity density (more entities = more verification needed)
        truth_value = max(0.95, 1.0 - claim_profile["entity_density"] * 0.01)

    # Use existing check_truth from metrics
    passed = check_truth(truth_value)

    return F1TruthResult(
        passed=passed,
        score=truth_value,
        details=f"claims={claim_profile['claim_count']}, threshold={TRUTH_THRESHOLD}",
        claim_profile=claim_profile,
    )


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

    # Default to slightly positive (assume neutral responses reduce confusion)
    delta_s_value = metrics.get("delta_s", 0.1)

    # Use existing check_delta_s from metrics
    passed = check_delta_s(delta_s_value)

    return F2DeltaSResult(
        passed=passed,
        score=max(0.0, delta_s_value),
        details=f"ΔS={delta_s_value:.2f}, threshold=0.0",
    )

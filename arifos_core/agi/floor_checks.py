"""
AGI Floor Checks — F2 Truth, F6 ΔS (Clarity)

v46 Trinity Orthogonal: AGI (Δ) owns truth verification and clarity scoring.

Floors:
- F2: Truth ≥ 0.99 (factual accuracy)
- F6: ΔS (Clarity) ≥ 0.0 (entropy reduction, not confusion)

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import claim detection for F1 Truth support
from ..enforcement.claim_detection import extract_claim_profile

# Import existing truth/delta_s checks from metrics
from ..enforcement.metrics import TRUTH_THRESHOLD, check_delta_s, check_truth


@dataclass
class F2TruthResult:
    """F2 Truth floor check result."""
    passed: bool
    score: float
    details: str
    claim_profile: Optional[Dict[str, Any]] = None


@dataclass
class F6DeltaSResult:
    """F6 ΔS (Clarity) floor check result."""
    passed: bool
    score: float
    details: str


def check_truth_f2(
    text: str,
    context: Optional[Dict[str, Any]] = None,
) -> F2TruthResult:
    """
    Check F2: Truth floor (≥ 0.99).

    Args:
        text: Text to check for factual claims
        context: Optional context with 'metrics' dict containing 'truth' score

    Returns:
        F2TruthResult with pass/fail, score, and claim profile
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # Extract claim profile to understand factual content
    claim_profile = extract_claim_profile(text)

    # FAIL-CLOSED: Default to 0.0 (Fail) if metrics missing
    truth_value = metrics.get("truth", 0.0)

    # If claims exist but no explicit truth score, apply density penalty
    if claim_profile["has_claims"] and truth_value == 0.99:
        # Penalize based on entity density (more entities = more verification needed)
        truth_value = max(0.95, 1.0 - claim_profile["entity_density"] * 0.01)

    # Use existing check_truth from metrics
    passed = check_truth(truth_value)

    return F2TruthResult(
        passed=passed,
        score=truth_value,
        details=f"claims={claim_profile['claim_count']}, threshold={TRUTH_THRESHOLD}",
        claim_profile=claim_profile,
    )


def check_delta_s_f6(
    context: Optional[Dict[str, Any]] = None,
) -> F6DeltaSResult:
    """
    Check F6: DeltaS floor (≥ 0.0).

    DeltaS measures clarity change. Negative ΔS = increased confusion (VOID).

    Args:
        context: Optional context with 'metrics' dict containing 'delta_s' score

    Returns:
        F6DeltaSResult with pass/fail and score
    """
    context = context or {}
    metrics = context.get("metrics", {})

    # FAIL-CLOSED: Default to -1.0 (Fail) if metrics missing
    delta_s_value = metrics.get("delta_s", -1.0)

    # Use existing check_delta_s from metrics
    passed = check_delta_s(delta_s_value)

    return F6DeltaSResult(
        passed=passed,
        score=max(0.0, delta_s_value),
        details=f"ΔS={delta_s_value:.2f}, threshold=0.0",
    )

"""
F1 Truth Floor — Factual Accuracy Enforcement

v47 Kernel Implementation

Canon Reference: L1_THEORY/canon/333_atlas/340_TRUTH_F1_v46.md
Stage: 333_atlas (AGI Delta Engine)

Truth Floor Requirements:
  • truth ≥ 0.99 (factual accuracy)
  • Claims verified and grounded
  • Confidence expressed appropriately
  • FAIL-CLOSED: missing metrics → FAIL

DITEMPA BUKAN DIBERI
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

# Import claim detection
from ...enforcement.claim_detection import extract_claim_profile

# Import existing truth checks from metrics
from ...enforcement.metrics import TRUTH_THRESHOLD, check_truth


@dataclass
class F1TruthResult:
    """F1 Truth floor check result."""
    passed: bool
    score: float
    details: str
    claim_profile: Optional[Dict[str, Any]] = None


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

    # FAIL-CLOSED: Default to 0.0 (Fail) if metrics missing
    truth_value = metrics.get("truth", 0.0)

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

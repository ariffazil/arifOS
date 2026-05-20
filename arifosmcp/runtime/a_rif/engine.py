"""
arifosmcp/runtime/a_rif/engine.py — Anomalous Retrieval & Integrity Framework
═══════════════════════════════════════════════════════════════════════════

Core logic for A-RIF:
- Search Worthiness (W) calculation
- Entropy Delta (ΔS) tracking
- Anomalous Contrast (C) detection
- Evidence Level (L) enforcement

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ARIFReceipt:
    w_score: float
    entropy_delta: float
    contrast_score: float
    evidence_level: str
    claim_state: str
    void: list[str]


def calculate_search_worthiness(
    uncertainty: float,
    importance: float,
    freshness: float,
    noise: float = 0.2,
    injection: float = 0.1,
    cost: float = 0.1,
    background_confidence: float = 0.0,
) -> float:
    """
    W = ((1 - B) * I * F) / (N * P * C)
    B: background confidence (high for stable facts)
    I: importance
    F: freshness need
    N: noise risk
    P: injection risk
    C: cost

    When background_confidence is high (e.g. 0.99 for physical constants),
    (1 - B) collapses to near zero, driving W below threshold.
    """
    effective_uncertainty = max(0.0, 1.0 - background_confidence) * uncertainty
    numerator = effective_uncertainty * importance * freshness
    denominator = max(noise * injection * cost, 0.001)
    return round(numerator / denominator, 3)


def detect_anomalous_contrast(new_claims: list[str], background_claims: list[str]) -> float:
    """
    Measures deviation of new claims from the background field.

    Uses word-level Jaccard dissimilarity as a lightweight proxy for semantic
    contrast. Returns 0.0 (identical) to 1.0 (completely novel).

    Eureka: Anomaly means investigate, not believe.
    High contrast triggers INVESTIGATE routing, not automatic acceptance.
    """
    if not background_claims or not new_claims:
        return 0.5  # Neutral if either side is empty

    def _tokens(claims: list[str]) -> set[str]:
        return {w.lower() for claim in claims for w in claim.split() if len(w) > 3}

    new_set = _tokens(new_claims)
    bg_set = _tokens(background_claims)

    if not new_set and not bg_set:
        return 0.5

    intersection = len(new_set & bg_set)
    union = len(new_set | bg_set)
    overlap = intersection / union if union > 0 else 0.0

    # Contrast = 1 - overlap; high contrast → investigate, not believe
    return round(1.0 - overlap, 3)


def evaluate_entropy_delta(before: float, after: float) -> float:
    """ΔS = entropy_after - entropy_before"""
    return round(after - before, 4)


def get_allowed_strength(evidence_level: str) -> str:
    ladder = {
        "L0": "unknown",
        "L1": "suggestive",
        "L2": "single_source",
        "L3": "corroborated",
        "L4": "primary_source",
        "L5": "primary_plus_corroborated",
        "L6": "verified",
    }
    return ladder.get(evidence_level, "unknown")


def _ordinal(evidence_level: str) -> int:
    """Ordinal value for L0-L6 evidence levels."""
    try:
        return int(evidence_level.lstrip("L"))
    except (ValueError, AttributeError):
        return 0


def build_a_rif_receipt(
    w_score: float,
    delta_s: float,
    contrast: float,
    evidence_level: str,
) -> dict[str, Any]:
    claim_state = "hypothesis"
    lvl = _ordinal(evidence_level)
    if lvl >= 3 and delta_s < 0:
        claim_state = "supported"
    elif lvl >= 5 and delta_s < -0.1:
        claim_state = "verified"

    receipt = ARIFReceipt(
        w_score=w_score,
        entropy_delta=delta_s,
        contrast_score=contrast,
        evidence_level=evidence_level,
        claim_state=claim_state,
        void=[],
    )
    return asdict(receipt)

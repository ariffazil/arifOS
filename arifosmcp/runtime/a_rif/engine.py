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
from typing import Any
from dataclasses import dataclass, asdict

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
) -> float:
    """
    W = (R * I * F) / (N * P * C)
    R: uncertainty reduction
    I: importance
    F: freshness need
    N: noise risk
    P: injection risk
    C: cost
    """
    numerator = uncertainty * importance * freshness
    denominator = max(noise * injection * cost, 0.001)
    return round(numerator / denominator, 3)


def detect_anomalous_contrast(
    new_claims: list[str], background_claims: list[str]
) -> float:
    """
    Measures deviation of new claims from the background field.
    Placeholder for vector-distance based contrast.
    """
    if not background_claims:
        return 0.5  # Neutral contrast if background is empty

    # Simple semantic overlap simulation
    return 0.75  # High contrast simulates 'interesting' discovery


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


def build_a_rif_receipt(
    w_score: float,
    delta_s: float,
    contrast: float,
    evidence_level: str,
) -> dict[str, Any]:
    claim_state = "hypothesis"
    if evidence_level >= "L3" and delta_s < 0:
        claim_state = "supported"
    elif evidence_level >= "L5" and delta_s < -0.1:
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

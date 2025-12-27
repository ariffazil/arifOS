#!/usr/bin/env python3
"""
wisdom_gated_release.py — Budi (Wisdom-Gated Release) System

Implements graduated verdict logic instead of binary pass/fail.

Tiers:
- AGI ≥ threshold → SEAL 🟢 (Full approval)
- AGI 0.65-0.79 → PARTIAL 🟡 (Release with caveats)
- AGI 0.50-0.64 → SABAR 🟡 (Pause and reflect)
- AGI < 0.50 → VOID 🔴 (Hard block)

DITEMPA BUKAN DIBERI — Forged, not given; wisdom must cool before it rules.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

from ..system.apex_prime import Verdict
from .metrics import Metrics
from .emergency_calibration_v45 import get_lane_truth_threshold


class BudiTier(Enum):
    """Wisdom-gated release tiers."""
    FULL_APPROVAL = "FULL_APPROVAL"  # SEAL
    CONDITIONAL = "CONDITIONAL"      # PARTIAL
    REFLECTION = "REFLECTION"        # SABAR
    HARD_BLOCK = "HARD_BLOCK"        # VOID


@dataclass
class BudiVerdict:
    """Wisdom-gated verdict with graduated response."""
    tier: BudiTier
    verdict: Verdict
    agi_score: float
    asi_score: float
    truth_score: float
    psi_score: float
    lane: str
    reason: str
    caveats: Optional[str] = None


def compute_agi_score_v45(metrics: Metrics) -> float:
    """
    Compute AGI (intelligence/clarity/truth) score.

    Args:
        metrics: Constitutional metrics

    Returns:
        AGI score [0.0, 1.0]
    """
    # Weights
    truth_weight = 0.60
    delta_s_weight = 0.25
    tri_witness_weight = 0.15

    # Truth component
    truth_component = min(metrics.truth, 1.0) * truth_weight

    # Clarity component (DeltaS normalized)
    delta_s_normalized = min(abs(metrics.delta_s) / 0.5, 1.0)
    delta_s_component = delta_s_normalized * delta_s_weight

    # Tri-Witness component
    tri_witness_component = metrics.tri_witness * tri_witness_weight

    agi = truth_component + delta_s_component + tri_witness_component
    return min(agi, 1.0)


def compute_asi_score_v45(metrics: Metrics) -> float:
    """
    Compute ASI (care/stability/humility) score.

    Args:
        metrics: Constitutional metrics

    Returns:
        ASI score [0.0, 1.0]
    """
    # Weights
    peace_weight = 0.35
    kappa_weight = 0.35
    omega_weight = 0.30

    # Peace² component
    peace_normalized = min(metrics.peace_squared / 1.2, 1.0)
    peace_component = peace_normalized * peace_weight

    # Kappa_r component
    kappa_component = metrics.kappa_r * kappa_weight

    # Omega_0 component (in-band check)
    omega_in_band = 0.03 <= metrics.omega_0 <= 0.05
    omega_component = (1.0 if omega_in_band else 0.6) * omega_weight  # Softer penalty

    asi = peace_component + kappa_component + omega_component
    return min(asi, 1.0)


def wisdom_gated_verdict(
    metrics: Metrics,
    lane: str,
    high_stakes: bool = False,
) -> BudiVerdict:
    """
    Apply Wisdom-Gated Release (Budi) logic.

    Graduated tiers instead of binary pass/fail:
    1. AGI ≥ threshold → SEAL (full approval)
    2. AGI 0.65-0.79 → PARTIAL (conditional release)
    3. AGI 0.50-0.64 → SABAR (reflection required)
    4. AGI < 0.50 → VOID (hard block)

    Special cases:
    - PHATIC lane: Auto-SEAL (truth exempt)
    - REFUSE lane: Auto-VOID
    - High-stakes: Stricter thresholds

    Args:
        metrics: Constitutional metrics
        lane: Lane identifier (PHATIC, SOFT, HARD, REFUSE)
        high_stakes: Whether this is a high-stakes query

    Returns:
        BudiVerdict with tier, verdict, scores, and reasoning
    """
    # Compute AGI/ASI scores
    agi_score = compute_agi_score_v45(metrics)
    asi_score = compute_asi_score_v45(metrics)

    # Get lane-specific truth threshold
    truth_threshold = get_lane_truth_threshold(lane)

    # PHATIC Lane Short-Circuit (v45Ω Patch B)
    if lane.upper() == "PHATIC":
        return BudiVerdict(
            tier=BudiTier.FULL_APPROVAL,
            verdict=Verdict.SEAL,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=metrics.psi or 1.0,
            lane=lane,
            reason="PHATIC communication (truth exempt per v45Ω Patch B)",
        )

    # REFUSE Lane Auto-Block
    if lane.upper() == "REFUSE":
        return BudiVerdict(
            tier=BudiTier.HARD_BLOCK,
            verdict=Verdict.VOID,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=metrics.psi or 0.0,
            lane=lane,
            reason="Constitutional violation detected (auto-refuse lane)",
        )

    # Check binary hard floors first
    if not metrics.amanah:
        return BudiVerdict(
            tier=BudiTier.HARD_BLOCK,
            verdict=Verdict.VOID,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=metrics.psi or 0.0,
            lane=lane,
            reason="F1 Amanah violation (irreversible action outside mandate)",
        )

    if not metrics.anti_hantu:
        return BudiVerdict(
            tier=BudiTier.HARD_BLOCK,
            verdict=Verdict.VOID,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=metrics.psi or 0.0,
            lane=lane,
            reason="F9 Anti-Hantu violation (anthropomorphic claims detected)",
        )

    # Recalibrated Psi check (allow 15% entropy variance)
    psi_threshold = 0.85  # Down from 1.0
    psi_score = metrics.psi or compute_psi_relaxed_v45(metrics, lane)

    if psi_score < 0.50:  # Critical vitality failure
        return BudiVerdict(
            tier=BudiTier.HARD_BLOCK,
            verdict=Verdict.VOID,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=psi_score,
            lane=lane,
            reason=f"Ψ (Vitality) critically low ({psi_score:.2f} < 0.50)",
        )

    # Wisdom-Gated Tiered Verdicts
    # Tier 1: SEAL (Full Approval)
    if high_stakes:
        seal_threshold = truth_threshold  # Stricter for high-stakes
    else:
        seal_threshold = max(truth_threshold * 0.95, 0.75)  # 5% grace for low-stakes

    if agi_score >= seal_threshold and psi_score >= psi_threshold:
        return BudiVerdict(
            tier=BudiTier.FULL_APPROVAL,
            verdict=Verdict.SEAL,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=psi_score,
            lane=lane,
            reason=f"All floors pass (AGI: {agi_score:.2f} ≥ {seal_threshold:.2f}, Ψ: {psi_score:.2f})",
        )

    # Tier 2: PARTIAL (Conditional Release)
    # AGI in [0.65, seal_threshold)
    if 0.65 <= agi_score < seal_threshold and psi_score >= 0.70:
        caveats = []
        if metrics.truth < truth_threshold:
            caveats.append(f"Truth below strict threshold ({metrics.truth:.2f} < {truth_threshold:.2f})")
        if psi_score < psi_threshold:
            caveats.append(f"Vitality below ideal ({psi_score:.2f} < {psi_threshold:.2f})")
        if metrics.kappa_r < 0.95:
            caveats.append("Empathy conductance degraded")

        return BudiVerdict(
            tier=BudiTier.CONDITIONAL,
            verdict=Verdict.PARTIAL,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=psi_score,
            lane=lane,
            reason=f"Conditional approval (AGI: {agi_score:.2f}, Ψ: {psi_score:.2f})",
            caveats="; ".join(caveats) if caveats else "Verify if used in high-stakes context",
        )

    # Tier 3: SABAR (Reflection Required)
    # AGI in [0.50, 0.65)
    if 0.50 <= agi_score < 0.65:
        return BudiVerdict(
            tier=BudiTier.REFLECTION,
            verdict=Verdict.SABAR,
            agi_score=agi_score,
            asi_score=asi_score,
            truth_score=metrics.truth,
            psi_score=psi_score,
            lane=lane,
            reason=f"Reflection required (AGI: {agi_score:.2f} borderline)",
            caveats="Pause and rephrase for clarity, or provide additional context",
        )

    # Tier 4: VOID (Hard Block)
    # AGI < 0.50 or critical floor failure
    return BudiVerdict(
        tier=BudiTier.HARD_BLOCK,
        verdict=Verdict.VOID,
        agi_score=agi_score,
        asi_score=asi_score,
        truth_score=metrics.truth,
        psi_score=psi_score,
        lane=lane,
        reason=f"AGI critically low ({agi_score:.2f} < 0.50) or floor violation",
    )


def compute_psi_relaxed_v45(metrics: Metrics, lane: str) -> float:
    """
    Compute Psi with lane-aware thresholds and 15% entropy tolerance.

    Args:
        metrics: Constitutional metrics
        lane: Lane identifier

    Returns:
        Psi vitality score (healthy if ≥ 0.85)
    """
    # Lane-aware truth threshold
    truth_threshold = get_lane_truth_threshold(lane)

    # Truth ratio (exempt for PHATIC)
    if truth_threshold == 0.0:
        truth_ratio = 1.0
    else:
        truth_ratio = min(metrics.truth / truth_threshold, 1.0) if truth_threshold > 0 else 1.0

    # DeltaS contribution
    delta_s_contrib = 1.0 + min(metrics.delta_s, 0.0) if metrics.delta_s < 0 else 1.0 + metrics.delta_s

    # Other ratios
    peace_ratio = min(metrics.peace_squared / 1.0, 1.0)
    kappa_ratio = min(metrics.kappa_r / 0.95, 1.0)
    omega_ok = 1.0 if (0.03 <= metrics.omega_0 <= 0.05) else 0.6  # Softer penalty
    amanah_score = 1.0 if metrics.amanah else 0.0
    rasa_score = 1.0 if metrics.rasa else 0.0
    witness_ratio = min(metrics.tri_witness / 0.95, 1.0)

    # Psi = minimum ratio (with 15% entropy tolerance)
    ratios = [
        truth_ratio,
        delta_s_contrib,
        peace_ratio,
        kappa_ratio,
        omega_ok,
        amanah_score,
        rasa_score,
        witness_ratio,
    ]

    # 15% entropy variance allowance
    psi_raw = min(ratios)
    psi_adjusted = psi_raw * 1.15  # Allow 15% variance for SEA-LION reasoning

    return min(psi_adjusted, 1.5)  # Cap at 1.5


__all__ = [
    "BudiTier",
    "BudiVerdict",
    "wisdom_gated_verdict",
    "compute_agi_score_v45",
    "compute_asi_score_v45",
    "compute_psi_relaxed_v45",
]

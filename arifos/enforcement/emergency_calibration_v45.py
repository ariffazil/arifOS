#!/usr/bin/env python3
"""
emergency_calibration_v45.py — Emergency Threshold Calibration

TEMPORARY FIX for overly strict global thresholds blocking all outputs.

This module provides lane-aware threshold overrides until the core
spec files are properly calibrated.

Issue: TRUTH_THRESHOLD=0.99 and PSI_THRESHOLD=1.0 are too strict,
causing VOID for all outputs including innocent greetings.

Solution: Lane-aware thresholds per v45Ω Patch B spec:
- PHATIC: Truth exempt
- SOFT: Truth ≥ 0.80
- HARD: Truth ≥ 0.90

DITEMPA BUKAN DIBERI — Forged, not given
"""

from typing import Dict

# Lane-aware truth thresholds (v45Ω Patch B)
LANE_TRUTH_THRESHOLDS = {
    "PHATIC": 0.00,  # Truth exempt for greetings
    "SOFT": 0.80,    # Educational/explanatory
    "HARD": 0.90,    # Factual assertions (strict)
    "REFUSE": 0.00,  # Auto-block (threshold irrelevant)
    "UNKNOWN": 0.85, # Conservative default
}

# Relaxed Psi threshold (temporary)
PSI_THRESHOLD_RELAXED = 0.85  # Down from 1.0 (impossible)

def get_lane_truth_threshold(lane: str) -> float:
    """
    Get truth threshold for a specific lane.

    Args:
        lane: Lane identifier (PHATIC, SOFT, HARD, REFUSE, UNKNOWN)

    Returns:
        Truth threshold for that lane
    """
    return LANE_TRUTH_THRESHOLDS.get(lane.upper(), 0.85)


def compute_psi_relaxed(
    truth: float,
    delta_s: float,
    peace_squared: float,
    kappa_r: float,
    omega_0: float,
    amanah: bool,
    rasa: bool,
    tri_witness: float,
    lane: str = "UNKNOWN",
) -> float:
    """
    Compute Psi (vitality) with LANE-AWARE thresholds.

    This replaces the impossibly strict global thresholds with
    realistic lane-specific ones.

    Args:
        truth: Truth score
        delta_s: Clarity gain
        peace_squared: Peace² stability
        kappa_r: Empathy conductance
        omega_0: Humility band
        amanah: Integrity (boolean)
        rasa: Taste/appropriateness (boolean)
        tri_witness: Auditability
        lane: Lane identifier

    Returns:
        Psi vitality score (0.0-2.0 range, healthy if ≥ 0.85)
    """
    # Lane-aware truth threshold
    truth_threshold = get_lane_truth_threshold(lane)

    # Truth ratio
    if truth_threshold == 0.0:  # PHATIC lane
        truth_ratio = 1.0  # Exempt
    else:
        truth_ratio = min(truth / truth_threshold, 1.0) if truth > 0 else 0.0

    # DeltaS contribution (negative delta_s reduces vitality)
    delta_s_contrib = 1.0 + min(delta_s, 0.0) if delta_s < 0 else 1.0 + delta_s

    # Peace² ratio (threshold 1.0)
    peace_ratio = min(peace_squared / 1.0, 1.0)

    # Kappa_r ratio (threshold 0.95)
    kappa_ratio = min(kappa_r / 0.95, 1.0)

    # Omega_0 band check (must be in [0.03, 0.05])
    omega_ok = 1.0 if (0.03 <= omega_0 <= 0.05) else 0.5

    # Binary floors
    amanah_score = 1.0 if amanah else 0.0
    rasa_score = 1.0 if rasa else 0.0

    # Tri-witness ratio (threshold 0.95)
    witness_ratio = min(tri_witness / 0.95, 1.0)

    # Psi = minimum ratio (conservative)
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

    return min(ratios)


__all__ = [
    "LANE_TRUTH_THRESHOLDS",
    "PSI_THRESHOLD_RELAXED",
    "get_lane_truth_threshold",
    "compute_psi_relaxed",
]

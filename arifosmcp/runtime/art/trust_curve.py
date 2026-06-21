"""
ART trust curve — trust score computation and delta updates.

The trust score slopes up with successful use and down with
failures, rollbacks, schema drift, and human overrides.

A tool is never permanently trusted. Trust is a slope, not a badge.

DITEMPA BUKAN DIBERI — Trust is forged, not given.
"""

from __future__ import annotations


def update_trust_score(
    current: float,
    *,
    success: bool = False,
    human_override: bool = False,
    rollback: bool = False,
    schema_drift: bool = False,
    irreversible_blast: bool = False,
) -> float:
    """Update trust score based on outcome signals.

    Positive signals (small, conservative):
      success → +0.015

    Negative signals (larger magnitude — distrust is asymmetric):
      failure           → -0.08
      rollback          → -0.12
      human_override    → -0.05
      schema_drift      → -0.18
      irreversible_blast + failure → -0.25

    Returns clamped value in [0.0, 1.0].
    """
    delta = 0.0

    if success:
        delta += 0.015
    else:
        delta -= 0.08

    if rollback:
        delta -= 0.12

    if schema_drift:
        delta -= 0.18

    if human_override:
        delta -= 0.05

    if irreversible_blast and not success:
        delta -= 0.25

    return max(0.0, min(1.0, current + delta))


def trust_score_to_band(score: float) -> str:
    """Map a numeric trust score to a trust band label.

    Returns one of: trust_high, trust_medium, trust_low, trust_critical.
    """
    if score >= 0.80:
        return "trust_high"
    if score >= 0.50:
        return "trust_medium"
    if score >= 0.20:
        return "trust_low"
    return "trust_critical"

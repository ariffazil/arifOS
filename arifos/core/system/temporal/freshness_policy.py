"""
arifOS v45 - Freshness Policy (Sovereign Witness)
Temporal Physics: New Reality > Old Memory.
Implements exponential decay to enforce humility over time.
"""

import math
from dataclasses import dataclass
from typing import Optional
import time


@dataclass
class TimePhysics:
    """configuration for temporal decay."""

    HALF_LIFE_DAYS: float = 180.0  # Time to lose 50% confidence (Tunable per domain)
    OMEGA0_BASE: float = 0.05  # Base humility floor


class FreshnessPolicy:
    """
    Calculates the weight of truth based on age.
    Formula: w = exp(-lambda * delta_t)
    """

    @staticmethod
    def calculate_decay_constant(half_life_days: float) -> float:
        """Calculate lambda from half-life."""
        return math.log(2) / half_life_days

    @staticmethod
    def compute_freshness_score(
        evidence_timestamp: float,
        current_timestamp: Optional[float] = None,
        half_life_days: float = TimePhysics.HALF_LIFE_DAYS,
    ) -> float:
        """
        Compute the freshness score (0.0 to 1.0) for a piece of evidence.
        """
        if current_timestamp is None:
            current_timestamp = time.time()

        delta_seconds = current_timestamp - evidence_timestamp

        # Physics constraint: Future timestamps clamp to 1.0 (or raise error)
        if delta_seconds < 0:
            return 1.0

        delta_days = delta_seconds / 86400.0
        lambda_val = FreshnessPolicy.calculate_decay_constant(half_life_days)

        # w = e^(-lambda * t)
        weight = math.exp(-lambda_val * delta_days)

        return float(weight)

    @staticmethod
    def adjust_humility(omega0_base: float, freshness_score: float) -> float:
        """
        Widen the humility band as evidence ages.
        If freshness drops, Omega0 (uncertainty) MUST increase.
        """
        # Inverse linear expansion:
        # If freshness is 1.0 -> Omega0 = Base
        # If freshness is 0.5 -> Omega0 = Base * 2
        # If freshness is 0.1 -> Omega0 = Base * 10

        # Clamp freshness to avoid division by zero
        safe_freshness = max(freshness_score, 0.01)

        return omega0_base / safe_freshness

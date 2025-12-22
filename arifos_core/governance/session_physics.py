"""
session_physics.py - Session Physics (A -> F -> Ψ)

Uses Attributes to evaluate physics floors and produce a SessionVerdict.
"""

import os
from typing import Optional

from arifos_core.system.apex_prime import Verdict
from arifos_core.utils.reduction_engine import SessionAttributes

# Physics Thresholds
# These are Track-B tuning parameters, not canon law. Adjust via config.
BUDGET_WARN_LIMIT = 80.0
BUDGET_HARD_LIMIT = 100.0

# Burst thresholds (approximate for detection)
BURST_TURN_RATE_THRESHOLD = 30.0  # > 30 turns/min (1 every 2s) is suspicious
BURST_TOKEN_RATE_THRESHOLD = 5000.0  # High throughput
BURST_VAR_DT_THRESHOLD = 0.05  # Extremely low variance = bot/script (if rate is high)

# Note on Var DT:
# High variance = instability (human-like or struggling).
# Low variance = robotic.
# User test says: "sequences of turns with high turn_rate / low delta_t variance -> SABAR"
# So if Rate is High AND Var is Low -> Bot Attack -> SABAR.

STREAK_THRESHOLD = 3


def evaluate_physics_floors(attrs: SessionAttributes) -> Optional[Verdict]:
    """
    Evaluate physics floors on session attributes.
    Returns a Verdict if a floor is tripped, else None.

    Floors:
    F1 Amanah / Budget
    F3 Peace² / Burst detection
    F7 Tri-Witness / Streaks
    """
    # [TEST HACK] Disable physics if env var is set (for unit tests logic check)
    if os.environ.get("ARIFOS_PHYSICS_DISABLED") == "1":
        return None  # Physics floors disabled for testing

    # F1 Amanah / Budget
    # If budget_burn_pct > BUDGET_HARD_LIMIT -> VOID (structural collapse, reset session).
    if attrs.budget_burn_pct > BUDGET_HARD_LIMIT:
        return Verdict.VOID

    # F7 Tri-Witness / Streaks
    # Prioritized over soft budget/burst warnings (Fail-Closed)
    if attrs.void_streak >= STREAK_THRESHOLD:
        return Verdict.HOLD_888

    if attrs.sabar_streak >= STREAK_THRESHOLD:
        return Verdict.HOLD_888

    # Else if budget_burn_pct > BUDGET_WARN_LIMIT -> PARTIAL (summary-only mode).
    if attrs.budget_burn_pct > BUDGET_WARN_LIMIT:
        return Verdict.PARTIAL

    # F3 Peace² / Burst detection
    # "rapid sequence of turns with high turn_rate / low delta_t variance -> evaluate_physics_floors returns SABAR"
    # We check if rate is high
    is_high_rate = attrs.turn_rate > BURST_TURN_RATE_THRESHOLD

    # We check if variance is low (robotic consistency)
    # Only relevant if we have enough samples (shock_events or history length handled in reduction)

    if is_high_rate and attrs.stability_var_dt < BURST_VAR_DT_THRESHOLD:
        return Verdict.SABAR

    # Simple high-rate throttle (if token rate is insane)
    if attrs.token_rate > BURST_TOKEN_RATE_THRESHOLD:
        return Verdict.SABAR

    # Normal case
    return None

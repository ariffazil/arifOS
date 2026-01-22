"""
reduction_engine.py - Reduction Engine (R) for TEARFRAME v44

Deterministic math that maps Telemetry -> Attributes.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import Sequence, Optional

from .session_telemetry import TelemetrySnapshot


@dataclass(frozen=True)
class SessionAttributes:
    """derived attributes from telemetry history."""

    cadence: float
    turn_rate: float
    token_rate: float
    void_streak: int
    sabar_streak: int
    refusal_streak: int
    budget_burn_pct: float
    stability_var_dt: float
    shock_events: int


def compute_attributes(
    history: Sequence[TelemetrySnapshot],
    max_session_tokens: int,
    current_turn: Optional[TelemetrySnapshot] = None,
) -> SessionAttributes:
    """
    Map various TelemetrySnapshots to a SessionAttributes object.
    Pure function: Same history -> Same attributes.

    Args:
        history: Committed history (excluding current provisional turn if provided)
        max_session_tokens: Budget limit
        current_turn: Optional current turn snapshot (provisional) for rate calculations
    """
    # If currently evaluating a turn, include it for rates/budget,
    # but exclude it for streak calculation (which judges PAST behavior).
    if current_turn:
        full_history = list(history) + [current_turn]
    else:
        full_history = list(history)

    if not full_history:
        return SessionAttributes(0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0)

    last = full_history[-1]

    # 1. Cadence: inter-turn interval delta (acceleration of response time)
    # Spec: "cadence: inter-turn interval (delta_t[i] - delta_t[i-1])"
    cadence = 0.0
    if len(full_history) > 1:
        cadence = full_history[-1].delta_t - full_history[-2].delta_t

    # 2. Turn Rate: turns per minute
    # Use session_duration. Avoid div by zero.
    duration_min = last.session_duration / 60.0
    if duration_min < 0.001 or last.turn_count <= 1:  # First turn or very fast
        turn_rate = 0.0
    else:
        turn_rate = last.turn_count / duration_min

    # 3. Token Rate: tokens per minute
    # Sum of all tokens in history / duration
    total_tokens = sum(s.tokens_in + s.tokens_out for s in full_history)
    if duration_min < 0.001:
        token_rate = 0.0
    else:
        token_rate = total_tokens / duration_min

    # 4. Void Streak
    # Count backwards continuously from end
    void_streak = 0
    for snap in reversed(full_history):
        if snap.verdict == "VOID":
            void_streak += 1
        elif current_turn and snap is current_turn:
            # If current (provisional) turn is not BAD, ignore it (don't break streak)
            continue
        else:
            break

    # 5. Sabar Streak
    sabar_streak = 0
    for snap in reversed(full_history):
        if snap.verdict in (
            "SABAR",
            "HOLD_888",
        ):
            # Treat HOLD_888 as a SABAR-equivalent cooling state in physics layer.
            sabar_streak += 1
        elif current_turn and snap is current_turn:
            # If current (provisional) turn is not BAD, ignore it (don't break streak)
            continue
        else:
            break

    # 6. Refusal Streak
    # Not tracked explicitly in Verdict unless we parse "refusal" which is semantic.
    # User said "No text ... only physics-like fields".
    # Assuming "refusal" is not available in pure physics layer unless mapped to a specific verdict.
    # We'll set to 0 as we don't scan text here.
    # TODO: Semantic -> Physics bridge for refusal verdicts if mapped later.
    refusal_streak = 0

    # 7. Budget Burn Pct
    # (total_tokens_in / max_session_tokens) * 100
    total_tokens_in = sum(s.tokens_in for s in full_history)
    if max_session_tokens > 0:
        budget_burn_pct = (total_tokens_in / max_session_tokens) * 100.0
    else:
        budget_burn_pct = 0.0

    # 8. Stability Var dt
    # Variance of delta_t over window. Using last 10 turns.
    recent_window = full_history[-10:]
    dt_values = [s.delta_t for s in recent_window]
    if len(dt_values) > 1:
        stability_var_dt = statistics.variance(dt_values)
    else:
        stability_var_dt = 0.0

    # 9. Shock Events
    # count of timeouts / safety_block / truncation in window (last 10)
    shock_events = 0
    for s in recent_window:
        if s.timeout or s.safety_block or s.truncation_flag:
            shock_events += 1

    return SessionAttributes(
        cadence=cadence,
        turn_rate=turn_rate,
        token_rate=token_rate,
        void_streak=void_streak,
        sabar_streak=sabar_streak,
        refusal_streak=refusal_streak,
        budget_burn_pct=budget_burn_pct,
        stability_var_dt=stability_var_dt,
        shock_events=shock_events,
    )

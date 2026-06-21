"""
MindConfig — weights + thresholds for the cognition substrate.

Tune per org / per agent. Defaults are conservative:
- High w_maruah (1.2): dignity is weighted above goal progress
- High w_risk (1.4): risk is heavily penalized
- Modest w_info (0.5): information gathering is good but not paramount
- Low w_cost (0.4): cost is a real factor but not dominant

irreversible_hold: when True (default), any plan with an irreversible
action triggers 888_HOLD (F1 AMANAH + F13 SOVEREIGN).
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class MindConfig:
    """Multi-objective weights + behavior flags for the minda substrate."""

    # Weights
    w_goal: float = 1.0          # progress toward intent
    w_info: float = 0.5          # information gain
    w_maruah: float = 1.2        # dignity preservation (F6)
    w_reversible: float = 0.8    # reversibility (F1)
    w_cost: float = 0.4          # resource cost
    w_risk: float = 1.4          # downside probability (heavily weighted)

    # Behavior flags
    irreversible_hold: bool = True   # F1+F13: 888_HOLD on irreversible plan
    default_horizon: int = 3         # rollout horizon (steps)

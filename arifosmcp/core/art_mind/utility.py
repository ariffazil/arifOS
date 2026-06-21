"""
UtilityEngine — multi-objective expected utility with F1-F13 constraints.

v0.1 — Linear weighted sum with hard maruah floor.
Future: Pareto frontier, lexicographic ordering, learned weights.
"""

from __future__ import annotations
from .config import MindConfig


# F6 EMPATHY: hard floor on maruah. Below this, utility is -inf.
# This is a CONSTRAINT, not a soft penalty. A plan that violates F6 is
# never chosen, regardless of how high its other scores.
MARUAH_HARD_FLOOR = 0.4


class UtilityEngine:
    """Score an outcome with weighted multi-objective utility.

    The score is a linear combination of 6 dimensions:
      - goal_progress (positive): toward the intent
      - info_gain (positive): reduces uncertainty
      - maruah (positive): preserves dignity
      - reversibility (positive): keeps options open
      - cost (negative): resource consumption
      - risk (negative): probability-weighted downside

    F6 EMPATHY: if maruah < MARUAH_HARD_FLOOR, return -inf. This is a hard
    constraint, not a soft penalty. The plan is rejected regardless of other
    scores.
    """

    NEG_INF = -1e9

    def __init__(self, config: MindConfig):
        self.config = config

    def score(self, outcome: dict[str, float]) -> float:
        # F6: hard maruah floor
        if outcome.get("maruah", 1.0) < MARUAH_HARD_FLOOR:
            return self.NEG_INF

        return (
            self.config.w_goal * outcome.get("goal_progress", 0.0)
            + self.config.w_info * outcome.get("info_gain", 0.0)
            + self.config.w_maruah * outcome.get("maruah", 1.0)
            + self.config.w_reversible * outcome.get("reversibility", 1.0)
            - self.config.w_cost * outcome.get("cost", 0.0)
            - self.config.w_risk * outcome.get("risk", 0.0)
        )

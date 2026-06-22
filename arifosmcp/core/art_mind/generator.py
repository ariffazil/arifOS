"""
CandidateGenerator — produces tool-chain plans for an intent.

v0.1 — Three canonical patterns:
  - observe_more:        safe, low progress (gather more info)
  - reason_then_search:  balanced (structured reasoning + targeted search)
  - forge_now:           high progress, high risk, often irreversible

Future: LLM-driven, goal-conditioned generation. v0.1 is fixed-pattern for
predictability and testability.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ToolAction:
    """One action in a plan.

    Attributes:
        name:         action identifier (e.g., "arif_observe")
        params:       action parameters
        reversible:   can this action be undone? (F1 AMANAH)
        cost:         rough cost proxy [0.0, 1.0+]
        blast_radius: "low" | "medium" | "high" | "unknown"
    """
    name: str
    params: dict = field(default_factory=dict)
    reversible: bool = True
    cost: float = 0.0
    blast_radius: str = "low"


@dataclass
class Plan:
    """A candidate plan: a sequence of ToolActions with expected outcomes.

    The expected_* fields are beliefs about the plan's effects, NOT promises.
    They are used by RolloutEngine to simulate outcomes and by UtilityEngine
    to score them.
    """
    id: str
    actions: list[ToolAction] = field(default_factory=list)
    expected_info_gain: float = 0.0
    expected_risk: float = 0.0
    expected_cost: float = 0.0
    expected_maruah: float = 1.0
    expected_reversibility: float = 1.0
    expected_goal_progress: float = 0.0


class CandidateGenerator:
    """Fixed 3-plan generator. Intent-parameterized.

    The three patterns are chosen to span the safety/progress tradeoff:
    - observe_more:  safest, slowest
    - reason_search: middle
    - forge_now:     fastest, riskiest (often irreversible → 888_HOLD)
    """

    def generate(
        self,
        intent: str,
        prior_uncertainty: float = 0.2,
    ) -> list[Plan]:
        """Return 3 candidate plans for the intent.

        The forge_now plan's risk scales with prior_uncertainty — when the
        world is poorly understood, committing to action is riskier.
        """
        observe = Plan(
            id="observe_more",
            actions=[
                ToolAction(
                    name="arif_observe",
                    params={"depth": "high"},
                    reversible=True,
                    cost=0.1,
                    blast_radius="low",
                ),
            ],
            expected_info_gain=0.9 - 0.3 * prior_uncertainty,
            expected_risk=0.05,
            expected_cost=0.1,
            expected_maruah=1.0,
            expected_reversibility=1.0,
            expected_goal_progress=0.3,
        )

        reason_search = Plan(
            id="reason_then_search",
            actions=[
                ToolAction(
                    name="arif_think",
                    params={"mode": "structured"},
                    reversible=True,
                    cost=0.1,
                    blast_radius="low",
                ),
                ToolAction(
                    name="arif_tool_search",
                    params={"scope": "targeted"},
                    reversible=True,
                    cost=0.2,
                    blast_radius="low",
                ),
            ],
            expected_info_gain=0.7,
            expected_risk=0.15,
            expected_cost=0.3,
            expected_maruah=1.0,
            expected_reversibility=1.0,
            expected_goal_progress=0.65,
        )

        forge = Plan(
            id="forge_now",
            actions=[
                ToolAction(
                    name="arif_forge",
                    params={"intent": intent},
                    reversible=False,  # forge is the canonical irreversible
                    cost=0.5,
                    blast_radius="medium",
                ),
            ],
            expected_info_gain=0.1,
            expected_risk=0.4 + 0.3 * prior_uncertainty,
            expected_cost=0.5,
            expected_maruah=0.7,  # lower because irreversible
            expected_reversibility=0.0,
            expected_goal_progress=0.9,
        )

        return [observe, reason_search, forge]

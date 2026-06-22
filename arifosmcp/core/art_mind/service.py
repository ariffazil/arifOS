"""
MindaService — the orchestrator that ties belief/generator/rollout/utility together.

v0.1 — Advisory only. Never executes. Just proposes.

The flow:
  1. Update belief (Bayesian nudge + provenance)
  2. Generate candidates (3 canonical patterns)
  3. Simulate + score each (horizon-damped, uncertainty-aware)
  4. 888_HOLD check (F1 AMANAH, F13 SOVEREIGN)
  5. Rank by score
  6. Compute confidence band (F2 TRUTH, F7 HUMILITY)
  7. Return ThinkResponse

Doctrine:
  ART may recommend. Judge authorizes. Vault witnesses.
  This service is the advisory layer. It does not execute.
  The arif_judge call is what authorizes any action.
"""

from __future__ import annotations
from typing import Optional

from .belief import BeliefEngine, BeliefState
from .generator import CandidateGenerator
from .rollout import RolloutEngine
from .utility import UtilityEngine
from .config import MindConfig
from .schemas import ThinkRequest, ThinkResponse, ScoredPlan


class MindaService:
    """The minda micro arifOS — pre-forge cognition substrate."""

    NEG_INF = -1e9
    CONFIDENCE_BAND_FLOOR = 0.0
    CONFIDENCE_BAND_CEILING = 1.0

    def __init__(self, config: Optional[MindConfig] = None):
        self.config = config or MindConfig()
        self.belief_engine = BeliefEngine()
        self.generator = CandidateGenerator()
        self.rollout_engine = RolloutEngine()
        self.utility_engine = UtilityEngine(self.config)

    def think(self, req: ThinkRequest) -> ThinkResponse:
        """Run the full cognition loop and return a ranked proposal.

        Advisory only. Never executes. The caller (typically arif_judge
        or an LLM agent loop) decides what to do with the proposal.
        """
        # 1. Belief update
        if req.prior_belief:
            prior = BeliefState(**req.prior_belief)
        else:
            prior = BeliefState()
        posterior = self.belief_engine.update(prior, req.observations)

        # 2. Generate candidates
        plans = self.generator.generate(req.intent, prior.uncertainty)

        # 3. Simulate + score + 888_HOLD check
        scored: list[ScoredPlan] = []
        for plan in plans:
            outcome = self.rollout_engine.simulate(
                posterior.uncertainty, plan, req.horizon
            )
            score = self.utility_engine.score(outcome)

            # F1 AMANAH + F13 SOVEREIGN: 888_HOLD on irreversible
            has_irreversible = any(not a.reversible for a in plan.actions)
            hold_888 = has_irreversible and self.config.irreversible_hold
            hold_reason: Optional[str] = None
            if hold_888:
                hold_reason = (
                    f"F1+F13: irreversible action in plan {plan.id}"
                )

            scored.append(
                ScoredPlan(
                    plan_id=plan.id,
                    score=score,
                    actions=[a.name for a in plan.actions],
                    outcome=outcome,
                    hold_888=hold_888,
                    reason=hold_reason,
                )
            )

        # 4. Rank by score (descending)
        scored.sort(key=lambda p: p.score, reverse=True)
        best = scored[0] if scored else None

        # 5. Empty case
        if not best:
            return ThinkResponse(
                best_plan_id="none",
                best_actions=[],
                score=self.NEG_INF,
                confidence_band=(0.0, 0.0),
                risk_envelope={},
                hold_888=True,
                hold_reason="no plans generated",
                ranked=[],
                posterior_uncertainty=posterior.uncertainty,
                provenance=posterior.provenance,
            )

        # 6. F2 TRUTH: confidence band, not point estimate.
        # F7 HUMILITY: never reach 1.0.
        # The band is the [0, 1] interval of uncertainty around the (possibly
        # unbounded) utility score. When the score is far outside [0, 1], the
        # band collapses to the nearest endpoint — we can't represent confidence
        # in a utility value that's outside the confidence scale.
        score_centered_low = max(self.CONFIDENCE_BAND_FLOOR, min(self.CONFIDENCE_BAND_CEILING, best.score))
        confidence_low = max(
            self.CONFIDENCE_BAND_FLOOR,
            score_centered_low - posterior.uncertainty,
        )
        confidence_high = min(
            self.CONFIDENCE_BAND_CEILING,
            score_centered_low + posterior.uncertainty,
        )

        return ThinkResponse(
            best_plan_id=best.plan_id,
            best_actions=best.actions,
            score=best.score,
            confidence_band=(confidence_low, confidence_high),
            risk_envelope=best.outcome,
            hold_888=best.hold_888,
            hold_reason=best.reason,
            ranked=scored,
            posterior_uncertainty=posterior.uncertainty,
            provenance=posterior.provenance,
        )

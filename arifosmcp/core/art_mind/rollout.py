"""
RolloutEngine — trajectory simulation over a horizon.

v0.1 — Simple horizon-damped simulation. Each plan is "rolled forward" with
uncertainty penalty. Future: full Bayesian Monte Carlo with sampling.
"""

from __future__ import annotations
from .generator import Plan


class RolloutEngine:
    """Simulate a plan's expected outcome over a horizon.

    The simulation is deterministic but uncertainty-aware:
    - Higher prior uncertainty → more risk, less goal progress
    - Longer horizons → diminishing per-step gains (damp)
    - Reversibility is preserved (it's a property of the plan, not the rollout)
    """

    DEFAULT_HORIZON = 3
    UNCERTAINTY_RISK_AMP = 0.3      # risk amplifier per unit uncertainty
    UNCERTAINTY_PROGRESS_AMP = 0.1  # progress penalty per unit uncertainty

    def simulate(
        self,
        prior_uncertainty: float,
        plan: Plan,
        horizon: int = DEFAULT_HORIZON,
    ) -> dict[str, float]:
        """Return outcome dict: {goal_progress, info_gain, risk, cost, maruah, reversibility}.

        Keys map to UtilityEngine.score() inputs.
        """
        damp = 1.0 / max(1, horizon)
        uncertainty_penalty = self.UNCERTAINTY_RISK_AMP * prior_uncertainty

        return {
            "goal_progress": plan.expected_goal_progress * (1.0 - self.UNCERTAINTY_PROGRESS_AMP * prior_uncertainty),
            "info_gain": plan.expected_info_gain * (1.0 - damp),
            "risk": plan.expected_risk + uncertainty_penalty,
            "cost": plan.expected_cost,
            "maruah": plan.expected_maruah,
            "reversibility": plan.expected_reversibility,
        }

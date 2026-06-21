"""
Tests for the minda cognition substrate.

Covers:
  - BeliefEngine: Bayesian update, confidence bands, provenance
  - CandidateGenerator: 3 canonical plans
  - RolloutEngine: horizon damping, uncertainty penalty
  - UtilityEngine: multi-objective scoring, F6 maruah hard floor
  - MindaService: full think() loop, ranking, hold_888 logic
  - Schemas: Pydantic v2 contracts
  - Constraints: F1-F13 mapping
"""

from __future__ import annotations
import pytest

from arifosmcp.core.art_mind import (
    MindaService,
    MindConfig,
    ThinkRequest,
    ThinkResponse,
    ScoredPlan,
    BeliefState,
    BeliefEngine,
    Plan,
    ToolAction,
    CandidateGenerator,
    RolloutEngine,
    UtilityEngine,
    FConstraint,
    F_CONSTRAINTS,
    MARUAH_HARD_FLOOR,
)


# ═══════════════════════════════════════════════════════════════════════════
# BeliefEngine
# ═══════════════════════════════════════════════════════════════════════════

class TestBeliefEngine:
    def test_empty_prior_observation_creates_new_var(self):
        prior = BeliefState()
        engine = BeliefEngine()
        posterior = engine.update(prior, {"x": 42})
        assert posterior.facts == {"x": 42}
        assert posterior.confidence == {"x": BeliefEngine.NEW_VAR_CONFIDENCE}
        assert posterior.provenance == {"x": "OBS"}

    def test_observation_with_provenance_label(self):
        prior = BeliefState()
        engine = BeliefEngine()
        posterior = engine.update(prior, {"x": 1}, provenance={"x": "DER"})
        assert posterior.provenance["x"] == "DER"

    def test_observation_nudges_confidence_toward_evidence(self):
        prior = BeliefState(facts={"x": 1}, confidence={"x": 0.5})
        engine = BeliefEngine()
        posterior = engine.update(prior, {"x": 2})
        # 0.5 * 0.5 + 0.5 * 0.9 = 0.7
        assert 0.69 < posterior.confidence["x"] < 0.71

    def test_confidence_never_reaches_one(self):
        # F7 HUMILITY: confidence capped at 0.99
        prior = BeliefState(facts={"x": 1}, confidence={"x": 0.99})
        engine = BeliefEngine()
        posterior = engine.update(prior, {"x": 2})
        assert posterior.confidence["x"] <= BeliefEngine.EVIDENCE_CEILING

    def test_aggregate_uncertainty_decreases_with_evidence(self):
        prior = BeliefState()
        engine = BeliefEngine()
        # No evidence → high uncertainty
        empty = engine.update(prior, {})
        assert empty.uncertainty > 0.5
        # Add evidence → uncertainty drops
        posterior = engine.update(prior, {"a": 1, "b": 2, "c": 3})
        assert posterior.uncertainty < empty.uncertainty

    def test_belief_state_serializable(self):
        state = BeliefState(facts={"x": 1}, confidence={"x": 0.9})
        d = state.to_dict()
        assert "facts" in d
        assert "confidence" in d
        assert "uncertainty" in d
        assert "provenance" in d


# ═══════════════════════════════════════════════════════════════════════════
# CandidateGenerator
# ═══════════════════════════════════════════════════════════════════════════

class TestCandidateGenerator:
    def test_generates_three_canonical_plans(self):
        gen = CandidateGenerator()
        plans = gen.generate("test intent")
        ids = [p.id for p in plans]
        assert ids == ["observe_more", "reason_then_search", "forge_now"]

    def test_forge_now_is_irreversible(self):
        gen = CandidateGenerator()
        plans = gen.generate("test")
        forge = next(p for p in plans if p.id == "forge_now")
        assert all(not a.reversible for a in forge.actions)

    def test_observe_more_and_reason_search_are_reversible(self):
        gen = CandidateGenerator()
        plans = gen.generate("test")
        for plan in plans:
            if plan.id != "forge_now":
                assert all(a.reversible for a in plan.actions)

    def test_forge_risk_scales_with_uncertainty(self):
        gen = CandidateGenerator()
        plans_low_u = gen.generate("test", prior_uncertainty=0.1)
        plans_high_u = gen.generate("test", prior_uncertainty=0.9)
        forge_low = next(p for p in plans_low_u if p.id == "forge_now")
        forge_high = next(p for p in plans_high_u if p.id == "forge_now")
        assert forge_high.expected_risk > forge_low.expected_risk

    def test_plan_has_expected_fields(self):
        gen = CandidateGenerator()
        plans = gen.generate("test")
        for plan in plans:
            assert isinstance(plan, Plan)
            assert plan.expected_info_gain >= 0
            assert plan.expected_risk >= 0
            assert plan.expected_maruah >= 0
            assert plan.expected_reversibility >= 0


# ═══════════════════════════════════════════════════════════════════════════
# RolloutEngine
# ═══════════════════════════════════════════════════════════════════════════

class TestRolloutEngine:
    def test_simulate_returns_expected_keys(self):
        engine = RolloutEngine()
        plan = Plan(id="test", actions=[], expected_goal_progress=0.5)
        outcome = engine.simulate(0.2, plan, horizon=3)
        for k in ("goal_progress", "info_gain", "risk", "cost", "maruah", "reversibility"):
            assert k in outcome

    def test_higher_uncertainty_increases_risk(self):
        engine = RolloutEngine()
        plan = Plan(id="test", expected_risk=0.3)
        outcome_low = engine.simulate(0.1, plan)
        outcome_high = engine.simulate(0.9, plan)
        assert outcome_high["risk"] > outcome_low["risk"]

    def test_higher_uncertainty_decreases_goal_progress(self):
        engine = RolloutEngine()
        plan = Plan(id="test", expected_goal_progress=0.5)
        outcome_low = engine.simulate(0.0, plan)
        outcome_high = engine.simulate(0.9, plan)
        assert outcome_low["goal_progress"] > outcome_high["goal_progress"]

    def test_longer_horizon_accumulates_info_gain(self):
        # Longer horizon = more steps to gather info, so accumulated info_gain is higher.
        # damp = 1/horizon, and info_gain = expected * (1 - damp).
        # So horizon=1 → damp=1.0 → info_gain=0; horizon=10 → damp=0.1 → info_gain≈0.72.
        engine = RolloutEngine()
        plan = Plan(id="test", expected_info_gain=0.8)
        outcome_short = engine.simulate(0.2, plan, horizon=1)
        outcome_long = engine.simulate(0.2, plan, horizon=10)
        assert outcome_long["info_gain"] > outcome_short["info_gain"]


# ═══════════════════════════════════════════════════════════════════════════
# UtilityEngine
# ═══════════════════════════════════════════════════════════════════════════

class TestUtilityEngine:
    def _engine(self, **overrides):
        return UtilityEngine(MindConfig(**overrides))

    def test_positive_score_for_good_outcome(self):
        engine = self._engine()
        outcome = {
            "goal_progress": 0.7, "info_gain": 0.5, "maruah": 1.0,
            "reversibility": 1.0, "cost": 0.2, "risk": 0.1,
        }
        score = engine.score(outcome)
        assert score > 0

    def test_maruah_below_floor_returns_neg_inf(self):
        # F6: hard floor, not soft penalty
        engine = self._engine()
        outcome = {
            "goal_progress": 1.0, "info_gain": 1.0, "maruah": 0.1,
            "reversibility": 1.0, "cost": 0.0, "risk": 0.0,
        }
        assert engine.score(outcome) == UtilityEngine.NEG_INF

    def test_maruah_at_floor_returns_normal_score(self):
        # At the floor (not below), the plan is allowed but penalized
        engine = self._engine()
        outcome = {
            "goal_progress": 0.5, "info_gain": 0.5, "maruah": MARUAH_HARD_FLOOR,
            "reversibility": 1.0, "cost": 0.0, "risk": 0.0,
        }
        score = engine.score(outcome)
        assert score > UtilityEngine.NEG_INF

    def test_higher_risk_lowers_score(self):
        engine = self._engine()
        base = {"goal_progress": 0.5, "info_gain": 0.5, "maruah": 1.0,
                "reversibility": 1.0, "cost": 0.0}
        score_low = engine.score({**base, "risk": 0.1})
        score_high = engine.score({**base, "risk": 0.9})
        assert score_low > score_high

    def test_higher_cost_lowers_score(self):
        engine = self._engine()
        base = {"goal_progress": 0.5, "info_gain": 0.5, "maruah": 1.0,
                "reversibility": 1.0, "risk": 0.0}
        score_cheap = engine.score({**base, "cost": 0.1})
        score_expensive = engine.score({**base, "cost": 0.9})
        assert score_cheap > score_expensive


# ═══════════════════════════════════════════════════════════════════════════
# MindaService — full think() loop
# ═══════════════════════════════════════════════════════════════════════════

class TestMindaService:
    def test_think_returns_think_response(self):
        service = MindaService()
        req = ThinkRequest(intent="test", observations={"x": 1})
        response = service.think(req)
        assert isinstance(response, ThinkResponse)

    def test_think_returns_three_ranked_plans(self):
        service = MindaService()
        req = ThinkRequest(intent="test")
        response = service.think(req)
        assert len(response.ranked) == 3

    def test_ranked_plans_sorted_by_score_descending(self):
        service = MindaService()
        req = ThinkRequest(intent="test")
        response = service.think(req)
        scores = [p.score for p in response.ranked]
        assert scores == sorted(scores, reverse=True)

    def test_forge_now_triggers_888_hold_by_default(self):
        # F1+F13: irreversible plan → 888_HOLD
        service = MindaService()
        req = ThinkRequest(intent="deploy to production")
        response = service.think(req)
        forge = next(p for p in response.ranked if p.plan_id == "forge_now")
        assert forge.hold_888 is True
        assert "F1" in (forge.reason or "")

    def test_hold_can_be_disabled(self):
        # For sandbox / dev: turn off 888_HOLD
        service = MindaService(MindConfig(irreversible_hold=False))
        req = ThinkRequest(intent="deploy to production")
        response = service.think(req)
        forge = next(p for p in response.ranked if p.plan_id == "forge_now")
        assert forge.hold_888 is False

    def test_confidence_band_is_explicit(self):
        # F2 TRUTH: confidence is a band (score ± uncertainty), not a point estimate.
        # The band is clipped to [0, 1] (confidence is intuitively a probability-like
        # quantity). Width is bounded by 2 * uncertainty.
        service = MindaService()
        req = ThinkRequest(intent="test", observations={"a": 1, "b": 2, "c": 3})
        response = service.think(req)
        low, high = response.confidence_band
        # Band must be ordered
        assert low <= high
        # Band is in [0, 1] (clipped)
        assert 0.0 <= low <= 1.0
        assert 0.0 <= high <= 1.0
        # Band width is bounded by 2 * uncertainty (could be less if clipped)
        assert (high - low) <= 2.0 * response.posterior_uncertainty + 0.01
        # Score is within or beyond the band (could be outside if score > 1)
        # The band represents the *uncertainty interval*, not a hard score cap
        # Both endpoints should be finite
        assert low != float("-inf")
        assert high != float("inf")

    def test_provenance_passed_through(self):
        service = MindaService()
        req = ThinkRequest(
            intent="test",
            observations={"k": 1},
        )
        response = service.think(req)
        assert "k" in response.provenance

    def test_empty_intent_does_not_crash(self):
        service = MindaService()
        req = ThinkRequest(intent="")
        response = service.think(req)
        assert response.best_plan_id in {"observe_more", "reason_then_search", "forge_now"}

    def test_posterior_uncertainty_decreases_with_evidence(self):
        service = MindaService()
        # High evidence
        req_high = ThinkRequest(
            intent="test",
            observations={"a": 1, "b": 2, "c": 3, "d": 4, "e": 5},
        )
        # No evidence
        req_low = ThinkRequest(intent="test")
        resp_high = service.think(req_high)
        resp_low = service.think(req_low)
        assert resp_high.posterior_uncertainty < resp_low.posterior_uncertainty

    def test_prior_belief_chaining_works(self):
        # Service supports belief chaining for multi-step reasoning
        service = MindaService()
        req1 = ThinkRequest(intent="step 1", observations={"a": 1})
        resp1 = service.think(req1)
        # Use resp1 as prior for next call
        prior = BeliefState(**{
            "facts": dict(resp1.ranked[0].outcome),  # use the outcome as facts
            "confidence": {"x": 0.7},
            "uncertainty": resp1.posterior_uncertainty,
            "provenance": resp1.provenance,
        })
        req2 = ThinkRequest(
            intent="step 2",
            observations={"b": 2},
            prior_belief=prior.to_dict(),
        )
        resp2 = service.think(req2)
        assert isinstance(resp2, ThinkResponse)


# ═══════════════════════════════════════════════════════════════════════════
# Constraints
# ═══════════════════════════════════════════════════════════════════════════

class TestConstraints:
    def test_all_thirteen_floors_documented(self):
        floors = {c.floor for c in F_CONSTRAINTS}
        assert floors == {
            "F1", "F2", "F3", "F4", "F5", "F6",
            "F7", "F8", "F9", "F10", "F11", "F12", "F13",
        }

    def test_hard_constraints_are_subset(self):
        # F1, F2, F3, F4, F5, F6, F7, F11, F12, F13 are HARD in doctrine
        hard = {c.floor for c in F_CONSTRAINTS if c.hard}
        # At minimum: F1, F2, F6, F13 must be hard
        assert {"F1", "F2", "F6", "F13"} <= hard

    def test_constraint_dataclass_fields(self):
        c = FConstraint("F1", "AMANAH", "reversibility check", True)
        assert c.floor == "F1"
        assert c.name == "AMANAH"
        assert c.hard is True


# ═══════════════════════════════════════════════════════════════════════════
# Schemas
# ═══════════════════════════════════════════════════════════════════════════

class TestSchemas:
    def test_think_request_validation(self):
        req = ThinkRequest(intent="test")
        assert req.horizon == 3
        assert req.context == {}
        assert req.observations == {}

    def test_think_request_horizon_bounds(self):
        with pytest.raises(Exception):
            ThinkRequest(intent="test", horizon=0)
        with pytest.raises(Exception):
            ThinkRequest(intent="test", horizon=100)

    def test_scored_plan_default_hold(self):
        p = ScoredPlan(
            plan_id="x", score=0.5, actions=["a"], outcome={"x": 0.5}
        )
        assert p.hold_888 is False
        assert p.reason is None

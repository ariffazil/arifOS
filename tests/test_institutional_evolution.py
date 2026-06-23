"""Tests for core/physics/institutional_evolution.py — invariant #15 DRAFT."""

from __future__ import annotations

import pytest

from core.physics.institutional_evolution import (
    SuccessionError,
    check_ai_adaptation_rate,
    check_human_attention_budget,
    check_institutional_evolution,
    check_institutional_succession,
    check_population_absorption,
)


class TestHumanAttentionBudget:
    def test_within_budget_passes(self):
        result = check_human_attention_budget(3600.0, 50)
        assert result["passed"] is True
        assert result["session_ok"] is True
        assert result["interventions_ok"] is True
        assert result["attention_score"] > 0.5

    def test_long_session_fails(self):
        result = check_human_attention_budget(20_000.0, 10)
        assert result["passed"] is False
        assert result["session_ok"] is False

    def test_too_many_interventions_fails(self):
        result = check_human_attention_budget(1000.0, 300)
        assert result["passed"] is False
        assert result["interventions_ok"] is False

    def test_raise_on_breach(self):
        with pytest.raises(SuccessionError):
            check_human_attention_budget(20_000.0, 10, raise_on_breach=True)


class TestInstitutionalSuccession:
    def test_clean_succession_passes(self):
        changes = [
            {
                "role": "vault_admin",
                "action": "transferred",
                "successor": "admin_b",
                "handoff_doc": "doc-1",
            }
        ]
        result = check_institutional_succession(changes, [])
        assert result["passed"] is True
        assert result["succession_score"] == 1.0

    def test_orphan_role_fails(self):
        changes = [{"role": "vault_admin", "action": "revoked"}]
        result = check_institutional_succession(changes, [])
        assert result["passed"] is False
        assert result["orphan_changes_count"] == 1

    def test_unacknowledged_obligations_fails(self):
        result = check_institutional_succession([], ["audit trail retention"])
        assert result["passed"] is False

    def test_raise_on_breach(self):
        with pytest.raises(SuccessionError):
            check_institutional_succession([], ["audit trail retention"], raise_on_breach=True)


class TestAIAdaptationRate:
    def test_reviewed_adaptation_passes(self):
        result = check_ai_adaptation_rate(100, 95)
        assert result["passed"] is True
        assert result["unreviewed_ratio"] <= 0.1

    def test_unreviewed_adaptation_fails(self):
        result = check_ai_adaptation_rate(100, 80)
        assert result["passed"] is False
        assert result["unreviewed_ratio"] == 0.2

    def test_zero_changes_passes(self):
        result = check_ai_adaptation_rate(0, 0)
        assert result["passed"] is True
        assert result["unreviewed_ratio"] == 0.0

    def test_raise_on_breach(self):
        with pytest.raises(SuccessionError):
            check_ai_adaptation_rate(100, 80, raise_on_breach=True)


class TestPopulationAbsorption:
    def test_sufficient_consent_passes(self):
        result = check_population_absorption(["community_a", "community_b"], 0.8)
        assert result["passed"] is True
        assert result["absorption_score"] > 1.0 or result["absorption_score"] == 1.0

    def test_insufficient_consent_fails(self):
        result = check_population_absorption(["community_a", "community_b"], 0.5)
        assert result["passed"] is False

    def test_raise_on_breach(self):
        with pytest.raises(SuccessionError):
            check_population_absorption(["community_a"], 0.5, raise_on_breach=True)


class TestUnifiedRunner:
    def test_all_pass(self):
        result = check_institutional_evolution(
            session_duration_s=3600.0,
            operator_interventions=50,
            role_changes=[
                {
                    "role": "vault_admin",
                    "action": "transferred",
                    "successor": "admin_b",
                    "handoff_doc": "doc-1",
                }
            ],
            changes_last_30d=100,
            human_reviews_last_30d=95,
            affected_communities=["community_a"],
            consent_coverage=0.8,
        )
        assert result["invariant"] == "I15_DRAFT"
        assert result["passed"] is True
        assert len(result["constraints"]) == 4

    def test_any_fail(self):
        result = check_institutional_evolution(
            session_duration_s=20_000.0,
            operator_interventions=50,
        )
        assert result["passed"] is False

    def test_raise_runs_first_breach(self):
        with pytest.raises(SuccessionError):
            check_institutional_evolution(
                session_duration_s=20_000.0,
                operator_interventions=50,
                raise_on_breach=True,
            )


# ═══════════════════════════════════════════════════════
# InstitutionalEvolutionGuard class-based tests
# ═══════════════════════════════════════════════════════


class TestGuardAttentionBudget:
    """Tests for InstitutionalEvolutionGuard.check_human_attention_budget"""

    def test_normal_session_passes(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        result = InstitutionalEvolutionGuard.check_human_attention_budget(3600.0, 50)
        assert result["passed"] is True
        assert result["verdict"] == "PASS"

    def test_fatigue_warning_sabar(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        result = InstitutionalEvolutionGuard.check_human_attention_budget(13000.0, 180)
        assert result["passed"] is True
        assert result["verdict"] == "SABAR"

    def test_session_exceeds_max_raises(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            AttentionBudgetExceededError,
        )

        with pytest.raises(AttentionBudgetExceededError):
            InstitutionalEvolutionGuard.check_human_attention_budget(20000.0, 10)

    def test_interventions_exceed_max_raises(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            AttentionBudgetExceededError,
        )

        with pytest.raises(AttentionBudgetExceededError):
            InstitutionalEvolutionGuard.check_human_attention_budget(1000.0, 300)

    def test_negative_values_raise_void(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            InstitutionalEvolutionError,
        )

        with pytest.raises(InstitutionalEvolutionError) as exc_info:
            InstitutionalEvolutionGuard.check_human_attention_budget(-1.0, -5)
        assert exc_info.value.verdict == "VOID"


class TestGuardPopulationAbsorption:
    """Tests for InstitutionalEvolutionGuard.check_population_absorption"""

    def test_adequate_consent_passes(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        result = InstitutionalEvolutionGuard.check_population_absorption(
            ["community_a", "community_b"], 0.8
        )
        assert result["passed"] is True
        assert result["verdict"] == "PASS"

    def test_insufficient_consent_raises(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            PopulationAbsorptionError,
        )

        with pytest.raises(PopulationAbsorptionError):
            InstitutionalEvolutionGuard.check_population_absorption(["community_a"], 0.4)

    def test_empty_communities_allowed(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        result = InstitutionalEvolutionGuard.check_population_absorption([], 0.5)
        assert result["passed"] is True

    def test_invalid_consent_raises_void(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            InstitutionalEvolutionError,
        )

        with pytest.raises(InstitutionalEvolutionError) as exc_info:
            InstitutionalEvolutionGuard.check_population_absorption(["c"], -0.1)
        assert exc_info.value.verdict == "VOID"


class TestGuardSuccession:
    """Tests for InstitutionalEvolutionGuard.check_institutional_succession"""

    def test_valid_succession_passes(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        changes = [
            {
                "role": "vault_admin",
                "action": "transferred",
                "successor": "admin_b",
                "handoff_doc": "doc-1",
            }
        ]
        result = InstitutionalEvolutionGuard.check_institutional_succession(changes, [])
        assert result["passed"] is True
        assert result["verdict"] == "PASS"

    def test_orphan_role_raises(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            SuccessionContinuityError,
        )

        with pytest.raises(SuccessionContinuityError):
            InstitutionalEvolutionGuard.check_institutional_succession(
                [{"role": "vault_admin", "action": "revoked"}], []
            )

    def test_unacknowledged_obligations_raises(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            SuccessionContinuityError,
        )

        with pytest.raises(SuccessionContinuityError):
            InstitutionalEvolutionGuard.check_institutional_succession(
                [], ["unresolved audit obligation"]
            )


class TestGuardAIAdaptation:
    """Tests for InstitutionalEvolutionGuard.check_ai_adaptation_rate"""

    def test_reviewed_changes_pass(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        result = InstitutionalEvolutionGuard.check_ai_adaptation_rate(100, 95)
        assert result["passed"] is True
        assert result["verdict"] == "PASS"

    def test_unreviewed_changes_raises(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            AIAdaptationRateExceededError,
        )

        with pytest.raises(AIAdaptationRateExceededError):
            InstitutionalEvolutionGuard.check_ai_adaptation_rate(100, 50)

    def test_negative_values_raises_void(self):
        from core.physics.institutional_evolution import (
            InstitutionalEvolutionGuard,
            InstitutionalEvolutionError,
        )

        with pytest.raises(InstitutionalEvolutionError) as exc_info:
            InstitutionalEvolutionGuard.check_ai_adaptation_rate(-1, 0)
        assert exc_info.value.verdict == "VOID"


class TestGuardEvaluateAll:
    """Tests for InstitutionalEvolutionGuard.evaluate_evolution_invariants"""

    def test_all_pass_returns_pass(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        payload = {
            "session_duration_s": 3600,
            "operator_interventions": 50,
            "affected_communities": ["comm_a"],
            "consent_coverage": 0.8,
            "role_changes": [
                {"role": "admin", "action": "transfer", "successor": "b", "handoff_doc": "d1"}
            ],
            "unacknowledged_obligations": [],
            "changes_last_30d": 100,
            "human_reviews_last_30d": 95,
        }
        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
        assert result["passed"] is True
        assert result["verdict"] == "PASS"
        assert len(result["results"]) == 4

    def test_attention_breach_yields_hold(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        payload = {
            "session_duration_s": 20000,
            "operator_interventions": 50,
        }
        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
        assert result["passed"] is False
        assert result["verdict"] == "HOLD_888"

    def test_absorption_breach_yields_sabar(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        payload = {
            "affected_communities": ["comm_a", "comm_b"],
            "consent_coverage": 0.3,
        }
        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
        assert result["passed"] is False
        assert result["verdict"] == "SABAR"

    def test_succession_breach_yields_hold(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        payload = {
            "role_changes": [{"role": "admin", "action": "revoked"}],
        }
        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
        assert result["passed"] is False
        assert result["verdict"] == "HOLD_888"

    def test_void_input_yields_void(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        payload = {
            "session_duration_s": -1,
            "operator_interventions": -5,
        }
        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
        assert result["passed"] is False
        assert result["verdict"] == "VOID"

    def test_doctrine_string_present(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        payload = {}
        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants(payload)
        assert "final_doctrine_canonical" in result
        assert "mortal humans" in result["final_doctrine_canonical"]
        assert "understand, inherit, contest, and recall" in result["final_doctrine_canonical"]

    def test_empty_payload_passes(self):
        from core.physics.institutional_evolution import InstitutionalEvolutionGuard

        result = InstitutionalEvolutionGuard.evaluate_evolution_invariants({})
        assert result["passed"] is True
        assert result["verdict"] == "PASS"

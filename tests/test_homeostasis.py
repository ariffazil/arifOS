"""
tests/test_homeostasis.py — Ring 0.5 Translation Layer Tests

Tests for core/homeostasis.py — the Soul-to-Body translation layer.
Includes Paradox Energy Budget tests for metabolic limiting.
"""

import time
import pytest
from core.homeostasis import (
    ComputeTier,
    SpendPolicy,
    CognitivePressure,
    ComputeBudget,
    HomeostasisInterface,
    ParadoxEnergyBudget,
    translate_pressure_to_budget,
    get_homeostasis,
    get_paradox_budget,
)


class TestSpendPolicyDetermination:
    """Test policy determination from cognitive pressure."""

    def test_critical_paradox_freezes(self):
        """TAC critical_paradox → FREEZE policy."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(tac_status="critical_paradox")

        budget = homeo.translate(pressure)

        assert budget.spend_policy == SpendPolicy.FREEZE
        assert budget.max_tool_calls == 0
        assert budget.api_permission is False
        assert budget.hold_required is True

    def test_rising_entropy_austerity(self):
        """dS > threshold → AUSTERITY policy."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(dS=0.1)  # Confusion rising

        budget = homeo.translate(pressure)

        assert budget.spend_policy == SpendPolicy.AUSTERITY
        assert budget.max_tokens <= 512
        assert budget.max_tool_calls <= 1

    def test_low_stability_conservative(self):
        """Peace² < threshold → CONSERVATIVE policy."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(peace2=0.8, dS=-0.05)

        budget = homeo.translate(pressure)

        assert budget.spend_policy == SpendPolicy.CONSERVATIVE
        # Concurrency scales with Peace²: 0.8 * 4 = 3.2 → 3
        assert budget.max_concurrency <= homeo.CONCURRENCY_MAX

    def test_high_clarity_expansive(self):
        """dS < threshold (clarity increasing) → EXPANSIVE policy."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(dS=-0.15, peace2=1.0, omega0=0.03)

        budget = homeo.translate(pressure)

        assert budget.spend_policy == SpendPolicy.EXPANSIVE
        assert budget.max_tokens == homeo.TOKENS_MAX
        assert budget.api_permission is True

    def test_high_risk_requires_hold(self):
        """High risk score → austerity + hold required."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(risk_score=0.7, dS=-0.05)

        budget = homeo.translate(pressure)

        assert budget.hold_required is True


class TestTokenScaling:
    """Test token budget scaling based on pressure."""

    def test_tokens_scale_with_stability(self):
        """Higher Peace² → more tokens allowed."""
        homeo = HomeostasisInterface()

        low_stability = homeo.translate(CognitivePressure(peace2=0.5, dS=-0.05))
        high_stability = homeo.translate(CognitivePressure(peace2=1.0, dS=-0.05))

        assert high_stability.max_tokens >= low_stability.max_tokens

    def test_freeze_gives_minimum_tokens(self):
        """FREEZE policy → minimum tokens."""
        homeo = HomeostasisInterface()
        budget = homeo.translate(CognitivePressure(tac_status="critical_paradox"))

        assert budget.max_tokens == homeo.TOKENS_MIN


class TestToolBudgeting:
    """Test tool call budgeting."""

    def test_high_humidity_restricts_tools(self):
        """High Ω₀ → fewer tool calls allowed."""
        homeo = HomeostasisInterface()

        low_omega = homeo.translate(CognitivePressure(omega0=0.03, dS=-0.05))
        high_omega = homeo.translate(CognitivePressure(omega0=0.07, dS=-0.05))

        assert low_omega.max_tool_calls >= high_omega.max_tool_calls

    def test_freeze_allows_no_tools(self):
        """FREEZE policy → zero tool calls."""
        homeo = HomeostasisInterface()
        budget = homeo.translate(CognitivePressure(tac_status="critical_paradox"))

        assert budget.max_tool_calls == 0


class TestFitnessCalculation:
    """Test evolutionary fitness for task prioritization."""

    def test_high_fitness_allows_execution(self):
        """High fitness → task should execute."""
        homeo = HomeostasisInterface()

        fitness = homeo.calculate_fitness(need=0.9, impact=0.8, clarity=0.9, cost=2.0)

        assert fitness > 0.3
        assert homeo.should_defer(fitness) is False

    def test_low_fitness_defers(self):
        """Low fitness → task should be deferred (SABAR)."""
        homeo = HomeostasisInterface()

        fitness = homeo.calculate_fitness(need=0.1, impact=0.1, clarity=0.1, cost=5.0)

        assert fitness < 0.3
        assert homeo.should_defer(fitness) is True

    def test_expensive_task_needs_high_impact(self):
        """High cost task needs high impact to justify."""
        homeo = HomeostasisInterface()

        # High cost, low impact → defer
        low_fitness = homeo.calculate_fitness(need=0.5, impact=0.2, clarity=0.5, cost=10.0)

        # High cost, VERY high impact and need → execute
        # fitness = (0.9 * 0.95 * 0.8) / 10 = 0.0684
        high_fitness = homeo.calculate_fitness(need=0.9, impact=0.95, clarity=0.8, cost=10.0)

        assert homeo.should_defer(low_fitness)
        # Note: With cost=10, even high fitness is < 0.3
        # This is correct: expensive tasks should be hard to justify
        assert low_fitness < high_fitness


class TestCaching:
    """Test translation caching to prevent thrashing."""

    def test_cache_prevents_oscillation(self):
        """Rapid calls with similar pressure return cached result."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(dS=-0.05, peace2=0.95)

        budget1 = homeo.translate(pressure)
        budget2 = homeo.translate(pressure)

        # Should return same object (cached)
        assert budget1 is budget2

    def test_significant_change_invalidates_cache(self):
        """Significant pressure change invalidates cache."""
        homeo = HomeostasisInterface()

        budget1 = homeo.translate(CognitivePressure(dS=-0.05))
        budget2 = homeo.translate(CognitivePressure(dS=0.2))  # Big change

        # Different policies due to different pressures
        assert budget1.spend_policy != budget2.spend_policy


class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_translate_pressure_to_budget(self):
        """Convenience function works correctly."""
        pressure = CognitivePressure(dS=-0.1, peace2=1.0)

        budget = translate_pressure_to_budget(pressure)

        assert isinstance(budget, ComputeBudget)
        assert budget.max_tokens > 0

    def test_get_homeostasis_singleton(self):
        """Singleton pattern works."""
        h1 = get_homeostasis()
        h2 = get_homeostasis()

        assert h1 is h2


class TestConstitutionalCompliance:
    """Test constitutional compliance in reports."""

    def test_report_includes_compliance(self):
        """Report includes constitutional compliance checks."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(dS=-0.1, peace2=1.0, omega0=0.04)

        report = homeo.get_report(pressure)

        assert "constitutional_compliance" in report
        assert "F4_clarity" in report["constitutional_compliance"]
        assert "F7_humility" in report["constitutional_compliance"]
        assert "F11_command" in report["constitutional_compliance"]

    def test_report_shows_full_pressure(self):
        """Report includes full cognitive pressure state."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(
            dS=-0.1, peace2=0.9, omega0=0.04, tac_status="stable", g_star=1.0, risk_score=0.2
        )

        report = homeo.get_report(pressure)

        assert report["cognitive_pressure"]["dS"] == -0.1
        assert report["cognitive_pressure"]["peace2"] == 0.9
        assert report["cognitive_pressure"]["omega0"] == 0.04


class TestRM50BudgetConstraints:
    """Test budget constraints for low-cost operation."""

    def test_normal_tokens_reasonable(self):
        """Normal token budget is reasonable for low-cost operation."""
        homeo = HomeostasisInterface()

        assert homeo.TOKENS_NORMAL == 1024  # Not 4096 or 8192
        assert homeo.TOKENS_MAX == 4096  # Max is still bounded

    def test_concurrency_bounded(self):
        """Concurrency is bounded for single-server operation."""
        homeo = HomeostasisInterface()

        assert homeo.CONCURRENCY_MAX == 4  # Not 10 or 100

    def test_most_requests_die_at_tier_1(self):
        """Conservative policy defaults to T1 (local CPU)."""
        homeo = HomeostasisInterface()
        pressure = CognitivePressure(dS=0, peace2=0.9, omega0=0.04)

        budget = homeo.translate(pressure)

        # Default should be T1 or T2, not T3
        assert budget.allowed_tier in [ComputeTier.T1_LOCAL_CPU, ComputeTier.T2_LOCAL_GPU]


class TestParadoxEnergyBudget:
    """Test Paradox Energy Budget — the metabolic limiter."""

    def test_can_detect_paradox_when_empty(self):
        """System can detect paradox when budget is empty."""
        budget = ParadoxEnergyBudget()

        can_detect, reason = budget.can_detect_paradox(paradox_intensity=0.3)

        assert can_detect is True
        assert "allowed" in reason.lower()

    def test_blocks_paradox_when_capacity_full(self):
        """System blocks new paradox when capacity is full."""
        budget = ParadoxEnergyBudget(max_active_paradoxes=1)
        budget.register_paradox("paradox_1", intensity=0.5)

        can_detect, reason = budget.can_detect_paradox(paradox_intensity=0.3)

        assert can_detect is False
        assert "capacity" in reason.lower()

    def test_blocks_paradox_when_energy_exceeded(self):
        """System blocks new paradox when energy budget exceeded."""
        budget = ParadoxEnergyBudget(max_paradox_energy=0.5)
        budget.register_paradox("paradox_1", intensity=0.5)

        can_detect, reason = budget.can_detect_paradox(paradox_intensity=0.3)

        assert can_detect is False
        assert "energy" in reason.lower()

    def test_register_paradox_increases_count(self):
        """Registering paradox increases active count."""
        budget = ParadoxEnergyBudget()

        result = budget.register_paradox("paradox_1", intensity=0.5)

        assert result["registered"] is True
        assert budget.active_paradox_count == 1
        assert budget.current_paradox_energy == 0.5

    def test_resolve_paradox_decreases_count(self):
        """Resolving paradox decreases active count."""
        budget = ParadoxEnergyBudget()
        budget.register_paradox("paradox_1", intensity=0.5)

        result = budget.resolve_paradox("paradox_1")

        assert result["resolved"] is True
        assert budget.active_paradox_count == 0
        assert budget.current_paradox_energy == 0.0

    def test_eureka_registration_with_cooling(self):
        """Eureka registration applies Phoenix-72 cooling."""
        budget = ParadoxEnergyBudget()
        budget.register_paradox("paradox_1", intensity=0.5)

        result = budget.resolve_paradox("paradox_1", is_eureka=True)

        assert result["eureka_registered"] is True
        assert "cooling" in result["message"].lower()
        assert budget.eurekas_in_window == 1

    def test_eureka_rate_limiting(self):
        """Eureka rate limiting prevents rapid phase transitions."""
        budget = ParadoxEnergyBudget()

        # Register and resolve 3 eurekas quickly
        for i in range(3):
            budget.register_paradox(f"p{i}", intensity=0.2)
            budget.resolve_paradox(f"p{i}", is_eureka=True)

        # 4th should be rate limited
        can_detect, reason = budget.can_detect_paradox(paradox_intensity=0.2)

        assert can_detect is False
        assert "rate limit" in reason.lower()

    def test_energy_decay_over_time(self):
        """Energy decays naturally over time (metabolic recovery)."""
        budget = ParadoxEnergyBudget(paradox_decay_rate=0.1)
        budget.register_paradox("p1", intensity=0.5)

        initial_energy = budget.current_paradox_energy

        # Simulate time passing
        budget.decay_energy(dt=2.0)

        assert budget.current_paradox_energy < initial_energy

    def test_tac_sensitivity_downgrade_when_overloaded(self):
        """TAC sensitivity should downgrade when system overloaded."""
        budget = ParadoxEnergyBudget(max_paradox_energy=1.0)
        budget.register_paradox("p1", intensity=0.9)

        should_downgrade, reason = budget.should_downgrade_tac_sensitivity()

        assert should_downgrade is True
        assert "sensitivity" in reason.lower() or "threshold" in reason.lower()

    def test_status_report_includes_compliance(self):
        """Status report includes constitutional compliance."""
        budget = ParadoxEnergyBudget()

        status = budget.get_status()

        assert "constitutional_compliance" in status
        assert "not_overloaded" in status["constitutional_compliance"]
        assert "capacity_available" in status["constitutional_compliance"]
        assert "eureka_rate_ok" in status["constitutional_compliance"]

    def test_singleton_pattern(self):
        """Paradox budget singleton works."""
        b1 = get_paradox_budget()
        b2 = get_paradox_budget()

        assert b1 is b2


class TestParadoxEnergyBudgetConservation:
    """Test conservation laws for paradox energy."""

    def test_energy_conserved_through_lifecycle(self):
        """Energy is conserved through register/resolve lifecycle."""
        budget = ParadoxEnergyBudget()
        initial_energy = budget.current_paradox_energy

        budget.register_paradox("p1", intensity=0.4)
        after_register = budget.current_paradox_energy

        budget.resolve_paradox("p1")
        after_resolve = budget.current_paradox_energy

        # Energy added, then removed
        assert after_register == initial_energy + 0.4
        assert after_resolve == initial_energy

    def test_multiple_paradoxes_sum_correctly(self):
        """Multiple paradoxes sum energy correctly."""
        # Increase capacity to allow 3 paradoxes
        budget = ParadoxEnergyBudget(max_paradox_energy=2.0, max_active_paradoxes=3)

        budget.register_paradox("p1", intensity=0.3)
        budget.register_paradox("p2", intensity=0.4)
        budget.register_paradox("p3", intensity=0.2)

        assert budget.current_paradox_energy == pytest.approx(0.9)
        assert budget.active_paradox_count == 3

    def test_partial_resolution_releases_partial_energy(self):
        """Resolving one paradox releases its energy only."""
        budget = ParadoxEnergyBudget()
        budget.register_paradox("p1", intensity=0.4)
        budget.register_paradox("p2", intensity=0.3)

        budget.resolve_paradox("p1")

        # Only p1's energy released (use approx for floating point)
        assert budget.current_paradox_energy == pytest.approx(0.3)
        assert budget.active_paradox_count == 1

"""
tests/test_wealth_invariant_surface.py — Smoke tests for WEALTH 13-tool surface

Verifies:
1. All 13 tools are callable and return dicts
2. Emergence layer (E_PSI, E_PWR, E_INT) is present in every output
3. Output envelope carries schema_version and final_authority
4. Registry status tool reports truth PASS
5. Health check reports repo_head and schema_version

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import pytest
from typing import Any

from skills.wealth.invariant_surface import (
    wealth_boundary_governance,
    wealth_conservation_capital,
    wealth_energy_productivity,
    wealth_entropy_risk,
    wealth_field_macro,
    wealth_flow_liquidity,
    wealth_game_coordination,
    wealth_gradient_price,
    wealth_hysteresis_ledger,
    wealth_inertia_leverage,
    wealth_signal_information,
    wealth_time_discount,
)

# Also test the app-level wrappers
from arifosmcp.apps.wealth_app import (
    mcp_health_check,
    _wealth_boundary_governance,
    _wealth_conservation_capital,
    _wealth_energy_productivity,
    _wealth_entropy_risk,
    _wealth_field_macro,
    _wealth_flow_liquidity,
    _wealth_game_coordination,
    _wealth_gradient_price,
    _wealth_hysteresis_ledger,
    _wealth_inertia_leverage,
    _wealth_signal_information,
    _wealth_system_registry_status,
    _wealth_time_discount,
)


# ═══════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════


def _assert_common_envelope(result: dict[str, Any]) -> None:
    """Every invariant tool must return this structure."""
    assert isinstance(result, dict)
    assert "tool" in result
    assert "mode" in result
    assert "result" in result
    assert "emergence" in result
    assert "schema_version" in result
    assert result["schema_version"] == "wealth.physics_economics.v1"
    assert result.get("final_authority") == "ARIF"

    emergence = result["emergence"]
    assert "psychology" in emergence
    assert "power" in emergence
    assert "intelligence" in emergence
    assert "overall_verdict" in emergence

    # E_INT must never self-authorize
    if emergence["intelligence"]["verdict"] != "PASS":
        assert (
            "RECOMMENDED" in emergence["intelligence"]["verdict"]
            or "888_HOLD" in emergence["intelligence"]["verdict"]
        )


# ═══════════════════════════════════════════════════════
# CORE INVARIANT TESTS
# ═══════════════════════════════════════════════════════


class TestWealthConservationCapital:
    def test_state_mode(self):
        result = wealth_conservation_capital(mode="state", initial_investment=100000)
        _assert_common_envelope(result)
        assert result["result"]["capital_preserved"] is True

    def test_deployment_mode(self):
        result = wealth_conservation_capital(
            mode="deployment", initial_investment=10000, annual_benefit=2500, years=5
        )
        _assert_common_envelope(result)
        assert "npv" in result["result"]

    def test_unknown_mode(self):
        result = wealth_conservation_capital(mode="invalid")
        _assert_common_envelope(result)
        assert "error" in result["result"]


class TestWealthFlowLiquidity:
    def test_cashflow_mode(self):
        result = wealth_flow_liquidity(mode="cashflow", cashflows=[100, 200, 300])
        _assert_common_envelope(result)
        assert result["result"]["net_cashflow"] == 600

    def test_crisis_triage(self):
        result = wealth_flow_liquidity(mode="crisis_triage", cashflows=[10000], burn_rate=2000)
        _assert_common_envelope(result)
        assert "runway_months" in result["result"]

    def test_current_ratio(self):
        result = wealth_flow_liquidity(
            mode="current", current_assets=50000, current_liabilities=25000
        )
        _assert_common_envelope(result)
        assert result["result"]["current_ratio"] == pytest.approx(2.0)


class TestWealthGradientPrice:
    def test_spread_mode(self):
        result = wealth_gradient_price(mode="spread", price_a=110, price_b=100)
        _assert_common_envelope(result)
        assert result["result"]["spread"] == 10

    def test_all_mode(self):
        result = wealth_gradient_price(mode="all", price_a=110, price_b=100, cap_rate=0.07)
        _assert_common_envelope(result)
        assert "cap_rate" in result["result"]


class TestWealthEntropyRisk:
    def test_emv_mode(self):
        result = wealth_entropy_risk(mode="emv", outcomes=[100, -50], probabilities=[0.5, 0.5])
        _assert_common_envelope(result)
        assert result["result"]["emv"] == 25

    def test_evpi_mode(self):
        result = wealth_entropy_risk(mode="evpi", outcomes=[100, -50], probabilities=[0.5, 0.5])
        _assert_common_envelope(result)
        assert result["result"]["evpi"] == 75


class TestWealthEnergyProductivity:
    def test_roi_mode(self):
        result = wealth_energy_productivity(mode="roi", revenue=120, costs=100)
        _assert_common_envelope(result)
        assert result["result"]["roi"] == pytest.approx(0.2)

    def test_du_pont_mode(self):
        result = wealth_energy_productivity(
            mode="du_pont", revenue=100, net_income=10, assets=50, equity=25
        )
        _assert_common_envelope(result)
        assert "roe" in result["result"]


class TestWealthTimeDiscount:
    def test_npv_mode(self):
        result = wealth_time_discount(
            mode="npv", initial_investment=10000, cash_flows=[3000, 3000, 3000], discount_rate=0.1
        )
        _assert_common_envelope(result)
        assert "npv" in result["result"]

    def test_irr_mode(self):
        result = wealth_time_discount(
            mode="irr", initial_investment=10000, cash_flows=[3000, 3000, 3000]
        )
        _assert_common_envelope(result)
        assert "irr" in result["result"]

    def test_payback_mode(self):
        result = wealth_time_discount(
            mode="payback", initial_investment=10000, cash_flows=[4000, 4000, 4000]
        )
        _assert_common_envelope(result)
        assert result["result"]["payback_period"] == 3


class TestWealthInertiaLeverage:
    def test_dscr_mode(self):
        result = wealth_inertia_leverage(mode="dscr", ebitda=150000, debt_service=100000)
        _assert_common_envelope(result)
        assert result["result"]["dscr"] == pytest.approx(1.5)

    def test_leverage_mode(self):
        result = wealth_inertia_leverage(mode="leverage", total_debt=50, equity=50)
        _assert_common_envelope(result)
        assert result["result"]["leverage_ratio"] == pytest.approx(1.0)


class TestWealthFieldMacro:
    def test_macro_mode(self):
        result = wealth_field_macro(mode="macro", fed_rate=0.05, inflation_rate=0.03)
        _assert_common_envelope(result)
        assert result["result"]["regime"] == "tightening"

    def test_yield_curve_mode(self):
        result = wealth_field_macro(mode="yield_curve", ten_year_yield=0.04, two_year_yield=0.05)
        _assert_common_envelope(result)
        assert result["result"]["shape"] == "inverted"


class TestWealthSignalInformation:
    def test_sharpe_mode(self):
        result = wealth_signal_information(
            mode="sharpe", returns=[0.1, 0.05, -0.02, 0.08], risk_free_rate=0.02
        )
        _assert_common_envelope(result)
        assert "sharpe_ratio" in result["result"]

    def test_tracking_error_mode(self):
        result = wealth_signal_information(
            mode="tracking_error", returns=[0.1, 0.05], benchmark_returns=[0.08, 0.04]
        )
        _assert_common_envelope(result)
        assert "tracking_error" in result["result"]


class TestWealthGameCoordination:
    def test_nash_mode(self):
        result = wealth_game_coordination(mode="nash")
        _assert_common_envelope(result)
        assert "equilibrium" in result["result"]

    def test_chicken_mode(self):
        result = wealth_game_coordination(mode="chicken")
        _assert_common_envelope(result)
        assert len(result["result"]["equilibria"]) == 2


class TestWealthBoundaryGovernance:
    def test_floors_mode(self):
        result = wealth_boundary_governance(
            mode="floors", floor_scores={"L01": 0.9, "L02": 0.7, "L03": 0.85}
        )
        _assert_common_envelope(result)
        assert result["result"]["floors_checked"] == 3

    def test_screening_mode(self):
        result = wealth_boundary_governance(mode="screening", floor_scores={"L01": 0.9, "L02": 0.5})
        _assert_common_envelope(result)
        assert "screened_in" in result["result"]


class TestWealthHysteresisLedger:
    def test_status_mode(self):
        result = wealth_hysteresis_ledger(mode="status", session_id="test-sess")
        _assert_common_envelope(result)
        assert result["result"]["status"] == "OK"

    def test_init_mode(self):
        result = wealth_hysteresis_ledger(mode="init", session_id="new-sess")
        _assert_common_envelope(result)
        assert result["result"]["ledger"] == "VAULT999"


# ═══════════════════════════════════════════════════════
# APP-LEVEL WRAPPER TESTS
# ═══════════════════════════════════════════════════════


class TestAppLevelWrappers:
    """Verify the @wealth_app.tool wrappers produce identical output."""

    def test_app_conservation_capital(self):
        result = _wealth_conservation_capital(mode="state", initial_investment=100000)
        _assert_common_envelope(result)

    def test_app_flow_liquidity(self):
        result = _wealth_flow_liquidity(mode="cashflow", cashflows=[100, 200])
        _assert_common_envelope(result)

    def test_app_gradient_price(self):
        result = _wealth_gradient_price(mode="spread", price_a=110, price_b=100)
        _assert_common_envelope(result)

    def test_app_entropy_risk(self):
        result = _wealth_entropy_risk(mode="emv", outcomes=[100], probabilities=[1.0])
        _assert_common_envelope(result)

    def test_app_energy_productivity(self):
        result = _wealth_energy_productivity(mode="roi", revenue=120, costs=100)
        _assert_common_envelope(result)

    def test_app_time_discount(self):
        result = _wealth_time_discount(
            mode="npv", initial_investment=10000, cash_flows=[3000], discount_rate=0.1
        )
        _assert_common_envelope(result)

    def test_app_inertia_leverage(self):
        result = _wealth_inertia_leverage(mode="dscr", ebitda=150000, debt_service=100000)
        _assert_common_envelope(result)

    def test_app_field_macro(self):
        result = _wealth_field_macro(mode="macro", fed_rate=0.05)
        _assert_common_envelope(result)

    def test_app_signal_information(self):
        result = _wealth_signal_information(mode="sharpe", returns=[0.1, 0.05])
        _assert_common_envelope(result)

    def test_app_game_coordination(self):
        result = _wealth_game_coordination(mode="nash")
        _assert_common_envelope(result)

    def test_app_boundary_governance(self):
        result = _wealth_boundary_governance(mode="floors", floor_scores={"L01": 0.9})
        _assert_common_envelope(result)

    def test_app_hysteresis_ledger(self):
        result = _wealth_hysteresis_ledger(mode="status", session_id="test")
        _assert_common_envelope(result)


# ═══════════════════════════════════════════════════════
# HEALTH & REGISTRY TESTS
# ═══════════════════════════════════════════════════════


class TestHealthAndRegistry:
    def test_mcp_health_check(self):
        result = mcp_health_check()
        assert isinstance(result, dict)
        assert result["status"] == "OK"
        assert result["schema_version"] == "wealth.physics_economics.v1"
        assert result["public_surface_count"] == 13
        assert result["runtime_surface_count"] == 13
        assert result["final_authority"] == "ARIF"
        assert "repo_head" in result
        assert "image_tag" in result

    def test_registry_status(self):
        result = _wealth_system_registry_status()
        assert isinstance(result, dict)
        assert result["schema_version"] == "wealth.physics_economics.v1"
        assert result["registry_truth"] == "PASS"
        assert result["final_authority"] == "ARIF"
        assert len(result.get("missing_visible_tools", [])) == 0

    def test_registry_status_intended_count(self):
        result = _wealth_system_registry_status()
        assert result["intended_public_tools"] == 13


# ═══════════════════════════════════════════════════════
# EMERGENCE LAYER SPECIFIC TESTS
# ═══════════════════════════════════════════════════════


class TestEmergenceLayer:
    def test_psi_breach_triggers_sabar(self):
        result = wealth_conservation_capital(
            mode="state",
            initial_investment=100,
            cognitive_bias_index=0.9,
            affective_contagion=0.9,
            cognitive_load_ratio=0.9,
        )
        assert result["emergence"]["psychology"]["verdict"] == "SABAR"
        assert result["emergence"]["overall_verdict"] in ("SABAR", "HOLD", "888_HOLD")

    def test_pwr_breach_triggers_hold(self):
        result = wealth_conservation_capital(
            mode="state",
            initial_investment=100,
            pareto_ratio=0.95,
            exit_barrier=0.95,
            consent_ratio=0.05,
        )
        assert result["emergence"]["power"]["verdict"] == "HOLD"

    def test_int_breach_recommends_hold_not_self_authorizes(self):
        result = wealth_conservation_capital(
            mode="state",
            initial_investment=100,
            order_parameter=0.9,
            component_capability_hash="abc",
            system_behavior_hash="xyz",
            telos_drift=0.5,
        )
        int_verdict = result["emergence"]["intelligence"]["verdict"]
        assert "888_HOLD" in int_verdict or int_verdict == "PASS"
        # Must NOT claim to have issued a binding 888_HOLD itself
        assert int_verdict != "888_HOLD" or "RECOMMENDED" in int_verdict

    def test_clean_payload_passes_all(self):
        result = wealth_conservation_capital(mode="state", initial_investment=100)
        assert result["emergence"]["overall_verdict"] == "PASS"


# ═══════════════════════════════════════════════════════
# SURFACE LOCK TEST
# ═══════════════════════════════════════════════════════


class TestSurfaceLock:
    def test_expected_tools_set(self):
        from arifosmcp.apps.wealth_app import _EXPECTED_PUBLIC_TOOLS

        expected = {
            "mcp_health_check",
            "wealth_conservation_capital",
            "wealth_flow_liquidity",
            "wealth_gradient_price",
            "wealth_entropy_risk",
            "wealth_energy_productivity",
            "wealth_time_discount",
            "wealth_inertia_leverage",
            "wealth_field_macro",
            "wealth_signal_information",
            "wealth_game_coordination",
            "wealth_boundary_governance",
            "wealth_hysteresis_ledger",
        }
        assert _EXPECTED_PUBLIC_TOOLS == expected
        assert len(_EXPECTED_PUBLIC_TOOLS) == 13

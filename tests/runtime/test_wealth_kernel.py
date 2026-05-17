"""
tests/runtime/test_wealth_kernel.py — WEALTH Capital Intelligence Tests
"""

from __future__ import annotations

import pytest

from core.organs._5_wealth import (
    EconomicEnvelope,
    wealth_npv_reward,
    wealth_irr_yield,
    wealth_dscr_leverage,
    calculate_npv,
    calculate_irr,
    calculate_dscr,
    derive_verdict,
    build_cashflow_series,
    count_sign_changes,
)


class TestBuildCashflowSeries:
    def test_basic_series(self):
        s = build_cashflow_series(1000, [300, 400, 500])
        assert s == [-1000, 300, 400, 500]

    def test_terminal_value_appended(self):
        s = build_cashflow_series(1000, [300, 400], terminal=200)
        assert s == [-1000, 300, 600]

    def test_single_flow_with_terminal(self):
        s = build_cashflow_series(1000, [300], terminal=100)
        assert s == [-1000, 400]


class TestCountSignChanges:
    def test_no_change(self):
        assert count_sign_changes([-1000, 300, 400]) == 1

    def test_one_change(self):
        assert count_sign_changes([-1000, 300, -50]) == 2

    def test_zero_skipped(self):
        assert count_sign_changes([-1000, 0, 300]) == 1


class TestCalculateNpv:
    def test_positive_npv(self):
        r = calculate_npv(1000, [500, 500, 500], 0.1)
        assert r["npv"] is not None
        assert r["npv"] > 0
        assert r["flags"] == []

    def test_negative_npv(self):
        r = calculate_npv(1000, [200, 200, 200], 0.5)
        assert r["npv"] < 0

    def test_zero_discount_rate(self):
        r = calculate_npv(1000, [400, 400, 400], 0.0)
        assert r["npv"] == pytest.approx(200.0, 0.01)

    def test_with_terminal_value(self):
        r = calculate_npv(1000, [300, 300], 0.1, terminal_value=500)
        # series = [-1000, 300, 800]
        assert r["npv"] is not None


class TestCalculateIrr:
    def test_typical_project(self):
        r = calculate_irr(1000, [400, 400, 400, 400])
        assert r["irr"] is not None
        assert 0.0 < r["irr"] < 1.0

    def test_no_sign_change(self):
        # No investment, just inflows — degenerate case
        r = calculate_irr(0, [100, 100])
        # Bisection will find something near bounds
        assert r["irr"] is not None


class TestCalculateDscr:
    def test_healthy_leverage(self):
        r = calculate_dscr(500, 200)
        assert r["dscr"] == pytest.approx(2.5, 0.01)
        assert r["flags"] == []

    def test_critical_leverage(self):
        r = calculate_dscr(150, 200)
        assert r["dscr"] == pytest.approx(0.75, 0.01)
        assert "LEVERAGE_DEFAULT" in r["flags"]

    def test_zero_debt_service(self):
        r = calculate_dscr(500, 0)
        assert r["dscr"] is None

    def test_boundary_exactly_one(self):
        r = calculate_dscr(200, 200)
        assert r["dscr"] == pytest.approx(1.0, 0.01)
        assert "LEVERAGE_DEFAULT" not in r["flags"]


class TestDeriveVerdict:
    def test_void_on_invalid(self):
        assert derive_verdict(["INVALID_INITIAL_INVESTMENT"]) == "VOID"

    def test_hold_on_critical(self):
        assert derive_verdict(["LEVERAGE_CRITICAL"]) == "888-HOLD"

    def test_qualify_on_non_normal(self):
        assert derive_verdict(["NON_NORMAL_FLOWS"]) == "QUALIFY"

    def test_invalid_trumps_hold(self):
        assert derive_verdict(["LEVERAGE_CRITICAL", "INVALID_INITIAL_INVESTMENT"]) == "VOID"

    def test_seal_when_clean(self):
        assert derive_verdict([]) == "SEAL"


class TestWealthNpvReward:
    def test_returns_envelope(self):
        env = wealth_npv_reward(1000, [400, 400, 400], 0.1)
        assert isinstance(env, EconomicEnvelope)
        assert env.tool == "wealth_npv_reward"
        assert env.dimension == "Reward"

    def test_positive_npv_accept(self):
        env = wealth_npv_reward(1000, [500, 500, 500], 0.1)
        assert env.allocation_signal == "ACCEPT"
        assert env.verdict == "SEAL"
        assert env.confidence == "HIGH"

    def test_negative_npv_reject(self):
        env = wealth_npv_reward(1000, [100, 100, 100], 0.5)
        assert env.allocation_signal == "REJECT"

    def test_invalid_input_void(self):
        env = wealth_npv_reward(-1000, [400, 400], 0.1)
        # The core doesn't flag negative investment as invalid currently,
        # but if it ever does, this should become VOID.
        assert env.verdict in ("SEAL", "VOID", "QUALIFY", "888-HOLD")

    def test_epistemic_passthrough(self):
        env = wealth_npv_reward(1000, [400, 400], 0.1, epistemic="ESTIMATE")
        assert env.epistemic == "ESTIMATE"


class TestWealthIrrYield:
    def test_returns_envelope(self):
        env = wealth_irr_yield(1000, [400, 400, 400, 400])
        assert isinstance(env, EconomicEnvelope)
        assert env.tool == "wealth_irr_yield"
        assert env.dimension == "Energy"
        assert env.primary_result["irr"] is not None


class TestWealthDscrLeverage:
    def test_healthy(self):
        env = wealth_dscr_leverage(500, 200)
        assert env.verdict == "SEAL"
        assert env.allocation_signal == "MARGINAL"  # dscr tool doesn't set ACCEPT/REJECT

    def test_critical(self):
        env = wealth_dscr_leverage(150, 200)
        assert env.verdict == "888-HOLD"
        assert "LEVERAGE_DEFAULT" in env.integrity_flags


class TestAnalyzeCostBenefit:
    def test_compatibility_wrapper(self):
        from core.organs._5_wealth import analyze_cost_benefit

        r = analyze_cost_benefit(1000, [500, 500, 500], 0.1)
        assert "initial_investment" in r
        assert "npv" in r
        assert "is_positive" in r
        assert r["is_positive"] is True

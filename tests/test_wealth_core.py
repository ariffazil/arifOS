"""
Test suite for core/organs/_5_wealth.py — Sovereign Valuation Kernel
════════════════════════════════════════════════════════════════════

Tests NPV, IRR, DSCR computations and EconomicEnvelope generation.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from core.organs._5_wealth import (
    EconomicEnvelope,
    calculate_npv,
    calculate_irr,
    calculate_dscr,
    wealth_npv_reward,
    wealth_irr_yield,
    wealth_dscr_leverage,
    derive_verdict,
    derive_allocation_signal,
    build_cashflow_series,
    count_sign_changes,
    round_value,
)


class TestRoundValue:
    def test_rounds_normally(self) -> None:
        assert round_value(3.14159265, 2) == 3.14

    def test_returns_none_for_none(self) -> None:
        assert round_value(None) is None

    def test_returns_inf_as_is(self) -> None:
        assert round_value(float("inf")) == float("inf")

    def test_returns_nan_as_is(self) -> None:
        assert math.isnan(round_value(float("nan")))


class TestCountSignChanges:
    def test_no_changes(self) -> None:
        assert count_sign_changes([1, 2, 3]) == 0

    def test_one_change(self) -> None:
        assert count_sign_changes([1, -1, -2]) == 1

    def test_ignores_zeros(self) -> None:
        assert count_sign_changes([1, 0, -1]) == 1

    def test_multiple_changes(self) -> None:
        assert count_sign_changes([1, -1, 2, -2]) == 3


class TestBuildCashflowSeries:
    def test_basic_series(self) -> None:
        series = build_cashflow_series(100, [10, 20, 30])
        assert series == [-100, 10, 20, 30]

    def test_with_terminal_value(self) -> None:
        series = build_cashflow_series(100, [10, 20], terminal=50)
        assert series == [-100, 10, 70]

    def test_terminal_alone(self) -> None:
        series = build_cashflow_series(100, [10], terminal=5)
        assert series == [-100, 15]


class TestCalculateNpv:
    def test_positive_npv(self) -> None:
        result = calculate_npv(100, [50, 60], 0.1)
        assert result["npv"] is not None
        assert result["npv"] > 0
        assert "INVALID_NPV" not in result["flags"]

    def test_negative_npv(self) -> None:
        result = calculate_npv(100, [30, 30], 0.5)
        assert result["npv"] is not None
        assert result["npv"] < 0

    def test_zero_rate(self) -> None:
        result = calculate_npv(100, [40, 60], 0.0)
        assert result["npv"] == 0.0

    def test_with_terminal(self) -> None:
        result = calculate_npv(100, [30, 30], 0.1, terminal_value=50)
        assert result["npv"] is not None
        assert result["npv"] < 0


class TestCalculateIrr:
    def test_irr_exists(self) -> None:
        result = calculate_irr(100, [60, 60])
        assert result["irr"] is not None
        assert -0.9 < result["irr"] < 1.0

    def test_simple_case(self) -> None:
        result = calculate_irr(100, [121])
        assert result["irr"] is not None
        assert abs(result["irr"] - 0.21) < 0.02


class TestCalculateDscr:
    def test_healthy_leverage(self) -> None:
        result = calculate_dscr(10, 5)
        assert result["dscr"] == 2.0
        assert result["flags"] == []

    def test_critical_leverage(self) -> None:
        result = calculate_dscr(4, 5)
        assert result["dscr"] == 0.8
        assert "LEVERAGE_DEFAULT" in result["flags"]

    def test_zero_debt(self) -> None:
        result = calculate_dscr(10, 0)
        assert result["dscr"] is None


class TestDeriveVerdict:
    def test_seal(self) -> None:
        assert derive_verdict([]) == "SEAL"
        assert derive_verdict(["NON_NORMAL_FLOWS"]) == "QUALIFY"

    def test_qualify(self) -> None:
        assert derive_verdict(["IRR_NOT_FOUND"]) == "QUALIFY"

    def test_hold(self) -> None:
        assert derive_verdict(["LEVERAGE_CRITICAL"]) == "888-HOLD"

    def test_void(self) -> None:
        assert derive_verdict(["INVALID_INITIAL_INVESTMENT"]) == "VOID"
        assert derive_verdict(["INVALID_INITIAL_INVESTMENT", "LEVERAGE_CRITICAL"]) == "VOID"


class TestDeriveAllocationSignal:
    def test_accept_positive_npv(self) -> None:
        assert derive_allocation_signal("wealth_npv_reward", {"npv": 100}, []) == "ACCEPT"

    def test_reject_negative_npv(self) -> None:
        assert derive_allocation_signal("wealth_npv_reward", {"npv": -50}, []) == "REJECT"

    def test_marginal_zero_npv(self) -> None:
        assert derive_allocation_signal("wealth_npv_reward", {"npv": 0}, []) == "MARGINAL"

    def test_invalid_returns_insufficient(self) -> None:
        assert (
            derive_allocation_signal("wealth_npv_reward", {"npv": 100}, ["INVALID_CASHFLOW_SERIES"])
            == "INSUFFICIENT_DATA"
        )

    def test_other_tool_marginal(self) -> None:
        assert derive_allocation_signal("wealth_irr_yield", {"irr": 0.1}, []) == "MARGINAL"


class TestWealthNpvReward:
    def test_returns_envelope(self) -> None:
        env = wealth_npv_reward(
            initial_investment=100,
            cash_flows=[50, 60],
            discount_rate=0.1,
        )
        assert isinstance(env, EconomicEnvelope)
        assert env.tool == "wealth_npv_reward"
        assert env.dimension == "Reward"
        assert env.verdict in ("SEAL", "QUALIFY", "888-HOLD", "VOID")
        assert "npv" in env.primary_result

    def test_epistemic_passed_through(self) -> None:
        env = wealth_npv_reward(
            initial_investment=100,
            cash_flows=[50, 60],
            discount_rate=0.1,
            epistemic="ESTIMATE",
        )
        assert env.epistemic == "ESTIMATE"


class TestWealthIrrYield:
    def test_returns_envelope(self) -> None:
        env = wealth_irr_yield(initial_investment=100, cash_flows=[60, 60])
        assert isinstance(env, EconomicEnvelope)
        assert env.tool == "wealth_irr_yield"
        assert env.dimension == "Energy"
        assert "irr" in env.primary_result


class TestWealthDscrLeverage:
    def test_healthy(self) -> None:
        env = wealth_dscr_leverage(ebitda=10, debt_service=5)
        assert env.verdict == "SEAL"
        assert env.primary_result["dscr"] == 2.0

    def test_critical(self) -> None:
        env = wealth_dscr_leverage(ebitda=4, debt_service=5)
        assert env.verdict == "888-HOLD"
        assert "LEVERAGE_DEFAULT" in env.integrity_flags


class TestWealthEdgeCases:
    def test_empty_cashflows(self) -> None:
        env = wealth_npv_reward(100, [], 0.1)
        assert env.primary_result["npv"] == -100.0

    def test_very_high_discount_rate(self) -> None:
        env = wealth_npv_reward(100, [1000, 1000], 0.99)
        assert env.primary_result["npv"] is not None

    def test_negative_initial_investment(self) -> None:
        env = wealth_npv_reward(-100, [50, 50], 0.1)
        series = build_cashflow_series(-100, [50, 50])
        assert series[0] == -100

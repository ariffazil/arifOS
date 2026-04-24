"""
skills/wealth/irr.py — IRR & MIRR

Internal-rate-of-return math ported from core.organs._5_wealth and
arifosmcp/tools_canonical.py (arifos_compute_finance[irr]).
"""

from __future__ import annotations

import math
from typing import Any

EPSILON = 1e-9


def _round_value(value: float | None, digits: int = 6) -> float | None:
    if value is None or not math.isfinite(value):
        return value
    return round(value, digits)


def _build_cashflow_series(initial: float, flows: list[float], terminal: float = 0) -> list[float]:
    series = [-abs(initial), *flows]
    if terminal and len(series) > 1:
        series[-1] += terminal
    return series


def _npv_from_series(series: list[float], rate: float) -> float:
    total = 0.0
    for i, cf in enumerate(series):
        total += cf / pow(1 + rate, i)
    return total


def irr(
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
) -> dict[str, Any]:
    """Approximate IRR via bisection search over [-0.9, 1.0]."""
    initial = initial_investment or 0
    flows = cash_flows or []
    series = _build_cashflow_series(initial, flows)

    f = lambda r: _npv_from_series(series, r)
    low, high = -0.9, 1.0
    for _ in range(100):
        mid = (low + high) / 2
        if f(mid) > 0:
            low = mid
        else:
            high = mid

    return {
        "irr": _round_value(mid),
        "flags": [],
    }


def mirr(
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    finance_rate: float = 0,
    reinvest_rate: float | None = None,
) -> dict[str, Any]:
    """Compute Modified IRR (MIRR) with explicit finance and reinvestment rates."""
    initial = initial_investment or 0
    flows = cash_flows or []
    if not flows:
        return {"mirr": None, "flags": ["INVALID_CASHFLOW_SERIES"]}

    n = len(flows)
    positive_total = sum(cf for cf in cash_flows if cf > 0)
    negative_total = abs(sum(cf for cf in cash_flows if cf < 0))

    if positive_total > 0 and negative_total > 0:
        f_rate = finance_rate if finance_rate else 0
        # Default reinvest_rate to IRR if not supplied
        if reinvest_rate is None:
            irr_result = irr(initial_investment=initial, cash_flows=flows)
            r_rate = irr_result.get("irr", 0) or 0
        else:
            r_rate = reinvest_rate
        mirr_num = positive_total * pow(1 + r_rate, n)
        mirr_den = abs(initial) * pow(1 + f_rate, n)
        if mirr_den > 0:
            mirr_val = pow(mirr_num / mirr_den, 1.0 / n) - 1
            return {
                "mirr": _round_value(mirr_val),
                "flags": [],
            }

    return {"mirr": None, "flags": []}

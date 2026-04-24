"""
skills/wealth/npv.py — NPV & Profitability Index

Net-present-value math ported from core.organs._5_wealth and
arifosmcp/tools_canonical.py (arifos_compute_finance[npv / profitability_index]).
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


def npv(
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
    terminal_value: float = 0,
) -> dict[str, Any]:
    """Evaluate NPV for an investment with optional terminal value."""
    initial = initial_investment or 0
    flows = cash_flows or []
    series = _build_cashflow_series(initial, flows, terminal_value)
    npv_val = _npv_from_series(series, discount_rate)

    return {
        "npv": _round_value(npv_val),
        "discount_rate": discount_rate,
        "initial_investment": initial_investment,
        "terminal_value": terminal_value,
        "criterion": "accept" if npv_val > 0 else "reject" if npv_val < 0 else "marginal",
        "flags": [] if math.isfinite(npv_val) else ["INVALID_NPV"],
    }


def profitability_index(
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
    terminal_value: float = 0,
) -> dict[str, Any]:
    """Compute the Profitability Index (PI) = PV of future cashflows / initial investment."""
    initial = initial_investment or 0
    flows = cash_flows or []
    series = _build_cashflow_series(initial, flows, terminal_value)
    npv_future = _npv_from_series(series, discount_rate)
    pv_total = abs(initial) + npv_future
    pi = pv_total / abs(initial) if initial else None

    return {
        "pi": _round_value(pi) if pi is not None else None,
        "npv": npv_future,
        "criterion": "accept" if pi and pi > 1 else "reject" if pi else "undefined",
    }

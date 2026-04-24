"""
skills/wealth/payback.py — Payback Period

Payback logic ported from arifosmcp/tools_canonical.py (arifos_compute_finance[payback]).
"""

from __future__ import annotations

from typing import Any


def payback(
    initial_investment: float | None = None,
    cash_flows: list[float] | None = None,
    discount_rate: float = 0,
) -> dict[str, Any]:
    """Compute simple and discounted payback periods."""
    cumulative = 0.0
    periods = 0
    cumulative_series: list[float] = []
    for i, cf in enumerate(cash_flows or []):
        cumulative += cf
        cumulative_series.append(cumulative)
        if cumulative >= (initial_investment or 0):
            periods = i + 1
            break

    disc_cumulative = 0.0
    disc_periods = None
    for i, cf in enumerate(cash_flows or []):
        disc_cumulative += cf / pow(1 + discount_rate, i) if discount_rate else cf
        if disc_cumulative >= (initial_investment or 0):
            disc_periods = i + 1
            break

    return {
        "simple_payback_period": periods,
        "discounted_payback_period": disc_periods,
        "unit": "years",
        "cumulative_cash_flows": cumulative_series,
    }

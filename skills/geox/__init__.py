"""
skills/geox/__init__.py — GEOX Domain Skill

Earth-witness computation primitives ported from the arifOS canonical physics engine.
Exports: petrophysics_compute, stratigraphy_correlate, geometry_build,
         monte_carlo, entropy_audit, growth_runway
"""

from __future__ import annotations

import math
from typing import Any

from .petrophysics import petrophysics_compute
from .stratigraphy import stratigraphy_correlate
from .geometry import geometry_build
from .monte_carlo import monte_carlo


def entropy_audit(cashflows: list[float] | None = None) -> dict[str, Any]:
    """Audit cashflow entropy and detect multiple-IRR conditions."""
    if not cashflows:
        return {"entropy_score": 0.0, "multiple_IRRs": False}

    prev = 0
    changes = 0
    for cf in cashflows:
        if abs(cf) < 1e-9:
            continue
        sign = 1 if cf > 0 else -1
        if prev != 0 and sign != prev:
            changes += 1
        prev = sign

    signs = [1 if cf >= 0 else -1 for cf in cashflows]
    pos = sum(1 for s in signs if s > 0)
    neg = sum(1 for s in signs if s < 0)
    n = len(signs)
    p_pos = pos / n if n > 0 else 0.5
    p_neg = neg / n if n > 0 else 0.5

    entropy = 0.0
    if p_pos > 0:
        entropy -= p_pos * math.log2(p_pos)
    if p_neg > 0:
        entropy -= p_neg * math.log2(p_neg)

    norm_entropy = entropy / math.log2(2) if math.log2(2) > 0 else 0
    return {
        "entropy_score": round(norm_entropy, 4),
        "multiple_IRRs": changes > 1,
    }


def growth_runway(
    cashflows: list[float] | None = None,
    burn_rate: float | None = None,
) -> dict[str, Any]:
    """Compute CAGR and runway months from a cashflow series."""
    if not cashflows or len(cashflows) < 2:
        return {"cagr": 0.0, "runway_months": 0}

    first, last = cashflows[0], cashflows[-1]
    n = len(cashflows) - 1
    cagr = (abs(last) / abs(first)) ** (1.0 / n) - 1 if first != 0 and n > 0 else 0.0
    runway_months = first / burn_rate if burn_rate and burn_rate > 0 and first > 0 else 0

    return {
        "cagr": round(cagr, 4),
        "runway_months": round(runway_months, 1),
    }


__all__ = [
    "petrophysics_compute",
    "stratigraphy_correlate",
    "geometry_build",
    "monte_carlo",
    "entropy_audit",
    "growth_runway",
]

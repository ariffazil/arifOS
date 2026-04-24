"""
skills/wealth/dscr.py — Debt Service Coverage Ratio

DSCR logic ported from core.organs._5_wealth and
arifosmcp/tools_canonical.py (arifos_compute_finance[dscr]).
"""

from __future__ import annotations

import math
from typing import Any

EPSILON = 1e-9


def _round_value(value: float | None, digits: int = 6) -> float | None:
    if value is None or not math.isfinite(value):
        return value
    return round(value, digits)


def dscr(
    ebitda: float | None = None,
    debt_service: float | None = None,
) -> dict[str, Any]:
    """Compute DSCR and adequacy criterion."""
    ebitda = ebitda or 0
    debt_service = debt_service or 0
    if debt_service == 0:
        return {"error": "debt_service cannot be zero"}

    dscr_val = ebitda / debt_service
    return {
        "dscr": _round_value(dscr_val),
        "ebitda": ebitda,
        "debt_service": debt_service,
        "criterion": "adequate" if dscr_val >= 1.25 else "inadequate",
        "flags": ["LEVERAGE_DEFAULT"] if dscr_val < 1.0 else [],
    }

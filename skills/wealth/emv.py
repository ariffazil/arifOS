"""
skills/wealth/emv.py — Expected Monetary Value

EMV logic ported from arifosmcp/tools_canonical.py (arifos_compute_finance[emv]).
"""

from __future__ import annotations

from typing import Any


def emv(
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
) -> dict[str, Any]:
    """Compute Expected Monetary Value from discrete outcomes and probabilities."""
    if not outcomes or not probabilities or len(outcomes) != len(probabilities):
        return {"error": "outcomes and probabilities must have same length"}

    emv_val = sum(o * p for o, p in zip(outcomes, probabilities))
    prob_sum = sum(probabilities)
    flags = [] if abs(prob_sum - 1.0) < 0.001 else ["PROBABILITY_MASS_INVALID"]

    return {
        "emv": round(emv_val, 6),
        "distribution": {"outcomes": outcomes, "probabilities": probabilities},
        "prob_sum": round(prob_sum, 6),
        "flags": flags,
    }

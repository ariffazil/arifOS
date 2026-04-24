"""
skills/geox/monte_carlo.py — Probabilistic Simulation

Monte Carlo engine ported from
arifosmcp/tools_canonical.py (arifos_compute_physics[monte_carlo]).
"""

from __future__ import annotations

import math
import random
from typing import Any


def monte_carlo(
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    iterations: int = 1000,
) -> dict[str, Any]:
    """Run a Monte Carlo simulation over discrete outcomes."""
    if not outcomes or not probabilities or len(outcomes) != len(probabilities):
        return {
            "error": "outcomes and probabilities must be non-empty and matching",
        }

    results: list[float] = []
    for _ in range(iterations):
        r = random.random()
        cumulative = 0.0
        for outcome, prob in zip(outcomes, probabilities):
            cumulative += prob
            if r <= cumulative:
                results.append(outcome)
                break

    if not results:
        results = [sum(o * p for o, p in zip(outcomes, probabilities))]

    mean_val = sum(results) / len(results)
    variance_val = sum((x - mean_val) ** 2 for x in results) / len(results)
    sorted_res = sorted(results)
    p10 = sorted_res[int(len(sorted_res) * 0.10)]
    p50 = sorted_res[int(len(sorted_res) * 0.50)]
    p90 = sorted_res[int(len(sorted_res) * 0.90)]

    return {
        "iterations": iterations,
        "mean": round(mean_val, 4),
        "std_dev": round(math.sqrt(variance_val), 4),
        "distribution": {
            "p10": round(p10, 4),
            "p50": round(p50, 4),
            "p90": round(p90, 4),
        },
        "confidence_intervals": {"90": [round(p10, 4), round(p90, 4)]},
    }

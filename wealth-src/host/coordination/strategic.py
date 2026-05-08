"""
Strategic / non-cooperative equilibrium approximation.
Best-response iteration for constrained linear-utility games.
"""

import copy
import math
from typing import Any, Dict, List

from host.coordination.lp_allocator import allocate


def nash_approximation(
    agents: List[dict],
    resources: Dict[str, float],
    max_iterations: int = 50,
    tolerance: float = 1e-4,
) -> Dict[str, Any]:
    """
    Approximate a generalized Nash equilibrium via best-response iteration.
    Each agent solves an LP taking others' allocations as fixed residual capacity.
    """
    if not agents or not resources:
        return {"equilibrium": {}, "converged": False, "iterations": 0, "flags": ["NO_AGENTS_OR_RESOURCES"]}

    res_names = list(resources.keys())
    n = len(agents)

    # Initialize equal split (or proportional to demand)
    current = {}
    for agent in agents:
        name = agent["name"]
        current[name] = {}
        for r in res_names:
            current[name][r] = resources[r] / max(n, 1)

    for iteration in range(1, max_iterations + 1):
        next_alloc = {}
        for agent in agents:
            name = agent["name"]
            # Residual capacity = total - sum of others' current allocations
            residual = {}
            for r in res_names:
                others_sum = sum(current[other["name"]].get(r, 0.0) for other in agents if other["name"] != name)
                residual[r] = max(0.0, resources[r] - others_sum)

            # Single-agent LP
            single_result = allocate([agent], residual)
            next_alloc[name] = single_result["allocations"].get(name, {r: 0.0 for r in res_names})

        # Check convergence
        max_diff = 0.0
        for name in current:
            for r in res_names:
                diff = abs(next_alloc[name][r] - current[name][r])
                max_diff = max(max_diff, diff)

        current = next_alloc
        if max_diff < tolerance:
            return {
                "equilibrium": {k: {r: round(v, 6) for r, v in vals.items()} for k, vals in current.items()},
                "converged": True,
                "iterations": iteration,
                "max_diff": round(max_diff, 8),
                "flags": [],
            }

    return {
        "equilibrium": {k: {r: round(v, 6) for r, v in vals.items()} for k, vals in current.items()},
        "converged": False,
        "iterations": max_iterations,
        "max_diff": round(max_diff, 8),
        "flags": ["NASH_NO_CONVERGENCE"],
    }

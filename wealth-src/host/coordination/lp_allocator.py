"""
Linear Programming allocator for multi-agent resource coordination.
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from scipy.optimize import linprog


def allocate(
    agents: List[dict],
    resources: Dict[str, float],
    constraints: Optional[List[dict]] = None,
) -> Dict[str, Any]:
    """
    Solve welfare-maximizing allocation under resource constraints.

    agents: list of {"name": str, "utility": {res: coeff}, "demand": {res: max}}
    resources: {res: supply}
    constraints: optional additional linear constraints (not implemented in MVP)
    """
    if not agents or not resources:
        return {
            "allocations": {},
            "total_welfare": 0.0,
            "shadow_prices": {},
            "feasible": False,
            "unmet_demand": {},
            "flags": ["NO_AGENTS_OR_RESOURCES"],
        }

    res_names = list(resources.keys())
    n_agents = len(agents)
    n_res = len(res_names)
    var_count = n_agents * n_res

    # Objective: maximize sum(utility_i_r * x_i_r)
    # linprog minimizes, so negate coefficients
    c = []
    bounds = []
    agent_index = {}
    for i, agent in enumerate(agents):
        agent_index[agent["name"]] = i
        for r in res_names:
            coeff = -float(agent.get("utility", {}).get(r, 0.0))
            c.append(coeff)
            demand = float(agent.get("demand", {}).get(r, math.inf))
            max_val = demand if math.isfinite(demand) and demand > 0 else math.inf
            bounds.append((0.0, max_val))

    # Resource constraints: sum_i x_i_r <= supply_r
    A_ub = []
    b_ub = []
    for ri, r in enumerate(res_names):
        row = [0.0] * var_count
        for i in range(n_agents):
            idx = i * n_res + ri
            row[idx] = 1.0
        A_ub.append(row)
        b_ub.append(float(resources[r]))

    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method="highs")

    if not result.success:
        return {
            "allocations": {},
            "total_welfare": 0.0,
            "shadow_prices": {},
            "feasible": False,
            "unmet_demand": {},
            "flags": ["LP_INFEASIBLE"],
        }

    # Reconstruct allocations
    allocations: Dict[str, Dict[str, float]] = {agent["name"]: {} for agent in agents}
    unmet_demand: Dict[str, Dict[str, float]] = {}
    for i, agent in enumerate(agents):
        name = agent["name"]
        unmet = {}
        for ri, r in enumerate(res_names):
            idx = i * n_res + ri
            val = float(result.x[idx])
            allocations[name][r] = round(val, 6)
            demand = float(agent.get("demand", {}).get(r, 0.0))
            if demand > 0:
                unmet[r] = round(max(0.0, demand - val), 6)
        if unmet:
            unmet_demand[name] = unmet

    # Shadow prices from dual (inequality multipliers)
    # We minimized -welfare, so marginals are negative; negate to get welfare/unit.
    shadow_prices = {}
    if result.ineqlin is not None and result.ineqlin.marginals is not None:
        for ri, r in enumerate(res_names):
            shadow_prices[r] = round(-float(result.ineqlin.marginals[ri]), 6)

    total_welfare = round(-result.fun, 6)

    flags = []
    if unmet_demand:
        flags.append("DEMAND_PARTIALLY_UNMET")

    return {
        "allocations": allocations,
        "total_welfare": total_welfare,
        "shadow_prices": shadow_prices,
        "feasible": True,
        "unmet_demand": unmet_demand,
        "flags": flags,
    }

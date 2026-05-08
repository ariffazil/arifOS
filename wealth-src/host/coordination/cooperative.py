"""
Cooperative game theory layer: Shapley values and core feasibility.
"""

import math
from itertools import combinations
from typing import Any, Dict, List, Optional

from host.coordination.lp_allocator import allocate


def _coalition_value(coalition: List[str], agents: List[dict], resources: Dict[str, float]) -> float:
    """Value of a coalition = optimal welfare achievable by its members alone."""
    members = [a for a in agents if a["name"] in coalition]
    if not members:
        return 0.0
    result = allocate(members, resources)
    return result["total_welfare"] if result["feasible"] else 0.0


def shapley_values(agents: List[dict], resources: Dict[str, float]) -> Dict[str, Any]:
    """
    Compute exact Shapley values for small agent sets (n <= 10).
    Returns attribution of total cooperative surplus to each agent.
    """
    names = [a["name"] for a in agents]
    n = len(names)
    if n == 0:
        return {"shapley": {}, "total_value": 0.0, "flags": ["NO_AGENTS"]}

    if n > 10:
        return {"shapley": {}, "total_value": 0.0, "flags": ["SHAPLEY_EXACT_LIMIT_EXCEEDED"]}

    # Precompute coalition values (sorted tuples for consistent keys)
    coalition_values = {}
    for size in range(n + 1):
        for combo in combinations(names, size):
            coalition_values[tuple(sorted(combo))] = _coalition_value(list(combo), agents, resources)

    total_value = coalition_values[tuple(sorted(names))]
    shapley = {name: 0.0 for name in names}

    for name in names:
        contrib = 0.0
        others = [x for x in names if x != name]
        for size in range(len(others) + 1):
            for combo in combinations(others, size):
                s = len(combo)
                weight = math.factorial(s) * math.factorial(n - s - 1) / math.factorial(n)
                without = combo
                with_name = tuple(sorted(combo + (name,)))
                contrib += weight * (coalition_values[with_name] - coalition_values[without])
        shapley[name] = round(contrib, 6)

    return {
        "shapley": shapley,
        "total_value": round(total_value, 6),
        "flags": [],
    }


def core_feasibility(
    agents: List[dict],
    resources: Dict[str, float],
    proposed_allocation: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, Any]:
    """
    Check whether a proposed allocation is in the core.
    If no proposal given, uses the LP-optimal allocation.
    """
    names = [a["name"] for a in agents]
    n = len(names)
    if n == 0:
        return {"in_core": False, "blocking_coalitions": [], "flags": ["NO_AGENTS"]}

    if proposed_allocation is None:
        lp_result = allocate(agents, resources)
        if not lp_result["feasible"]:
            return {"in_core": False, "blocking_coalitions": [], "flags": ["LP_INFEASIBLE"]}
        proposed_allocation = lp_result["allocations"]

    # Compute each agent's proposed welfare
    agent_welfare = {}
    for agent in agents:
        name = agent["name"]
        welfare = 0.0
        for res, val in proposed_allocation.get(name, {}).items():
            coeff = float(agent.get("utility", {}).get(res, 0.0))
            welfare += coeff * val
        agent_welfare[name] = round(welfare, 6)

    blocking = []
    # For n > 8, sample coalitions rather than enumerating all
    enumerate_all = n <= 8
    coalitions_to_check = []
    if enumerate_all:
        for size in range(1, n + 1):
            coalitions_to_check.extend(combinations(names, size))
    else:
        # Check singletons and grand coalition always; sample mid-size
        for name in names:
            coalitions_to_check.append((name,))
        coalitions_to_check.append(tuple(names))
        import random
        random.seed(42)
        for size in range(2, n):
            for combo in combinations(names, size):
                if random.random() < 0.1:
                    coalitions_to_check.append(combo)

    for combo in coalitions_to_check:
        coalition_value = _coalition_value(list(combo), agents, resources)
        proposed_value = sum(agent_welfare[name] for name in combo)
        if proposed_value < coalition_value - 1e-6:
            blocking.append({
                "coalition": list(combo),
                "proposed_value": round(proposed_value, 6),
                "coalition_value": round(coalition_value, 6),
                "gap": round(coalition_value - proposed_value, 6),
            })

    in_core = len(blocking) == 0
    flags = [] if in_core else ["CORE_BLOCK_DETECTED"]

    return {
        "in_core": in_core,
        "blocking_coalitions": blocking,
        "agent_welfare": agent_welfare,
        "flags": flags,
    }

"""
Commons-risk scoring using actual LP shadow prices and scarcity metrics.
"""

import math
from typing import Any, Dict, List

from host.coordination.lp_allocator import allocate


def commons_risk(
    agents: List[dict],
    resources: Dict[str, float],
) -> Dict[str, Any]:
    """
    Compute tragedy-of-the-commons risk from an LP perspective.
    Uses shadow prices, unmet demand, and scarcity ratios.
    """
    lp_result = allocate(agents, resources)
    if not lp_result["feasible"]:
        return {
            "tragedy_risk": 1.0,
            "scarcity_index": 1.0,
            "shadow_prices": {},
            "flags": ["ALLOCATION_INFEASIBLE"],
        }

    total_demand = {r: 0.0 for r in resources}
    for agent in agents:
        for r in resources:
            total_demand[r] += float(agent.get("demand", {}).get(r, 0.0))

    scarcity = {}
    for r, supply in resources.items():
        demand = total_demand.get(r, 0.0)
        scarcity[r] = min(1.0, max(0.0, (demand - supply) / max(demand, 1e-9)))

    # Aggregate tragedy risk as weighted scarcity by shadow price
    shadow = lp_result.get("shadow_prices", {})
    weighted_scarcity = 0.0
    weight_sum = 0.0
    for r in resources:
        sp = shadow.get(r, 0.0)
        weighted_scarcity += scarcity[r] * sp
        weight_sum += max(sp, 1e-9)

    tragedy_risk = min(1.0, weighted_scarcity / max(weight_sum, 1e-9)) if weight_sum > 0 else max(scarcity.values()) if scarcity else 0.0
    unmet_count = sum(1 for a in lp_result.get("unmet_demand", {}).values() if a)

    flags = []
    if tragedy_risk > 0.5:
        flags.append("TRAGEDY_OF_COMMONS")
    if unmet_count > 0:
        flags.append("DEMAND_PARTIALLY_UNMET")

    return {
        "tragedy_risk": round(tragedy_risk, 4),
        "scarcity_index": {r: round(v, 4) for r, v in scarcity.items()},
        "shadow_prices": shadow,
        "unmet_agents": unmet_count,
        "flags": flags,
    }

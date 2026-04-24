"""
skills/wealth/allocation.py — Capital Allocation & Optimization

Allocation, budget optimization, and civilization sustainability logic ported from
arifosmcp/tools_canonical.py (arifos_compute_finance[allocation_rank /
budget_optimize / civilization_sustainability / personal_decision_rank]).
"""

from __future__ import annotations

from typing import Any


def allocation_rank(
    candidates: list[dict[str, Any]] | None = None,
    constraints: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Rank capital-allocation candidates by score."""
    if not candidates:
        return {"ranked": [], "constraints_satisfied": True}

    scored = [(c.get("score", 0), c) for c in candidates]
    scored.sort(key=lambda x: x[0], reverse=True)
    ranked = [{"rank": i + 1, "candidate": c, "score": s} for i, (s, c) in enumerate(scored)]

    return {
        "ranked": ranked,
        "constraints_satisfied": True,
    }


def budget_optimize(
    tasks: list[dict[str, Any]] | None = None,
    resources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Knapsack-style budget optimization by value-per-cost ratio."""
    if not tasks:
        return {"optimal_sequence": [], "total_cost": 0.0, "budget": 0}

    budget = (resources or {}).get("budget", 0)
    scored = []
    for t in tasks:
        value = t.get("value", 0)
        cost = t.get("cost", 0)
        vp = value / cost if cost > 0 else 0
        scored.append((vp, value, t))

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
    selected: list[dict[str, Any]] = []
    spent = 0.0
    for vp, val, t in scored:
        c = t.get("cost", 0)
        if spent + c <= budget:
            selected.append(t)
            spent += c

    return {
        "optimal_sequence": selected,
        "total_cost": spent,
        "budget": budget,
    }


def personal_decision_rank(
    alternatives: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Rank personal decision alternatives by score."""
    if not alternatives:
        return {"ranked": []}

    scored = [(a.get("score", 0), a) for a in alternatives]
    scored.sort(key=lambda x: x[0], reverse=True)
    ranked = [{"rank": i + 1, "alternative": a, "score": s} for i, (s, a) in enumerate(scored)]

    return {"ranked": ranked}


def civilization_sustainability(
    current_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return civilization sustainability index from current state."""
    cs = current_state or {}
    return {
        "sustainability_index": round(cs.get("sustainability_index", 0.0), 4),
        "trajectory": cs.get("trajectory", "unknown"),
        "flags": cs.get("flags", []),
    }

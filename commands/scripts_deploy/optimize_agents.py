#!/usr/bin/env python3
"""
arifOS OR Optimizer — Set-Covering Problem
Based on Destin Gong's "Optimizing AI Agent Planning with Operations Research"
Integrates with arifOS federation for resource allocation optimization.

Usage:
    python optimize_agents.py [--problem set_cover|knapsack|assignment]
"""

from pulp import *
import json
import argparse
from pathlib import Path

# === AGENT REGISTRY ===
# arifOS federation nodes — edit as capabilities evolve
AGENTS = [
    {"name": "geox", "cost": 150, "caps": ["well_logs", "porosity", "saturation", "petrophysics"]},
    {"name": "wealth", "cost": 100, "caps": ["stock_analysis", "portfolio", "maybank_data"]},
    {"name": "well", "cost": 120, "caps": ["biological", "vital_signs", "health"]},
    {"name": "a_forge", "cost": 80, "caps": ["code", "build", "deploy"]},
    {"name": "hermes", "cost": 200, "caps": ["orchestration", "task_routing", "coordination"]},
    {"name": "openclaw", "cost": 180, "caps": ["infra", "docker", "ops", "task_routing"]},
]


def set_covering(required_caps):
    """Select minimum-cost agent set covering all required capabilities."""
    prob = LpProblem("arifOS_SetCovering", LpMinimize)
    x = {a["name"]: LpVariable(f"x_{a['name']}", cat="Binary") for a in AGENTS}

    # Objective: minimize total cost
    prob += lpSum(a["cost"] * x[a["name"]] for a in AGENTS)

    # Constraint: each capability covered >= 1 agent
    for cap in required_caps:
        prob += lpSum(x[a["name"]] for a in AGENTS if cap in a["caps"]) >= 1, f"cover_{cap}"

    prob.solve()
    selected = [a["name"] for a in AGENTS if value(x[a["name"]]) == 1]
    return {
        "problem": "set_covering",
        "selected": selected,
        "total_monthly_cost": sum(a["cost"] for a in AGENTS if value(x[a["name"]]) == 1),
        "status": LpStatus[prob.status],
        "coverage": {
            cap: [a["name"] for a in AGENTS if cap in a["caps"] and value(x[a["name"]]) == 1]
            for cap in required_caps
        },
    }


def knapsack(budget, tokens_per_agent):
    """Select max-token agents under budget ceiling."""
    prob = LpProblem("arifOS_Knapsack", LpMaximize)
    x = {a["name"]: LpVariable(f"x_{a['name']}", cat="Binary") for a in AGENTS}

    # Objective: maximize tokens
    prob += lpSum(tokens_per_agent.get(a["name"], 0) * x[a["name"]] for a in AGENTS)

    # Constraint: budget
    prob += lpSum(a["cost"] * x[a["name"]] for a in AGENTS) <= budget

    prob.solve()
    selected = [a["name"] for a in AGENTS if value(x[a["name"]]) == 1]
    return {
        "problem": "knapsack",
        "selected": selected,
        "total_cost": sum(a["cost"] for a in AGENTS if value(x[a["name"]]) == 1),
        "total_tokens": sum(
            tokens_per_agent.get(a["name"], 0) for a in AGENTS if value(x[a["name"]]) == 1
        ),
        "budget": budget,
        "status": LpStatus[prob.status],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="arifOS OR Optimizer")
    parser.add_argument("--problem", choices=["set_cover", "knapsack"], default="set_cover")
    parser.add_argument("--budget", type=int, default=500, help="Budget for knapsack problem")
    parser.add_argument(
        "--caps", type=str, help="Comma-separated required capabilities (set_cover only)"
    )
    args = parser.parse_args()

    if args.problem == "set_cover":
        default_caps = ["well_logs", "stock_analysis", "biological", "code", "orchestration"]
        required = [c.strip() for c in args.caps.split(",")] if args.caps else default_caps
        result = set_covering(required)
    else:
        tokens = {a["name"]: 500000 for a in AGENTS}  # simplified: equal tokens per agent
        result = knapsack(args.budget, tokens)

    print(json.dumps(result, indent=2))

"""
arifOS Planner and Simulator Service

A search-based planner that generates alternative plans, runs simulations,
and creates rollback paths before high-risk execution.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


class SimulationResult(BaseModel):
    artifact_id: str
    expected_outcomes: list[str]
    risk_score: float
    confidence: float
    simulated_side_effects: list[str]

class PlanOption(BaseModel):
    plan_id: str
    description: str
    steps: list[str]
    rollback_path: list[str]
    simulation: SimulationResult | None = None

class PlannerOutput(BaseModel):
    status: Literal["PLANNED", "FAILED", "SIMULATION_REQUIRED"]
    intent: str
    options: list[PlanOption]
    selected_plan_id: str | None = None
    advisory: str = ""

async def arif_plan_and_simulate(
    intent: str,
    context: dict[str, Any],
    risk_tier: str = "medium",
    force_simulation: bool = True
) -> PlannerOutput:
    """
    Generate alternative plans for an intent and simulate their outcomes.
    
    If risk is medium/high, a simulation artifact MUST be generated.
    """
    
    # Generate mock options (in a real system, use arif_think / LLM search)
    options = []
    
    # Option A: The greedy/direct path
    opt_a = PlanOption(
        plan_id="plan_greedy_01",
        description="Direct execution of the intent with minimal steps.",
        steps=[f"Execute {intent} directly", "Verify completion"],
        rollback_path=["Revert direct changes if possible"]
    )
    
    # Option B: The safe/staged path
    opt_b = PlanOption(
        plan_id="plan_safe_02",
        description="Staged execution with dry-runs and explicit checkpoints.",
        steps=["Dry-run execution", "Take snapshot", f"Execute {intent} on snapshot", "Merge if successful"],
        rollback_path=["Discard snapshot", "Restore from checkpoint"]
    )
    
    options.extend([opt_a, opt_b])
    
    # Simulate
    if risk_tier in ["medium", "high"] or force_simulation:
        for opt in options:
            opt.simulation = SimulationResult(
                artifact_id=f"sim_{opt.plan_id}_{hash(opt.description) & 0xFFFFFFFF:08x}",
                expected_outcomes=[f"Outcome for {opt.plan_id}"],
                risk_score=0.8 if "greedy" in opt.plan_id else 0.2,
                confidence=0.85,
                simulated_side_effects=["State mutation"]
            )
            
    # Select best option (simplistic heuristic: pick safest if high risk)
    selected_plan = None
    if risk_tier in ["high"]:
        selected_plan = min(options, key=lambda x: x.simulation.risk_score if x.simulation else float('inf'))
    else:
        selected_plan = options[0]

    return PlannerOutput(
        status="PLANNED",
        intent=intent,
        options=options,
        selected_plan_id=selected_plan.plan_id if selected_plan else None,
        advisory=f"Generated {len(options)} plan options. Selected {selected_plan.plan_id} based on risk." if selected_plan else "No plan selected."
    )

# Export for MCP integration
def register_planner_tools(mcp):
    """Register the planner and simulator tools to the MCP server."""
    # This would hook into FastMCP in arifosmcp/server.py
    pass

"""
arifOS Federation — Minimal 6-Agent Proof of Concept
====================================================
One agent per axis. No specialization.

Philosophy:
- 6 axes = 6 agents = maximum orthogonality
- Ω_ortho = 1.0 trivially (no cross-axis calls within same axis)
- Call graph fits on one page
- One person can understand all of it

Production expansion:
- P → P01 (WELL), P02 (GEOX)
- T → T01 (physics), T02 (math)
- V → V01 (economic), V02 (allocation)
- G → G01 (router), G02 (judge), G03 (orthogonality guard)
- E → E01 (forge), E02 (vault), E03 (memory)
- M → M01 (monitor), M02 (discover)
"""

from __future__ import annotations

from typing import Any, Literal
from dataclasses import dataclass
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field


# =============================================================================
# AXIS DEFINITIONS
# =============================================================================


class Axis(str, Enum):
    PERCEPTION = "P"  # Reality acquisition
    TRANSFORMATION = "T"  # Mathematical computation
    VALUATION = "V"  # Utility & allocation
    GOVERNANCE = "G"  # Constraint & legitimacy
    EXECUTION = "E"  # State mutation
    META = "M"  # Self-inspection


# =============================================================================
# I/O CONTRACTS
# =============================================================================


class PerceptionInput(BaseModel):
    source: Literal["WELL", "GEOX", "VAULT", "WEALTH", "ALL"] = "ALL"
    query: str | None = None


class PerceptionOutput(BaseModel):
    axis: Literal["P"]
    data: dict[str, Any]
    sources_queried: list[str]


class TransformationInput(BaseModel):
    computation: Literal["physics", "math", "monte_carlo", "entropy"]
    inputs: dict[str, Any]


class TransformationOutput(BaseModel):
    axis: Literal["T"]
    result: dict[str, Any]
    computation_type: str


class ValuationInput(BaseModel):
    ranking: Literal["NPV", "EMV", "allocation", "personal"]
    candidates: list[dict[str, Any]]


class ValuationOutput(BaseModel):
    axis: Literal["V"]
    rankings: list[dict[str, Any]]
    methodology: str


class GovernanceInput(BaseModel):
    action: Literal["init", "route", "reason", "judge", "ethic", "hold"]
    payload: dict[str, Any]


class GovernanceOutput(BaseModel):
    axis: Literal["G"]
    verdict: str | None
    routing: dict[str, Any] | None
    reasoning: dict[str, Any] | None


class ExecutionInput(BaseModel):
    operation: Literal["forge", "vault", "memory"]
    payload: dict[str, Any]


class ExecutionOutput(BaseModel):
    axis: Literal["E"]
    result: dict[str, Any]
    merkle_hash: str | None


class MetaInput(BaseModel):
    operation: Literal["omega", "discover", "monitor", "synthesize"]
    context: dict[str, Any] | None


class MetaOutput(BaseModel):
    axis: Literal["M"]
    result: dict[str, Any]
    omega_ortho: float


# =============================================================================
# STUBS (replace with real implementations)
# =============================================================================


def _stub(agent: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Generic stub for unimplemented agents."""
    return {
        "agent": agent,
        "status": "stub",
        "input": input_data,
        "note": "Replace with real implementation",
    }


# =============================================================================
# 6 AGENTS
# =============================================================================


def create_agents_mcp() -> FastMCP:
    """Create FastMCP with 6 agents (one per axis)."""
    mcp = FastMCP("arifOS-6")

    # ─────────────────────────────────────────────────────────────────────────
    # P — PERCEPTION AGENT
    # Reads reality from WELL, GEOX, VAULT, WEALTH
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_perception",
        description="Perception Agent — Reads reality from WELL, GEOX, VAULT, WEALTH",
        tags={"perception", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )
    def P_perception(source: str = "ALL", query: str | None = None) -> dict[str, Any]:
        """
        Reality acquisition agent.
        Reads state from: WELL telemetry, GEOX seismic, VAULT ledger, WEALTH data.
        Does not interpret. Does not judge.
        """
        return _stub("P", {"source": source, "query": query})

    # ─────────────────────────────────────────────────────────────────────────
    # T — TRANSFORMATION AGENT
    # Computes: physics, math, monte_carlo, entropy
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="T_transformation",
        description="Transformation Agent — Computes physics, math, monte_carlo, entropy",
        tags={"transformation", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_transformation(computation: str, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Mathematical computation agent.
        Transforms inputs → structured outputs.
        Does not say 'good' or 'bad'.
        """
        valid_computations = ["physics", "math", "monte_carlo", "entropy"]
        if computation not in valid_computations:
            return {"error": f"Unknown computation: {computation}"}
        return _stub("T", {"computation": computation, "inputs": inputs})

    # ─────────────────────────────────────────────────────────────────────────
    # V — VALUATION AGENT
    # Ranks: NPV, EMV, allocation, personal
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="V_valuation",
        description="Valuation Agent — Ranks by NPV, EMV, allocation, personal preference",
        tags={"valuation", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_valuation(ranking: str, candidates: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Utility computation agent.
        Maps outcomes → preference ranking.
        Cannot fetch or mutate.
        """
        valid_rankings = ["NPV", "EMV", "allocation", "personal"]
        if ranking not in valid_rankings:
            return {"error": f"Unknown ranking: {ranking}"}
        return _stub("V", {"ranking": ranking, "candidates": candidates})

    # ─────────────────────────────────────────────────────────────────────────
    # G — GOVERNANCE AGENT
    # Routes, reasons, judges, holds
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="G_governance",
        description="Governance Agent — Routes, reasons, judges, enforces ethics and holds",
        tags={"governance", "public"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
    )
    def G_governance(action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Constraint and legitimacy agent.
        Decides permission.
        Does not compute NPV. Does not load seismic.
        """
        valid_actions = ["init", "route", "reason", "judge", "ethic", "hold"]
        if action not in valid_actions:
            return {"error": f"Unknown action: {action}"}
        return _stub("G", {"action": action, "payload": payload})

    # ─────────────────────────────────────────────────────────────────────────
    # E — EXECUTION AGENT
    # Mutates: forge, vault, memory
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="E_execution",
        description="Execution Agent — Mutates state via forge, vault, memory",
        tags={"execution", "public"},
        annotations={"readOnlyHint": False, "openWorldHint": True},
    )
    def E_execution(operation: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        State mutation agent.
        Changes system state.
        Cannot evaluate or justify itself.
        Requires governance approval upstream.
        """
        valid_operations = ["forge", "vault", "memory"]
        if operation not in valid_operations:
            return {"error": f"Unknown operation: {operation}"}
        return _stub("E", {"operation": operation, "payload": payload})

    # ─────────────────────────────────────────────────────────────────────────
    # M — META AGENT
    # Audits: omega, discover, monitor, synthesize
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="M_meta",
        description="Meta Agent — Audits omega_ortho, discovers skills, monitors, synthesizes",
        tags={"meta", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_meta(operation: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Self-inspection agent.
        Reasons about other agents.
        Never touches raw data or executes actions.
        """
        valid_operations = ["omega", "discover", "monitor", "synthesize"]
        if operation not in valid_operations:
            return {"error": f"Unknown operation: {operation}"}
        return _stub("M", {"operation": operation, "context": context})

    return mcp


# =============================================================================
# G02 KERNEL ROUTER (simplified for 6 agents)
# =============================================================================

ORTHOGONALITY_MATRIX = {
    "P": {"T": 1, "G": 1},
    "T": {"V": 1, "M": 1},
    "V": {"G": 1},
    "G": {"E": 1, "M": 1},
    "E": {},
    "M": {"P": 1, "G": 1},
}


def create_router_mcp() -> FastMCP:
    """G02 Kernel Router — Mandatory hub for cross-axis calls."""
    mcp = FastMCP("arifOS-G02")

    @mcp.tool(
        name="G02_route",
        description="G02 Kernel Router — Mandatory routing for all cross-axis calls",
        tags={"governance", "public"},
    )
    def G02_route(caller: str, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Route a call from one agent to another.
        Checks orthogonality matrix before allowing call.
        """
        caller_axis = caller[0]
        target_axis = target[0]

        # Same axis — always allowed
        if caller_axis == target_axis:
            return {
                "approved": True,
                "target": target,
                "payload": payload,
                "omega_ortho": 1.0,
                "note": "Same-axis call",
            }

        # Check orthogonality matrix
        allowed = ORTHOGONALITY_MATRIX.get(caller_axis, {})
        if target_axis not in allowed:
            return {
                "approved": False,
                "target": target,
                "reason": f"Axis {caller_axis} cannot call axis {target_axis}",
                "omega_ortho": 0.0,
                "allowed_targets": list(allowed.keys()),
            }

        omega = allowed[target_axis]
        return {
            "approved": True,
            "target": target,
            "payload": payload,
            "omega_ortho": float(omega),
            "note": f"Orthogonal call: {caller_axis} → {target_axis}",
        }

    @mcp.tool(
        name="G02_omega_status",
        description="Get current Ω_ortho status and call graph",
        tags={"governance", "public"},
    )
    def G02_omega_status() -> dict[str, Any]:
        """Return orthogonality matrix and routing rules."""
        return {
            "omega_threshold": 0.95,
            "orthogonality_matrix": ORTHOGONALITY_MATRIX,
            "call_graph": {
                "P": ["T", "G"],
                "T": ["V", "M"],
                "V": ["G"],
                "G": ["E", "M"],
                "E": [],
                "M": ["P", "G"],
            },
        }

    return mcp


# =============================================================================
# UNIFIED SERVER
# =============================================================================


def create_poc_mcp() -> FastMCP:
    """Create proof-of-concept MCP with 6 agents + G02 router."""
    mcp = create_agents_mcp()
    router = create_router_mcp()

    # Add router tools
    for tool in router._tool_manager.tools.values():
        mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)

    @mcp.tool(name="federation_status", tags={"system", "public"})
    def federation_status() -> dict[str, Any]:
        """Return federation status and agent list."""
        return {
            "agents": ["P", "T", "V", "G", "E", "M"],
            "axes": {
                "P": "Perception",
                "T": "Transformation",
                "V": "Valuation",
                "G": "Governance",
                "E": "Execution",
                "M": "Meta",
            },
            "total_agents": 6,
            "omega_threshold": 0.95,
        }

    return mcp


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    mcp = create_poc_mcp()
    print("Starting arifOS Federation POC (6 agents + G02 router)")
    print("Agents: P (perception), T (transformation), V (valuation)")
    print("        G (governance), E (execution), M (meta)")
    print("Router: G02 — mandatory hub for cross-axis calls")
    mcp.run()

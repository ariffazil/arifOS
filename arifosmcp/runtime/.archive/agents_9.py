"""
arifOS Federation — Production 9-Agent Architecture
====================================================
9 agents. Axes expanded where epistemically necessary.

Production expansion from 6:
- P → P01 (WELL reader), P02 (GEOX reader)
- T → T01 (physics), T02 (math)
- V → V01 (economic), V02 (allocation)
- G → G01 (init/router), G02 (judge), G03 (orthogonality guard)
- E → E01 (forge), E02 (vault), E03 (memory)
- M → M01 (monitor), M02 (discover)

Axes stay clean. Witness separation preserved.
"""

from __future__ import annotations

from typing import Any, Literal
from dataclasses import dataclass
from enum import Enum

from fastmcp import FastMCP
from pydantic import BaseModel, Field


import os
from .memory_engine import MemoryEngine

# Global Memory Engine instance
memory_engine = MemoryEngine(
    postgres_url=os.getenv("ARIFOS_VAULT_URL", os.getenv("DATABASE_URL")),
    qdrant_url=os.getenv("QDRANT_URL", "http://qdrant:6333"),
    ollama_url=os.getenv("OLLAMA_EMBEDDING_URL", "http://A-FORGE-ollama:11434"),
    embedding_model=os.getenv("EMBEDDING_MODEL", "bge-m3")
)

# =============================================================================
# AXIS DEFINITIONS
# =============================================================================


class Axis(str, Enum):
    PERCEPTION = "P"
    TRANSFORMATION = "T"
    VALUATION = "V"
    GOVERNANCE = "G"
    EXECUTION = "E"
    META = "M"


# =============================================================================
# I/O CONTRACTS
# =============================================================================


class P01_WELLInput(BaseModel):
    action: Literal["state", "readiness", "floor_scan", "log"]


class P01_WELLOutput(BaseModel):
    agent: Literal["P01"]
    data: dict[str, Any]


class P02_GEOXInput(BaseModel):
    action: Literal["scene", "prospect", "stoiip", "skills"]
    params: dict[str, Any]


class P02_GEOXOutput(BaseModel):
    agent: Literal["P02"]
    data: dict[str, Any]


class T01_PhysicsInput(BaseModel):
    computation: Literal["petrophysics", "stratigraphy", "geometry", "timing"]
    params: dict[str, Any]


class T01_PhysicsOutput(BaseModel):
    agent: Literal["T01"]
    result: dict[str, Any]


class T02_MathInput(BaseModel):
    computation: Literal["irr", "monte_carlo", "entropy", "growth"]
    params: dict[str, Any]


class T02_MathOutput(BaseModel):
    agent: Literal["T02"]
    result: dict[str, Any]


class V01_EconomicInput(BaseModel):
    method: Literal["NPV", "EMV", "DSCR", "payback"]
    cashflows: list[float]
    params: dict[str, Any]


class V01_EconomicOutput(BaseModel):
    agent: Literal["V01"]
    value: float
    methodology: str


class V02_AllocationInput(BaseModel):
    candidates: list[dict[str, Any]]
    constraints: dict[str, Any]


class V02_AllocationOutput(BaseModel):
    agent: Literal["V02"]
    rankings: list[dict[str, Any]]


class G01_RouterInput(BaseModel):
    caller: str
    target: str
    payload: dict[str, Any]


class G01_RouterOutput(BaseModel):
    approved: bool
    target: str
    omega_ortho: float
    reason: str


class G02_JudgeInput(BaseModel):
    candidate_action: dict[str, Any]
    dry_run: bool = False


class G02_JudgeOutput(BaseModel):
    agent: Literal["G02"]
    verdict: Literal["SEAL", "PARTIAL", "VOID", "HOLD"]
    floor_results: dict[str, Any]


class G03_OrthogonalityInput(BaseModel):
    tool_outputs: list[Any]
    model_traces: list[Any]


class G03_OrthogonalityOutput(BaseModel):
    agent: Literal["G03"]
    omega_ortho: float
    verdict: Literal["PASS", "HOLD", "VOID"]


class E01_ForgeInput(BaseModel):
    plan: dict[str, Any]
    verdict: str


class E01_ForgeOutput(BaseModel):
    agent: Literal["E01"]
    manifest: dict[str, Any]
    receipt: dict[str, Any]


class E02_VaultInput(BaseModel):
    operation: Literal["seal", "read", "anchor"]
    record: dict[str, Any]


class E02_VaultOutput(BaseModel):
    agent: Literal["E02"]
    merkle_hash: str
    seal_id: str


class E03_MemoryInput(BaseModel):
    operation: Literal["store", "retrieve", "forget"]
    memory: dict[str, Any]
    tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"]


class E03_MemoryOutput(BaseModel):
    agent: Literal["E03"]
    result: dict[str, Any]


class M01_MonitorInput(BaseModel):
    metrics: list[str] = ["floors", "omega", "entropy"]


class M01_MonitorOutput(BaseModel):
    agent: Literal["M01"]
    floors: dict[str, Any]
    thermodynamics: dict[str, float]


class M02_DiscoverInput(BaseModel):
    query: str
    domain: str | None = None


class M02_DiscoverOutput(BaseModel):
    agent: Literal["M02"]
    skills: list[dict[str, Any]]


# =============================================================================
# STUBS
# =============================================================================


def _stub(agent: str, data: dict[str, Any]) -> dict[str, Any]:
    return {"agent": agent, "status": "stub", "data": data}


# =============================================================================
# 9 AGENTS
# =============================================================================


def create_agents_mcp() -> FastMCP:
    """Create FastMCP with 9 production agents."""
    mcp = FastMCP("arifOS-9")

    # ─────────────────────────────────────────────────────────────────────────
    # P01 — WELL PERCEPTION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="P01_WELL",
        description="WELL Perception — Read biological telemetry and readiness",
        tags={"perception", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P01_WELL(action: str) -> dict[str, Any]:
        """WELL telemetry reader."""
        return _stub("P01", {"action": action})

    # ─────────────────────────────────────────────────────────────────────────
    # P02 — GEOX PERCEPTION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="P02_GEOX",
        description="GEOX Perception — Read seismic, prospect, skills",
        tags={"perception", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P02_GEOX(action: str, params: dict[str, Any]) -> dict[str, Any]:
        """GEOX data reader."""
        return _stub("P02", {"action": action, "params": params})

    # ─────────────────────────────────────────────────────────────────────────
    # T01 — PHYSICS TRANSFORMATION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="T01_physics",
        description="Physics Transformation — Petrophysics, stratigraphy, geometry",
        tags={"transformation", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T01_physics(computation: str, params: dict[str, Any]) -> dict[str, Any]:
        """Physics computation."""
        return _stub("T01", {"computation": computation, "params": params})

    # ─────────────────────────────────────────────────────────────────────────
    # T02 — MATH TRANSFORMATION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="T02_math",
        description="Math Transformation — IRR, monte_carlo, entropy, growth",
        tags={"transformation", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T02_math(computation: str, params: dict[str, Any]) -> dict[str, Any]:
        """Mathematical computation."""
        return _stub("T02", {"computation": computation, "params": params})

    # ─────────────────────────────────────────────────────────────────────────
    # V01 — ECONOMIC VALUATION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="V01_economic",
        description="Economic Valuation — NPV, EMV, DSCR, payback",
        tags={"valuation", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V01_economic(method: str, cashflows: list[float], params: dict[str, Any]) -> dict[str, Any]:
        """Economic valuation."""
        return _stub("V01", {"method": method, "cashflows": cashflows, "params": params})

    # ─────────────────────────────────────────────────────────────────────────
    # V02 — ALLOCATION VALUATION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="V02_allocation",
        description="Allocation Valuation — Rank candidates under constraints",
        tags={"valuation", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V02_allocation(
        candidates: list[dict[str, Any]], constraints: dict[str, Any]
    ) -> dict[str, Any]:
        """Allocation ranking."""
        return _stub("V02", {"candidates": candidates, "constraints": constraints})

    # ─────────────────────────────────────────────────────────────────────────
    # G01 — ROUTER
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="G01_router",
        description="G01 Router — Mandatory hub for cross-axis calls",
        tags={"governance", "public"},
    )
    def G01_router(caller: str, target: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Kernel router."""
        ORTHOGONALITY = {
            "P01": ["T01", "T02", "G01", "G02"],
            "P02": ["T01", "T02", "G01", "G02"],
            "T01": ["V01", "V02", "M01", "M02"],
            "T02": ["V01", "V02", "M01", "M02"],
            "V01": ["G01", "G02"],
            "V02": ["G01", "G02"],
            "G01": ["E01", "E02", "E03", "M01", "M02"],
            "G02": ["E01", "E02", "E03", "M01", "M02"],
            "E01": [],
            "E02": [],
            "E03": [],
            "M01": ["P01", "P02", "G01", "G02"],
            "M02": ["P01", "P02", "G01", "G02"],
        }
        allowed = ORTHOGONALITY.get(caller, [])
        if target not in allowed and target[0] == caller[0]:
            return {"approved": True, "target": target, "omega_ortho": 1.0, "reason": "same-axis"}
        if target not in allowed:
            return {
                "approved": False,
                "target": target,
                "omega_ortho": 0.0,
                "reason": f"not allowed: {allowed}",
            }
        return {"approved": True, "target": target, "omega_ortho": 1.0, "reason": "orthogonal"}

    # ─────────────────────────────────────────────────────────────────────────
    # G02 — JUDGE
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="G02_judge",
        description="G02 Judge — Constitutional verdict (SEAL/PARTIAL/VOID/HOLD)",
        tags={"governance", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G02_judge(candidate_action: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
        """Constitutional judgment."""
        return _stub("G02", {"candidate_action": candidate_action, "dry_run": dry_run})

    # ─────────────────────────────────────────────────────────────────────────
    # G03 — ORTHOGONALITY GUARD
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="G03_orthogonality",
        description="G03 Orthogonality Guard — Enforce Ω_ortho >= 0.95",
        tags={"governance", "public"},
    )
    def G03_orthogonality(tool_outputs: list[Any], model_traces: list[Any]) -> dict[str, Any]:
        """Ω_ortho enforcement."""
        return _stub("G03", {"tool_outputs": len(tool_outputs), "model_traces": len(model_traces)})

    # ─────────────────────────────────────────────────────────────────────────
    # E01 — FORGE EXECUTION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="E01_forge",
        description="E01 Forge — Execution manifest and dispatch",
        tags={"execution", "public"},
        annotations={"readOnlyHint": False, "openWorldHint": True},
    )
    def E01_forge(plan: dict[str, Any], verdict: str) -> dict[str, Any]:
        """Forge execution."""
        return _stub("E01", {"plan": plan, "verdict": verdict})

    # ─────────────────────────────────────────────────────────────────────────
    # E02 — VAULT EXECUTION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="E02_vault",
        description="E02 Vault — Merkle-hashed ledger append",
        tags={"execution", "public"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
    )
    def E02_vault(operation: str, record: dict[str, Any]) -> dict[str, Any]:
        """Vault operations."""
        return _stub("E02", {"operation": operation, "record": record})

    # ─────────────────────────────────────────────────────────────────────────
    # E03 — MEMORY EXECUTION
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="E03_memory",
        description="E03 Memory — MemoryContract store/retrieve/forget (5-tier governed)",
        tags={"execution", "public"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
    )
    async def E03_memory(operation: str, memory: dict, tier: str) -> dict:
        """Memory operations via MemoryEngine."""
        try:
            result = await memory_engine.execute(operation, memory, tier)
            return {"agent": "E03", "result": result}
        except Exception as e:
            return {"agent": "E03", "result": {"status": "error", "message": str(e)}}

    # ─────────────────────────────────────────────────────────────────────────
    # M01 — MONITOR
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="M01_monitor",
        description="M01 Monitor — Real-time F1-F13 + ΔS + Ω₀ dashboard",
        tags={"meta", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M01_monitor(metrics: list[str]) -> dict[str, Any]:
        """System monitoring."""
        return _stub("M01", {"metrics": metrics})

    # ─────────────────────────────────────────────────────────────────────────
    # M02 — DISCOVER
    # ─────────────────────────────────────────────────────────────────────────
    @mcp.tool(
        name="M02_discover",
        description="M02 Discover — Skill registry and dependency mapping",
        tags={"meta", "public"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M02_discover(query: str, domain: str | None = None) -> dict[str, Any]:
        """Skill discovery."""
        return _stub("M02", {"query": query, "domain": domain})

    return mcp


# =============================================================================
# ORTHOGONALITY MATRIX (for reference)
# =============================================================================

ORTHOGONALITY_RULES = """
Production 9-Agent Orthogonality Matrix
=======================================

Axis Separation:
- P01 (WELL) and P02 (GEOX) are epistemically different witnesses
- T01 (physics) and T02 (math) are different computation types
- V01 (economic) and V02 (allocation) are different ranking methods
- G01 (router), G02 (judge), G03 (orthogonality) are different governance functions

Cross-Axis Call Graph:
  P01, P02 → T01, T02, G01, G02    (Perception can call Transformation and Governance)
  T01, T02 → V01, V02, M01, M02    (Transformation can call Valuation and Meta)
  V01, V02 → G01, G02               (Valuation can call Governance)
  G01, G02, G03 → E01, E02, E03, M01, M02  (Governance can call Execution and Meta)
  E01, E02, E03 → ∅                 (Execution cannot call anyone)
  M01, M02 → P01, P02, G01, G02     (Meta can call Perception and Governance)

Ω_ortho threshold: >= 0.95
"""


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    mcp = create_agents_mcp()
    print("Starting arifOS Federation Production (9 agents)")
    print("Agents: P01 (WELL), P02 (GEOX)")
    print("        T01 (physics), T02 (math)")
    print("        V01 (economic), V02 (allocation)")
    print("        G01 (router), G02 (judge), G03 (orthogonality)")
    print("        E01 (forge), E02 (vault), E03 (memory)")
    print("        M01 (monitor), M02 (discover)")
    mcp.run()

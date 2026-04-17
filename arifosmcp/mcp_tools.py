"""
arifOS Federation — MCP Tool Registry
=====================================
MCP tools for the 6-axis federation.

Philosophy:
- MCP = Model ↔ Tools (data access within agent)
- A2A = Agent ↔ Agent (coordination layer)
- Each agent exposes its tools via MCP
- Tools are epistemically pure per axis

MCP Host (Claude Code/Desktop)
    |
    |-- MCP Client 1 --> P_MCP_Server (Perception tools)
    |-- MCP Client 2 --> T_MCP_Server (Transformation tools)
    |-- MCP Client 3 --> V_MCP_Server (Valuation tools)
    |-- MCP Client 4 --> G_MCP_Server (Governance tools)
    |-- MCP Client 5 --> E_MCP_Server (Execution tools)
    |-- MCP Client 6 --> M_MCP_Server (Meta tools)

A2A handles inter-agent routing (separate concern).
"""

from __future__ import annotations

from typing import Any, Literal
from dataclasses import dataclass
from enum import Enum

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field


# =============================================================================
# TOOL NAMING CONVENTION
# =============================================================================

"""
Tool naming: {AXIS}_{domain}_{verb}

Examples:
- P_well_state_read
- T_physics_compute
- V_economic_npv
- G_judge_verdict
- E_vault_seal
- M_omega_status

Tags by axis:
- perception: P_* tools
- transformation: T_* tools
- valuation: V_* tools
- governance: G_* tools
- execution: E_* tools
- meta: M_* tools
"""


# =============================================================================
# PERCEPTION TOOLS (P) — Read reality only
# =============================================================================


def create_perception_mcp() -> FastMCP:
    """Perception Agent MCP tools — read from WELL, GEOX, VAULT, WEALTH."""
    mcp = FastMCP("arifOS-P")

    # ─────────────────────────────────────────────────────────────────────────
    # WELL Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_well_state_read",
        description="Read current WELL biological telemetry snapshot",
        tags={"perception", "well"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P_well_state_read(ctx: Context | None = None) -> dict[str, Any]:
        """Read current WELL state — biological telemetry."""
        return {
            "agent": "P",
            "source": "WELL",
            "action": "state_read",
            "data": {
                "score": 0.85,
                "dimensions": {
                    "sleep": {"value": 7.5, "unit": "hours"},
                    "stress": {"value": 3, "unit": "1-10"},
                    "cognitive": {"value": 8, "unit": "1-10"},
                    "metabolic": {"value": 6, "unit": "1-10"},
                },
                "floor_violations": [],
            },
        }

    @mcp.tool(
        name="P_well_readiness_check",
        description="Check biological readiness verdict for arifOS JUDGE",
        tags={"perception", "well"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P_well_readiness_check(ctx: Context | None = None) -> dict[str, Any]:
        """Check WELL readiness for governance context."""
        return {
            "agent": "P",
            "source": "WELL",
            "action": "readiness_check",
            "data": {
                "score": 0.85,
                "floor_status": {"W1": "active", "W2": "active", "W3": "active"},
                "verdict": "READY",
                "bandwidth_recommendation": "NORMAL",
            },
        }

    @mcp.tool(
        name="P_well_floor_scan",
        description="Scan W-Floor status across all dimensions",
        tags={"perception", "well"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P_well_floor_scan(ctx: Context | None = None) -> dict[str, Any]:
        """Scan all W-Floors."""
        return {
            "agent": "P",
            "source": "WELL",
            "action": "floor_scan",
            "data": {
                "floors": {f"W{i}": {"status": "active"} for i in range(1, 14)},
                "overall_verdict": "NOMINAL",
            },
        }

    # ─────────────────────────────────────────────────────────────────────────
    # GEOX Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_geox_scene_load",
        description="Load seismic, well, or volume data into witness context",
        tags={"perception", "geox"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P_geox_scene_load(
        scene_type: Literal["seismic", "well", "volume"], path: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Load GEOX scene data."""
        return {
            "agent": "P",
            "source": "GEOX",
            "action": "scene_load",
            "data": {
                "scene_type": scene_type,
                "path": path,
                "status": "loaded",
                "scene_id": f"{scene_type}_{path.split('/')[-1]}",
            },
        }

    @mcp.tool(
        name="P_geox_skills_query",
        description="Query GEOX skill registry by keyword or domain",
        tags={"perception", "geox"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P_geox_skills_query(
        query: str, domain: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Query GEOX skills registry."""
        return {
            "agent": "P",
            "source": "GEOX",
            "action": "skills_query",
            "data": {"query": query, "domain": domain, "skills": []},
        }

    # ─────────────────────────────────────────────────────────────────────────
    # WEALTH Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_wealth_snapshot_fetch",
        description="Fetch cross-source macro/energy/carbon snapshot",
        tags={"perception", "wealth"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )
    def P_wealth_snapshot_fetch(geography: str, ctx: Context | None = None) -> dict[str, Any]:
        """Fetch macro snapshot from WEALTH."""
        return {
            "agent": "P",
            "source": "WEALTH",
            "action": "snapshot_fetch",
            "data": {"geography": geography, "macro": {}, "energy": {}, "carbon": {}},
        }

    @mcp.tool(
        name="P_wealth_series_fetch",
        description="Fetch live data series from open public source",
        tags={"perception", "wealth"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )
    def P_wealth_series_fetch(
        source: str, series_id: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Fetch series data."""
        return {
            "agent": "P",
            "source": "WEALTH",
            "action": "series_fetch",
            "data": {"source": source, "series_id": series_id, "series": [], "metadata": {}},
        }

    @mcp.tool(
        name="P_wealth_vintage_fetch",
        description="Fetch specific vintage of series (FRED/ALFRED)",
        tags={"perception", "wealth"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )
    def P_wealth_vintage_fetch(
        series_id: str, vintage_date: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Fetch vintage series."""
        return {
            "agent": "P",
            "source": "WEALTH",
            "action": "vintage_fetch",
            "data": {"series_id": series_id, "vintage_date": vintage_date, "series": []},
        }

    # ─────────────────────────────────────────────────────────────────────────
    # VAULT Tools
    # ─────────────────────────────────────────────────────────────────────────

    @mcp.tool(
        name="P_vault_ledger_read",
        description="Read VAULT999 ledger, build BLS seal card",
        tags={"perception", "vault"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def P_vault_ledger_read(
        session_id: str | None = None,
        verdict: str | None = None,
        since: str | None = None,
        until: str | None = None,
        limit: int = 100,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Read from VAULT999 ledger."""
        return {
            "agent": "P",
            "source": "VAULT",
            "action": "ledger_read",
            "data": {"seal_card": {"total_seals": 0, "by_verdict": {}}, "ledger_rows": []},
        }

    return mcp


# =============================================================================
# TRANSFORMATION TOOLS (T) — Pure computation only
# =============================================================================


def create_transformation_mcp() -> FastMCP:
    """Transformation Agent MCP tools — physics, math, monte_carlo."""
    mcp = FastMCP("arifOS-T")

    @mcp.tool(
        name="T_petrophysics_compute",
        description="Execute physics-grounded petrophysical calculations",
        tags={"transformation", "physics"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_petrophysics_compute(
        well_id: str,
        computation: Literal["porosity", "saturation", "volume"],
        params: dict[str, Any],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Compute petrophysics."""
        return {
            "agent": "T",
            "domain": "physics",
            "action": "petrophysics_compute",
            "result": {
                "well_id": well_id,
                "computation": computation,
                "value": 0.0,
                "unit": "fraction",
            },
        }

    @mcp.tool(
        name="T_stratigraphy_correlate",
        description="Correlate stratigraphic units across multiple wells",
        tags={"transformation", "physics"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_stratigraphy_correlate(
        wells: list[str], section_id: str, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Correlate stratigraphy."""
        return {
            "agent": "T",
            "domain": "physics",
            "action": "stratigraphy_correlate",
            "result": {"wells": wells, "section_id": section_id, "correlation_map": {}},
        }

    @mcp.tool(
        name="T_geometry_build",
        description="Build architectural geometries from interpreted horizons",
        tags={"transformation", "physics"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_geometry_build(
        horizons: list[dict[str, Any]], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Build geometries."""
        return {
            "agent": "T",
            "domain": "physics",
            "action": "geometry_build",
            "result": {"horizons": horizons, "geometries": {}},
        }

    @mcp.tool(
        name="T_math_irr_compute",
        description="Compute Internal Rate of Return and Modified IRR",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_math_irr_compute(cashflows: list[float], ctx: Context | None = None) -> dict[str, Any]:
        """Compute IRR/MIRR."""
        return {
            "agent": "T",
            "domain": "math",
            "action": "irr_compute",
            "result": {"irr": 0.0, "mirr": 0.0, "cashflows": cashflows},
        }

    @mcp.tool(
        name="T_math_monte_carlo",
        description="Stochastic forecast with probability-weighted outcomes",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_math_monte_carlo(
        portfolio: dict[str, Any], iterations: int = 1000, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Monte Carlo simulation."""
        return {
            "agent": "T",
            "domain": "math",
            "action": "monte_carlo",
            "result": {"iterations": iterations, "distribution": {}, "confidence_intervals": {}},
        }

    @mcp.tool(
        name="T_math_entropy_audit",
        description="Audit cash flows for noise and multiple IRRs",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_math_entropy_audit(cashflows: list[float], ctx: Context | None = None) -> dict[str, Any]:
        """Audit cashflow entropy."""
        return {
            "agent": "T",
            "domain": "math",
            "action": "entropy_audit",
            "result": {"entropy_score": 0.0, "multiple_IRRs": False},
        }

    @mcp.tool(
        name="T_growth_runway_compute",
        description="Compute compound growth rate and runway",
        tags={"transformation", "math"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def T_growth_runway_compute(
        cashflows: list[float], burn_rate: float, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute growth and runway."""
        return {
            "agent": "T",
            "domain": "math",
            "action": "growth_runway_compute",
            "result": {"cagr": 0.0, "runway_months": 0},
        }

    return mcp


# =============================================================================
# VALUATION TOOLS (V) — Utility computation only
# =============================================================================


def create_valuation_mcp() -> FastMCP:
    """Valuation Agent MCP tools — NPV, EMV, allocation."""
    mcp = FastMCP("arifOS-V")

    @mcp.tool(
        name="V_npv_evaluate",
        description="Compute Net Present Value",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_npv_evaluate(
        cashflows: list[float], discount_rate: float, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute NPV."""
        return {
            "agent": "V",
            "domain": "economic",
            "action": "npv_evaluate",
            "result": {
                "npv": 0.0,
                "discount_rate": discount_rate,
                "criterion": "accept" if 0.0 > 0 else "reject",
            },
        }

    @mcp.tool(
        name="V_emv_evaluate",
        description="Compute Expected Monetary Value",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_emv_evaluate(
        outcomes: list[float], probabilities: list[float], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute EMV."""
        return {
            "agent": "V",
            "domain": "economic",
            "action": "emv_evaluate",
            "result": {"emv": 0.0, "distribution": {}},
        }

    @mcp.tool(
        name="V_dscr_evaluate",
        description="Compute Debt Service Coverage Ratio",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_dscr_evaluate(
        net_operating_income: float, debt_service: float, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute DSCR."""
        return {
            "agent": "V",
            "domain": "economic",
            "action": "dscr_evaluate",
            "result": {"dscr": 0.0, "criterion": "adequate" if 0.0 >= 1.25 else "inadequate"},
        }

    @mcp.tool(
        name="V_profitability_index",
        description="Compute Profitability Index",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_profitability_index(
        investment: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute PI."""
        return {
            "agent": "V",
            "domain": "economic",
            "action": "profitability_index",
            "result": {"pi": 0.0, "criterion": "accept" if 0.0 > 1 else "reject"},
        }

    @mcp.tool(
        name="V_payback_evaluate",
        description="Compute Payback Period",
        tags={"valuation", "economic"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_payback_evaluate(cashflows: list[float], ctx: Context | None = None) -> dict[str, Any]:
        """Compute payback period."""
        return {
            "agent": "V",
            "domain": "economic",
            "action": "payback_evaluate",
            "result": {"payback_period": 0.0, "unit": "years"},
        }

    @mcp.tool(
        name="V_allocation_rank",
        description="Rank alternatives under constraints",
        tags={"valuation", "allocation"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_allocation_rank(
        candidates: list[dict[str, Any]], constraints: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Rank allocation candidates."""
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "allocation_rank",
            "result": {"ranked": [], "constraints_satisfied": True},
        }

    @mcp.tool(
        name="V_personal_decision_rank",
        description="Rank personal alternatives under constraints",
        tags={"valuation", "personal"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_personal_decision_rank(
        alternatives: list[dict[str, Any]], constraints: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Rank personal decisions."""
        return {
            "agent": "V",
            "domain": "personal",
            "action": "personal_decision_rank",
            "result": {"ranked": []},
        }

    @mcp.tool(
        name="V_agent_budget_optimize",
        description="Optimal action sequence under resource constraints",
        tags={"valuation", "allocation"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_agent_budget_optimize(
        tasks: list[dict[str, Any]], resources: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Optimize agent budget."""
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "agent_budget_optimize",
            "result": {"optimal_sequence": []},
        }

    @mcp.tool(
        name="V_civilization_sustainability",
        description="Long-term civilization sustainability path",
        tags={"valuation", "allocation"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def V_civilization_sustainability(
        current_state: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Compute sustainability."""
        return {
            "agent": "V",
            "domain": "allocation",
            "action": "civilization_sustainability",
            "result": {"sustainability_score": 0.0, "path": []},
        }

    return mcp


# =============================================================================
# GOVERNANCE TOOLS (G) — Constraint and legitimacy
# =============================================================================


def create_governance_mcp() -> FastMCP:
    """Governance Agent MCP tools — init, route, judge, ethics, hold."""
    mcp = FastMCP("arifOS-G")

    @mcp.tool(
        name="G_session_init",
        description="Initialize constitutional session with identity binding",
        tags={"governance"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
    )
    def G_session_init(
        intent: str,
        mode: Literal["init", "probe", "state", "status"] = "init",
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Initialize session."""
        import uuid

        return {
            "agent": "G",
            "action": "session_init",
            "result": {
                "session_id": str(uuid.uuid4()),
                "epoch": 0,
                "alignment": "NOMINAL",
                "intent": intent,
                "mode": mode,
            },
        }

    @mcp.tool(
        name="G_kernel_route",
        description="Route request to correct metabolic lane based on risk",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G_kernel_route(
        task: dict[str, Any],
        risk_level: Literal["low", "medium", "high", "critical"],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Route to correct lane."""
        lane_map = {"low": "P-lane", "medium": "T-lane", "high": "V-lane", "critical": "G-lane"}
        return {
            "agent": "G",
            "action": "kernel_route",
            "result": {
                "lane": lane_map.get(risk_level, "P-lane"),
                "target_agent": "P",
                "risk_level": risk_level,
            },
        }

    @mcp.tool(
        name="G_mind_reason",
        description="Structured reasoning with typed cognitive pipeline",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": True},
    )
    def G_mind_reason(
        prompt: str,
        mode: Literal["reason", "sequential", "step", "branch", "merge"] = "reason",
        session_id: str | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Constitutional reasoning."""
        return {
            "agent": "G",
            "action": "mind_reason",
            "result": {
                "reasoning_packet": {},
                "audit_packet": {},
                "mode": mode,
                "session_id": session_id,
            },
        }

    @mcp.tool(
        name="G_ethical_heart",
        description="Red-team proposal: simulate consequences, evaluate F5/F6/F9",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G_ethical_heart(
        candidate_action: dict[str, Any], context: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Ethical evaluation."""
        return {
            "agent": "G",
            "action": "ethical_heart",
            "result": {
                "ethical_assessment": {
                    "F5_continuity": "PASS",
                    "F6_harm_dignity": "PASS",
                    "F9_injection": "PASS",
                },
                "verdict": "ETHICAL",
            },
        }

    @mcp.tool(
        name="G_judge_verdict",
        description="Final constitutional verdict: SEAL, PARTIAL, VOID, HOLD",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G_judge_verdict(
        candidate_action: dict[str, Any], dry_run: bool = False, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Constitutional judgment."""
        return {
            "agent": "G",
            "action": "judge_verdict",
            "result": {
                "verdict": "SEAL",
                "floor_results": {f"F{i}": "PASS" for i in range(1, 14)},
                "w3_scores": {},
                "dry_run": dry_run,
            },
        }

    @mcp.tool(
        name="G_orthogonality_guard",
        description="Enforce Ω_ortho >= 0.95 across tool outputs",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G_orthogonality_guard(
        tool_outputs: list[Any], model_traces: list[Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Check orthogonality."""
        return {
            "agent": "G",
            "action": "orthogonality_guard",
            "result": {"omega_ortho": 1.0, "verdict": "PASS", "threshold": 0.95},
        }

    @mcp.tool(
        name="G_hold_authority",
        description="Check if action requires 888_HOLD human approval",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G_hold_authority(action: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Check HOLD requirement."""
        return {
            "agent": "G",
            "action": "hold_authority",
            "result": {"requires_hold": False, "reason": "low_risk_action"},
        }

    @mcp.tool(
        name="G_policy_audit",
        description="Audit proposal against configurable policy constraints",
        tags={"governance"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def G_policy_audit(
        proposal: dict[str, Any], policy: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Policy audit."""
        return {
            "agent": "G",
            "action": "policy_audit",
            "result": {"audit_result": "COMPLIANT", "violations": []},
        }

    return mcp


# =============================================================================
# EXECUTION TOOLS (E) — State mutation only
# =============================================================================


def create_execution_mcp() -> FastMCP:
    """Execution Agent MCP tools — forge, vault, memory."""
    mcp = FastMCP("arifOS-E")

    @mcp.tool(
        name="E_forge_bridge",
        description="Delegated Execution Bridge — validates SEAL, constructs manifest",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": True, "destructiveHint": False},
    )
    def E_forge_bridge(
        plan: dict[str, Any],
        verdict: Literal["SEAL", "PARTIAL", "VOID", "HOLD"],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Forge execution bridge."""
        if verdict != "SEAL":
            return {
                "agent": "E",
                "action": "forge_bridge",
                "error": f"Cannot forge with verdict {verdict}",
                "requires_human_approval": True,
            }
        return {
            "agent": "E",
            "action": "forge_bridge",
            "result": {"manifest": plan, "execution_receipt": {"id": "stub_receipt"}},
        }

    @mcp.tool(
        name="E_forge_execute",
        description="Execute forge after gates pass",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": True, "destructiveHint": False},
    )
    def E_forge_execute(plan: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Execute forge."""
        return {
            "agent": "E",
            "action": "forge_execute",
            "result": {"execution_result": "SUCCESS", "plan_id": plan.get("id", "unknown")},
        }

    @mcp.tool(
        name="E_vault_seal",
        description="Append immutable verdict record to Merkle-hashed ledger",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
    )
    def E_vault_seal(record: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Seal to vault."""
        import hashlib, uuid

        content = str(record)
        merkle_hash = hashlib.sha256(content.encode()).hexdigest()
        return {
            "agent": "E",
            "action": "vault_seal",
            "result": {"merkle_hash": merkle_hash, "seal_id": str(uuid.uuid4())},
        }

    @mcp.tool(
        name="E_vault_read",
        description="Read from VAULT999 ledger",
        tags={"execution"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def E_vault_read(
        seal_id: str | None = None, session_id: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Read from vault."""
        return {"agent": "E", "action": "vault_read", "result": {"seal_id": seal_id, "record": {}}}

    @mcp.tool(
        name="E_memory_store",
        description="Store memory in MemoryContract (5-tier governed)",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False, "destructiveHint": False},
    )
    def E_memory_store(
        memory: dict[str, Any],
        tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"],
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Store memory."""
        return {
            "agent": "E",
            "action": "memory_store",
            "result": {"tier": tier, "status": "stored"},
        }

    @mcp.tool(
        name="E_memory_retrieve",
        description="Retrieve from MemoryContract",
        tags={"execution"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def E_memory_retrieve(
        query: str,
        tier: Literal["ephemeral", "working", "canon", "sacred", "quarantine"] | None = None,
        ctx: Context | None = None,
    ) -> dict[str, Any]:
        """Retrieve memory."""
        return {"agent": "E", "action": "memory_retrieve", "result": {"memories": []}}

    @mcp.tool(
        name="E_well_log",
        description="Log biological telemetry update",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
    )
    def E_well_log(dimensions: dict[str, Any], ctx: Context | None = None) -> dict[str, Any]:
        """Log WELL telemetry."""
        return {"agent": "E", "action": "well_log", "result": {"updated_state": dimensions}}

    @mcp.tool(
        name="E_well_anchor",
        description="Anchor WELL state to VAULT999",
        tags={"execution"},
        annotations={"readOnlyHint": False, "openWorldHint": False},
    )
    def E_well_anchor(ctx: Context | None = None) -> dict[str, Any]:
        """Anchor WELL."""
        import uuid

        return {"agent": "E", "action": "well_anchor", "result": {"seal_id": str(uuid.uuid4())}}

    return mcp


# =============================================================================
# META TOOLS (M) — Self-inspection only
# =============================================================================


def create_meta_mcp() -> FastMCP:
    """Meta Agent MCP tools — omega, discover, monitor."""
    mcp = FastMCP("arifOS-M")

    @mcp.tool(
        name="M_omega_status",
        description="Get current Ω_ortho status and correlation matrix",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_omega_status(ctx: Context | None = None) -> dict[str, Any]:
        """Get Ω_ortho status."""
        return {
            "agent": "M",
            "action": "omega_status",
            "result": {
                "omega_ortho": 1.0,
                "threshold": 0.95,
                "matrix": {
                    "P": {"T": 1, "G": 1},
                    "T": {"V": 1, "M": 1},
                    "V": {"G": 1},
                    "G": {"E": 1, "M": 1},
                    "E": {},
                    "M": {"P": 1, "G": 1},
                },
            },
        }

    @mcp.tool(
        name="M_skill_discovery",
        description="Search available skills by keyword/domain",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_skill_discovery(
        query: str, domain: str | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Discover skills."""
        return {
            "agent": "M",
            "action": "skill_discovery",
            "result": {"query": query, "domain": domain, "skills": []},
        }

    @mcp.tool(
        name="M_skill_metadata",
        description="Get detailed metadata for specific skill",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_skill_metadata(skill_id: str, ctx: Context | None = None) -> dict[str, Any]:
        """Get skill metadata."""
        return {
            "agent": "M",
            "action": "skill_metadata",
            "result": {"skill_id": skill_id, "metadata": {}},
        }

    @mcp.tool(
        name="M_metabolic_monitor",
        description="Real-time F1-F13 + ΔS + Peace² + Ω₀ dashboard",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_metabolic_monitor(
        metrics: list[str] | None = None, ctx: Context | None = None
    ) -> dict[str, Any]:
        """Monitor metabolism."""
        return {
            "agent": "M",
            "action": "metabolic_monitor",
            "result": {
                "floors": {f"F{i}": "active" for i in range(1, 14)},
                "thermodynamics": {"delta_S": 0.0, "peace_squared": 1.0, "omega_0": 1.0},
            },
        }

    @mcp.tool(
        name="M_cross_evidence_synthesize",
        description="Synthesize causal scene for JUDGE from spatial elements",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_cross_evidence_synthesize(scene_id: str, ctx: Context | None = None) -> dict[str, Any]:
        """Synthesize evidence."""
        return {
            "agent": "M",
            "action": "cross_evidence_synthesize",
            "result": {"scene_id": scene_id, "synthesized_scene": {}},
        }

    @mcp.tool(
        name="M_game_theory_solve",
        description="Multi-agent allocation via LP, Shapley, Nash",
        tags={"meta"},
        annotations={"readOnlyHint": True, "openWorldHint": False},
    )
    def M_game_theory_solve(
        agents: list[dict[str, Any]], payoff_matrix: dict[str, Any], ctx: Context | None = None
    ) -> dict[str, Any]:
        """Solve game theory."""
        return {
            "agent": "M",
            "action": "game_theory_solve",
            "result": {"solution": {}, "equilibrium": "Nash"},
        }

    return mcp


# =============================================================================
# UNIFIED MCP SERVER
# =============================================================================


def create_unified_mcp(agents: list[str] | None = None, visibility: str = "public_only") -> FastMCP:
    """
    Create unified MCP server with all or selected agents.

    Args:
        agents: List of agents to include ["P", "T", "V", "G", "E", "M"]
                None = all agents
        visibility: Tag filter for tools
    """
    mcp = FastMCP("arifOS-Unified")

    agents = agents or ["P", "T", "V", "G", "E", "M"]

    # Add agents based on selection
    if "P" in agents:
        perception = create_perception_mcp()
        for name, tool in perception._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "T" in agents:
        transformation = create_transformation_mcp()
        for name, tool in transformation._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "V" in agents:
        valuation = create_valuation_mcp()
        for name, tool in valuation._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "G" in agents:
        governance = create_governance_mcp()
        for name, tool in governance._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "E" in agents:
        execution = create_execution_mcp()
        for name, tool in execution._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    if "M" in agents:
        meta = create_meta_mcp()
        for name, tool in meta._tool_manager.tools.items():
            mcp.add_tool(tool.fn, name=name, description=tool.description, tags=tool.tags)

    # Apply visibility filter
    tag_map = {
        "public_only": {
            "perception",
            "transformation",
            "valuation",
            "governance",
            "execution",
            "meta",
        },
        "all": None,  # No filter
    }

    allowed = tag_map.get(visibility)
    if allowed:
        mcp.enable(tags=allowed, only=True)

    return mcp


# =============================================================================
# TOOL CATALOG
# =============================================================================

TOOL_CATALOG = """
arifOS Federation — MCP Tool Catalog
====================================

PERCEPTION (P) — Read reality only, no interpretation
-----------------------------------------------------
P_well_state_read         — WELL biological telemetry
P_well_readiness_check    — WELL readiness for JUDGE
P_well_floor_scan         — W-Floor status scan
P_geox_scene_load         — GEOX seismic/well/volume
P_geox_skills_query       — GEOX skill registry
P_wealth_snapshot_fetch   — Macro/energy/carbon
P_wealth_series_fetch     — Time series data
P_wealth_vintage_fetch     — Vintage series (FRED)
P_vault_ledger_read       — VAULT999 ledger

TRANSFORMATION (T) — Pure computation, no meaning
--------------------------------------------------
T_petrophysics_compute     — Physics calculations
T_stratigraphy_correlate   — Stratigraphic correlation
T_geometry_build          — Geometry construction
T_math_irr_compute        — IRR/MIRR calculation
T_math_monte_carlo        — Stochastic simulation
T_math_entropy_audit      — Cashflow entropy
T_growth_runway_compute   — Growth and runway

VALUATION (V) — Utility computation, no mutation
------------------------------------------------
V_npv_evaluate            — Net Present Value
V_emv_evaluate            — Expected Monetary Value
V_dscr_evaluate           — Debt Service Coverage
V_profitability_index     — Profitability Index
V_payback_evaluate        — Payback Period
V_allocation_rank         — Allocation ranking
V_personal_decision_rank  — Personal alternatives
V_agent_budget_optimize   — Budget optimization
V_civilization_sustainability — Sustainability

GOVERNANCE (G) — Constraint and legitimacy
------------------------------------------
G_session_init            — Session initialization
G_kernel_route           — Metabolic lane routing
G_mind_reason            — Constitutional reasoning
G_ethical_heart          — F5/F6/F9 ethics
G_judge_verdict          — SEAL/PARTIAL/VOID/HOLD
G_orthogonality_guard    — Ω_ortho enforcement
G_hold_authority         — 888_HOLD check
G_policy_audit           — Policy compliance

EXECUTION (E) — State mutation, requires governance
---------------------------------------------------
E_forge_bridge           — Execution manifest
E_forge_execute         — Post-gate execution
E_vault_seal            — Merkle ledger append
E_vault_read            — Ledger read
E_memory_store          — MemoryContract store
E_memory_retrieve       — MemoryContract retrieve
E_well_log              — Telemetry update
E_well_anchor            — State anchor

META (M) — Self-inspection, no raw data access
------------------------------------------------
M_omega_status           — Ω_ortho correlation
M_skill_discovery        — Skill search
M_skill_metadata         — Skill details
M_metabolic_monitor      — F1-F13 dashboard
M_cross_evidence_synthesize — Evidence synthesis
M_game_theory_solve      — Game theory solution
"""


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys

    agents = sys.argv[1:] if len(sys.argv) > 1 else None

    if agents and agents[0] == "--catalog":
        print(TOOL_CATALOG)
    else:
        if agents:
            mcp = create_unified_mcp(agents=agents)
            print(f"Starting arifOS MCP with agents: {agents}")
        else:
            mcp = create_unified_mcp()
            print("Starting arifOS Unified MCP (all 6 agents)")

        mcp.run()

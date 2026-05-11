"""
arifosmcp/mcp_tools.py — 13-Tool Canonical Surface
==================================================
Hard cutover: 13 tools only. No P/T/V/E/M legacy registrations.
DITEMPA BUKAN DIBERI — Forged, Not Given

Constitutional (5)  : init, sense, mind, heart, judge  (registered via runtime/tools.py)
Infrastructure (3)  : kernel, memory, vault              (registered via runtime/tools.py)
Canonical Engines (5): compute_physics, compute_finance, compute_civilization, oracle_bio, oracle_world

MCP tool registrations via agent factory stubs + direct canonical engine registration.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

# Import canonical engines
try:
    from arifosmcp.tools_canonical import (
        arifos_compute_civilization,
        arifos_compute_finance,
        arifos_compute_physics,
        arifos_oracle_bio,
        arifos_oracle_world,
    )

    CANONICAL_AVAILABLE = True
except ImportError:
    CANONICAL_AVAILABLE = False


# =============================================================================
# PERCEPTION AGENT — oracle_bio (WELL state)
# =============================================================================


def create_perception_mcp() -> FastMCP:
    """Perception Agent MCP tools — arifos_oracle_bio for WELL state."""
    mcp = FastMCP("arifOS-P")

    if CANONICAL_AVAILABLE:

        @mcp.tool(
            name="arifos_oracle_bio",
            description="WELL state oracle: snapshot_read | readiness_check | floor_scan | log_update | deltascan (Proof-of-Friction gate: pass action_weight + kappa_r via dimensions)",
        )
        async def oracle_bio(
            mode: str,
            session_id: str | None = None,
            ctx: Any = None,
            dimensions: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            return await arifos_oracle_bio(
                mode=mode, session_id=session_id, ctx=ctx, dimensions=dimensions
            )

    return mcp


# =============================================================================
# TRANSFORMATION AGENT — compute_physics (petrophysics, stratigraphy, geometry, monte_carlo, entropy, growth)
# =============================================================================


def create_transformation_mcp() -> FastMCP:
    """Transformation Agent MCP tools — arifos_compute_physics for physics/math."""
    mcp = FastMCP("arifOS-T")

    if CANONICAL_AVAILABLE:

        @mcp.tool(
            name="arifos_compute_physics",
            description="Physics engine: petrophysics | stratigraphy_correlate | geometry_build | monte_carlo | entropy_audit | growth_runway",
        )
        async def compute_physics(
            mode: str,
            session_id: str | None = None,
            well_id: str | None = None,
            computation: str | None = None,
            params: dict[str, Any] | None = None,
            wells: list[str] | None = None,
            section_id: str | None = None,
            horizons: list[dict[str, Any]] | None = None,
            outcomes: list[float] | None = None,
            probabilities: list[float] | None = None,
            iterations: int = 1000,
            cashflows: list[float] | None = None,
            burn_rate: float | None = None,
            ctx: Any = None,
        ) -> dict[str, Any]:
            return await arifos_compute_physics(
                mode=mode,
                session_id=session_id,
                well_id=well_id,
                computation=computation,
                params=params,
                wells=wells,
                section_id=section_id,
                horizons=horizons,
                outcomes=outcomes,
                probabilities=probabilities,
                iterations=iterations,
                cashflows=cashflows,
                burn_rate=burn_rate,
                ctx=ctx,
            )

    return mcp


# =============================================================================
# VALUATION AGENT — compute_finance (npv, irr, dscr, emv, payback, etc.)
# =============================================================================


def create_valuation_mcp() -> FastMCP:
    """Valuation Agent MCP tools — arifos_compute_finance for finance/economic."""
    mcp = FastMCP("arifOS-V")

    if CANONICAL_AVAILABLE:

        @mcp.tool(
            name="arifos_compute_finance",
            description="Finance engine: npv | irr | mirr | emv | dscr | payback | profitability_index | allocation_rank | personal_decision_rank | budget_optimize | civilization_sustainability",
        )
        async def compute_finance(
            mode: str,
            session_id: str | None = None,
            initial_investment: float | None = None,
            cash_flows: list[float] | None = None,
            discount_rate: float = 0,
            terminal_value: float = 0,
            finance_rate: float = 0,
            reinvest_rate: float = 0,
            outcomes: list[float] | None = None,
            probabilities: list[float] | None = None,
            ebitda: float | None = None,
            debt_service: float | None = None,
            candidates: list[dict[str, Any]] | None = None,
            constraints: dict[str, Any] | None = None,
            alternatives: list[dict[str, Any]] | None = None,
            tasks: list[dict[str, Any]] | None = None,
            resources: dict[str, Any] | None = None,
            current_state: dict[str, Any] | None = None,
            ctx: Any = None,
        ) -> dict[str, Any]:
            return await arifos_compute_finance(
                mode=mode,
                session_id=session_id,
                initial_investment=initial_investment,
                cash_flows=cash_flows,
                discount_rate=discount_rate,
                terminal_value=terminal_value,
                finance_rate=finance_rate,
                reinvest_rate=reinvest_rate,
                outcomes=outcomes,
                probabilities=probabilities,
                ebitda=ebitda,
                debt_service=debt_service,
                candidates=candidates,
                constraints=constraints,
                alternatives=alternatives,
                tasks=tasks,
                resources=resources,
                current_state=current_state,
                ctx=ctx,
            )

    return mcp


# =============================================================================
# GOVERNANCE AGENT — compute_civilization (sustainability, game_theory, cross_evidence)
# =============================================================================


def create_governance_mcp() -> FastMCP:
    """Governance Agent MCP tools — arifos_compute_civilization for civilization-level compute."""
    mcp = FastMCP("arifOS-G")

    if CANONICAL_AVAILABLE:

        @mcp.tool(
            name="arifos_compute_civilization",
            description="Civilization engine: sustainability_path | game_theory | cross_evidence_synthesize",
        )
        async def compute_civilization(
            mode: str,
            session_id: str | None = None,
            agents: list[dict[str, Any]] | None = None,
            payoff_matrix: dict[str, Any] | None = None,
            scene_id: str | None = None,
            current_state: dict[str, Any] | None = None,
            ctx: Any = None,
        ) -> dict[str, Any]:
            return await arifos_compute_civilization(
                mode=mode,
                session_id=session_id,
                agents=agents,
                payoff_matrix=payoff_matrix,
                scene_id=scene_id,
                current_state=current_state,
                ctx=ctx,
            )

    return mcp


# =============================================================================
# EXECUTION AGENT — oracle_world (geox, wealth series)
# =============================================================================


def create_execution_mcp() -> FastMCP:
    """Execution Agent MCP tools — arifos_oracle_world for geox/wealth scene + series data."""
    mcp = FastMCP("arifOS-E")

    if CANONICAL_AVAILABLE:

        @mcp.tool(
            name="arifos_oracle_world",
            description="World oracle: geox_scene_load | geox_skills_query | macro_snapshot | series_fetch | series_vintage_fetch",
        )
        async def oracle_world(
            mode: str,
            session_id: str | None = None,
            scene_type: str | None = None,
            path: str | None = None,
            query: str = "",
            domain: str | None = None,
            geography: str | None = None,
            source: str | None = None,
            series_id: str | None = None,
            vintage_date: str | None = None,
            ctx: Any = None,
        ) -> dict[str, Any]:
            return await arifos_oracle_world(
                mode=mode,
                session_id=session_id,
                scene_type=scene_type,
                path=path,
                query=query,
                domain=domain,
                geography=geography,
                source=source,
                series_id=series_id,
                vintage_date=vintage_date,
                ctx=ctx,
            )

    return mcp


# =============================================================================
# META AGENT — stub (no separate tools; arifos_vault handles metabolic state via mode="read")
# =============================================================================


def create_meta_mcp() -> FastMCP:
    """Meta Agent MCP tools — stub (metabolic state routed through arifos_vault with mode='read')."""
    mcp = FastMCP("arifOS-M")
    return mcp


# =============================================================================
# UNIFIED MCP SERVER
# =============================================================================


def create_unified_mcp(agents: list[str] | None = None, visibility: str = "public_only") -> FastMCP:
    """Create unified MCP server with all or selected agents."""
    mcp = FastMCP("arifOS-Unified")
    agents = agents or ["P", "T", "V", "G", "E", "M"]

    def _get_tools(fastmcp_instance):
        try:
            components = fastmcp_instance._local_provider._components
            return {k: v for k, v in components.items() if k.startswith("tool:")}
        except (AttributeError, TypeError):
            return {}

    if "P" in agents:
        perception = create_perception_mcp()
        for _key, tool in _get_tools(perception).items():
            mcp.add_tool(tool)
    if "T" in agents:
        transformation = create_transformation_mcp()
        for _key, tool in _get_tools(transformation).items():
            mcp.add_tool(tool)
    if "V" in agents:
        valuation = create_valuation_mcp()
        for _key, tool in _get_tools(valuation).items():
            mcp.add_tool(tool)
    if "G" in agents:
        governance = create_governance_mcp()
        for _key, tool in _get_tools(governance).items():
            mcp.add_tool(tool)
    if "E" in agents:
        execution = create_execution_mcp()
        for _key, tool in _get_tools(execution).items():
            mcp.add_tool(tool)
    if "M" in agents:
        meta = create_meta_mcp()
        for _key, tool in _get_tools(meta).items():
            mcp.add_tool(tool)

    return mcp


# =============================================================================
# TOOL CATALOG
# =============================================================================

TOOL_CATALOG = """arifOS 13-Tool Canonical Surface — arif_<noun>_<verb> namespace (v1.1 patch 2026-05-12)
=================================================================================================

GOVERNED LOOP (13):  [canonical arif_<noun>_<verb> surface — AGENTS.md SOT]
  000  arif_session_init       — Identity bootstrap, session anchor
  111  arif_sense_observe      — Physical reality grounding (GEOX / Δ organ)
  222  arif_evidence_fetch     — Web / external evidence retrieval
  333  arif_mind_reason        — Constitutional reasoning (F2/F7/F8)
  444h arif_heart_critique     — Ethical critique, F9/F12 safety gate
  444r arif_kernel_route       — Metabolic syscall routing (444_ROUTER)
       arif_reply_compose      — Dual-axis governed response composition
  555  arif_memory_recall      — Vector memory retrieval (Qdrant + bge-m3)
  666g arif_gateway_connect    — A2A mesh, agent-to-agent governed connection
  777  arif_ops_measure        — Health probe, brent_score, ops telemetry
  888  arif_judge_deliberate   — Constitutional verdict engine (888_JUDGE)
  999  arif_vault_seal         — Append-only VAULT999 ledger write
  010  arif_forge_execute      — A-FORGE dispatch (requires 888 SEAL)

DEPRECATED (do not use):  arifos_<name> names retired 2026-04-19 hard cutover.
  Canonical surface lives in arifosmcp/constitutional_map.py
  Legacy constants frozen in arifosmcp/capability_map.py (backward compat only)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

__all__ = [
    "create_perception_mcp",
    "create_transformation_mcp",
    "create_valuation_mcp",
    "create_governance_mcp",
    "create_execution_mcp",
    "create_meta_mcp",
    "create_unified_mcp",
    "TOOL_CATALOG",
]

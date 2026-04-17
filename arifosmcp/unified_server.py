"""
arifOS Federation — Unified MCP Server
======================================
66 cognitive primitives + G02 Kernel Router

FastMCP server with:
- 66 agents organized by 6 axes (P/T/V/G/E/M)
- G02 Kernel Router as mandatory hub
- Tag-based visibility filtering
- Ω_ortho correlation tracking

Usage:
    python unified_server.py

Or import:
    from unified_server import create_unified_mcp
    mcp = create_unified_mcp()
    mcp.run()
"""

from __future__ import annotations

from typing import Any
from fastmcp import FastMCP

from agents_66 import (
    create_agents_mcp,
    PERCEPTION_TOOLS,
    TRANSFORMATION_TOOLS,
    VALUATION_TOOLS,
    GOVERNANCE_TOOLS,
    EXECUTION_TOOLS,
    META_TOOLS,
)
from g02_router import create_router_mcp, route_call, RouteRequest, get_omega_status


# =============================================================================
# TAG VISIBILITY FILTERS
# =============================================================================

TAG_FILTERS = {
    "public_only": {"public"},
    "with_scaffold": {"public", "scaffold"},
    "all_visible": {"public", "scaffold", "internal"},
    "governance_only": {"governance"},
    "execution_only": {"execution"},
}


# =============================================================================
# AXIS VIEW (groups tools by axis for display)
# =============================================================================

AXIS_VIEW = {
    "P": {"name": "Perception", "description": "Reality acquisition", "count": 11},
    "T": {"name": "Transformation", "description": "Mathematical computation", "count": 11},
    "V": {"name": "Valuation", "description": "Utility & allocation", "count": 11},
    "G": {"name": "Governance", "description": "Constraint & legitimacy", "count": 11},
    "E": {"name": "Execution", "description": "State mutation", "count": 11},
    "M": {"name": "Meta-Cognition", "description": "Self-inspection", "count": 11},
}


# =============================================================================
# ORTHOGONALITY VERIFICATION
# =============================================================================

ORTHOGONALITY_RULES = """
AXIS ORTHOGONALITY MATRIX:
==========================

         P    T    V    G    E    M
    P    0    1    0    1    0    0
    T    0    0    1    0    0    1
    V    0    0    0    1    0    0
    G    0    0    0    0    1    1
    E    0    0    0    0    0    0
    M    1    0    0    1    0    0

0 = Cannot call (would create correlation)
1 = Orthogonal call (allowed)

CROSS-AXIS CALL RULES:
======================
P → T, G    (Perception can call Transformation and Governance)
T → V, M    (Transformation can call Valuation and Meta)
V → G       (Valuation can call Governance only)
G → E, M    (Governance can call Execution and Meta)
E → ∅       (Execution cannot call anyone)
M → P, G    (Meta can call Perception and Governance)

Ω_ortho threshold: >= 0.95
"""


# =============================================================================
# TOOL CATALOG (for agent discovery)
# =============================================================================

TOOL_CATALOG = """
arifOS Federation — 66 Agent Catalog
=====================================

PERCEPTION AXIS (P01-P11)
-------------------------
P01  well_state_reader          — Expose WELL biological telemetry
P02  well_readiness_reflector  — Readiness verdict for JUDGE
P03  well_floor_scanner         — W-Floor status scan
P04  macro_snapshot_fetcher     — Macro/energy/carbon snapshot
P05  series_fetcher             — Live data series from public source
P06  vintage_fetcher            — Vintage series (FRED/ALFRED)
P07  source_reconciler          — Cross-source divergence detection
P08  ingest_health_monitor      — Bus health metrics
P09  geospatial_verifier        — Physical reality grounding
P10  spatial_context_extractor  — Spatial context extraction
P11  vault_ledger_reader        — VAULT999 ledger read

TRANSFORMATION AXIS (T01-T11)
------------------------------
T01  petrophysics_engine         — Physics-grounded petrophysics
T02  stratigraphic_correlator     — Stratigraphic correlation
T03  seismic_horizon_picker       — 3D volume horizon picking
T04  geometry_builder             — Architectural geometries
T05  attribute_audit_engine       — Kozeny-Carman permeability
T06  timing_verification_engine   — Trap-charge timing
T07  monte_carlo_simulator        — Stochastic forecast
T08  irr_mirr_calculator          — IRR/MIRR computation
T09  growth_runway_calculator      — CAGR and runway
T10  entropy_cashflow_auditor     — Cashflow entropy audit
T11  economic_audit_calculator     — Constitutional audit

VALUATION AXIS (V01-V11)
------------------------
V01  npv_evaluator               — Net Present Value
V02  profitability_index          — Profitability Index
V03  emv_risk_evaluator          — Expected Monetary Value
V04  dscr_evaluator               — Debt Service Coverage
V05  payback_evaluator            — Payback Period
V06  networth_state_evaluator     — Balance sheet
V07  cashflow_flow_evaluator      — Metabolic liquidity
V08  personal_decision_ranker     — Personal alternatives
V09  agent_budget_optimizer       — Optimal action sequence
V10  civilization_sustainability_allocator — Long-term sustainability
V11  allocation_score_kernel      — Sovereign allocation verdict

GOVERNANCE AXIS (G01-G11)
--------------------------
G01  session_initializer           — Constitutional session init
G02  kernel_router                 — MANDATORY HUB (see g02_router.py)
G03  constitutional_mind           — Structured reasoning pipeline
G04  ethical_heart                — F5/F6/F9 ethical simulation
G05  final_judge                  — SEAL/PARTIAL/VOID/HOLD
G07  wealth_floor_checker          — F1-F13 for wealth proposals
G08  well_floor_authority          — W-Floor status
G09  orthogonality_guard          — Ω_ortho >= 0.95 enforcement
G10  policy_auditor               — Policy constraint audit
G11  hold_authority               — 888_HOLD check

EXECUTION AXIS (E01-E11)
------------------------
E01  forge_bridge                 — Execution manifest builder
E04  wealth_transaction_recorder   — Transaction to VAULT999
E05  portfolio_snapshot_recorder  — Portfolio snapshot to VAULT999
E06  well_log_writer              — Telemetry update
E07  well_pressure_signal         — Cognitive pressure signal
E08  well_anchor                  — WELL state to VAULT999
E09  session_anchor               — Session to VAULT999
E10  vault_sealer                 — Merkle ledger append
E11  memory_store                 — MemoryContract store

META-COGNITION AXIS (M01-M11)
-----------------------------
M01  memory_retriever             — MemoryContract query
M02  skill_discovery_agent        — Skill registry search
M03  skill_metadata_agent          — Skill metadata lookup
M04  skill_dependency_mapper       — Skill dependency graph
M05  risk_computation_toac        — ToAC risk score
M06  prospect_judge_router         — Prospect routing
M07  cross_evidence_synthesizer    — Causal scene synthesis
M08  coordination_equilibrium_solver — Multi-agent equilibrium
M09  game_theory_solver           — LP/Shapley/Nash
M10  civilization_coordination_analyzer — Sustainability coordination
M11  metabolic_monitor            — F1-F13 + ΔS + Peace² + Ω₀
"""


# =============================================================================
# CROSS-AXIS CALL EXAMPLE
# =============================================================================

CALL_EXAMPLE = """
Example: P01 calls T01 via G02

Step 1: P01 requests route through G02
    Request: {
        "caller_agent": "P01",
        "target_agent": "T01",
        "input_data": {...}
    }

Step 2: G02 checks ALLOWED_CALLS["P"] = {"T", "G"}
    T01 is in allowed set ✓

Step 3: G02 checks ORTHOGONALITY_MATRIX["P"]["T"] = 1
    Orthogonal ✓

Step 4: G02 records call, computes Ω_ortho
    Ω_ortho = 1.0 ✓

Step 5: G02 returns approved routing
    Response: {
        "approved": true,
        "target_agent": "T01",
        "lane": "T-lane",
        "omega_ortho": 1.0,
        "correlation_detected": false
    }

Step 6: Caller executes via T-lane with T01 agent
"""


# =============================================================================
# FACTORY FUNCTION
# =============================================================================


def create_unified_mcp(
    visibility_filter: str = "public_only",
    enable_router: bool = True,
) -> FastMCP:
    """
    Create unified arifOS Federation MCP server.

    Args:
        visibility_filter: Tag filter for visible tools
            - "public_only" (default): Only public tools
            - "with_scaffold": Include scaffold tools
            - "all_visible": Include internal tools
        enable_router: Enable G02 Kernel Router tools

    Returns:
        Configured FastMCP server
    """
    mcp = FastMCP("arifOS-Federation-66")

    # Register all 66 agents
    create_agents_mcp(mcp)

    # Apply visibility filter
    allowed_tags = TAG_FILTERS.get(visibility_filter, {"public"})
    mcp.enable(tags=allowed_tags, only=True)

    # Enable G02 Kernel Router if requested
    if enable_router:
        router_mcp = create_router_mcp()
        for tool in router_mcp._tool_manager.tools.values():
            mcp.add_tool(
                tool.fn,
                name=tool.name,
                description=tool.description,
                tags=tool.tags,
            )

    # Add informational tools
    @mcp.tool(tags={"system", "public"})
    def federation_catalog() -> str:
        """Return the 66 agent catalog."""
        return TOOL_CATALOG

    @mcp.tool(tags={"system", "public"})
    def federation_orthogonality_rules() -> str:
        """Return orthogonality matrix and cross-axis call rules."""
        return ORTHOGONALITY_RULES

    @mcp.tool(tags={"system", "public"})
    def federation_omega_status() -> dict[str, Any]:
        """Return current Ω_ortho status."""
        return get_omega_status()

    @mcp.tool(tags={"system", "public"})
    def federation_axes() -> dict[str, Any]:
        """Return axis definitions and tool counts."""
        return AXIS_VIEW

    @mcp.tool(tags={"system", "public"})
    def federation_call_example() -> str:
        """Return example of cross-axis call via G02."""
        return CALL_EXAMPLE

    return mcp


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import sys

    visibility = sys.argv[1] if len(sys.argv) > 1 else "public_only"
    enable_router = "--no-router" not in sys.argv

    print(f"Starting arifOS Federation MCP (visibility={visibility}, router={enable_router})")

    mcp = create_unified_mcp(
        visibility_filter=visibility,
        enable_router=enable_router,
    )
    mcp.run()

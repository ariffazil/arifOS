"""
arifosmcp/mcp_tools.py — 13-Tool Canonical Surface
==================================================
Hard cutover: 13 tools only. No P/T/V/E/M legacy registrations.
DITEMPA BUKAN DIBERI — Forged, Not Given

Constitutional (5)  : init, sense, mind, heart, judge
Infrastructure (3)  : kernel, memory, vault
Canonical Engines (5): compute_physics, compute_finance, compute_civilization, oracle_bio, oracle_world
"""

from __future__ import annotations

import os
from typing import Annotated, Any

from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# Canonical engines (created in tools_canonical.py)
try:
    from arifosmcp.tools_canonical import (
        arifos_compute_physics,
        arifos_compute_finance,
        arifos_compute_civilization,
        arifos_oracle_bio,
        arifos_oracle_world,
    )
    CANONICAL_AVAILABLE = True
except ImportError:
    CANONICAL_AVAILABLE = False


# =============================================================================
# GOVERNANCE METADATA HELPER
# =============================================================================

def _gov(
    role: str,
    risk: str,
    ledger: str,
    floors: list[str],
    *,
    requires_judge: bool = False,
    requires_human: bool = False,
    reversible: str = "reversible",
    mutability: str = "read",
) -> dict:
    return {
        "constitutional_role": role,
        "risk_tier": risk,
        "requires_judge": requires_judge,
        "requires_human_confirm": requires_human,
        "reversibility": reversible,
        "mutability": mutability,
        "ledger_class": ledger,
        "floor_anchors": floors,
    }


# =============================================================================
# GLOBAL STATE (shared across calls)
# =============================================================================

WELL_STATE_PATH = os.getenv("WELL_STATE_PATH", "/root/WELL/state.json")


def _load_well_state() -> dict[str, Any]:
    from pathlib import Path
    if not Path(WELL_STATE_PATH).exists():
        return {"operator_id": "arif", "metrics": {}, "well_score": 50, "floors_violated": []}
    import json
    with open(WELL_STATE_PATH) as f:
        return json.load(f)


# =============================================================================
# PERCEPTION AGENT — WELL oracle (stub, delegates to canonical)
# =============================================================================

def create_perception_mcp() -> FastMCP:
    """Perception Agent MCP tools — stub, delegates to arifos_oracle_bio."""
    mcp = FastMCP("arifOS-P")
    return mcp


# =============================================================================
# TRANSFORMATION AGENT — Physics/Math (stub, delegates to canonical)
# =============================================================================

def create_transformation_mcp() -> FastMCP:
    """Transformation Agent MCP tools — stub, delegates to arifos_compute_physics."""
    mcp = FastMCP("arifOS-T")
    return mcp


# =============================================================================
# VALUATION AGENT — Finance/Economic (stub, delegates to canonical)
# =============================================================================

def create_valuation_mcp() -> FastMCP:
    """Valuation Agent MCP tools — stub, delegates to arifos_compute_finance."""
    mcp = FastMCP("arifOS-V")
    return mcp


# =============================================================================
# GOVERNANCE AGENT — Stub
# =============================================================================

def create_governance_mcp() -> FastMCP:
    """Governance Agent MCP tools — STUB (delegated to arifOS canonical tools)."""
    mcp = FastMCP("arifOS-G")
    return mcp


# =============================================================================
# EXECUTION AGENT — Well anchor (stub)
# =============================================================================

def create_execution_mcp() -> FastMCP:
    """Execution Agent MCP tools — STUB."""
    mcp = FastMCP("arifOS-E")
    return mcp


# =============================================================================
# META AGENT — Skills/Metabolic (stub)
# =============================================================================

def create_meta_mcp() -> FastMCP:
    """Meta Agent MCP tools — STUB."""
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
        for key, tool in _get_tools(perception).items():
            mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)
    if "T" in agents:
        transformation = create_transformation_mcp()
        for key, tool in _get_tools(transformation).items():
            mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)
    if "V" in agents:
        valuation = create_valuation_mcp()
        for key, tool in _get_tools(valuation).items():
            mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)
    if "G" in agents:
        governance = create_governance_mcp()
        for key, tool in _get_tools(governance).items():
            mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)
    if "E" in agents:
        execution = create_execution_mcp()
        for key, tool in _get_tools(execution).items():
            mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)
    if "M" in agents:
        meta = create_meta_mcp()
        for key, tool in _get_tools(meta).items():
            mcp.add_tool(tool.fn, name=tool.name, description=tool.description, tags=tool.tags)

    return mcp


# =============================================================================
# TOOL CATALOG (13 canonical tools)
# =============================================================================

TOOL_CATALOG = """arifOS 13-Tool Canonical Surface (Hard Cutover 2026-04-19)
=================================================================

CONSTITUTIONAL (5):
  arifos_init         — Constitutional session anchor
  arifos_sense        — Physical reality grounding (GEOX)
  arifos_mind         — Constitutional reasoning
  arifos_heart        — Ethical critique and safety simulation
  arifos_judge        — Final constitutional verdict (888_JUDGE)

INFRASTRUCTURE (3):
  arifos_kernel       — Metabolic orchestration
  arifos_memory       — Governed context retrieval
  arifos_vault        — Sealed Merkle audit logging

CANONICAL ENGINES (5):
  arifos_compute_physics      — petrophysics | stratigraphy | geometry | monte_carlo | entropy_audit | growth_runway
  arifos_compute_finance      — npv | irr | mirr | emv | dscr | payback | PI | allocation | budget_optimize
  arifos_compute_civilization — sustainability_path | game_theory | cross_evidence_synthesize
  arifos_oracle_bio           — snapshot_read | readiness_check | floor_scan | log_update
  arifos_oracle_world         — geox_scene_load | geox_skills_query | macro_snapshot | series_fetch | series_vintage_fetch

TOTAL: 13 TOOLS
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

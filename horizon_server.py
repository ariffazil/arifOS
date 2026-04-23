"""
arifOS Horizon Server — FastMCP 2.x Compatible Entry Point
=========================================================
Uses simple @mcp.tool() decorators directly.
Works on Horizon (FastMCP 2.x) without FastMCP 3.x FunctionTool API.

Usage:
    fastmcp run horizon_server.py
    python horizon_server.py

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import sys

_project_root = os.path.dirname(os.path.abspath(__file__))
_arifosmcp_root = os.path.join(_project_root, "arifosmcp")
for _p in (_project_root, _arifosmcp_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dotenv import load_dotenv

_env_path = os.path.join(_project_root, "arifosmcp", ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)

from fastmcp import FastMCP

mcp = FastMCP("arifOS-Horizon")

from arifosmcp.tools_canonical import (
    arifos_compute_physics,
    arifos_compute_finance,
    arifos_compute_civilization,
    arifos_oracle_bio,
    arifos_oracle_world,
)


@mcp.tool(
    name="arifos_compute_physics",
    description="Physics engine: petrophysics | stratigraphy_correlate | geometry_build | monte_carlo | entropy_audit | growth_runway",
)
async def compute_physics(
    mode: str,
    session_id: str | None = None,
    well_id: str | None = None,
    computation: str | None = None,
    params: dict | None = None,
    wells: list[str] | None = None,
    section_id: str | None = None,
    horizons: list[dict] | None = None,
    outcomes: list[float] | None = None,
    probabilities: list[float] | None = None,
    iterations: int = 1000,
    cashflows: list[float] | None = None,
    burn_rate: float | None = None,
) -> dict:
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
    )


@mcp.tool(
    name="arifos_compute_finance",
    description="Finance engine: npv | irr | mirr | emv | dscr | payback | profitability_index | allocation_rank | personal_decision_rank | budget_optimize | civilization_sustainability",
)
async def compute_finance(
    mode: str,
    session_id: str | None = None,
    cashflows: list[float] | None = None,
    rate: float | None = None,
    investment: float | None = None,
    params: dict | None = None,
) -> dict:
    return await arifos_compute_finance(
        mode=mode,
        session_id=session_id,
        cashflows=cashflows,
        rate=rate,
        investment=investment,
        params=params,
    )


@mcp.tool(
    name="arifos_compute_civilization",
    description="Civilization engine: sustainability_path | game_theory | cross_evidence_synthesize",
)
async def compute_civilization(
    mode: str, session_id: str | None = None, params: dict | None = None
) -> dict:
    return await arifos_compute_civilization(
        mode=mode, session_id=session_id, params=params
    )


@mcp.tool(
    name="arifos_oracle_bio",
    description="WELL state oracle: snapshot_read | readiness_check | floor_scan | log_update",
)
async def oracle_bio(
    mode: str, session_id: str | None = None, dimensions: dict | None = None
) -> dict:
    return await arifos_oracle_bio(
        mode=mode, session_id=session_id, dimensions=dimensions
    )


@mcp.tool(
    name="arifos_oracle_world",
    description="World oracle: geox_scene_load | geox_skills_query | macro_snapshot | series_fetch | series_vintage_fetch",
)
async def oracle_world(
    mode: str, session_id: str | None = None, params: dict | None = None
) -> dict:
    return await arifos_oracle_world(mode=mode, session_id=session_id, params=params)


if __name__ == "__main__":
    mcp.run()

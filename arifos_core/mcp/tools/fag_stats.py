"""
MCP Tool: arifos_fag_stats

Exposes FAG (File Access Governance) statistics and audit information.
Provides insight into constitutional floor performance and v45.0.3 hardening metrics.

Tool Interface:
    Input: { "root": str? }
    Output: { "stats": dict, "health": dict }
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from arifos_core.apex.governance.fag import FAG


class FAGStatsRequest(BaseModel):
    """Request model for arifos_fag_stats tool."""
    root: str = Field(default=".", description="Root directory to check stats for")


class FAGStatsResponse(BaseModel):
    """Response model for arifos_fag_stats tool."""
    stats: Dict[str, int] = Field(..., description="Access statistics (granted, denied, floor fails)")
    health: Dict[str, Any] = Field(..., description="Health check results (v45.0.3)")
    root: str = Field(..., description="Root jail path")


def arifos_fag_stats(request: FAGStatsRequest) -> FAGStatsResponse:
    """
    Get FAG access statistics and health status.

    Args:
        request: FAGStatsRequest with root

    Returns:
        FAGStatsResponse with statistics and health data
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=True,
            persist_stats=True,  # Load persisted stats if they exist
            job_id="mcp-fag-stats",
        )

        return FAGStatsResponse(
            stats=fag.access_stats,
            health=fag.health_check(),
            root=str(fag.root),
        )
    except Exception as e:
        return FAGStatsResponse(
            stats={},
            health={"status": "ERROR", "error": str(e)},
            root=request.root,
        )


# MCP Tool metadata
TOOL_METADATA = {
    "name": "arifos_fag_stats",
    "description": (
        "Retrieve FAG access statistics and constitutional health status. "
        "Reports totals for granted/denied access, floor-specific failures, "
        "and v45.0.3 metrics (snapshots, rollbacks, watchdog anomalies)."
    ),
    "input_schema": FAGStatsRequest.model_json_schema(),
    "output_schema": FAGStatsResponse.model_json_schema(),
    "constitutional_floors": ["F8"],
    "version": "v45.3.0",
}

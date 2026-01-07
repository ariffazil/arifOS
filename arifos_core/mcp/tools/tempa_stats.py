"""
MCP Tool: tempa_stats (vTEMPA External)

Exposes FAG access statistics and audit information.
vTEMPA = Governed File Access for External MCP (formerly FAG for internal).

Version: v45.3.0
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from arifos_core.apex.governance.fag import FAG


class FAGStatsRequest(BaseModel):
    """Request model for fag_stats tool."""
    session_id: Optional[str] = Field(None, description="Filter stats by session ID")
    root: str = Field(default=".", description="Root directory for FAG instance")


class FAGStatsResponse(BaseModel):
    """Response model for fag_stats tool."""
    total_granted: int = Field(default=0, description="Successful read operations (SEAL)")
    total_denied: int = Field(default=0, description="Denied read operations (VOID)")
    f1_amanah_blocks: int = Field(default=0, description="F1 Amanah violations (jail escape, permission)")
    f2_truth_blocks: int = Field(default=0, description="F2 Truth violations (not found, not a file)")
    f4_delta_s_blocks: int = Field(default=0, description="F4 ΔS violations (binary, encoding)")
    f9_c_dark_blocks: int = Field(default=0, description="F9 C_dark violations (forbidden patterns)")
    success_rate: float = Field(default=0.0, description="Percentage of granted access (0-100)")
    session_active: bool = Field(default=True, description="Whether FAG session is active")


def fag_stats(request: FAGStatsRequest) -> FAGStatsResponse:
    """
    Get FAG access statistics.

    Returns aggregated statistics on file access attempts,
    categorized by floor violation type.

    Args:
        request: FAGStatsRequest with optional session filter

    Returns:
        FAGStatsResponse with access counts and success rate

    Examples:
        >>> fag_stats(FAGStatsRequest())
        FAGStatsResponse(
            total_granted=150,
            total_denied=12,
            f9_c_dark_blocks=5,
            success_rate=92.59
        )
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=True,
            enable_ledger=False,
            job_id=request.session_id or "mcp-fag-stats",
            persist_stats=True,  # Load persisted stats if available
        )

        # Get statistics from FAG instance
        stats = fag.get_access_statistics()

        return FAGStatsResponse(
            total_granted=stats.get("total_granted", 0),
            total_denied=stats.get("total_denied", 0),
            f1_amanah_blocks=stats.get("f1_amanah_fail", 0),
            f2_truth_blocks=stats.get("f2_truth_fail", 0),
            f4_delta_s_blocks=stats.get("f4_delta_s_fail", 0),
            f9_c_dark_blocks=stats.get("f9_c_dark_fail", 0),
            success_rate=stats.get("success_rate", 0.0),
            session_active=True,
        )
    except ValueError as e:
        # Root directory doesn't exist - return empty stats
        return FAGStatsResponse(
            session_active=False,
        )
    except Exception as e:
        # Any other error - return empty stats
        return FAGStatsResponse(
            session_active=False,
        )


# Synchronous wrapper for MCP server
def tempa_stats_sync(request: FAGStatsRequest) -> FAGStatsResponse:
    """Synchronous version of tempa_stats."""
    return tempa_stats(request)


# MCP Tool metadata
TOOL_METADATA = {
    "name": "tempa_stats",
    "description": (
        "vTEMPA: Get FAG access statistics. Returns counts of granted/denied "
        "operations categorized by floor violation type (F1, F2, F4, F9)."
    ),
    "input_schema": FAGStatsRequest.model_json_schema(),
    "output_schema": FAGStatsResponse.model_json_schema(),
    "constitutional_floors": [],
    "version": "v45.3.0",
}

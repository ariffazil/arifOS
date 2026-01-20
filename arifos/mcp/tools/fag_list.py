"""
MCP Tool: arifos_fag_list

Exposes FAG (File Access Governance) as an MCP tool for governed directory listing.
Filters forbidden patterns (F9 C_dark) and protected no-touch zones (v45.0.3).

Tool Interface:
    Input: { "path": str?, "root": str?, "human_seal_token": str? }
    Output: { "entries": list, "root": str, "path": str }
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from arifos.core.apex.governance.fag import FAG


class FAGListRequest(BaseModel):
    """Request model for arifos_fag_list tool."""
    path: str = Field(default=".", description="Directory path to list (relative to root)")
    root: str = Field(default=".", description="Root directory for jailed access")
    human_seal_token: Optional[str] = Field(None, description="Token to bypass protected path restrictions")


class DirectoryEntry(BaseModel):
    """Metadata for a single directory entry."""
    name: str
    type: str  # "file" or "directory"
    size: int
    modified: str


class FAGListResponse(BaseModel):
    """Response model for arifos_fag_list tool."""
    entries: List[DirectoryEntry] = Field(default_factory=list, description="List of directory entries")
    root: str = Field(..., description="Root jail path")
    path: str = Field(..., description="Relative path listed")
    error: Optional[str] = Field(None, description="Error message if listing failed")


def arifos_fag_list(request: FAGListRequest) -> FAGListResponse:
    """
    List directory contents with constitutional governance (FAG).

    Filters entries according to F9 C_dark (secrets) and v45.0.3 protected paths.

    Args:
        request: FAGListRequest with path and root

    Returns:
        FAGListResponse with filtered directory entries
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=True,
            human_seal_token=request.human_seal_token,
            job_id="mcp-fag-list",
        )

        entries = fag.list_dir(request.path)

        return FAGListResponse(
            entries=[DirectoryEntry(**e) for e in entries],
            root=str(fag.root),
            path=request.path,
        )
    except Exception as e:
        return FAGListResponse(
            entries=[],
            root=request.root,
            path=request.path,
            error=str(e),
        )


# MCP Tool metadata
TOOL_METADATA = {
    "name": "arifos_fag_list",
    "description": (
        "List directory contents with constitutional governance (FAG). "
        "Filters out secrets (F9 C_dark) and protected no-touch zones (v45.0.3). "
        "Requires HUMAN_SEAL_TOKEN for protected path visibility."
    ),
    "parameters": FAGListRequest.model_json_schema(),
    "output_schema": FAGListResponse.model_json_schema(),
    "constitutional_floors": ["F1", "F9"],
    "version": "v45.3.0",
}

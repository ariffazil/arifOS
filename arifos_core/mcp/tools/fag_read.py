"""
MCP Tool: arifos_fag_read

Exposes FAG (File Access Governance) as an MCP tool for governed file reading.

Tool Interface:
    Input: { "path": str, "root": str? }
    Output: { "verdict": str, "content": str?, "reason": str?, "floor_scores": dict }

Constitutional Floors Enforced:
    F1 Amanah, F2 Truth, F4 DeltaS, F5 Peace², F7 Omega0, F8 G, F9 C_dark
"""

from __future__ import annotations

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from arifos_core.governance.fag import FAG, FAGReadResult


class FAGReadRequest(BaseModel):
    """Request model for arifos_fag_read tool."""
    path: str = Field(..., description="Path to file (relative to root or absolute within root)")
    root: str = Field(default=".", description="Root directory for jailed access")
    enable_ledger: bool = Field(default=True, description="Log access to Cooling Ledger")


class FAGReadResponse(BaseModel):
    """Response model for arifos_fag_read tool."""
    verdict: str = Field(..., description="SEAL, VOID, or HOLD")
    path: str = Field(..., description="File path that was accessed")
    content: Optional[str] = Field(None, description="File content (if SEAL)")
    reason: Optional[str] = Field(None, description="Reason for denial (if not SEAL)")
    floor_scores: Optional[Dict[str, float]] = Field(None, description="Constitutional floor scores")
    ledger_entry_id: Optional[str] = Field(None, description="Cooling Ledger entry ID")


def arifos_fag_read(request: FAGReadRequest) -> FAGReadResponse:
    """
    Read file with constitutional governance (FAG).
    
    Enforces 9 constitutional floors on file access:
    - F1 Amanah: Root jail enforcement
    - F2 Truth: File must exist and be readable
    - F4 DeltaS: Reject binary/unreadable files
    - F5 Peace²: Read-only, non-destructive
    - F7 Omega0: Return verdict + uncertainty
    - F8 G: Log all access to Cooling Ledger
    - F9 C_dark: Block secrets, credentials, forbidden patterns
    
    Args:
        request: FAGReadRequest with path, root, and options
    
    Returns:
        FAGReadResponse with verdict, content (if SEAL), and floor scores
    
    Examples:
        >>> arifos_fag_read(FAGReadRequest(path="README.md"))
        FAGReadResponse(verdict="SEAL", content="...", ...)
        
        >>> arifos_fag_read(FAGReadRequest(path=".env"))
        FAGReadResponse(verdict="VOID", reason="F9 C_dark FAIL: Forbidden pattern")
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=True,
            enable_ledger=request.enable_ledger,
            job_id="mcp-fag-read",
        )
    except ValueError as e:
        # Root directory error
        return FAGReadResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F1 Amanah FAIL: Invalid root directory - {e}",
            floor_scores={"F1_amanah": 0.0},
        )
    
    # Execute read with FAG
    result: FAGReadResult = fag.read(request.path)
    
    # Convert to response model
    return FAGReadResponse(
        verdict=result.verdict,
        path=result.path,
        content=result.content,
        reason=result.reason,
        floor_scores=result.floor_scores,
        ledger_entry_id=result.ledger_entry_id,
    )


# MCP Tool metadata
TOOL_METADATA = {
    "name": "arifos_fag_read",
    "description": (
        "Read file with constitutional governance (FAG). "
        "Enforces 9 constitutional floors: root jail (F1 Amanah), "
        "existence check (F2 Truth), binary rejection (F4 DeltaS), "
        "read-only safety (F5 Peace²), uncertainty handling (F7 Omega0), "
        "ledger logging (F8 G), and secret blocking (F9 C_dark)."
    ),
    "input_schema": FAGReadRequest.model_json_schema(),
    "output_schema": FAGReadResponse.model_json_schema(),
    "constitutional_floors": ["F1", "F2", "F4", "F5", "F7", "F8", "F9"],
    "version": "v41.0.0-alpha",
}

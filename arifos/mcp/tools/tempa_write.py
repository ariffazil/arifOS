"""
MCP Tool: tempa_write (vTEMPA External)

Exposes FAG.write_validate() as external MCP tool for constitutional write validation.
vTEMPA = Governed File Access for External MCP (formerly FAG for internal).

Constitutional Floors Enforced:
    F1 Amanah - Root jail, reversible changes only
    F4 ΔS - Patch must reduce entropy
    F5 Peace² - Non-destructive by default
    F9 C_dark - Block writes to forbidden patterns

CRITICAL: This tool NEVER auto-executes writes.
All writes return HOLD for human approval (F1 Amanah compliance).

Version: v45.3.0
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from arifos.apex.governance.fag import FAG, FAGWritePlan, FAGWriteResult


class FAGWriteRequest(BaseModel):
    """Request model for fag_write tool."""
    path: str = Field(..., description="Path to file (relative to root)")
    operation: Literal["create", "patch", "delete"] = Field(..., description="Write operation type")
    content: Optional[str] = Field(None, description="File content for create, or new content for patch")
    diff: Optional[str] = Field(None, description="Unified diff for patch operations")
    justification: str = Field(..., description="Reason for this write operation")
    read_sha256: Optional[str] = Field(None, description="SHA256 of file before patch (proof of read)")
    read_bytes: Optional[int] = Field(None, description="Byte count of file before patch")
    root: str = Field(default=".", description="Root directory for jailed access")


class FAGWriteResponse(BaseModel):
    """Response model for fag_write tool."""
    verdict: str = Field(..., description="SEAL (validated) | HOLD (needs approval) | VOID (rejected)")
    path: str = Field(..., description="File path that was validated")
    reason: str = Field(..., description="Explanation of verdict")
    floor_violations: List[str] = Field(default_factory=list, description="List of floor violations")
    requires_human_approval: bool = Field(default=True, description="Always True - writes need human approval")


def fag_write(request: FAGWriteRequest) -> FAGWriteResponse:
    """
    Validate file write with constitutional governance (FAG).

    IMPORTANT: This tool validates write plans but NEVER executes them.
    All writes require human approval per F1 Amanah.

    Enforces constitutional floors:
    - F1 Amanah: Root jail enforcement, reversible changes only
    - F4 ΔS: Patch must not increase entropy (no massive rewrites)
    - F5 Peace²: Non-destructive by default
    - F9 C_dark: Block writes to forbidden patterns

    Write Contract Rules:
    1. No New Files - HOLD unless in sandbox (.arifos_clip/, scratch/)
    2. Canon Lock - VOID for creates in L1_THEORY/
    3. Patch Only - HOLD if no diff provided
    4. Rewrite Threshold - HOLD if deletion_ratio > 30%
    5. Read Before Write - HOLD if no read_proof (sha256 + bytes)
    6. Delete Gate - HOLD for any delete operation

    Args:
        request: FAGWriteRequest with path, operation, and validation data

    Returns:
        FAGWriteResponse with verdict and approval requirement

    Examples:
        >>> fag_write(FAGWriteRequest(
        ...     path="src/main.py",
        ...     operation="patch",
        ...     diff="--- a/src/main.py\\n+++ b/src/main.py\\n...",
        ...     justification="Fix bug in main()",
        ...     read_sha256="abc123...",
        ...     read_bytes=1024
        ... ))
        FAGWriteResponse(verdict="SEAL", requires_human_approval=True, ...)

        >>> fag_write(FAGWriteRequest(
        ...     path="L1_THEORY/canon/new.md",
        ...     operation="create",
        ...     justification="Add new canon"
        ... ))
        FAGWriteResponse(verdict="VOID", reason="Canon zone amendment-only", ...)
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=False,  # Allow write validation (not execution)
            enable_ledger=True,
            job_id="mcp-fag-write",
        )
    except ValueError as e:
        return FAGWriteResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F1 Amanah FAIL: Invalid root directory - {e}",
            floor_violations=["F1_Amanah"],
            requires_human_approval=True,
        )

    # Build write plan
    plan = FAGWritePlan(
        target_path=request.path,
        operation=request.operation,
        justification=request.justification,
        diff=request.diff,
        read_sha256=request.read_sha256,
        read_bytes=request.read_bytes,
    )

    # Validate write plan
    result: FAGWriteResult = fag.write_validate(plan)

    return FAGWriteResponse(
        verdict=result.verdict,
        path=result.path,
        reason=result.reason,
        floor_violations=result.floor_violations or [],
        requires_human_approval=True,  # Always True per F1 Amanah
    )


# Synchronous wrapper for MCP server
def tempa_write_sync(request: FAGWriteRequest) -> FAGWriteResponse:
    """Synchronous version of tempa_write."""
    return tempa_write(request)


# MCP Tool metadata
TOOL_METADATA = {
    "name": "tempa_write",
    "description": (
        "vTEMPA: Validate file write with constitutional governance. "
        "NEVER auto-executes - all writes require human approval. "
        "Enforces: root jail (F1 Amanah), entropy control (F4 ΔS), "
        "non-destruction (F5 Peace²), secret blocking (F9 C_dark)."
    ),
    "parameters": FAGWriteRequest.model_json_schema(),
    "output_schema": FAGWriteResponse.model_json_schema(),
    "constitutional_floors": ["F1", "F4", "F5", "F9"],
    "version": "v45.3.0",
}

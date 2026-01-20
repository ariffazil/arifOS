"""
MCP Tool: arifos_fag_write

Exposes FAG (File Access Governance) as an MCP tool for governed file writing.
Enforces the FAG Write Contract (v42.2) and v45.0.3 hardening features.

Tool Interface:
    Input: {
        "path": str,
        "operation": "create" | "patch" | "delete",
        "justification": str,
        "diff": str?,
        "read_proof": {
            "sha256": str,
            "bytes": int,
            "mtime_ns": int?,
            "excerpt": str?
        }?,
        "root": str?,
        "human_seal_token": str?
    }
    Output: { "verdict": str, "path": str, "reason": str, "floor_violations": list?, "rollback_id": str? }
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

from arifos.core.apex.governance.fag import FAG, FAGWritePlan, FAGWriteResult


class ReadProof(BaseModel):
    """Verifiable read proof for FAG Write Contract."""
    sha256: str = Field(..., description="SHA-256 hash of the file content before modification")
    bytes: int = Field(..., description="Size of the file in bytes")
    mtime_ns: Optional[int] = Field(None, description="Last modification time in nanoseconds")
    excerpt: Optional[str] = Field(None, description="First/last 64 bytes of content for visual verification")


class FAGWriteRequest(BaseModel):
    """Request model for arifos_fag_write tool."""
    path: str = Field(..., description="Target path for write operation")
    operation: Literal["create", "patch", "delete"] = Field(..., description="Type of operation")
    justification: str = Field(..., description="Reason for the modification")
    diff: Optional[str] = Field(None, description="Unified diff for patch operations")
    read_proof: Optional[ReadProof] = Field(None, description="Proof of prior read for anti-fake compliance")
    root: str = Field(default=".", description="Root directory for jailed access")
    human_seal_token: Optional[str] = Field(None, description="Token to bypass protected path restrictions")


class FAGWriteResponse(BaseModel):
    """Response model for arifos_fag_write tool."""
    verdict: str = Field(..., description="SEAL, VOID, or HOLD")
    path: str = Field(..., description="Path that was targeted")
    reason: str = Field(..., description="Explanation of the verdict")
    floor_violations: Optional[List[str]] = Field(None, description="List of constitutional floors violated")
    rollback_id: Optional[str] = Field(None, description="Snaphot rollback ID (v45.0.3)")


def arifos_fag_write(request: FAGWriteRequest) -> FAGWriteResponse:
    """
    Validate a write operation with constitutional governance (FAG).

    Enforces the FAG Write Contract:
    - Rule 1: Canon Lock (L1_THEORY is immutable)
    - Rule 2: No New Files (outside sandbox/allowlist)
    - Rule 3: Delete Gate (requires human approval)
    - Rule 4: Read Before Write (verifiable read proof required)
    - Rule 5: Patch Only (no full file rewrites)
    - Rule 6: Rewrite Threshold (max 30% deletion)
    - v45.0.3: Mutation Watchdog (anomaly detection)
    - v45.0.3: Pre-Mutate Snapshot (rollback contract)

    Args:
        request: FAGWriteRequest with operation details

    Returns:
        FAGWriteResponse with verdict and reasoning
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=False,  # Allow write validation
            human_seal_token=request.human_seal_token,
            job_id="mcp-fag-write",
        )
    except ValueError as e:
        return FAGWriteResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F1 Amanah FAIL: Invalid root directory - {e}",
            floor_violations=["F1_amanah"],
        )

    # Construct FAGWritePlan
    plan = FAGWritePlan(
        target_path=request.path,
        operation=request.operation,
        justification=request.justification,
        diff=request.diff,
        read_sha256=request.read_proof.sha256 if request.read_proof else None,
        read_bytes=request.read_proof.bytes if request.read_proof else None,
        read_mtime_ns=request.read_proof.mtime_ns if request.read_proof else None,
        read_excerpt=request.read_proof.excerpt if request.read_proof else None,
    )

    # Execute write validation
    result: FAGWriteResult = fag.write_validate(plan)

    # Convert to response
    return FAGWriteResponse(
        verdict=result.verdict,
        path=result.path,
        reason=result.reason,
        floor_violations=result.floor_violations,
        rollback_id=result.rollback_id,
    )


# MCP Tool metadata
TOOL_METADATA = {
    "name": "arifos_fag_write",
    "description": (
        "Validate a file write operation with constitutional governance (FAG). "
        "Enforces the Write Contract: canon lock, no new files, delete gate, "
        "read-before-write proof, patch-only, and rewrite thresholds. "
        "Includes v45.0.3 hardening: watchdog anomalies and rollback snapshots."
    ),
    "parameters": FAGWriteRequest.model_json_schema(),
    "output_schema": FAGWriteResponse.model_json_schema(),
    "constitutional_floors": ["F1", "F2", "F3", "F5", "F7", "F8", "F9"],
    "version": "v45.3.0",
}

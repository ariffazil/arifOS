"""
MCP Tool: tempa_list (vTEMPA External)

Exposes constitutional directory listing with forbidden pattern filtering.
vTEMPA = Governed File Access for External MCP (formerly FAG for internal).

Constitutional Floors Enforced:
    F1 Amanah - Root jail enforcement
    F9 C_dark - Filter secrets, credentials from listing

Version: v45.3.0
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from arifos_core.apex.governance.fag import BINARY_EXTENSIONS, FAG, FORBIDDEN_PATTERNS


class FAGFileEntry(BaseModel):
    """Single file entry in directory listing."""
    name: str = Field(..., description="File/directory name")
    path: str = Field(..., description="Relative path from root")
    is_dir: bool = Field(..., description="True if directory")
    size: Optional[int] = Field(None, description="File size in bytes (None for directories)")
    extension: Optional[str] = Field(None, description="File extension")
    is_binary: bool = Field(default=False, description="True if binary file")


class FAGListRequest(BaseModel):
    """Request model for fag_list tool."""
    path: str = Field(default=".", description="Directory path to list (relative to root)")
    pattern: str = Field(default="*", description="Glob pattern to match")
    max_depth: int = Field(default=1, description="Maximum recursion depth (1 = current dir only)")
    root: str = Field(default=".", description="Root directory for jailed access")
    include_hidden: bool = Field(default=False, description="Include hidden files (starting with .)")


class FAGListResponse(BaseModel):
    """Response model for fag_list tool."""
    verdict: str = Field(..., description="SEAL | VOID")
    path: str = Field(..., description="Directory path that was listed")
    entries: List[FAGFileEntry] = Field(default_factory=list, description="Directory entries")
    total_count: int = Field(default=0, description="Total entries found")
    filtered_count: int = Field(default=0, description="Entries hidden by F9 C_dark")
    reason: Optional[str] = Field(None, description="Reason if VOID")


def _matches_forbidden(path_str: str) -> bool:
    """Check if path matches any forbidden pattern."""
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, path_str):
            return True
    return False


def fag_list(request: FAGListRequest) -> FAGListResponse:
    """
    List directory with constitutional governance (FAG).

    Filters out forbidden patterns (F9 C_dark) for transparency.
    Returns filtered_count so caller knows files were hidden.

    Enforces constitutional floors:
    - F1 Amanah: Root jail enforcement (can't list outside root)
    - F9 C_dark: Filter secrets, credentials, forbidden patterns

    Args:
        request: FAGListRequest with path, pattern, and options

    Returns:
        FAGListResponse with entries and filter stats

    Examples:
        >>> fag_list(FAGListRequest(path="."))
        FAGListResponse(verdict="SEAL", entries=[...], filtered_count=2)

        >>> fag_list(FAGListRequest(path="../../../etc"))
        FAGListResponse(verdict="VOID", reason="F1 Amanah FAIL: Outside root jail")
    """
    try:
        fag = FAG(
            root=request.root,
            read_only=True,
            enable_ledger=False,  # Don't log listings
            job_id="mcp-fag-list",
        )
    except ValueError as e:
        return FAGListResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F1 Amanah FAIL: Invalid root directory - {e}",
        )

    # Resolve target directory
    try:
        if request.path == ".":
            target = fag.root
        else:
            target = (fag.root / request.path).resolve()

        # F1 Amanah: Check jail
        try:
            target.relative_to(fag.root)
        except ValueError:
            return FAGListResponse(
                verdict="VOID",
                path=request.path,
                reason=f"F1 Amanah FAIL: Path outside root jail - {target}",
            )

        if not target.exists():
            return FAGListResponse(
                verdict="VOID",
                path=request.path,
                reason=f"F2 Truth FAIL: Directory does not exist - {target}",
            )

        if not target.is_dir():
            return FAGListResponse(
                verdict="VOID",
                path=request.path,
                reason=f"F2 Truth FAIL: Not a directory - {target}",
            )
    except Exception as e:
        return FAGListResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F1 Amanah FAIL: Path resolution error - {e}",
        )

    # List directory with filtering
    entries: List[FAGFileEntry] = []
    filtered_count = 0

    try:
        for item in target.iterdir():
            # Skip hidden files unless requested
            if not request.include_hidden and item.name.startswith("."):
                filtered_count += 1
                continue

            # Get relative path for pattern matching
            rel_path = str(item.relative_to(fag.root))

            # F9 C_dark: Filter forbidden patterns
            if _matches_forbidden(rel_path) or _matches_forbidden(item.name):
                filtered_count += 1
                continue

            # Build entry
            is_binary = item.suffix.lower() in BINARY_EXTENSIONS if item.is_file() else False

            entries.append(FAGFileEntry(
                name=item.name,
                path=rel_path,
                is_dir=item.is_dir(),
                size=item.stat().st_size if item.is_file() else None,
                extension=item.suffix if item.is_file() else None,
                is_binary=is_binary,
            ))
    except PermissionError:
        return FAGListResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F1 Amanah FAIL: Permission denied - {target}",
        )
    except Exception as e:
        return FAGListResponse(
            verdict="VOID",
            path=request.path,
            reason=f"F7 Omega0 ALERT: Unexpected error - {e}",
        )

    # Sort entries (directories first, then files)
    entries.sort(key=lambda e: (not e.is_dir, e.name.lower()))

    return FAGListResponse(
        verdict="SEAL",
        path=request.path,
        entries=entries,
        total_count=len(entries),
        filtered_count=filtered_count,
    )


# Synchronous wrapper for MCP server
def tempa_list_sync(request: FAGListRequest) -> FAGListResponse:
    """Synchronous version of tempa_list."""
    return tempa_list(request)


# MCP Tool metadata
TOOL_METADATA = {
    "name": "tempa_list",
    "description": (
        "vTEMPA: List directory with constitutional governance. "
        "Filters forbidden patterns (secrets, .env, credentials) per F9 C_dark. "
        "Returns filtered_count for transparency."
    ),
    "parameters": FAGListRequest.model_json_schema(),
    "output_schema": FAGListResponse.model_json_schema(),
    "constitutional_floors": ["F1", "F9"],
    "version": "v45.3.0",
}

"""
mcp_claude.py - Claude MCP Binding for @WELL

Model Context Protocol server for Claude Desktop and Claude Code.
Exposes @WELL file care operations as MCP tools.

Usage in Claude Desktop (claude_desktop_config.json):
{
    "mcpServers": {
        "well": {
            "command": "python",
            "args": ["-m", "arifos_core.mcp.tools.well.mcp_claude"],
            "env": {
                "WELL_REPO_ROOT": "/path/to/repo"
            }
        }
    }
}

Version: v42.0.0
License: AGPL-3.0

DITEMPA BUKAN DIBERI - Forged, not given
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

# Try to import MCP library
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    # FastMCP not installed - provide helpful error
    print("ERROR: MCP library not installed.")
    print("Install with: pip install mcp")
    sys.exit(1)

# Import @WELL core from L3
try:
    from arifos_core.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        create_well_file_care,
    )
except ImportError:
    # Add parent paths for standalone testing
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from arifos_core.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        create_well_file_care,
    )


# -----------------------------------------------------------------------------
# MCP Server Setup
# -----------------------------------------------------------------------------

# Create FastMCP server
mcp = FastMCP("@WELL File Care")

# Create @WELL instance (repo root from env or current directory)
REPO_ROOT = os.environ.get("WELL_REPO_ROOT")
well = create_well_file_care(REPO_ROOT)


# -----------------------------------------------------------------------------
# MCP Tools
# -----------------------------------------------------------------------------


@mcp.tool()
def well_status() -> Dict[str, Any]:
    """
    Get @WELL status and configuration.

    Returns version, repo root, protected files, and valid layers.
    """
    return {
        "version": WellConstants.VERSION,
        "codename": WellConstants.CODENAME,
        "repo_root": str(well.repo_root),
        "audit_log": str(well.audit_log_path),
        "protected_files": list(WellConstants.PROTECTED_FILES),
        "valid_layers": list(WellConstants.VALID_LAYERS),
    }


@mcp.tool()
def well_list_files(
    path: str = ".",
    pattern: str = "*",
    recursive: bool = False,
) -> Dict[str, Any]:
    """
    List files in a directory with protection status.

    Args:
        path: Directory path (relative to repo root)
        pattern: Glob pattern to filter files (e.g., "*.py")
        recursive: Whether to recurse into subdirectories

    Returns:
        List of files with path, size, checksum, and protection status.
    """
    files = well.list_files(path=path, pattern=pattern, recursive=recursive)
    return {
        "path": path,
        "pattern": pattern,
        "recursive": recursive,
        "files": files,
        "total": len(files),
    }


@mcp.tool()
def well_check_health() -> Dict[str, Any]:
    """
    Check repository structure health.

    Validates layer directories, file counts, and common issues.
    Returns health status, issues, warnings, and suggestions.
    """
    report = well.check_health()
    return report.to_dict()


@mcp.tool()
def well_heal_structure(create_missing_layers: bool = True) -> Dict[str, Any]:
    """
    Heal repository structure by creating missing directories.

    Args:
        create_missing_layers: Whether to create missing L1-L7 directories

    Returns:
        Updated health report with actions taken.
    """
    report = well.heal_structure(create_missing_layers=create_missing_layers)
    return report.to_dict()


@mcp.tool()
def well_relocate(
    source: str,
    target: str,
    create_backup: bool = True,
) -> Dict[str, Any]:
    """
    Relocate (move) a file with full audit trail.

    F1 Amanah compliant: Creates backup, verifies checksum, logs operation.
    Protected files (.git, LICENSE, etc.) cannot be moved.

    Args:
        source: Source file path (relative to repo root)
        target: Target file path (relative to repo root)
        create_backup: Whether to create a backup before moving (default: True)

    Returns:
        Operation result with success status, message, and audit entry.
    """
    result = well.relocate(
        source=source,
        target=target,
        create_backup=create_backup,
    )
    return result.to_dict()


@mcp.tool()
def well_duplicate(source: str, target: str) -> Dict[str, Any]:
    """
    Duplicate (copy) a file with audit trail.

    Creates a copy while preserving the original.
    Verifies checksum integrity after copy.

    Args:
        source: Source file path (relative to repo root)
        target: Target file path (relative to repo root)

    Returns:
        Operation result with success status, message, and audit entry.
    """
    result = well.duplicate(source=source, target=target)
    return result.to_dict()


@mcp.tool()
def well_retire(path: str, archive_dir: str = "archive") -> Dict[str, Any]:
    """
    Retire (archive) a file instead of deleting it.

    Moves file to archive directory with timestamp.
    Protected files cannot be retired.

    Args:
        path: File path to retire (relative to repo root)
        archive_dir: Archive directory (default: "archive")

    Returns:
        Operation result with success status and new location.
    """
    result = well.retire(path=path, archive_dir=archive_dir)
    return result.to_dict()


@mcp.tool()
def well_undo_last() -> Dict[str, Any]:
    """
    Undo the last reversible operation.

    Reverses the most recent relocate or duplicate operation.
    Uses backup files created during the original operation.

    Returns:
        Operation result with success status and what was undone.
    """
    result = well.undo_last()
    return result.to_dict()


@mcp.tool()
def well_batch_relocate(
    operations: List[Dict[str, str]],
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Batch relocate files.

    888_HOLD triggered if batch size exceeds 10 files.
    Use dry_run=True to validate operations without executing.

    Args:
        operations: List of {"source": "...", "target": "..."} dictionaries
        dry_run: If True, validate but don't execute

    Returns:
        Batch result with success count, failure count, and individual results.
    """
    results = well.batch_relocate(operations=operations, dry_run=dry_run)

    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful

    return {
        "total": len(results),
        "successful": successful,
        "failed": failed,
        "dry_run": dry_run,
        "results": [r.to_dict() for r in results],
    }


@mcp.tool()
def well_audit_history(limit: int = 100) -> Dict[str, Any]:
    """
    Get audit trail history.

    Args:
        limit: Maximum number of entries to return (default: 100)

    Returns:
        Audit history with operation IDs, timestamps, and results.
    """
    well.load_audit_history()
    history = well.get_audit_history(limit=limit)

    return {
        "total": len(history),
        "entries": [e.to_dict() for e in history],
    }


@mcp.tool()
def well_save_snapshot(name: str = "") -> Dict[str, Any]:
    """
    Save a full snapshot of the repository structure.

    Creates a JSON file with all file paths and checksums.
    Useful before major migrations.

    Args:
        name: Optional snapshot name (default: timestamp only)

    Returns:
        Snapshot filename and location.
    """
    snapshot_name = well.save_snapshot(name=name)
    return {
        "success": True,
        "snapshot_name": snapshot_name,
        "snapshot_dir": str(well.snapshot_dir),
    }


# -----------------------------------------------------------------------------
# MCP Resources
# -----------------------------------------------------------------------------


@mcp.resource("well://status")
def resource_status() -> str:
    """@WELL status as a resource."""
    status = well_status()
    return f"""@WELL File Care v{status['version']}

Repo Root: {status['repo_root']}
Audit Log: {status['audit_log']}

Protected Files: {', '.join(status['protected_files'][:5])}...
Valid Layers: {', '.join(status['valid_layers'])}

DITEMPA BUKAN DIBERI - Forged, not given
"""


@mcp.resource("well://health")
def resource_health() -> str:
    """Repository health report as a resource."""
    report = well.check_health()

    status = "HEALTHY" if report.is_healthy else "UNHEALTHY"
    issues = "\n".join(f"  - {i}" for i in report.issues) or "  None"
    warnings = "\n".join(f"  - {w}" for w in report.warnings) or "  None"

    layers = "\n".join(
        f"  {layer}: {'OK' if ok else 'MISSING'}"
        for layer, ok in report.layer_status.items()
    )

    return f"""@WELL Health Report

Status: {status}
Files: {report.file_count}
Directories: {report.directory_count}

Issues:
{issues}

Warnings:
{warnings}

Layer Status:
{layers}
"""


# -----------------------------------------------------------------------------
# Entry Point
# -----------------------------------------------------------------------------


def main():
    """Run the MCP server."""
    print(f"@WELL MCP Server v{WellConstants.VERSION}")
    print(f"Repo Root: {well.repo_root}")
    print("DITEMPA BUKAN DIBERI - Forged, not given")
    print()

    # Run the MCP server
    mcp.run()


if __name__ == "__main__":
    main()

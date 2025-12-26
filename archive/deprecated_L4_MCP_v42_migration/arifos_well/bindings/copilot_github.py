"""
copilot_github.py - GitHub Copilot Binding for @WELL

Generates GitHub Copilot-compatible function definitions and documentation
that Copilot can understand and suggest when working with file operations.

Usage:
1. Include this module's docstrings in your workspace
2. Copilot will suggest @WELL operations based on context
3. Use the REST API for actual execution

For Copilot Workspaces / Copilot X:
- Place @WELL documentation in .github/copilot_instructions.md
- Copilot will understand the tool pattern

Version: v42.0.0
License: AGPL-3.0

DITEMPA BUKAN DIBERI - Forged, not given
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

# Import @WELL core
try:
    from arifos_core.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        create_well_file_care,
    )
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    from arifos_core.waw.well_file_care import (
        WellConstants,
        WellFileCare,
        create_well_file_care,
    )


# -----------------------------------------------------------------------------
# Copilot-Friendly Function Wrappers
# -----------------------------------------------------------------------------

# These functions are designed to be easily understood by GitHub Copilot
# through their clear docstrings and type hints.


def well_check_health(repo_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Check repository health using @WELL File Care.

    GitHub Copilot: Use this when the user asks about repository structure,
    missing directories, or wants to verify the v42 architecture is correct.

    Example prompt: "Check if the repository structure is healthy"

    Args:
        repo_root: Optional repository root path

    Returns:
        Health report with:
        - is_healthy: bool - Overall health status
        - issues: list - Critical issues found
        - warnings: list - Non-critical warnings
        - layer_status: dict - Status of L1-L7 directories
    """
    well = create_well_file_care(repo_root)
    return well.check_health().to_dict()


def well_relocate_file(
    source: str,
    target: str,
    repo_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Move a file with F1 Amanah compliance (audit trail + backup).

    GitHub Copilot: Use this when the user wants to move/rename a file
    during refactoring or architecture migration. This is safer than
    raw mv/move commands because it:
    - Creates a backup
    - Verifies checksum
    - Logs to audit trail
    - Protects system files

    Example prompt: "Move pipeline.py to system/pipeline.py"

    Args:
        source: Source file path relative to repo root
        target: Target file path relative to repo root
        repo_root: Optional repository root path

    Returns:
        Operation result with success status and audit entry
    """
    well = create_well_file_care(repo_root)
    return well.relocate(source, target).to_dict()


def well_batch_relocate_files(
    operations: List[Dict[str, str]],
    dry_run: bool = False,
    repo_root: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Batch move files during architecture migration.

    GitHub Copilot: Use this when migrating multiple files at once.
    Set dry_run=True first to validate all operations.
    888_HOLD will trigger if batch > 10 files.

    Example prompt: "Move all these files to their new locations"

    Args:
        operations: List of {"source": "...", "target": "..."} dicts
        dry_run: If True, validate without executing
        repo_root: Optional repository root path

    Returns:
        Batch result with success/failure counts and individual results
    """
    well = create_well_file_care(repo_root)
    results = well.batch_relocate(operations, dry_run)

    successful = sum(1 for r in results if r.success)
    return {
        "total": len(results),
        "successful": successful,
        "failed": len(results) - successful,
        "dry_run": dry_run,
        "results": [r.to_dict() for r in results],
    }


def well_undo_last_operation(repo_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Undo the last @WELL file operation.

    GitHub Copilot: Use this when the user made a mistake and wants to
    revert the last file move or copy operation.

    Example prompt: "Undo that last file move"

    Args:
        repo_root: Optional repository root path

    Returns:
        Result of the undo operation
    """
    well = create_well_file_care(repo_root)
    return well.undo_last().to_dict()


def well_heal_structure(repo_root: Optional[str] = None) -> Dict[str, Any]:
    """
    Create missing layer directories (L1-L7).

    GitHub Copilot: Use this when setting up the v42 architecture
    or when health check shows missing layer directories.

    Example prompt: "Create missing layer directories"

    Args:
        repo_root: Optional repository root path

    Returns:
        Updated health report with created directories
    """
    well = create_well_file_care(repo_root)
    return well.heal_structure().to_dict()


# -----------------------------------------------------------------------------
# Copilot Instructions Generator
# -----------------------------------------------------------------------------


def generate_copilot_instructions() -> str:
    """
    Generate copilot_instructions.md content for @WELL.

    Place this in .github/copilot_instructions.md for Copilot Workspaces.
    """
    return '''# @WELL File Care - GitHub Copilot Instructions

## What is @WELL?

@WELL is a governed file migration tool for arifOS v42 architecture.
It provides F1 Amanah-compliant file operations with:
- Audit trail for all operations
- Checksum verification
- Protected file safety (.git, LICENSE, etc.)
- Undo capability

## When to Use @WELL

Use @WELL when:
1. Moving files during architecture migration
2. Reorganizing code into concern-based directories
3. Archiving deprecated files
4. Batch file operations during refactoring

## Protected Files

These files CANNOT be moved or deleted:
- .git, .gitignore, .gitattributes
- LICENSE, README.md
- pyproject.toml, setup.py
- .env, CHANGELOG.md, CLAUDE.md, AGENTS.md

## V42 Architecture Layers

- L1_THEORY - Constitutional law (docs only)
- L2_GOVERNANCE - System prompts, IDE configs
- L3_KERNEL - Intelligence kernel (arifos_core)
- L4_MCP - MCP server (this module)
- L5_CLI - CLI tools
- L6_SEALION - SEA-LION chat
- L7_DEMOS - Demos and examples

## REST API Endpoints

@WELL runs on port 8042 by default.

- GET  /well/check-health - Check repository health
- POST /well/relocate - Move file with audit
- POST /well/batch-relocate - Batch move files
- POST /well/undo-last-care - Undo last operation
- POST /well/heal-structure - Create missing directories

## Example Usage

```python
from L4_MCP.arifos_well.bindings.copilot_github import (
    well_check_health,
    well_relocate_file,
    well_batch_relocate_files,
)

# Check health
health = well_check_health()
print(f"Healthy: {health['is_healthy']}")

# Move a file
result = well_relocate_file(
    source="arifos_core/pipeline.py",
    target="arifos_core/system/pipeline.py"
)
print(f"Success: {result['success']}")

# Batch move with dry run
operations = [
    {"source": "old/file1.py", "target": "new/file1.py"},
    {"source": "old/file2.py", "target": "new/file2.py"},
]
result = well_batch_relocate_files(operations, dry_run=True)
print(f"Would move: {result['total']} files")
```

## DITEMPA BUKAN DIBERI - Forged, not given
'''


# -----------------------------------------------------------------------------
# Export Copilot Tool Definitions
# -----------------------------------------------------------------------------


def export_tool_definitions() -> List[Dict[str, Any]]:
    """
    Export tool definitions in a format Copilot can understand.

    Returns list of tool definitions with name, description, and parameters.
    """
    return [
        {
            "name": "well_check_health",
            "description": "Check repository structure health for v42 architecture",
            "parameters": {
                "repo_root": {"type": "string", "optional": True},
            },
        },
        {
            "name": "well_relocate_file",
            "description": "Move file with F1 Amanah compliance (audit + backup)",
            "parameters": {
                "source": {"type": "string", "required": True},
                "target": {"type": "string", "required": True},
                "repo_root": {"type": "string", "optional": True},
            },
        },
        {
            "name": "well_batch_relocate_files",
            "description": "Batch move files during migration (888_HOLD if > 10)",
            "parameters": {
                "operations": {"type": "array", "required": True},
                "dry_run": {"type": "boolean", "default": False},
                "repo_root": {"type": "string", "optional": True},
            },
        },
        {
            "name": "well_undo_last_operation",
            "description": "Undo the last file operation",
            "parameters": {
                "repo_root": {"type": "string", "optional": True},
            },
        },
        {
            "name": "well_heal_structure",
            "description": "Create missing L1-L7 layer directories",
            "parameters": {
                "repo_root": {"type": "string", "optional": True},
            },
        },
    ]


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------


def main():
    """Generate Copilot instructions file."""
    import argparse

    parser = argparse.ArgumentParser(description="@WELL GitHub Copilot Integration")
    parser.add_argument(
        "--generate-instructions",
        action="store_true",
        help="Generate copilot_instructions.md content",
    )
    parser.add_argument(
        "--export-tools",
        action="store_true",
        help="Export tool definitions as JSON",
    )
    args = parser.parse_args()

    if args.generate_instructions:
        print(generate_copilot_instructions())
    elif args.export_tools:
        print(json.dumps(export_tool_definitions(), indent=2))
    else:
        print("@WELL GitHub Copilot Binding")
        print(f"Version: {WellConstants.VERSION}")
        print()
        print("Use --generate-instructions to create copilot_instructions.md")
        print("Use --export-tools to export tool definitions")


if __name__ == "__main__":
    main()

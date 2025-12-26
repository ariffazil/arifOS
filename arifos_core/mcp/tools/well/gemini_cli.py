"""
gemini_cli.py - Google Gemini CLI Binding for @WELL

Provides function declarations in Google Gemini/Vertex AI format
for @WELL file care operations.

Usage with Gemini API:
```python
import google.generativeai as genai
from L4_MCP.arifos_well.bindings.gemini_cli import get_gemini_tools

tools = get_gemini_tools()
model = genai.GenerativeModel('gemini-pro', tools=tools)
response = model.generate_content("Check repo health")
```

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
# Gemini Function Declarations
# -----------------------------------------------------------------------------


def get_gemini_tools() -> List[Dict[str, Any]]:
    """
    Get @WELL tools in Google Gemini function declaration format.

    Returns list of function declarations compatible with:
    - Google Gemini API (tools parameter)
    - Vertex AI Generative Models
    - AI Studio
    """
    return [
        {
            "function_declarations": [
                {
                    "name": "well_status",
                    "description": "Get @WELL file care status and configuration. Returns version, repo root, list of protected files, and valid v42 architecture layers.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                {
                    "name": "well_list_files",
                    "description": "List files in a directory with protection status. Shows which files are protected from modification.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path relative to repo root. Default: current directory",
                            },
                            "pattern": {
                                "type": "string",
                                "description": "Glob pattern to filter files, e.g., '*.py' for Python files",
                            },
                            "recursive": {
                                "type": "boolean",
                                "description": "Whether to search subdirectories recursively",
                            },
                        },
                        "required": [],
                    },
                },
                {
                    "name": "well_check_health",
                    "description": "Check repository structure health for arifOS v42 architecture. Validates that L1 through L7 layer directories exist, counts files, and identifies structural issues.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                {
                    "name": "well_heal_structure",
                    "description": "Create missing layer directories to fix repository structure. Creates L1_THEORY through L7_DEMOS if they don't exist.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "create_missing_layers": {
                                "type": "boolean",
                                "description": "Whether to create missing L1-L7 directories. Default: true",
                            },
                        },
                        "required": [],
                    },
                },
                {
                    "name": "well_relocate",
                    "description": "Move a file with full audit trail and integrity verification. Creates backup, verifies SHA-256 checksum, and logs the operation. Protected files like .git, LICENSE cannot be moved.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source file path relative to repository root",
                            },
                            "target": {
                                "type": "string",
                                "description": "Target file path relative to repository root",
                            },
                            "create_backup": {
                                "type": "boolean",
                                "description": "Create a backup before moving. Default: true",
                            },
                        },
                        "required": ["source", "target"],
                    },
                },
                {
                    "name": "well_duplicate",
                    "description": "Copy a file while preserving the original. Verifies checksum integrity after copying.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "Source file path",
                            },
                            "target": {
                                "type": "string",
                                "description": "Target file path for the copy",
                            },
                        },
                        "required": ["source", "target"],
                    },
                },
                {
                    "name": "well_retire",
                    "description": "Archive a file instead of deleting. Moves the file to an archive directory with a timestamp suffix. Safer than deletion.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to archive",
                            },
                            "archive_dir": {
                                "type": "string",
                                "description": "Archive directory name. Default: 'archive'",
                            },
                        },
                        "required": ["path"],
                    },
                },
                {
                    "name": "well_undo_last",
                    "description": "Undo the most recent file operation. Reverses the last relocate or duplicate operation using backup files.",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                {
                    "name": "well_batch_relocate",
                    "description": "Move multiple files at once. Triggers 888_HOLD safety check if more than 10 files. Use dry_run to preview changes first.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operations": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "source": {"type": "string"},
                                        "target": {"type": "string"},
                                    },
                                    "required": ["source", "target"],
                                },
                                "description": "List of source/target pairs to move",
                            },
                            "dry_run": {
                                "type": "boolean",
                                "description": "If true, validate operations without executing. Default: false",
                            },
                        },
                        "required": ["operations"],
                    },
                },
                {
                    "name": "well_audit_history",
                    "description": "View audit trail of all @WELL file operations. Shows operation history with timestamps and results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of entries to return. Default: 100",
                            },
                        },
                        "required": [],
                    },
                },
            ],
        },
    ]


# -----------------------------------------------------------------------------
# Tool Executor for Gemini
# -----------------------------------------------------------------------------


class GeminiWellExecutor:
    """
    Executes @WELL tool calls from Gemini function call responses.

    Usage:
    ```python
    executor = GeminiWellExecutor(repo_root="/path/to/repo")

    # Process function call from Gemini response
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'function_call'):
            result = executor.execute(part.function_call)
    ```
    """

    def __init__(self, repo_root: Optional[str] = None):
        """Initialize executor with repository root."""
        self.well = create_well_file_care(repo_root)

    def execute(self, function_call: Any) -> Dict[str, Any]:
        """
        Execute a Gemini function call.

        Args:
            function_call: FunctionCall object from Gemini response

        Returns:
            Function execution result
        """
        name = function_call.name
        args = dict(function_call.args) if function_call.args else {}

        return self.execute_by_name(name, args)

    def execute_by_name(
        self,
        name: str,
        args: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a function by name and arguments.

        Args:
            name: Function name
            args: Function arguments

        Returns:
            Execution result
        """
        handlers = {
            "well_status": self._status,
            "well_list_files": self._list_files,
            "well_check_health": self._check_health,
            "well_heal_structure": self._heal_structure,
            "well_relocate": self._relocate,
            "well_duplicate": self._duplicate,
            "well_retire": self._retire,
            "well_undo_last": self._undo_last,
            "well_batch_relocate": self._batch_relocate,
            "well_audit_history": self._audit_history,
        }

        handler = handlers.get(name)
        if not handler:
            return {"error": f"Unknown function: {name}"}

        try:
            return handler(args)
        except Exception as e:
            return {"error": str(e)}

    def _status(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "version": WellConstants.VERSION,
            "codename": WellConstants.CODENAME,
            "repo_root": str(self.well.repo_root),
            "protected_files": list(WellConstants.PROTECTED_FILES),
            "valid_layers": list(WellConstants.VALID_LAYERS),
        }

    def _list_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        files = self.well.list_files(
            path=args.get("path", "."),
            pattern=args.get("pattern", "*"),
            recursive=args.get("recursive", False),
        )
        return {"files": files, "count": len(files)}

    def _check_health(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.check_health().to_dict()

    def _heal_structure(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.heal_structure(
            create_missing_layers=args.get("create_missing_layers", True),
        ).to_dict()

    def _relocate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.relocate(
            source=args["source"],
            target=args["target"],
            create_backup=args.get("create_backup", True),
        ).to_dict()

    def _duplicate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.duplicate(
            source=args["source"],
            target=args["target"],
        ).to_dict()

    def _retire(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.retire(
            path=args["path"],
            archive_dir=args.get("archive_dir", "archive"),
        ).to_dict()

    def _undo_last(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.undo_last().to_dict()

    def _batch_relocate(self, args: Dict[str, Any]) -> Dict[str, Any]:
        results = self.well.batch_relocate(
            operations=args["operations"],
            dry_run=args.get("dry_run", False),
        )
        successful = sum(1 for r in results if r.success)
        return {
            "total": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": [r.to_dict() for r in results],
        }

    def _audit_history(self, args: Dict[str, Any]) -> Dict[str, Any]:
        self.well.load_audit_history()
        history = self.well.get_audit_history(limit=args.get("limit", 100))
        return {
            "total": len(history),
            "entries": [e.to_dict() for e in history],
        }


# -----------------------------------------------------------------------------
# Gemini Manifest (for AI Studio)
# -----------------------------------------------------------------------------


def get_gemini_manifest() -> Dict[str, Any]:
    """
    Get @WELL manifest for Google AI Studio.

    This manifest describes the @WELL tools for use in AI Studio experiments.
    """
    return {
        "name": "@WELL File Care",
        "version": WellConstants.VERSION,
        "description": (
            "Governed file operations for arifOS v42 architecture. "
            "Provides F1 Amanah-compliant file migrations with audit trail, "
            "checksum verification, and undo capability."
        ),
        "author": "arifOS Project",
        "license": "AGPL-3.0",
        "repository": "https://github.com/ariffazil/arifOS",
        "tags": ["file-operations", "migration", "governance", "arifOS"],
        "capabilities": [
            "File relocation with audit trail",
            "File duplication with integrity check",
            "File archival (retire) instead of delete",
            "Batch operations with safety limits",
            "Undo last operation",
            "Repository health check",
            "Structure healing",
        ],
        "protected_files": list(WellConstants.PROTECTED_FILES),
        "architecture_layers": list(WellConstants.VALID_LAYERS),
        "api_endpoint": "http://localhost:8042",
        "tools": get_gemini_tools()[0]["function_declarations"],
    }


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------


def main():
    """Generate Gemini tool definitions and manifests."""
    import argparse

    parser = argparse.ArgumentParser(description="@WELL Google Gemini Integration")
    parser.add_argument(
        "--export-tools",
        action="store_true",
        help="Export Gemini function declarations",
    )
    parser.add_argument(
        "--export-manifest",
        action="store_true",
        help="Export Gemini manifest for AI Studio",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Test executor with sample calls",
    )
    args = parser.parse_args()

    if args.export_tools:
        print(json.dumps(get_gemini_tools(), indent=2))
    elif args.export_manifest:
        print(json.dumps(get_gemini_manifest(), indent=2))
    elif args.test:
        executor = GeminiWellExecutor()
        print("Testing @WELL Gemini Executor...")
        print()

        # Test status
        result = executor.execute_by_name("well_status", {})
        print(f"Status: v{result['version']}")
        print()

        # Test health check
        result = executor.execute_by_name("well_check_health", {})
        print(f"Health: {'HEALTHY' if result['is_healthy'] else 'UNHEALTHY'}")
        print(f"  Layers: {sum(result['layer_status'].values())}/{len(result['layer_status'])}")
        print()

        print("Tests complete!")
    else:
        print("@WELL Google Gemini Binding")
        print(f"Version: {WellConstants.VERSION}")
        print()
        print("Use --export-tools to get Gemini function declarations")
        print("Use --export-manifest to get AI Studio manifest")
        print("Use --test to run sample function calls")


if __name__ == "__main__":
    main()

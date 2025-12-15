"""
chatgpt_codex.py - ChatGPT Codex / OpenAI Function Calling Binding for @WELL

Provides OpenAI function calling format for @WELL file care operations.
Compatible with ChatGPT Codex, GPT-4 API, and OpenAI Assistants.

Usage with OpenAI API:
```python
import openai
from L4_MCP.arifos_well.bindings.chatgpt_codex import get_openai_tools

tools = get_openai_tools()
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[...],
    tools=tools,
)
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
# OpenAI Function Definitions
# -----------------------------------------------------------------------------


def get_openai_tools() -> List[Dict[str, Any]]:
    """
    Get @WELL tools in OpenAI function calling format.

    Returns list of tool definitions compatible with:
    - OpenAI ChatCompletion API (tools parameter)
    - OpenAI Assistants API
    - ChatGPT Codex
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "well_status",
                "description": "Get @WELL status and configuration including version, repo root, protected files, and valid layers.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_list_files",
                "description": "List files in a directory with protection status. Returns file paths, sizes, checksums, and whether files are protected.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Directory path relative to repo root (default: '.')",
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Glob pattern to filter files (e.g., '*.py')",
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "Whether to recurse into subdirectories",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_check_health",
                "description": "Check repository structure health. Validates v42 layer directories (L1-L7), counts files, and identifies issues like missing directories or files in wrong locations.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_heal_structure",
                "description": "Heal repository structure by creating missing layer directories (L1_THEORY through L7_DEMOS).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "create_missing_layers": {
                            "type": "boolean",
                            "description": "Whether to create missing L1-L7 directories (default: true)",
                        },
                    },
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_relocate",
                "description": "Move a file with F1 Amanah compliance. Creates backup, verifies checksum, and logs to audit trail. Protected files (.git, LICENSE, etc.) cannot be moved.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source file path relative to repo root",
                        },
                        "target": {
                            "type": "string",
                            "description": "Target file path relative to repo root",
                        },
                        "create_backup": {
                            "type": "boolean",
                            "description": "Whether to create backup before moving (default: true)",
                        },
                    },
                    "required": ["source", "target"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_duplicate",
                "description": "Copy a file with audit trail. Creates a copy while preserving the original. Verifies checksum integrity after copy.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Source file path relative to repo root",
                        },
                        "target": {
                            "type": "string",
                            "description": "Target file path relative to repo root",
                        },
                    },
                    "required": ["source", "target"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_retire",
                "description": "Archive a file instead of deleting it. Moves file to archive directory with timestamp. Protected files cannot be retired.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path to retire",
                        },
                        "archive_dir": {
                            "type": "string",
                            "description": "Archive directory (default: 'archive')",
                        },
                    },
                    "required": ["path"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_undo_last",
                "description": "Undo the last reversible @WELL operation. Reverses the most recent relocate or duplicate operation.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_batch_relocate",
                "description": "Batch move multiple files. 888_HOLD triggers if batch exceeds 10 files. Use dry_run=true to validate first.",
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
                            "description": "List of {source, target} operations",
                        },
                        "dry_run": {
                            "type": "boolean",
                            "description": "If true, validate without executing",
                        },
                    },
                    "required": ["operations"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "well_audit_history",
                "description": "Get audit trail history showing all @WELL operations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum entries to return (default: 100)",
                        },
                    },
                    "required": [],
                },
            },
        },
    ]


# -----------------------------------------------------------------------------
# Tool Executor
# -----------------------------------------------------------------------------


class WellToolExecutor:
    """
    Executes @WELL tool calls from OpenAI API responses.

    Usage:
    ```python
    executor = WellToolExecutor(repo_root="/path/to/repo")

    # Process tool call from OpenAI response
    result = executor.execute(
        tool_name="well_relocate",
        arguments={"source": "old.py", "target": "new.py"}
    )
    ```
    """

    def __init__(self, repo_root: Optional[str] = None):
        """Initialize executor with repository root."""
        self.well = create_well_file_care(repo_root)

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a @WELL tool call.

        Args:
            tool_name: Name of the tool to execute
            arguments: Tool arguments from OpenAI response

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool_name is unknown
        """
        # Map tool names to methods
        tool_map = {
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

        handler = tool_map.get(tool_name)
        if not handler:
            raise ValueError(f"Unknown tool: {tool_name}")

        return handler(arguments)

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
        return {"files": files, "total": len(files)}

    def _check_health(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.check_health().to_dict()

    def _heal_structure(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self.well.heal_structure(
            create_missing_layers=args.get("create_missing_layers", True)
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
# GPT Actions Schema (for ChatGPT Custom GPTs)
# -----------------------------------------------------------------------------


def get_gpt_actions_schema() -> Dict[str, Any]:
    """
    Get OpenAPI schema for ChatGPT Custom GPT Actions.

    This schema defines @WELL as an Action that a Custom GPT can use.
    Requires a running @WELL REST API server.
    """
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "@WELL File Care API",
            "description": "Governed file operations for arifOS v42 architecture",
            "version": WellConstants.VERSION,
        },
        "servers": [
            {
                "url": "http://localhost:8042",
                "description": "@WELL local server",
            },
        ],
        "paths": {
            "/well/check-health": {
                "get": {
                    "operationId": "checkHealth",
                    "summary": "Check repository health",
                    "responses": {
                        "200": {
                            "description": "Health report",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/HealthReport"},
                                },
                            },
                        },
                    },
                },
            },
            "/well/relocate": {
                "post": {
                    "operationId": "relocateFile",
                    "summary": "Move file with audit trail",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RelocateRequest"},
                            },
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Operation result",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/OperationResult"},
                                },
                            },
                        },
                    },
                },
            },
        },
        "components": {
            "schemas": {
                "HealthReport": {
                    "type": "object",
                    "properties": {
                        "is_healthy": {"type": "boolean"},
                        "issues": {"type": "array", "items": {"type": "string"}},
                        "warnings": {"type": "array", "items": {"type": "string"}},
                        "layer_status": {"type": "object"},
                    },
                },
                "RelocateRequest": {
                    "type": "object",
                    "required": ["source", "target"],
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "create_backup": {"type": "boolean", "default": True},
                    },
                },
                "OperationResult": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "operation_type": {"type": "string"},
                        "source_path": {"type": "string"},
                        "target_path": {"type": "string"},
                        "message": {"type": "string"},
                    },
                },
            },
        },
    }


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------


def main():
    """Generate OpenAI tool definitions and schemas."""
    import argparse

    parser = argparse.ArgumentParser(description="@WELL ChatGPT Codex Integration")
    parser.add_argument(
        "--export-tools",
        action="store_true",
        help="Export OpenAI tools JSON",
    )
    parser.add_argument(
        "--export-actions",
        action="store_true",
        help="Export GPT Actions OpenAPI schema",
    )
    args = parser.parse_args()

    if args.export_tools:
        print(json.dumps(get_openai_tools(), indent=2))
    elif args.export_actions:
        print(json.dumps(get_gpt_actions_schema(), indent=2))
    else:
        print("@WELL ChatGPT Codex Binding")
        print(f"Version: {WellConstants.VERSION}")
        print()
        print("Use --export-tools to get OpenAI function definitions")
        print("Use --export-actions to get GPT Actions schema")


if __name__ == "__main__":
    main()

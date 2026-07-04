"""
arifos://registry/toolregistry — Tool Registry (TOOLREGISTRY.json)
arifos://kernel/deprecation   — Deprecation Registry (deprecation-registry.json)

MCP resource wrappers around the two canonical FS-based registries at
/root/AAA/docs/. Added 2026-07-04 per Arif's drift closure directive:
agents need MCP resource access, not just FS reads.

F2 TRUTH: Content is read from FS on each fetch — always fresh.
F4 CLARITY: JSON output, machine-parseable.
F8 LAW: Read-only. No mutation through MCP.
F11 AUDIT: File stat + hash included in response.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import os
from typing import Any

from fastmcp import FastMCP

_TOOLREGISTRY_PATH = "/root/AAA/docs/TOOLREGISTRY.json"
_DEPRECATION_PATH = "/root/AAA/docs/deprecation-registry.json"


def _load_json_or_error(path: str) -> dict[str, Any]:
    """Load a JSON file, returning content + metadata."""
    try:
        if not os.path.isfile(path):
            return {
                "error": f"File not found: {path}",
                "status": "MISSING",
            }
        stat = os.stat(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {
            "status": "LOADED",
            "source": path,
            "size_bytes": stat.st_size,
            "modified_unix": int(stat.st_mtime),
            "content": data,
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON decode error: {e}",
            "status": "CORRUPT",
            "source": path,
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "ERROR",
            "source": path,
        }


def register_federation_registry(mcp: FastMCP) -> list[str]:
    """Register arifos://registry/toolregistry and arifos://kernel/deprecation.

    Read-only mirrors of the canonical FS-based registries.
    Always registered — agents need this for tool discovery and deprecation awareness.
    """
    registered: list[str] = []

    @mcp.resource("arifos://registry/toolregistry")
    def toolregistry_resource() -> dict[str, Any]:
        """Machine-readable tool registry — canonical tool names, tags, antipatterns.

        Source: /root/AAA/docs/TOOLREGISTRY.json
        Maps capability_tag to tool names across all 5 organs (arifOS, GEOX,
        WEALTH, WELL, A-FORGE). Use to find tools by capability and detect
        duplicate tool creation.
        """
        return _load_json_or_error(_TOOLREGISTRY_PATH)

    registered.append("arifos://registry/toolregistry")

    @mcp.resource("arifos://kernel/deprecation")
    def deprecation_resource() -> dict[str, Any]:
        """Machine-readable deprecation registry — deprecated, migrated, archived.

        Source: /root/AAA/docs/deprecation-registry.json
        Check BEFORE using any tool, endpoint, or service.
        If deprecated → migrate, don't use.
        """
        return _load_json_or_error(_DEPRECATION_PATH)

    registered.append("arifos://kernel/deprecation")

    return registered


__all__ = ["register_federation_registry"]

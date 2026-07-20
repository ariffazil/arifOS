"""
arifos://registry/* — Canonical Federation Registries (single read path)

Per CANONICAL_REGISTRY_GOVERNANCE.md:
- One canonical write authority per registry (kernel-governed for cross-organ truth).
- Organs register surfaces; kernel canonicalizes + adds provenance.
- All federation queries ("what tools?", "active agents?") MUST use these or kernel tools.
- Direct FS or per-organ lists = domain only, not federation truth.

Current exposed:
- arifos://registry/toolregistry → capability surface across organs
- arifos://kernel/deprecation → deprecated surfaces

F2 TRUTH: Always fresh from source on fetch. Provenance (source, hash, modified, authority) included.
F4 CLARITY: One path. No "which registry did you read?"
F8 LAW: Read-only here. Writes go through kernel arifos_registry/ + governed tools only.
F11 AUDIT: Full stat + hash + authority ref. Drift with master index = VOID.

See: /root/arifOS/registry/00-master-index.yaml + CANONICAL_REGISTRY_GOVERNANCE.md
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from fastmcp import FastMCP

_TOOLREGISTRY_PATH = "/root/AAA/docs/TOOLREGISTRY.json"
_DEPRECATION_PATH = "/root/AAA/docs/deprecation-registry.json"


def _load_json_or_error(path: str, registry_name: str = "unknown") -> dict[str, Any]:
    """Load a JSON file, returning content + full provenance metadata.

    Per CANONICAL_REGISTRY_GOVERNANCE.md: every response carries authority, hash, freshness.
    This makes the read path auditable and drift-detectable.
    """
    try:
        if not os.path.isfile(path):
            return {
                "error": f"File not found: {path}",
                "status": "MISSING",
                "authority": "CANONICAL_REGISTRY_GOVERNANCE.md",
                "registry": registry_name,
            }
        stat = os.stat(path)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        content_hash = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]
        return {
            "status": "LOADED",
            "authority": "arifOS kernel (see CANONICAL_REGISTRY_GOVERNANCE.md)",
            "registry": registry_name,
            "source": path,
            "size_bytes": stat.st_size,
            "modified_unix": int(stat.st_mtime),
            "content_hash": content_hash,
            "provenance": {
                "written_via": "kernel-governed path (or legacy file under transition)",
                "read_path": f"arifos://registry/{registry_name}",
                "note": "Single source of truth for federation. Organs must not treat per-organ lists as canonical for cross-organ queries.",
            },
            "content": data,
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"JSON decode error: {e}",
            "status": "CORRUPT",
            "authority": "CANONICAL_REGISTRY_GOVERNANCE.md",
            "registry": registry_name,
            "source": path,
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "ERROR",
            "authority": "CANONICAL_REGISTRY_GOVERNANCE.md",
            "registry": registry_name,
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
        """THE SINGLE READ PATH for federation tool registry.

        Per CANONICAL_REGISTRY_GOVERNANCE.md + FEDERATION_MEMORY.md: this is the bureaucratic/institutional memory layer in the ladder.
        Kernel (arifos_registry.MCPToolRegistry) ONLY canonical source. Write only via register().
        All organs/agents use this for federation view. Part of agentic flow: institutionalise before act.
        """
        # TODO: replace load with live from MCPToolRegistry.get_federation_view() + stores
        return _load_json_or_error(_TOOLREGISTRY_PATH, "toolregistry")

    registered.append("arifos://registry/toolregistry")

    @mcp.resource("arifos://kernel/deprecation")
    def deprecation_resource() -> dict[str, Any]:
        """Machine-readable deprecation registry — deprecated, migrated, archived.

        Source: /root/AAA/docs/deprecation-registry.json
        Check BEFORE using any tool, endpoint, or service.
        If deprecated → migrate, don't use.
        """
        return _load_json_or_error(_DEPRECATION_PATH, "deprecation")

    registered.append("arifos://kernel/deprecation")

    return registered


__all__ = ["register_federation_registry"]

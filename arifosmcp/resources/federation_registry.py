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


def _build_tools_registry_view() -> dict[str, Any]:
    """Dynamically build organ health and tool count view for web pulse and registries."""
    import time
    import urllib.request

    organs_config = [
        {"organ": "arifOS", "port": 8088, "role": "Constitutional Kernel", "authority": "SOVEREIGN_GATE"},
        {"organ": "A-FORGE", "port": 7072, "role": "Engineering Actuator", "authority": "MUTATE_BOUNDED"},
        {"organ": "GEOX", "port": 8081, "role": "Earth Reasoning", "authority": "READ_OBSERVE"},
        {"organ": "WEALTH", "port": 18082, "role": "Capital Physics", "authority": "READ_OBSERVE"},
        {"organ": "WELL", "port": 18083, "role": "Human Readiness", "authority": "READ_OBSERVE"},
        {"organ": "arifFlow", "port": 7073, "role": "Metabolism & FQ", "authority": "READ_OBSERVE"},
        {"organ": "FRAME", "port": 18085, "role": "Observer & Drift", "authority": "OBSERVE_ONLY"},
        {"organ": "FED", "port": 7074, "role": "Federation Router", "authority": "ADVISORY_ONLY"},
        {"organ": "CHRON", "port": 18102, "role": "Temporal Consequence", "authority": "READ_OBSERVE"},
    ]
    organs_out = []
    healthy_count = 0
    total_tools = 121

    if os.path.exists("/root/arifOS/arifosmcp/tool_registry.json"):
        try:
            with open("/root/arifOS/arifosmcp/tool_registry.json") as f:
                tr = json.load(f)
                total_tools = tr.get("total_surface", 121)
        except Exception:
            pass

    for cfg in organs_config:
        entry = dict(cfg)
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{cfg['port']}/health", headers={"User-Agent": "arifOS/pulse"})
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                data = json.loads(resp.read().decode())
                entry["healthy"] = True
                entry["tool_count_mcp"] = data.get("tool_count", data.get("tools", 0))
                healthy_count += 1
        except Exception:
            entry["healthy"] = False
            entry["tool_count_mcp"] = 0
        organs_out.append(entry)

    summary = {
        "organs_healthy": healthy_count,
        "organs_total": len(organs_config),
        "tools_total_mcp": total_tools,
    }
    return {
        "summary": summary,
        "organs": organs_out,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def register_federation_registry(mcp: FastMCP) -> list[str]:
    """Register arifos://registry/toolregistry, arifos://tools/registry, and arifos://kernel/deprecation.

    Read-only mirrors of the canonical FS-based registries.
    Always registered — agents need this for tool discovery and deprecation awareness.
    """
    registered: list[str] = []

    @mcp.resource("arifos://registry/toolregistry")
    def toolregistry_resource() -> dict[str, Any]:
        """THE SINGLE READ PATH for federation tool registry."""
        path = _TOOLREGISTRY_PATH if os.path.isfile(_TOOLREGISTRY_PATH) else "/root/arifOS/arifosmcp/tool_registry.json"
        return _load_json_or_error(path, "toolregistry")

    registered.append("arifos://registry/toolregistry")

    @mcp.resource("arifos://tools/registry")
    def tools_registry_alias() -> str:
        """Alias for web pulse & federation tools view: returns JSON string with summary and organs."""
        return json.dumps(_build_tools_registry_view())

    registered.append("arifos://tools/registry")

    @mcp.resource("arifos://kernel/deprecation")
    def deprecation_resource() -> dict[str, Any]:
        """Machine-readable deprecation registry — deprecated, migrated, archived."""
        return _load_json_or_error(_DEPRECATION_PATH, "deprecation")

    registered.append("arifos://kernel/deprecation")

    return registered


__all__ = ["register_federation_registry"]

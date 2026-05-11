from __future__ import annotations

import os
from typing import Any

from arifosmcp.constitutional_map import list_canonical_tools, list_constitutional_tools
from arifosmcp.runtime.build_info import get_build_info

try:
    from arifosmcp.tools_canonical import TOOL_ALIAS_MAP
except Exception:  # pragma: no cover - defensive fallback
    TOOL_ALIAS_MAP = {}


CANONICAL_13: tuple[str, ...] = tuple(list_constitutional_tools())
CANONICAL_15: tuple[str, ...] = tuple(list_canonical_tools())

BLOCKED_PUBLIC_PREFIXES: tuple[str, ...] = (
    "arifos_",
    "_arifos_",
    "wealth_",
    "afwell_",
    "geox_",
    "geoxarifos_",
)

VALID_PUBLIC_SURFACE_MODES: tuple[str, ...] = (
    "canonical13",
    "canonical15",
    "expanded45",
)


def _alias_public_name(alias_name: str) -> str:
    namespace = "arifos"
    clean_name = alias_name
    if alias_name.startswith(("P_geox_", "E_geox_")):
        namespace = "geoxarifOS"
        clean_name = alias_name.replace("P_geox_", "").replace("E_geox_", "")
    elif alias_name.startswith(("V_", "P_wealth_")):
        namespace = "wealth"
        clean_name = alias_name.replace("V_", "").replace("P_wealth_", "")
    elif alias_name.startswith(("P_well_", "E_well_")):
        namespace = "AFWELL"
        clean_name = alias_name.replace("P_well_", "").replace("E_well_", "")
    return f"{namespace}_{clean_name}"


EXPANDED_45: tuple[str, ...] = tuple(
    list(dict.fromkeys([*CANONICAL_15, *(_alias_public_name(name) for name in TOOL_ALIAS_MAP)]))
)


def normalize_public_surface_mode(mode: str | None = None) -> str:
    raw = (mode or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_SURFACE_MODE", "") or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_TOOL_PROFILE", "") or "").strip().lower()

    profile_map = {
        "public": "canonical13",
        "chatgpt": "canonical13",
        "agnostic_public": "canonical13",
        "canonical13": "canonical13",
        "canonical15": "canonical15",
        "internal": "expanded45",
        "expanded45": "expanded45",
    }
    return profile_map.get(raw, "canonical13")


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    resolved = normalize_public_surface_mode(mode)
    if resolved == "canonical13":
        return CANONICAL_13
    if resolved == "expanded45":
        return EXPANDED_45
    return CANONICAL_15


def public_boundary_allows(name: str, mode: str | None = None) -> bool:
    lowered = (name or "").strip().lower()
    if not lowered or lowered.startswith(BLOCKED_PUBLIC_PREFIXES):
        return False
    return name in set(public_tool_names_for_mode(mode))


def public_surface_state(mode: str | None = None) -> dict[str, Any]:
    resolved = normalize_public_surface_mode(mode)
    tool_names = list(public_tool_names_for_mode(resolved))
    diagnostic_tools = [name for name in tool_names if name in {"arif_ping", "arif_selftest"}]
    return {
        "mode": resolved,
        "tools_registered": len(tool_names),
        "kernel_tools": len(CANONICAL_13),
        "diagnostic_tools": diagnostic_tools,
        "tool_names": tool_names,
        "canonical13_count": len(CANONICAL_13),
        "canonical15_count": len(CANONICAL_15),
        "blocked_public_prefixes": list(BLOCKED_PUBLIC_PREFIXES),
    }


# ─── Federation Status Spine ─────────────────────────────────────────────────
# Canonical public endpoints for the arifOS Federation.
# All public-facing metadata derives from here — no manual duplication.

SYSTEM_NAME = "arifOS Federation"
SYSTEM_ROLE = "constitutional_kernel"

CANONICAL_MCP_ENDPOINT = "https://mcp.arif-fazil.com/mcp"
CANONICAL_STATUS_ENDPOINT = "https://mcp.arif-fazil.com/status.json"
CANONICAL_HEALTH_ENDPOINT = "https://mcp.arif-fazil.com/health"
CANONICAL_READY_ENDPOINT = "https://mcp.arif-fazil.com/ready"
HUMAN_LANDING = "https://arifos.arif-fazil.com/"

# Peer sovereign processors — peer intelligences, NOT sub-tools of arifOS.
# Each has its own governance floor, MCP transport, and update cycle.
PEER_SOVEREIGNS: dict[str, dict[str, Any]] = {
    "arifos": {
        "role": "constitutional_kernel",
        "mcp": True,
        "public_endpoint": CANONICAL_MCP_ENDPOINT,
        "internal_host": "arifosmcp",
        "internal_port": 8080,
        "mcp_path": "/mcp",
        "health_path": "/health",
        "ready_path": "/ready",
        "tools": 13,
        "prompts": 8,
        "resources": 5,
        "protocol_version": "2025-03-26",
    },
    "geox": {
        "role": "earth_intelligence_processor",
        "mcp": True,
        "public_endpoint": "https://geox.arif-fazil.com/mcp",
        "internal_host": "geox",
        "internal_port": 8081,
        "mcp_path": "/mcp",
        "health_path": None,
        "ready_path": None,
        "tools": None,
        "prompts": None,
        "resources": None,
        "protocol_version": "2025-03-26",
        "probe_note": "No /health endpoint — probe /mcp via MCP initialize",
    },
    "wealth": {
        "role": "capital_intelligence_processor",
        "mcp": True,
        "public_endpoint": "https://wealth.arif-fazil.com/mcp",
        "internal_host": "wealth-organ",
        "internal_port": 8000,
        "mcp_path": "/mcp",
        "health_path": "/health",
        "ready_path": None,
        "tools": None,
        "prompts": None,
        "resources": None,
        "protocol_version": "2025-03-26",
    },
    "aforge": {
        "role": "bridge",
        "mcp": False,
        "public_endpoint": "http://a-forge:3001",
        "internal_host": "aaa-a2a",
        "internal_port": 3001,
        "bridge_only": True,
    },
}

PUBLIC_STATUS_VALUES: set[str] = {
    "ok",
    "degraded",
    "down",
    "missing",
    "unknown",
    "bridge_only",
}


# Build-time truth — derived at import from build_info
_BUILD_INFO = get_build_info()

VERSION: str = _BUILD_INFO["version"]
COMMIT_SHORT: str = _BUILD_INFO["build"]["commit_short"]
PROTOCOL_VERSION: str = _BUILD_INFO["protocol_version"]
GOVERNANCE_VERSION: str = _BUILD_INFO["governance_version"]
FLOORS_ACTIVE: int = _BUILD_INFO["floors_active"]
SOURCE_REPO: str = _BUILD_INFO["source_repo"]


def public_surface() -> dict[str, Any]:
    """Canonical public surface payload — single source of truth.

    All public-facing version counts, endpoint URLs, and metadata
    MUST be derived from here. README, llms.txt, status.json, and
    landing pages consume this function, not hardcoded values.
    """
    return {
        "system": SYSTEM_NAME,
        "version": VERSION,
        "commit": COMMIT_SHORT,
        "protocol_version": PROTOCOL_VERSION,
        "governance_version": GOVERNANCE_VERSION,
        "floors_active": FLOORS_ACTIVE,
        "canonical": {
            "mcp": CANONICAL_MCP_ENDPOINT,
            "status": CANONICAL_STATUS_ENDPOINT,
            "health": CANONICAL_HEALTH_ENDPOINT,
            "ready": CANONICAL_READY_ENDPOINT,
            "landing": HUMAN_LANDING,
        },
        "mcp": {
            "endpoint": CANONICAL_MCP_ENDPOINT,
            "transport": "streamable-http",
            "protocol_version": PROTOCOL_VERSION,
            "tools": 13,
            "prompts": 8,
            "resources": 5,
        },
        "source_repo": SOURCE_REPO,
        "seal": "DITEMPA BUKAN DIBERI",
    }


def federation_summary() -> dict[str, Any]:
    """Lightweight summary for embedding in other surfaces."""
    s = public_surface()
    return {
        "system": s["system"],
        "version": s["version"],
        "commit": s["commit"],
        "mcp_tools": s["mcp"]["tools"],
        "mcp_prompts": s["mcp"]["prompts"],
        "floors_active": s["floors_active"],
    }

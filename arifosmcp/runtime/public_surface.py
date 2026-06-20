from __future__ import annotations

import os
from typing import Any

from arifosmcp.constitutional_map import CANONICAL_TOOLS, list_constitutional_tools
from arifosmcp.prompts import CANONICAL_PROMPTS
from arifosmcp.resources import (
    CANONICAL_RESOURCES,
    EMBODIED_RESOURCES,
    EVIDENCE_RESOURCES,
    TREE777_RESOURCES,
)
from arifosmcp.runtime.build import get_build_info

try:
    from arifosmcp.tools_canonical import TOOL_ALIAS_MAP
except Exception:  # pragma: no cover - defensive fallback
    TOOL_ALIAS_MAP = {}


CANONICAL_13: tuple[str, ...] = tuple(list_constitutional_tools())
# CANONICAL_13 is the single canonical set (was previously duplicated as CANONICAL_15)

# ── Canary Probes — always-on transport diagnostics (Canonical13 enforcement) ──
# These 6 zero-floor probes are ALWAYS registered on the public wire surface.
# They require no session, no actor, no governance — pure transport diagnostics.
CANARY_PROBES: tuple[str, ...] = (
    "arif_ping",
    "arif_conformance_report",
    "arif_schema_echo",
    "arif_version_echo",
    "arif_transport_echo",
    "arif_initialize_probe",
)

# ── Canonical13 Public Surface (= canonical kernel + canary probes) ──────────
# This is the DEFAULT public wire surface. 13 constitutional + 6 canary = 19 tools.
CANONICAL13_PUBLIC_SURFACE: tuple[str, ...] = tuple(
    list(dict.fromkeys([*CANONICAL_13, *CANARY_PROBES]))
)

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


# Diagnostic tools — reversible governance inspectors, not canonical constitutional tools.
# These are the ONLY non-canonical tools that have live FastMCP handlers.
DIAGNOSTIC_TOOLS: tuple[str, ...] = (
    "arif_ping",
    # ── Transport Canary Layer (Phase 0, 2026-06-14) ──
    "arif_schema_echo",
    "arif_version_echo",
    "arif_transport_echo",
    "arif_initialize_probe",
    # ── Legacy diagnostics ──
    "arif_stack_health_probe",
    "arif_scan_local_instructions",
    "arif_organ_consensus",
    "arif_session_budget",
    "arif_floor_status",
    "mcp_drift_check",
    "hermes_system_status",
    "hermes_vault_query",
    "hermes_epistemic_check",
    "hermes_fact_check",
    "hermes_cross_verify",
    "hermes_plan_review",
    "hermes_memory_steward",
    # ── Shadow Geometry Tools (Phase 2, 2026-06-16) ──
    "arif_self_evaluate",
    "arif_model_compare",
)

# EXPANDED_45 — the honest expanded public surface.
# Previously this included ~28 ghost aliases (wealth_*, AFWELL_*, geoxarifOS_*,
# arifos_T_*, arifos_M_*) that have NO FastMCP handlers. Those aliases created
# ontology drift: the registry claimed 41 tools but only 19 were callable.
# PHOENIX-72 fix: EXPANDED_45 now contains ONLY tools with actual handlers.
# Canonical 13 + Diagnostic 6 = 19 registrable tools.
# The old ghost aliases are preserved below as DOMAIN_ALIASES for documentation
# and future implementation tracking, but they are NOT part of any public mode.
EXPANDED_45: tuple[str, ...] = tuple(list(dict.fromkeys([*CANONICAL_13, *CANARY_PROBES, *DIAGNOSTIC_TOOLS])))

# DOMAIN_ALIASES — planned domain-specific tools that currently have NO FastMCP
# handlers. They exist in the alias map as implementation targets, not as live
# public tools. Do NOT include these in drift check manifests or public modes.
DOMAIN_ALIASES: tuple[str, ...] = tuple(_alias_public_name(name) for name in TOOL_ALIAS_MAP)


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
        "canonical15": "canonical13",  # deprecated alias — canonical count is 13
        "internal": "expanded45",
        "expanded45": "expanded45",
    }
    return profile_map.get(raw, "canonical13")


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    """
    Return the public tool names for a given surface mode.

    canonical13 (default): CANONICAL_13 + CANARY_PROBES (19 tools).
        This is the honest default wire surface — 13 kernel + 6 canary probes.
    expanded45: CANONICAL_13 + DIAGNOSTIC_TOOLS (gated tools included).
        Only active when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.

    INTERNAL_ONLY filter: tools registered in CANONICAL_TOOLS with
    access == "internal_only" are NEVER exposed via any public mode.
    """
    resolved = normalize_public_surface_mode(mode)
    if resolved == "expanded45":
        candidates = EXPANDED_45
    else:
        # canonical13: 13 kernel + 6 canary probes = 19 tools on the default wire.
        # Canary probes are transport diagnostics (ping, echo, version, init_probe).
        candidates = CANONICAL13_PUBLIC_SURFACE
    # Filter out internal_only tools regardless of mode.
    return tuple(
        name
        for name in candidates
        if CANONICAL_TOOLS.get(name, {}).get("access") != "internal_only"
    )


def public_boundary_allows(name: str, mode: str | None = None) -> bool:
    lowered = (name or "").strip().lower()
    if not lowered or lowered.startswith(BLOCKED_PUBLIC_PREFIXES):
        return False
    return name in set(public_tool_names_for_mode(mode))


def public_surface_state(mode: str | None = None) -> dict[str, Any]:
    resolved = normalize_public_surface_mode(mode)
    tool_names = list(public_tool_names_for_mode(resolved))
    diagnostic_tools = [name for name in tool_names if name in set(DIAGNOSTIC_TOOLS)]
    return {
        "mode": resolved,
        "tools_registered": len(tool_names),
        "kernel_tools": len(CANONICAL_13),
        "diagnostic_tools": diagnostic_tools,
        "tool_names": tool_names,
        "canonical13_count": len(CANONICAL_13),
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
        "internal_host": "127.0.0.1",
        "internal_port": 8088,
        "mcp_path": "/mcp",
        "health_path": "/health",
        "ready_path": "/ready",
        "tools": 13,
        "prompts": len(CANONICAL_PROMPTS),
        "resources": len(CANONICAL_RESOURCES),
        "protocol_version": "2025-03-26",
    },
    "geox": {
        "role": "earth_intelligence_processor",
        "mcp": True,
        "public_endpoint": "https://geox.arif-fazil.com/mcp",
        "internal_host": "127.0.0.1",
        "internal_port": 18081,
        "mcp_path": "/mcp",
        "health_path": "/health",
        "ready_path": None,
        "tools": None,
        "prompts": None,
        "resources": None,
        "protocol_version": "2025-03-26",
        "probe_note": "Systemd GEOX bridge endpoint. Do not use retired Docker-era 8081 metadata.",
    },
    "wealth": {
        "role": "capital_intelligence_processor",
        "mcp": True,
        "public_endpoint": "https://wealth.arif-fazil.com/mcp",
        "internal_host": "127.0.0.1",
        "internal_port": 18082,
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
    registered_resource_families = (
        len(CANONICAL_RESOURCES)
        + len(EVIDENCE_RESOURCES)
        + len(EMBODIED_RESOURCES)
        + len(TREE777_RESOURCES)
    )
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
            "prompts": len(CANONICAL_PROMPTS),
            "resources": len(CANONICAL_RESOURCES),
            "canonical_resources": len(CANONICAL_RESOURCES),
            "registered_resource_families": registered_resource_families,
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

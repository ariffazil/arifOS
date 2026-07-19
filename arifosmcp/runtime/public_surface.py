from __future__ import annotations

import os
from typing import Any

from arifosmcp.constitutional_map import CANONICAL_TOOLS
from arifosmcp.prompts import CANONICAL_PROMPTS
from arifosmcp.resources import (
    CANONICAL_RESOURCES,
    EMBODIED_RESOURCES,
    EVIDENCE_RESOURCES,
    TREE777_RESOURCES,
)
from arifosmcp.runtime.build import get_build_info
from arifosmcp.abi.kernel_abi import (
    normalize_profile,
    profile_contract,
    semantic_tool_names,
    tool_names_for_profile as abi_tool_names_for_profile,
)

# The permanent contract is semantic: eight capability IDs in
# abi/capability_registry.json.
KERNEL_ABI_8: tuple[str, ...] = semantic_tool_names()
PUBLIC_AGENT_6: tuple[str, ...] = abi_tool_names_for_profile("public_agent")

# Compatibility constants remain importable, but their numeric suffixes are
# not authoritative.
FORGE_NEXT_8: tuple[str, ...] = KERNEL_ABI_8
CANONICAL_12: tuple[str, ...] = KERNEL_ABI_8
CANONICAL_13: tuple[str, ...] = KERNEL_ABI_8
CANONICAL_9: tuple[str, ...] = KERNEL_ABI_8
CANONICAL_7: tuple[str, ...] = KERNEL_ABI_8
CANONICAL13_PUBLIC_SURFACE: tuple[str, ...] = KERNEL_ABI_8

# Canary probe absorbed into arif_init(mode=canary).
CANARY_PROBES: tuple[str, ...] = ()
DEPRECATED_CANARY_CHILDREN: tuple[str, ...] = (
    "arif_ping",
    "arif_schema_echo",
    "arif_version_echo",
    "arif_transport_echo",
    "arif_initialize_probe",
    # arif_conformance_report REMOVED 2026-07-17 (drift fix): was declared
    # deprecated-but-resolvable, but runtime rejects it as "Unknown tool"
    # because it is not in the capability graph. Per audit verdict:
    # "advertised-but-uncallable is worse than absent." Canonical interface
    # is now arif_canary(mode=conformance_report).
)

# SDK long-name aliases stay empty on the public wire surface.
CANONICAL_LONG_NAME_ALIASES: tuple[str, ...] = ()  # intentionally empty

VALID_PUBLIC_SURFACE_MODES: tuple[str, ...] = (
    "public_agent",
    "trusted_agent",
    "executor",
    "sovereign",
    "operator",
    "legacy",
)

BLOCKED_PUBLIC_PREFIXES: tuple[str, ...] = (
    # arif_* is the canonical public facade. Block only internal/organ prefixes
    # that should never appear on the public wire surface.
    "_arif_",
    "wealth_",
    "afwell_",
    "geox_",
    "geoxarifos_",
)


# A-FORGE owns execution; arifOS keeps governance and can route to it.


# Diagnostic tools are reversible inspectors, not canonical constitutional tools.
DIAGNOSTIC_TOOLS: tuple[str, ...] = (
    "arifos_ping",
    "arifos_schema_echo",
    "arifos_version_echo",
    "arifos_transport_echo",
    "arifos_initialize_probe",
    "arifos_stack_health_probe",
    "arifos_scan_local_instructions",
    "arifos_organ_consensus",
    "arifos_session_budget",
    "arifos_floor_status",
    "mcp_drift_check",
    "arifos_vault_query",
    "arifos_self_evaluate",
    "arifos_model_compare",
    "arifos_bridge_connect",
    "arifos_gate_judge",
    "arifos_gateway_connect",
    "arifos_heart_critique",
    "arifos_kernel_attest",
    "arifos_kernel_health",
    "arifos_kernel_intercept",
    "arifos_paradox_status",
    "arifos_selftest",
    "arifos_tool_exists",
    "arifos_resolve_tool",
    "arifos_discover_margins",
    "arifos_bridge_mcp_server",
    "arifos_synthesize_canon",
    "arifos_retrieve_tools",
)

# ZEN absorbed into canonical modes; handlers remain for compatibility.
ZEN_ABSORBED: frozenset[str] = frozenset(
    {
        "arif_triage",  # → arif_init(mode=preflight|triage)
        "arif_act",  # → arif_forge (internal alias)
        "arif_fetch",  # → arif_observe(mode=fetch)
        "arif_critique",  # → arif_think(mode=critique)
        "arif_bridge_connect",  # → arif_route(mode=bridge)
    }
)

# Operator diagnostics are a separate layer, not a ninth kernel capability.
EXPANDED_45: tuple[str, ...] = tuple(list(dict.fromkeys([*KERNEL_ABI_8, *DIAGNOSTIC_TOOLS])))

def normalize_public_surface_mode(mode: str | None = None) -> str:
    """Resolve a host-supplied name to a platform-neutral policy profile."""
    raw = (mode or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_SURFACE_MODE", "") or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_TOOL_PROFILE", "") or "").strip().lower()
    return normalize_profile(raw or None)


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    """Return MCP provider bindings for the requested semantic profile."""
    resolved = normalize_public_surface_mode(mode)
    contract = profile_contract(resolved)
    candidates = abi_tool_names_for_profile(resolved)
    if contract.get("diagnostics"):
        expose_dev_tools = os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        candidates = EXPANDED_45 if expose_dev_tools else PUBLIC_AGENT_6
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
    """Report the resolved ABI profile and its provider bindings."""
    resolved = normalize_public_surface_mode(mode)
    tool_names = list(public_tool_names_for_mode(resolved))
    diagnostic_names = [name for name in tool_names if name in set(DIAGNOSTIC_TOOLS)]
    return {
        "mode": resolved,
        "abi_version": "1.0.0",
        "capability_count": len(KERNEL_ABI_8),
        "profile": resolved,
        "tools_registered": len(tool_names),
        "kernel_tools": len(tool_names),
        "canonical_count": len(tool_names),
        "diagnostic_tools": diagnostic_names,
        "tool_names": tool_names,
        "blocked_public_prefixes": list(BLOCKED_PUBLIC_PREFIXES),
    }


# Canonical public endpoints for the arifOS Federation.

SYSTEM_NAME = "arifOS Federation"
SYSTEM_ROLE = "constitutional_kernel"

CANONICAL_MCP_ENDPOINT = "https://mcp.arif-fazil.com/mcp"
CANONICAL_STATUS_ENDPOINT = "https://mcp.arif-fazil.com/status.json"
CANONICAL_HEALTH_ENDPOINT = "https://mcp.arif-fazil.com/health"
CANONICAL_READY_ENDPOINT = "https://mcp.arif-fazil.com/ready"
HUMAN_LANDING = "https://arifos.arif-fazil.com/"

# C2-5 fix (2026-06-21): the previous human-landing URL was being served
# as an MCP endpoint by some platform harnesses (e.g. the agent that hit
# `arifos.arif-fazil.com/mcp` instead of `mcp.arif-fazil.com/mcp`).
# These are the DEPRECATED MCP endpoints — listed so the kernel can
# detect when a client is pointed at the wrong host and surface the
# canonical URL in the response.
#
# NOTE: `arifos.arif-fazil.com` is still the canonical HUMAN LANDING
# (marketing/docs surface, not MCP). Only the /mcp path on that host is
# deprecated as an MCP endpoint.
DEPRECATED_ENDPOINTS: tuple[str, ...] = (
    "https://arifos.arif-fazil.com/mcp",
    "https://arifos.arif-fazil.com/sse",
    "http://arifos.arif-fazil.com:8088/mcp",
)

# C2-6 fix (2026-06-21): MCP spec version pin. Previously `_MCP_SPEC_VERSION`
# in tools.py was "2025-11-25" but `PEER_SOVEREIGNS.arifos.protocol_version`
# was "2025-03-26" — two declared canonicals. Pin:
#   - CANONICAL: the version this server declares in its initialize response
#   - PREFERRED: the version clients SHOULD use going forward
#   - SUPPORTED: both versions still work (for backward compat)
# Both versions are accepted at the wire; 2025-11-25 is preferred for new clients.
MCP_SPEC_VERSION_CANONICAL = "2025-11-25"
MCP_SPEC_VERSION_PREFERRED = "2025-11-25"
MCP_SPEC_VERSION_LEGACY = "2025-03-26"
MCP_SPEC_VERSIONS_SUPPORTED = ("2025-11-25", "2025-03-26")


def canonical_mcp_endpoint() -> str:
    """Return the single canonical MCP endpoint. C2-5 invariant.

    Every component that needs to advertise an MCP URL MUST call this
    function rather than hardcoding. Use this for:
      - tools/list responses
      - initialize response
      - any documentation generator
      - any client-side redirect hint
    """
    return CANONICAL_MCP_ENDPOINT


def deprecated_endpoint_redirect_hint(received_url: str | None) -> str | None:
    """If the client hit a deprecated URL, return the canonical redirect target.

    Returns None if `received_url` is canonical or unrecognized.
    """
    if not received_url:
        return None
    if received_url in DEPRECATED_ENDPOINTS:
        return CANONICAL_MCP_ENDPOINT
    return None


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
        "tools": len(CANONICAL_12),  # dynamic from CANONICAL_12 tuple — single source of truth
        "prompts": len(CANONICAL_PROMPTS),
        "resources": len(CANONICAL_RESOURCES),
        "protocol_version": "2025-11-25",  # aligned with MCP_SPEC_VERSION_CANONICAL
    },
    "geox": {
        "role": "earth_intelligence_processor",
        "mcp": True,
        "public_endpoint": "https://geox.arif-fazil.com/mcp",
        "internal_host": "127.0.0.1",
        "internal_port": 8081,  # fixed 2026-06-28: was 18081 (Docker-era stale)
        "mcp_path": "/mcp",
        "health_path": "/health",
        "ready_path": None,
        "tools": None,
        "prompts": None,
        "resources": None,
        "protocol_version": "2025-11-25",  # fixed 2026-06-28: was 2025-03-26 — aligned with MCP_SPEC_VERSION_CANONICAL
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
        "protocol_version": "2025-11-25",  # fixed 2026-06-28: was 2025-03-26 — aligned with MCP_SPEC_VERSION_CANONICAL
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

    Tool count derived from live public_surface_state(), NOT hardcoded.
    """
    surface_state = public_surface_state()
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
            "tools": surface_state["kernel_tools"],
            "tools_registered": surface_state["tools_registered"],
            "surface_mode": surface_state["mode"],
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

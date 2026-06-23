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

CANONICAL_13: tuple[str, ...] = tuple(
    name for name in list_constitutional_tools()
    if not (CANONICAL_TOOLS.get(name, {}).get("_deprecated", False)
            or CANONICAL_TOOLS.get(name, {}).get("deprecated", False))
)
# CANONICAL_13 is the single canonical set — deprecated aliases excluded.

# ── Canary Probe — always-on transport diagnostic (Canonical13 enforcement) ──
# This zero-floor probe is ALWAYS registered on the public wire surface.
# It requires no session, no actor, no governance — pure transport diagnostics.
CANARY_PROBES: tuple[str, ...] = ("arif_canary",)

# ── SDK long-name aliases (2026-06-23 unification) ───────────────────────────
# ChatGPT Apps SDK and legacy clients expect arif_<noun>_<verb> names.
# These are first-class aliases pointing to the same handlers as the short
# canonical names in CANONICAL_13. They do NOT create new operations.
CANONICAL_LONG_NAME_ALIASES: tuple[str, ...] = (
    "arif_session_init",
    "arif_sense_observe",
    "arif_evidence_fetch",
    "arif_mind_reason",
    "arif_heart_critique",
    "arif_reply_compose",
    "arif_memory_recall",
    "arif_gateway_connect",
    "arif_ops_measure",
    "arif_judge_deliberate",
    "arif_vault_seal",
    "arif_forge_execute",
)

# ── Canonical13 Public Surface (= canonical kernel + SDK aliases + canary) ───
# This is the DEFAULT public wire surface. 16 canonical short names +
# 12 SDK long-name aliases + 1 canary probe = 29 tools.
CANONICAL13_PUBLIC_SURFACE: tuple[str, ...] = tuple(
    list(dict.fromkeys([*CANONICAL_13, *CANONICAL_LONG_NAME_ALIASES, *CANARY_PROBES]))
)

BLOCKED_PUBLIC_PREFIXES: tuple[str, ...] = (
    # "arifos_" is blocked from tools/list but NOT from dispatch.
    # _LEGACY_ALIASES in tools.py routes arifos_* → arif_* at call time.
    # Full surface unblock when execution gate + constitutional_map aligned.
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


# Diagnostic tools — reversible governance inspectors, not canonical constitutional tools.
# These are the ONLY non-canonical tools that have live FastMCP handlers.
DIAGNOSTIC_TOOLS: tuple[str, ...] = (
    "arif_ping",
    # ── Transport Canary Layer (Phase 0, 2026-06-14) ──
    "arif_conformance_report",
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
EXPANDED_45: tuple[str, ...] = tuple(
    list(dict.fromkeys([*CANONICAL_13, *CANONICAL_LONG_NAME_ALIASES, *CANARY_PROBES, *DIAGNOSTIC_TOOLS]))
)

# DOMAIN_ALIASES were removed 2026-06-21 — TOOL_ALIAS_MAP was dead code
# with 84 ghost aliases that had no FastMCP handlers. Cleared by FORGE audit.
# See: forge_work/arifos-mcp-tool-audit-2026-06-21.md

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
        "canonical15": "canonical13",  # deprecated alias — canonical count is 15
        "internal": "expanded45",
        "expanded45": "expanded45",
    }
    return profile_map.get(raw, "canonical13")


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    """
    Return the public tool names for a given surface mode.

    canonical13 (default): CANONICAL_13 + CANARY_PROBES (22 tools).
        This is the honest default wire surface — 15 canonical tools + 1 canary probe.
    expanded45: CANONICAL_13 + DIAGNOSTIC_TOOLS (gated tools included).
        Only active when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.

    INTERNAL_ONLY filter: tools registered in CANONICAL_TOOLS with
    access == "internal_only" are NEVER exposed via any public mode.
    """
    resolved = normalize_public_surface_mode(mode)
    if resolved == "expanded45":
        candidates = EXPANDED_45
    else:
        # canonical13: 15 canonical tools + 1 canary probe = 16 tools on the default wire.
        # Canary probe is a transport diagnostic (multimode arif_canary).
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
        "tools": 13,
        "prompts": len(CANONICAL_PROMPTS),
        "resources": len(CANONICAL_RESOURCES),
        "protocol_version": "2025-11-25",  # aligned with MCP_SPEC_VERSION_CANONICAL
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

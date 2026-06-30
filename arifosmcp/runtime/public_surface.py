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

# ═─ 7-Tool MCP Facade (F4 CLARITY: one intent = one public tool) ─═══════════
# Public agents see only these 7 verbs. Everything else is an internal alias,
# diagnostic probe, or hidden helper. See /root/AAA/skills/arifos-recursive-audit
# and AGENTIC_AFFORDANCE_GUIDE.md for doctrine.
CANONICAL_7: tuple[str, ...] = (
    "arif_init",  # 000 — Start here. Session bootstrap + actor identity. Precedes all other calls.
    "arif_observe",  # 111 — Ground in reality. External evidence, vitals, repo map.
    "arif_think",  # 333 — Reason, plan, critique. Cognitive engine for complex decisions.
    "arif_route",  # 444 — Select organ/tool. Bridge when intent→tool mapping is uncertain.
    "arif_judge",  # 888 — Constitutional verdict. SEAL/HOLD/SABAR/VOID. Evidence→plan→judge pipeline.
    "arif_act",  # 900 — Execute only after valid SEAL. Requires seal_verdict_id + approved_action_hash.
    "arif_seal",  # 999 — Permanent record. VAULT999 hash chain. Irreversible.
)

# Deprecated alias for internal code that still imports CANONICAL_13.
CANONICAL_13: tuple[str, ...] = CANONICAL_7
# CANONICAL_7 is the single public canonical set.

# ── Canary Probe — transport diagnostic, now internal-only ─────────────────
# The canary is a pure transport probe. In the 7-tool facade it is no longer
# advertised on the public wire surface; it remains available as a diagnostic
# helper for federation operators and health checks.
CANARY_PROBES: tuple[str, ...] = ("arif_canary",)

# ── SDK long-name aliases (DEPRECATED 2026-06-23 — kernel freeze) ─────────────
# FROZEN 2026-06-23 + PURGED 2026-06-30: aliases removed from public wire surface.
# Backend handlers still resolve via _CANONICAL_HANDLERS + _LEGACY_ALIASES for
# backward compatibility, but tools/list returns ONLY canonical names.
# See: forge_work/BANGANG-ALIAS-PURGE-2026-06-30.md
CANONICAL_LONG_NAME_ALIASES: tuple[str, ...] = ()  # intentionally empty

# ── Canonical7 Public Surface (= exactly 7 canonical verbs) ─────────────────
# F13 ratified 2026-06-23: exactly 7 public verbs.
# Everything else (plumbing, aliases, diagnostics) is internal and filtered.
# ── Canonical 7 Public Surface (F13 ratified 2026-06-23) ─────────────────
# The public surface is exactly 7 verbs. The name CANONICAL13_PUBLIC_SURFACE
# is retained for backward compat but is semantically CANONICAL_7.
CANONICAL13_PUBLIC_SURFACE: tuple[str, ...] = CANONICAL_7

# Preferred canonical names for surface modes (2026-06-30 clarity fix):
#   "canonical7"  → 7 constitutional verbs (default public)
#   "canonical13" → DEPRECATED alias for "canonical7" — kept for backward compat
#   "expanded45"  → canonical7 + all diagnostics (operator/debug)
VALID_PUBLIC_SURFACE_MODES: tuple[str, ...] = (
    "canonical7",  # preferred — matches the number 7
    "canonical13",  # deprecated alias — still works, maps to canonical7
    "expanded45",  # operator/debug surface
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


# Diagnostic tools — reversible governance inspectors, not canonical constitutional tools.
# These are the ONLY non-canonical tools that have live FastMCP handlers.
DIAGNOSTIC_TOOLS: tuple[str, ...] = (
    "arifos_ping",
    # ── Transport Canary Layer (Phase 0, 2026-06-14) ──
    "arifos_schema_echo",
    "arifos_version_echo",
    "arifos_transport_echo",
    "arifos_initialize_probe",
    # ── Legacy diagnostics ──
    "arifos_stack_health_probe",
    "arifos_scan_local_instructions",
    "arifos_organ_consensus",
    "arifos_session_budget",
    "arifos_floor_status",
    "mcp_drift_check",
    "arifos_vault_query",
    # ── Shadow Geometry Tools (Phase 2, 2026-06-16) ──
    "arifos_self_evaluate",
    "arifos_model_compare",
    # ── Internal helpers (non-deprecated) ──
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
    # ── Eureka Margin Discovery Substrate (Phase 2, 2026-06-29) ──
    "arifos_discover_margins",
    "arifos_bridge_mcp_server",
    "arifos_synthesize_canon",
    # ── BM25 Tool Retrieval (Ratel insight, 2026-06-29) ──
    "arifos_retrieve_tools",
)

# EXPANDED_45 — the honest expanded public surface (FROZEN 2026-06-23).
# SDK aliases removed — canonical 7 verbs + diagnostics.
# CANARY_PROBES (arif_canary dispatcher) is internal-only and not surfaced here;
# the individual probe modes (arif_conformance_report, arif_schema_echo, etc.)
# are already included in DIAGNOSTIC_TOOLS.
EXPANDED_45: tuple[str, ...] = tuple(list(dict.fromkeys([*CANONICAL_7, *DIAGNOSTIC_TOOLS])))

# DOMAIN_ALIASES were removed 2026-06-21 — TOOL_ALIAS_MAP was dead code
# with 84 ghost aliases that had no FastMCP handlers. Cleared by FORGE audit.
# See: forge_work/arifos-mcp-tool-audit-2026-06-21.md


def normalize_public_surface_mode(mode: str | None = None) -> str:
    """Resolve surface mode. canonical7 (default) = 7 verbs. expanded45 = 7 + diagnostics.

    canonical13 is a deprecated alias for canonical7 — it always meant 7 tools
    (the 13 was a historical count, never the current canonical number).
    """
    raw = (mode or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_SURFACE_MODE", "") or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_TOOL_PROFILE", "") or "").strip().lower()

    profile_map = {
        "canonical7": "canonical7",
        "public": "canonical7",
        "chatgpt": "canonical7",
        "agnostic_public": "canonical7",
        "canonical13": "canonical7",  # deprecated alias — canonical count is 7
        "canonical15": "canonical7",  # deprecated alias
        "internal": "expanded45",
        "expanded45": "expanded45",
    }
    return profile_map.get(raw, "canonical7")


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    """
    Return the public tool names for a given surface mode.

    canonical7 (default): CANONICAL_7 (7 constitutional verbs).
        F13 ratified 2026-06-23: exactly 7 public verbs.
        One intent = one public tool. No SDK aliases, no diagnostics on the wire.
    expanded45: CANONICAL_7 + DIAGNOSTIC_TOOLS (operator/debug surface).
        Only active when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
        Adds arif_conformance_report, arif_canary, and other read-only diagnostics.

    INTERNAL_ONLY filter: tools registered in CANONICAL_TOOLS with
    access == "internal_only" are NEVER exposed via any public mode.
    """
    resolved = normalize_public_surface_mode(mode)
    if resolved == "expanded45":
        expose_dev_tools = os.getenv("ARIFOS_MCP_EXPOSE_DEV_TOOLS", "false").lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        candidates = EXPANDED_45 if expose_dev_tools else CANONICAL13_PUBLIC_SURFACE
    else:
        # canonical7 (default): exactly the 7 canonical verbs.
        # Also handles "canonical13" (deprecated alias).
        candidates = CANONICAL13_PUBLIC_SURFACE  # == CANONICAL_7
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
    """Report the public tool surface state for the given mode.

    Two profiles (2026-06-30 clarity):
      canonical7 — 7 constitutional verbs (public agents, default)
      expanded45 — canonical7 + diagnostics (operator/debug, ARIFOS_MCP_EXPOSE_DEV_TOOLS=true)
    """
    resolved = normalize_public_surface_mode(mode)
    tool_names = list(public_tool_names_for_mode(resolved))
    diagnostic_names = [name for name in tool_names if name in set(DIAGNOSTIC_TOOLS)]
    return {
        "mode": resolved,
        "mode_aliases": {
            "canonical7": "7 constitutional verbs (public default)",
            "canonical13": "DEPRECATED alias for canonical7",
            "expanded45": "canonical7 + arif_conformance_report + arif_canary + diagnostics (operator/debug)",
        },
        "tools_registered": len(tool_names),
        "kernel_tools": len(CANONICAL_7),
        "canonical_count": len(CANONICAL_7),
        "diagnostic_tools": diagnostic_names,
        "tool_names": tool_names,
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
        "tools": len(CANONICAL_7),  # dynamic from CANONICAL_7 tuple — single source of truth
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

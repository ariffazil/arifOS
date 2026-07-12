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

# ══ Metabolic public surface (F4 CLARITY: one stage = one public verb) ══════
# Audit 2026-07-09 (Spine P0 cleanup):
#   - arif_triage REMOVED from public wire — absorbed into arif_init(mode=preflight|triage|status)
#   - arif_fetch / arif_search / arif_explore → modes of arif_observe (no live aliases)
#   - arif_delegate → not an alias of arif_route
#   - arif_bridge_connect / arif_memory retained (HIGH path + memory governor)
# One intent = one canonical name. Deprecated names = thin log wrappers only.
CANONICAL_12: tuple[str, ...] = (
    "arif_init",  # 000  — Session bootstrap (+ modes: preflight, triage, status)
    "arif_observe",  # 111  — Reality sensing (modes: search, fetch, ingest, vitals, atlas)
    "arif_think",  # 333  — Cognitive engine
    "arif_route",  # 444  — Organ router (modes: route, bridge)
    "arif_bridge_connect",  # 444b — Direct organ bridge (HIGH)
    "arif_critique",  # 555  — Maruah/risk assessment
    "arif_memory",  # 555m — Memory governor
    "arif_judge",  # 666  — Constitutional verdict
    "arif_forge",  # 777  — Guarded execution
    "arif_compose",  # 888  — Response composer
    "arif_seal",  # 999  — VAULT999 seal
    "arif_verify",  # E1   — JITU pre-execution gate (SEAL token verification)
    # ── Entropy Integrity Mesh — Kernel tools (v2026.07.12) ─────────
    "arif_entropy_observe",  # E2 — Register entropy observations
    "arif_j_state_assess",  # E3 — Fuse observations into J-state
    "arif_correction_probe",  # E4 — Generate challenges, classify responses
    "arif_consequence_trace",  # E5 — Trace decision consequences
    "arif_entropy_route",  # E6 — Route entropy questions to organs
    "arif_j_gate",  # E7 — Convert J-state to action posture
)

# ── FORGE_NEXT_8 — F13 SOVEREIGN surface collapse (2026-07-12) ──────────
# WS4 cycle-end. 8 canonical verbs the kernel serves to MCP clients.
# CONSENSUS (AUDITOR + OPS + PLANNER, 2026-07-12 14:00Z):
#   - memory IN (F1/F11 backbone: recall, promote, forget; scar continuity)
#   - compose OUT (cosmetic formatting — every LLM composes its own replies)
# 10 retired verbs map INTO the 8 via modes/internalisation:
#   arif_critique           → arif_think(mode=redteam|critique)
#   arif_bridge_connect     → arif_route(mode=bridge)
#   arif_entropy_observe    → arif_observe(mode=entropy_dS)
#   arif_entropy_route      → arif_observe(mode=entropy_dS)
#   arif_j_state_assess     → arif_judge (internal stage)
#   arif_correction_probe   → arif_think (internal)
#   arif_consequence_trace  → arif_forge preflight (internal)
#   arif_j_gate             → arif_forge gate (internal)
#   arif_verify             → hardcoded first step in arif_forge (was JITU gate)
#   arif_compose            → DELETED (agent composes)
# Pending: AGENTS.md canonical-8 doc update (memory-above-compose).
FORGE_NEXT_8: tuple[str, ...] = (
    "arif_init",  # 000 — Session bootstrap
    "arif_observe",  # 111 — Reality sensing
    "arif_think",  # 333 — Cognitive engine (absorbs redteam/critique)
    "arif_route",  # 444 — Organ router (absorbs bridge)
    "arif_judge",  # 666 — Constitutional verdict (absorbs j_state_assess)
    "arif_forge",  # 777 — Guarded execution (absorbs verify, j_gate, consequence_trace)
    "arif_seal",  # 999 — VAULT999 append
    "arif_memory",  # 555m — Memory governor (cross-cutting DAG)
)

# ── DEPRECATED ALIASES (backward compat only) ─────────────────────────────
CANONICAL_13: tuple[str, ...] = (
    CANONICAL_12  # DEPRECATED — use CANONICAL_12 (registry.py, surface_consistency.py)
)
CANONICAL_9: tuple[str, ...] = CANONICAL_12  # DEPRECATED — use CANONICAL_12
CANONICAL_7: tuple[str, ...] = CANONICAL_12  # DEPRECATED — use CANONICAL_12
CANONICAL13_PUBLIC_SURFACE: tuple[str, ...] = CANONICAL_12  # DEPRECATED alias

# ── Canary Probe — transport diagnostic, absorbed into arif_init(mode=canary) ──
# arif_canary remains absorbed as a mode of arif_init. Its 6 child names are
# DEPRECATED → use arif_init(mode=canary). They are kept as internal aliases
# for backward compatibility only.
CANARY_PROBES: tuple[str, ...] = ()
DEPRECATED_CANARY_CHILDREN: tuple[str, ...] = (
    "arif_ping",
    "arif_schema_echo",
    "arif_version_echo",
    "arif_transport_echo",
    "arif_initialize_probe",
    "arif_conformance_report",
)

# ── SDK long-name aliases (DEPRECATED 2026-06-23 — kernel freeze) ─────────────
# FROZEN 2026-06-23 + PURGED 2026-06-30 + RE-PURGED 2026-07-04: aliases removed
# from public wire surface. Backend handlers still resolve via _LEGACY_ALIASES for
# backward compatibility, but tools/list returns ONLY canonical 13 names.
# See: forge_work/BANGANG-ALIAS-PURGE-2026-06-30.md and the 2026-07-04 YELLOW re-purge.
CANONICAL_LONG_NAME_ALIASES: tuple[str, ...] = ()  # intentionally empty

# ── Canonical 13 Public Surface (CANONICAL-13 2026-07-07) ─────────────
# The public surface is exactly 13 tools = 9 stages + 3 evidence/preflight/bridge + memory.
# The name CANONICAL_9 is retained as deprecated alias for backward compat.


# Preferred canonical names for surface modes (2026-07-07 CANONICAL-13):
#   "canonical13" → 13 canonical tools (default public)
#   "canonical9"  → DEPRECATED alias for "canonical13"
#   "canonical12" → DEPRECATED alias for "canonical13"
#   "canonical7"  → DEPRECATED alias for "canonical13"
#   "expanded45"  → canonical13 + all diagnostics (operator/debug)
VALID_PUBLIC_SURFACE_MODES: tuple[str, ...] = (
    "canonical13",  # preferred — 13 canonical tools
    "canonical9",  # deprecated alias — maps to canonical13
    "canonical12",  # deprecated alias — maps to canonical13
    "canonical7",  # deprecated alias — maps to canonical13
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


# ══ ARIFOS ↔ A-FORGE Namespace Separation (F4 CLARITY) ══════════════════════
# arifOS and A-FORGE share verb collisions on: judge, seal, execute, act.
# The delegation table below makes explicit which tool runs where, and why.
# Option A (route-only) was ratified 2026-07-01: arifOS = governance facade,
# A-FORGE = execution engine. No tool removal — explicit delegation clarifies roles.
#
# ┌──────────────────────┬───────────────────────────┬─────────────────────┐
# │ arifOS (this repo)   │ A-FORGE (:7071/:7072)    │ Delegation          │
# ├──────────────────────┼───────────────────────────┼─────────────────────┤
# │ arif_judge          │ forge_judge_proxy         │ arifOS = local      │
# │   888 constitutional │   (arifOS→A-FORGE bridge) │ governance/judgment │
# │   verdict, SEAL/     │   A-FORGE cannot self-    │ No external call    │
# │   HOLD/SABAR/VOID    │   authorize; arifOS holds │ for judge           │
# │                      │   final veto               │                     │
# ├──────────────────────┼───────────────────────────┼─────────────────────┤
# │ arif_seal           │ forge_seal                │ arifOS = local      │
# │   999 VAULT999       │   (A-FORGE vault seal)   │ Only arifOS writes  │
# │   immutable ledger   │                           │ to VAULT999         │
# │                      │                           │ No delegation       │
# ├──────────────────────┼───────────────────────────┼─────────────────────┤
# │ arif_act            │ (internal only)           │ arifOS = local      │
# │   900 execution      │   wraps _arif_forge_      │ arif_act verifies   │
# │   gate; requires     │   execute after SEAL      │ SEAL then calls     │
# │   seal_verdict_id +  │   verification via         │ _arif_forge_execute │
# │   approved_action_   │   A2ASealVerifier         │ locally             │
# │   hash              │                           │                     │
# ├──────────────────────┼───────────────────────────┼─────────────────────┤
# │ arif_forge_execute  │ forge_execute             │ arifOS = local      │
# │   (010 FORGE stage) │   (A-FORGE motor cortex)  │ Both run locally;   │
# │   plan-gated build, │   REST/MCP execution,      │ arifOS has own      │
# │   artifact produce  │   lease + SCAR + witness   │ forge_exec handler  │
# ├──────────────────────┼───────────────────────────┼─────────────────────┤
# │ (none — arifOS does │ forge_dry_run, forge_*    │ A-FORGE owns        │
# │  not expose these   │  filesystem, git, docker,  │ engineering tools    │
# │  on public surface) │  postgres, etc.            │ arifOS has deprec.  │
# │                      │                           │ proxy → A-FORGE     │
# │                      │                           │ (removal 2026-07-15)│
# └──────────────────────┴───────────────────────────┴─────────────────────┘
#
# Blast radius of collision: NONE. Infrastructure already separates the two
# namespaces. The deprecation proxy for forge_* (server.py §forge-ladder)
# routes external callers to A-FORGE MCP automatically when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.
# The only remaining "collision" is documentation ambiguity — fixed by this table.
# See: forge_work/AFORGE-ARIFOS-COLLISION-AUDIT-2026-07-01.md


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
# Diagnostics are appended to the canonical 13 tools.
EXPANDED_45: tuple[str, ...] = tuple(list(dict.fromkeys([*CANONICAL_12, *DIAGNOSTIC_TOOLS])))

# DOMAIN_ALIASES were removed 2026-06-21 — TOOL_ALIAS_MAP was dead code
# with 84 ghost aliases that had no FastMCP handlers. Cleared by FORGE audit.
# See: forge_work/arifos-mcp-tool-audit-2026-06-21.md


def normalize_public_surface_mode(mode: str | None = None) -> str:
    """Resolve surface mode. canonical13 (default) = 13 canonical tools. expanded45 = canonical13 + diagnostics.

    canonical9 / canonical12 / canonical7 are deprecated aliases that always
    mean the canonical public set — now the 13-tool surface.
    """
    raw = (mode or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_SURFACE_MODE", "") or "").strip().lower()
    if not raw:
        raw = (os.getenv("ARIFOS_PUBLIC_TOOL_PROFILE", "") or "").strip().lower()

    profile_map = {
        # F13 SOVEREIGN — 2026-07-12: forge_next_8 is the new canonical
        # default public surface for the arifOS MCP wire. WS4 cycle-end
        # surface collapse. Legacy modes still resolve to canonical13
        # (18-tool) for backward compat callers.
        "forge_next_8": "forge_next_8",
        "forge-next-8": "forge_next_8",
        "canonical13": "canonical13",
        "canonical9": "canonical13",  # deprecated alias
        "canonical12": "canonical13",  # deprecated alias
        "canonical7": "canonical13",  # deprecated alias
        "canonical15": "canonical13",  # deprecated alias
        "public": "forge_next_8",  # F13 default
        "chatgpt": "forge_next_8",
        "agnostic_public": "forge_next_8",
        "internal": "expanded45",
        "expanded45": "expanded45",
    }
    return profile_map.get(raw, "canonical13")


def current_public_surface_mode() -> str:
    return normalize_public_surface_mode(None)


# Lookup table: resolved surface profile name → tuple of canonical verbs.
# FORGE_NEXT_8 (8) is the default — per F13 SOVEREIGN directive 2026-07-12.
_SURFACE_VERB_TABLE: dict[str, tuple[str, ...]] = {
    "forge_next_8": FORGE_NEXT_8,
    "canonical13": CANONICAL_12,
    "expanded45": EXPANDED_45,
}


def public_tool_names_for_mode(mode: str | None = None) -> tuple[str, ...]:
    """
    Return the public tool names for a given surface mode.

    canonical13 (default): CANONICAL_12 (13 canonical tools).
        CANONICAL-13 2026-07-07: 9 stages + 3 evidence/preflight/bridge + memory governor.
        One intent = one public verb.
    expanded45: CANONICAL_12 + DIAGNOSTIC_TOOLS (operator/debug surface).
        Only active when ARIFOS_MCP_EXPOSE_DEV_TOOLS=true.

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
        candidates = EXPANDED_45 if expose_dev_tools else CANONICAL_12
    elif resolved == "forge_next_8":
        # F13 SOVEREIGN 2026-07-12: 8-verb wire surface. The 10 retired
        # verbs continue to live in CANONICAL_TOOLS (kernel handlers
        # remain wired) but are now hidden from tools/list output unless
        # the caller explicitly switches back to canonical13 / expanded45.
        candidates = FORGE_NEXT_8
    else:
        # canonical13 (legacy default): the 13-tool wire surface.
        candidates = CANONICAL_12
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

    Two profiles (2026-07-07 CANONICAL-13):
      canonical13 — 13 canonical tools (13 tools, public default)
      expanded45  — canonical13 + diagnostics (operator/debug, ARIFOS_MCP_EXPOSE_DEV_TOOLS=true)
    """
    resolved = normalize_public_surface_mode(mode)
    tool_names = list(public_tool_names_for_mode(resolved))
    diagnostic_names = [name for name in tool_names if name in set(DIAGNOSTIC_TOOLS)]
    return {
        "mode": resolved,
        "mode_aliases": {
            "canonical12": "12 canonical tools (public default; CANONICAL-12 2026-07-07)",
            "canonical9": "DEPRECATED alias for canonical13",
            "canonical12": "DEPRECATED alias for canonical13",
            "canonical7": "DEPRECATED alias for canonical13",
            "expanded45": "canonical13 + diagnostics (operator/debug)",
        },
        "tools_registered": len(tool_names),
        "kernel_tools": len(CANONICAL_12),
        "canonical_count": len(CANONICAL_12),
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

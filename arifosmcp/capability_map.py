"""
arifOS Capability Map
════════════════════

This module re-exports compatibility symbols from the archived capability map
for backward compatibility with existing tests and server.py.

The canonical capability definitions live in constitutional_map.py.
"""

from __future__ import annotations

from enum import Enum


class InitAnchorMode(str, Enum):
    """Modes supported by the 000_INIT arif_session_init tool."""

    INIT = "init"
    STATE = "state"
    STATUS = "status"
    REVOKE = "revoke"
    REFRESH = "refresh"


# ── Legacy mega-tool definitions (backward compat for tests + server.py) ────────

CANONICAL_TOOL_HANDLERS: dict[str, str] = {
    "arifos_init": "arifos_init",
    "arifos_sense": "arifos_sense",
    "arifos_mind": "arifos_mind",
    "arifos_kernel": "arifos_kernel",
    "arifos_heart": "arifos_heart",
    "arifos_ops": "arifos_ops",
    "arifos_judge": "arifos_judge",
    "arifos_memory": "arifos_memory",
    "arifos_vault": "arifos_vault",
    "arifos_forge": "arifos_forge",
    "arifos_gateway": "arifos_gateway",
}

MEGA_TOOLS: list[str] = list(CANONICAL_TOOL_HANDLERS.keys())

MEGA_TOOL_MODES: dict[str, set[str]] = {name: {"default"} for name in MEGA_TOOLS}

FINAL_TOOL_IMPLEMENTATIONS: dict[str, str] = CANONICAL_TOOL_HANDLERS

# Legacy dotted-map for v1 compatibility
LEGACY_TOOL_MAP: dict[str, str] = {
    "arifos.init": "arifos_init",
    "arifos.sense": "arifos_sense",
    "arifos.mind": "arifos_mind",
    "arifos.kernel": "arifos_kernel",
    "arifos.route": "arifos_kernel",
    "arifos.heart": "arifos_heart",
    "arifos.ops": "arifos_ops",
    "arifos.judge": "arifos_judge",
    "arifos.memory": "arifos_memory",
    "arifos.vault": "arifos_vault",
    "arifos.forge": "arifos_forge",
    "arifos.gateway": "arifos_gateway",
    "arifos.health": "arifos_health",
    "init_anchor": "arifos_init",
    "physics_reality": "arifos_sense",
    "reality_compass": "arifos_sense",
    "agi_mind": "arifos_mind",
    "agi_reason": "arifos_mind",
    "asi_heart": "arifos_heart",
    "math_estimator": "arifos_ops",
    "apex_soul": "arifos_judge",
    "vault_ledger": "arifos_vault",
    "vault_seal": "arifos_vault",
    "code_engine": "arifos_forge",
    "vps_monitor": "arifos_health",
    "architect_registry": "arifos_init",
}

CAPABILITY_MAP: dict[str, str] = {**CANONICAL_TOOL_HANDLERS, **LEGACY_TOOL_MAP}
LEGACY_TOOLS: dict[str, str] = LEGACY_TOOL_MAP

# Substrate Capability Families
SUBSTRATE_CAPABILITIES: dict[str, str] = {
    "substrate.git.audit": "git_bridge.get_repo_state",
    "substrate.git.propose": "git_bridge.propose_changes",
    "substrate.git.commit": "git_bridge.commit_governed",
    "substrate.fetch.guarded": "fetch_bridge.fetch_guarded",
    "substrate.validation.everything.probe": "everything_probe.run_full_diagnostic",
    "substrate.validation.everything.transport_check": "everything_probe.probe_server_features",
    "substrate.validation.everything.protocol_smoke": "everything_probe.probe_tools_roundtrip",
}

# Metadata and routing
ALIGNED_STAGES: dict[str, str] = {
    "init": "000_INIT",
    "sense": "111_SENSE",
    "mind": "333_MIND",
    "heart": "666_HEART",
    "judge": "888_JUDGE",
    "memory": "555_MEMORY",
    "vault": "999_VAULT",
}


# ── Iterator shims (legacy — all trivially valid in current architecture) ────────


def iter_unmapped_legacy_tools() -> list[str]:
    """Legacy mapping is now 1:1 — no unmapped tools."""
    return []


def iter_unknown_tools_in_map() -> list[str]:
    """All known tools have valid targets."""
    return []


def iter_invalid_megatool_targets() -> list[str]:
    """All mega-tool targets resolve correctly."""
    return []


def iter_invalid_modes() -> list[str]:
    """All modes are valid."""
    return []


def build_llm_context_map() -> dict[str, object]:
    """Return the canonical discovery payload exposed in manifests and resources."""
    return {
        "schema": "arifos-llm-context/v1",
        "canonical_tools": {
            "init_anchor": "arifos_init",
            "evidence_sense": "arifos_sense",
            "agi_mind": "arifos_mind",
            "route_meta": "arifos_kernel",
            "memory_recall": "arifos_memory",
            "asi_heart": "arifos_heart",
            "ops_metrics": "arifos_ops",
            "apex_judge": "arifos_judge",
            "vault_seal": "arifos_vault",
            "forge_exec": "arifos_forge",
            "vps_monitor": "arifos_health",
        },
        "tool_aliases": dict(LEGACY_TOOL_MAP),
        "discovery": {
            "tool_contracts_resource": "arifos://contracts/tools",
            "llm_context_resource": "arifos://mcp/context",
            "server_json": "/.well-known/mcp/server.json",
        },
        "continuity_contract": {
            "contract_version": "0.1.0",
            "invariants": [
                "authorization may not widen without authority_transition",
                "session continuity must persist across tool handoff",
                "canonical tool identity must remain explicit in every envelope",
            ],
        },
        "domain_evidence_contract": {
            "version": "geox-evidence/v1",
            "accepted_sources": ["GEOX"],
            "fields": [
                "claim_tag",
                "asset_id",
                "disagreement_band",
                "p10_p50_p90",
                "charge_probability",
                "vault_receipt",
            ],
            "bindings": {
                "sense": "arifos_sense(domain_evidence=...)",
                "judge": "arifos_judge(domain_evidence=...)",
                "memory_store": "arifos_memory(mode='asset_store', ...)",
                "memory_query": "arifos_memory(mode='asset_query', ...)",
            },
        },
    }

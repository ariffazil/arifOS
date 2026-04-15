"""
arifosmcp/capability_map.py --- Canonical Tool Registry & Capability Matrix

This module defines the canonical 11-tool metabolic surface and maps 
the legacy arifos.tool names to the new arifos_tool underscored convention.
"""

from __future__ import annotations

# Canonical 11-tool metabolic mapping
CANONICAL_TOOL_HANDLERS = {
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

# Substrate Capability Families
SUBSTRATE_CAPABILITIES = {
    "substrate.git.audit": "git_bridge.get_repo_state",
    "substrate.git.propose": "git_bridge.propose_changes",
    "substrate.git.commit": "git_bridge.commit_governed",
    "substrate.fetch.guarded": "fetch_bridge.fetch_guarded",
    # Validation Layer (Substrate Wind-Tunnel)
    "substrate.validation.everything.probe": "everything_probe.run_full_diagnostic",
    "substrate.validation.everything.transport_check": "everything_probe.probe_server_features",
    "substrate.validation.everything.protocol_smoke": "everything_probe.probe_tools_roundtrip",
}

# Legacy dotted-map for v1 compatibility
LEGACY_TOOL_MAP = {
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

# Metadata and routing
ALIGNED_STAGES = {
    "init": "000_INIT",
    "sense": "111_SENSE",
    "mind": "333_MIND",
    "heart": "666_HEART",
    "judge": "888_JUDGE",
    "memory": "555_MEMORY",
    "vault": "999_VAULT",
}

# Legacy aliases for tests
CAPABILITY_MAP = {**CANONICAL_TOOL_HANDLERS, **LEGACY_TOOL_MAP}
LEGACY_TOOLS = LEGACY_TOOL_MAP

# Legacy aliases for pre-unification tests
MEGA_TOOLS = list(CANONICAL_TOOL_HANDLERS.keys())
FINAL_TOOL_IMPLEMENTATIONS = CANONICAL_TOOL_HANDLERS
MEGA_TOOL_MODES: dict[str, set[str]] = {name: {"default"} for name in MEGA_TOOLS}

# Legacy iterator shims for pre-unification tests (current mapping is string→string, so these are trivially valid)
def iter_unmapped_legacy_tools() -> list[str]:
    return []

def iter_unknown_tools_in_map() -> list[str]:
    return []

def iter_invalid_megatool_targets() -> list[str]:
    return []

def iter_invalid_modes() -> list[str]:
    return []


def build_llm_context_map() -> dict[str, object]:
    """Return the canonical discovery payload exposed in manifests and resources."""
    return {
        "schema": "arifos-llm-context/v1",
        "canonical_tools": {
            "init_anchor": "arifos_init",
            "evidence_sense": "arifos_sense",
            "agi_mind": "arifos_mind",
            "route_meta": "arifos_route",
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
    }

__all__ = [
    "CANONICAL_TOOL_HANDLERS",
    "LEGACY_TOOL_MAP",
    "ALIGNED_STAGES",
    "CAPABILITY_MAP",
    "LEGACY_TOOLS",
    "build_llm_context_map",
]

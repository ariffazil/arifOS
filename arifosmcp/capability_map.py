"""
arifosmcp/capability_map.py --- Canonical Tool Registry & Capability Matrix

This module defines the canonical 11-tool metabolic surface and maps 
the legacy arifos.tool names to the new arifos_tool underscored convention.
"""

# Canonical 11-tool metabolic mapping
CANONICAL_TOOL_HANDLERS = {
    "arifos_init": "arifos_init",
    "arifos_sense": "arifos_sense",
    "arifos_mind": "arifos_mind",
    "arifos_heart": "arifos_heart",
    "arifos_judge": "arifos_judge",
    "arifos_memory": "arifos_memory",
    "arifos_vault": "arifos_vault",
    "arifos_math": "arifos_math",
    "arifos_kernel": "arifos_kernel",
    "arifos_code": "arifos_code",
    "arifos_architect": "arifos_architect",
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
    "arifos.heart": "arifos_heart",
    "arifos.judge": "arifos_judge",
    "arifos.memory": "arifos_memory",
    "arifos.vault": "arifos_vault",
    "arifos.math": "arifos_math",
    "arifos.kernel": "arifos_kernel",
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
CAPABILITY_MAP = CANONICAL_TOOL_HANDLERS
LEGACY_TOOLS = LEGACY_TOOL_MAP

__all__ = [
    "CANONICAL_TOOL_HANDLERS",
    "LEGACY_TOOL_MAP",
    "ALIGNED_STAGES",
    "CAPABILITY_MAP",
    "LEGACY_TOOLS",
]

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

__all__ = [
    "CANONICAL_TOOL_HANDLERS",
    "LEGACY_TOOL_MAP",
    "ALIGNED_STAGES",
]

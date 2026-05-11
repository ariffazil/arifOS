"""
arifOS 13-Tool MCP Surface Registry
DITEMPA BUKAN DIBERI — 999 SEAL

Canonical MCP surface for the arifOS constitutional kernel.
Tools: arifos_000_init, arifos_111_sense, arifos_222_witness, arifos_333_mind,
       arifos_444_kernel, arifos_555_memory, arifos_666_heart, arifos_777_ops,
       arifos_888_judge, arifos_999_vault, arifos_gateway, arifos_sabar, arifos_forge

Organ adapters (GEOX/WEALTH/WELL): internal only, not external MCP calls.
"""

from .registry import (
    register_arifos_tools,
    register_arifos_prompts,
    register_arifos_resources,
)

__all__ = [
    "register_arifos_tools",
    "register_arifos_prompts",
    "register_arifos_resources",
]

"""
arifOS MCP Bridge Shim

This module re-exports from codebase.mcp.core.bridge for backward compatibility.
New code should import directly from codebase.mcp.core.bridge.

DITEMPA BUKAN DIBERI
"""

# Re-export all public symbols from core.bridge
from codebase.mcp.core.bridge import (
    BridgeError,
    BridgeRouter,
    CircuitBreaker,
    _FALLBACK_RESPONSE,
    _serialize,
    bridge_init_router,
    bridge_agi_router,
    bridge_atlas_router,
    bridge_asi_router,
    bridge_asi_stakeholder_router,
    bridge_asi_diffusion_router,
    bridge_asi_audit_router,
    bridge_apex_router,
    bridge_vault_router,
    bridge_reality_check_router,
    bridge_trinity_loop_router,
    bridge_context_docs_router,
    bridge_prompt_router,
    get_bridge_router,
)

__all__ = [
    "BridgeError",
    "BridgeRouter",
    "CircuitBreaker",
    "_FALLBACK_RESPONSE",
    "_serialize",
    "bridge_init_router",
    "bridge_agi_router",
    "bridge_atlas_router",
    "bridge_asi_router",
    "bridge_asi_stakeholder_router",
    "bridge_asi_diffusion_router",
    "bridge_asi_audit_router",
    "bridge_apex_router",
    "bridge_vault_router",
    "bridge_reality_check_router",
    "bridge_trinity_loop_router",
    "bridge_context_docs_router",
    "bridge_prompt_router",
    "get_bridge_router",
]

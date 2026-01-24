"""
⚠️ DEPRECATED: arifos.mcp (v51.0.0)

This module is LEGACY. Use AAA_MCP instead.

Migration:
  OLD: python -m arifos.mcp
  NEW: python -m AAA_MCP

  OLD: from arifos.mcp import mcp_agi_genius
  NEW: from AAA_MCP.bridge import bridge_agi_router

The arifos package is now a LIBRARY (the Brain).
The AAA_MCP package is the APPLICATION (the Body).

This module will be removed in v52.

DITEMPA BUKAN DIBERI
"""

import warnings

__version__ = "51.0.0"
__deprecated__ = True

warnings.warn(
    "arifos.mcp is deprecated. Use AAA_MCP instead. "
    "Run: python -m AAA_MCP",
    DeprecationWarning,
    stacklevel=2
)

# Lazy imports to avoid circular dependencies
def __getattr__(name):
    """Lazy load module components."""
    if name in ("TOOLS", "TOOL_DESCRIPTIONS", "create_trinity_server", "main_stdio", "main_sse"):
        from arifos.mcp.trinity_server import TOOLS, TOOL_DESCRIPTIONS, create_trinity_server, main_stdio, main_sse
        return locals()[name]

    if name in ("mcp_000_init", "mcp_agi_genius", "mcp_asi_act", "mcp_apex_judge", "mcp_999_vault"):
        from arifos.mcp.tools.mcp_trinity import mcp_000_init, mcp_agi_genius, mcp_asi_act, mcp_apex_judge, mcp_999_vault
        return locals()[name]

    if name == "create_sse_app":
        from arifos.mcp.sse import create_sse_app
        return create_sse_app

    if name in ("MCPCoreBridge", "ToolRegistry", "ToolLink", "get_bridge"):
        from arifos.mcp.bridge import MCPCoreBridge, ToolRegistry, ToolLink, get_bridge
        return locals()[name]

    raise AttributeError(f"module 'arifos.mcp' has no attribute '{name}'")


__all__ = [
    # Server
    "TOOLS",
    "TOOL_DESCRIPTIONS",
    "create_trinity_server",
    "main_stdio",
    "main_sse",
    "create_sse_app",

    # Tools
    "mcp_000_init",
    "mcp_agi_genius",
    "mcp_asi_act",
    "mcp_apex_judge",
    "mcp_999_vault",

    # Bridge (v50.5.25)
    "MCPCoreBridge",
    "ToolRegistry",
    "ToolLink",
    "get_bridge",
]

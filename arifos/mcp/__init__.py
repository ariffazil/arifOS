"""
arifOS MCP Module (v50.5.25)
5-Tool Trinity Constitutional Framework

Tools:
  000_init    → Gate (Authority + Injection + Amanah)
  agi_genius  → Mind (SENSE → THINK → ATLAS → FORGE)
  asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
  apex_judge  → Soul (EUREKA → JUDGE → PROOF)
  999_vault   → Seal (Merkle + zkPC + Immutable Log)

Bridge:
  MCPCoreBridge → Connects MCP tools to Core engines
  ToolRegistry  → External tool link registry

Mnemonic: "Init the Genius, Act with Heart, Judge at Apex, seal in Vault."

Usage:
  python -m arifos.mcp              # Trinity stdio (default)
  python -m arifos.mcp trinity-sse  # Trinity SSE for Railway

DITEMPA BUKAN DIBERI
"""

__version__ = "50.5.25"

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

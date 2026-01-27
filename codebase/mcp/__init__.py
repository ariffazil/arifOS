"""
codebase MCP Server Package (v53.1.0-SEAL)

Model Context Protocol implementation for arifOS constitutional AI governance.

Entry points:
- codebase-mcp-sse    # SSE transport (Railway/Cloud)
- aaa-mcp-sse         # Alias

Note: Heavy imports are done lazily to avoid startup delays.

DITEMPA BUKAN DIBERI
"""

__version__ = "v53.1.0-SEAL"

# Lazy imports - only expose metadata at package level
# Tool classes should be imported directly when needed:
#   from codebase.mcp.tools import TrinityHatTool, AGITool, ASITool, APEXTool, VaultTool
#   from codebase.mcp.bridge import bridge_agi_router, bridge_asi_router, bridge_apex_router

__all__ = ["__version__"]

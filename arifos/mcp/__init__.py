"""
arifOS MCP Server (v52.0.0-SEAL)
Authority: Muhammad Arif bin Fazil
Principle: Unified Trinity Interface (F1-F13)

Modules:
  arifos.mcp.server    - MCP Standard Server (stdio)
  arifos.mcp.sse       - MCP SSE Server (Railway/HTTP)
  arifos.mcp.bridge    - Zero-logic core adapter
  arifos.mcp.tools     - Tool implementations

Usage:
  python -m arifos.mcp trinity      # Standard Trinity tools
  python -m arifos.mcp trinity-sse  # SSE Server for Railway

DITEMPA BUKAN DIBERI
"""

__version__ = "v52.0.0"



from arifos.mcp.server import create_mcp_server

from arifos.mcp.sse import create_sse_app

from arifos.mcp.mode_selector import get_mcp_mode, MCPMode

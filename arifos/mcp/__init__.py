"""
arifOS MCP Server (v52.5.1-SEAL)
Authority: Muhammad Arif bin Fazil
Principle: Unified AAA Interface (AGI ∩ ASI ∩ APEX, F1-F13)

Modules:
  arifos.mcp.server    - MCP Standard Server (stdio)
  arifos.mcp.sse       - MCP SSE Server (Railway/HTTP)
  arifos.mcp.bridge    - Zero-logic core adapter
  arifos.mcp.tools     - Tool implementations

Usage:
  python -m arifos.mcp          # Standard AAA tools (stdio)
  python -m arifos.mcp sse      # SSE Server for Railway

DITEMPA BUKAN DIBERI
"""

__version__ = "v52.0.0"

def create_mcp_server(*args, **kwargs):
    from .server import create_mcp_server as _create
    return _create(*args, **kwargs)

def create_sse_app(*args, **kwargs):
    from .sse import create_sse_app as _create
    return _create(*args, **kwargs)

def get_mcp_mode(*args, **kwargs):
    from .mode_selector import get_mcp_mode as _get
    return _get(*args, **kwargs)

# Re-export MCPMode
from .mode_selector import MCPMode
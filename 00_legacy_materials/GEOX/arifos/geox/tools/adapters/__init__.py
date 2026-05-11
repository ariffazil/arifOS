"""
GEOX Tool Adapters — Host-specific transport wrappers.
DITEMPA BUKAN DIBERI
"""

# FastMCP adapter is the primary/default adapter
from .fastmcp_adapter import mcp, main, create_server

__all__ = ["mcp", "main", "create_server"]

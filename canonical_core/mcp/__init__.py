"""
canonical_core MCP Server Package (v52.5.1-SEAL)

Model Context Protocol implementation for arifOS constitutional AI governance.

Entry points:
- python -m canonical_core.mcp         # stdio transport (Claude Desktop)
- python -m canonical_core.mcp.sse     # SSE transport (Railway/Cloud)

DITEMPA BUKAN DIBERI
"""

__version__ = "v52.5.1-SEAL"

# MCP server imports
from canonical_core.mcp.server import main as server_main
from canonical_core.mcp.sse import mcp as sse_server

# Tool imports
from canonical_core.mcp.tools.mcp_trinity import (
    mcp_000_init,
    mcp_agi_genius,
    mcp_asi_act,
    mcp_apex_judge,
    mcp_999_vault,
)

__all__ = [
    "server_main",
    "sse_server",
    "mcp_000_init",
    "mcp_agi_genius",
    "mcp_asi_act",
    "mcp_apex_judge",
    "mcp_999_vault",
]

"""
arifosmcp/runtime/server.py — DEPRECATED

This file is now a redirect to the unified server at the project root.
Use `from server import mcp, LEGACY_TOOL_MAP` instead.

For backward compatibility, this module re-exports from the root server.
"""

import sys
import os

# Ensure root is in path
_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _root not in sys.path:
    sys.path.insert(0, _root)

# Import from unified server
from server import mcp, create_aaa_mcp_server, app, LEGACY_TOOL_MAP

__all__ = ["mcp", "create_aaa_mcp_server", "app", "LEGACY_TOOL_MAP"]

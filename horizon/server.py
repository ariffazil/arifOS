"""
horizon/server.py — DEPRECATED

Use the unified server at project root instead:
    from server import mcp

This file redirects to the canonical location for backward compatibility.
"""

import sys
import os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from server import mcp, create_aaa_mcp_server

__all__ = ["mcp", "create_aaa_mcp_server"]

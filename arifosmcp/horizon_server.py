"""
arifOS Horizon Server — FastMCP 2.x Compatible Entry Point
=========================================================
Uses simple @mcp.tool() decorators from mcp_tools.py.
Works on Horizon (FastMCP 2.x) without FastMCP 3.x FunctionTool API.

Usage:
    fastmcp run horizon_server.py
    python horizon_server.py

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import os
import sys

_project_root = os.path.dirname(os.path.abspath(__file__))
_parent_root = os.path.dirname(_project_root)
for _p in (_project_root, _parent_root):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from dotenv import load_dotenv

_env_path = os.path.join(_project_root, ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path, override=True)

from arifosmcp.mcp_tools import create_unified_mcp

mcp = create_unified_mcp()

if __name__ == "__main__":
    mcp.run()

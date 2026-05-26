"""
tools_hardened_dispatch — backward-compatibility re-export stub.

This module was refactored into arifosmcp.runtime.tools during PHOENIX-73C.
The import aliases below restore backward compatibility for:
  - __main__.py  (stdio server)
  - apps/geox_bridge.py
  - runtime/shadow/comparator.py
  - runtime/output_formatter.py (comment reference)
  - tests that reference tools_hardened_dispatch.get_tool_handler
"""
from __future__ import annotations

from arifosmcp.runtime.dispatcher import get_shadow_backends
from arifosmcp.runtime.tools import get_tool_handler

__all__ = ["get_tool_handler", "get_shadow_backends"]

"""
arifosmcp/runtime/server.py — DEPRECATED

This file is now a redirect to the unified server at the project root.
Use `from server import mcp, LEGACY_TOOL_MAP` instead.

For backward compatibility, this module re-exports from the root server.
"""

import sys
import os

# Get the project root (two levels up from this file)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Remove the current directory from path to avoid circular import
_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir in sys.path:
    sys.path.remove(_current_dir)

# Remove the runtime directory from path
_runtime_dir = os.path.dirname(_current_dir)
if _runtime_dir in sys.path:
    sys.path.remove(_runtime_dir)

# Remove arifosmcp directory if present
_arifosmcp_dir = os.path.dirname(_runtime_dir)
if _arifosmcp_dir in sys.path:
    sys.path.remove(_arifosmcp_dir)

# Add project root at the beginning
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Now import from the root server.py
from server import mcp, create_aaa_mcp_server, app, LEGACY_TOOL_MAP

__all__ = ["mcp", "create_aaa_mcp_server", "app", "LEGACY_TOOL_MAP"]

# If this file is run directly, run the main server
if __name__ == "__main__":
    import runpy
    _server_path = os.path.join(_project_root, "server.py")
    runpy.run_path(_server_path, run_name="__main__")

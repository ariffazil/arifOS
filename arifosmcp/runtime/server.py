"""
arifosmcp/runtime/server.py — Runtime Entry Point

This module re-exports from the root server.py which contains the unified
FastMCP server with all REST routes (/health, /tools, /mcp) registered.
"""

import sys
import os

# Get the project root (three levels up from this file: runtime -> arifosmcp -> project_root)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root at the beginning of sys.path if not already present
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import from the root server.py after setting up the path
# This imports the already-initialized FastMCP instance with all routes
_import_error_msg: str | None = None
try:
    from server import mcp, app
except ImportError as e:
    _import_error_msg = str(e)
    # Fallback: if import fails, create minimal app for health check
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import from root server.py: {e}")

    from fastapi import FastAPI
    app = FastAPI()

    @app.get("/health")
    async def fallback_health():
        return {"status": "degraded", "error": f"Import failed: {_import_error_msg}"}

    mcp = None

def create_aaa_mcp_server():
    """Factory function for __main__.py compatibility."""
    return mcp

__all__ = ["mcp", "app", "create_aaa_mcp_server"]

# If this file is run directly, run the main server from root
if __name__ == "__main__":
    import runpy
    _server_path = os.path.join(_project_root, "server.py")
    runpy.run_path(_server_path, run_name="__main__")

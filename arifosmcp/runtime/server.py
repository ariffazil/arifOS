"""
arifosmcp/runtime/server.py — Runtime Entry Point

This module re-exports from `arifosmcp.server`, the packaged FastMCP server
with all REST routes (/health, /tools, /mcp) registered.
"""

import os
import sys

# Get the project root (three levels up from this file: runtime -> arifosmcp -> project_root)
_project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add project root at the beginning of sys.path if not already present
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

# Import the packaged server module after setting up the path.
# This is the image-shipped authority for app + mcp.
_import_error_msg: str | None = None
try:
    from arifosmcp.server import app, mcp
except ImportError as e:
    _import_error_msg = str(e)
    # Fallback: if import fails, create minimal app for health check
    import logging

    logger = logging.getLogger(__name__)
    logger.error(f"Failed to import from arifosmcp.server: {e}")

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

# If this file is run directly, run the packaged canonical server entrypoint.
if __name__ == "__main__":
    from arifosmcp.server import main

    main()

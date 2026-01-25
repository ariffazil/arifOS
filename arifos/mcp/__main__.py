"""
arifOS MCP Entry Point (v52.4.0)

Usage:
  python -m arifos.mcp              # AAA Gateway (Stdio) - Default
  python -m arifos.mcp sse          # AAA Gateway (SSE)
  python -m arifos.mcp trinity      # Legacy Monolith (Stdio)
  python -m arifos.mcp trinity-sse  # Legacy Monolith (SSE)

DITEMPA BUKAN DIBERI
"""

import asyncio
import sys
import logging
import os

# Legacy Imports (Lazy load in future optimization, but needed for specific routes)
from arifos.mcp.server import main_stdio as legacy_stdio
from arifos.mcp.sse import create_sse_app as legacy_create_sse_app

def run_legacy_sse():
    """Run Legacy Monolith SSE server."""
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    app = legacy_create_sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)

def run_gateway_sse():
    """Run AAA Gateway SSE server."""
    from arifos.mcp.gateway import mcp
    # Gateway (FastMCP) handles its own uvicorn run internally via .run(transport="sse")
    # But usually .run() is blocking.
    mcp.run(transport="sse")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "default"

    if arg == "sse":
        # New AAA Gateway SSE
        run_gateway_sse()
    
    elif arg == "trinity-sse":
        # Legacy Monolith SSE (Backward Compatibility)
        run_legacy_sse()
        
    elif arg == "trinity":
        # Legacy Monolith Stdio
        asyncio.run(legacy_stdio())
        
    else:
        # Default: AAA Gateway Stdio
        # This handles 'python -m arifos.mcp' without args
        from arifos.mcp.gateway import mcp
        mcp.run(transport="stdio")
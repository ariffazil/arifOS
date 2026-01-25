"""
arifOS MCP Entry Point (v52.4.1)
CRITICAL FIX: Production SSE + Health Checks + FastMCP Integration
"""

import sys
import os
import uvicorn
from fastmcp import FastMCP

# ------------------------------------------------------------------------------
# PRODUCTION SSE SERVER (with Health Checks for Railway)
# ------------------------------------------------------------------------------

def create_production_app():
    """Create FastMCP app with explicit health endpoint."""
    
    # Import the universal gateway which defines the tools
    from arifos.mcp.gateway import mcp, mount_server
    from arifos.mcp.trinity_server import TOOLS as MONOLITH_TOOLS
    
    # In production/monolith mode, we need to ensure tools are registered on the gateway
    # If gateway.py logic didn't auto-mount (e.g. env var differences), force it here.
    # The gateway.py uses ARIFOS_CLUSTER env var.
    
    # Get underlying Starlette app
    app = mcp.app

    # Add health endpoint (F11 Authority - system must be verifiable)
    @app.get("/health")
    async def health_check():
        # Count tools to verify registration
        tool_count = len(mcp._tool_manager._tools) if hasattr(mcp, "_tool_manager") else 0
        return {
            "status": "healthy",
            "mode": "sse",
            "version": os.environ.get("ARIFOS_VERSION", "v52.4.1"),
            "tools": tool_count,
            "verdict": "SEAL",
            "authority": "arif"
        }

    # Add root endpoint (ChatGPT Dev Mode expects /)
    @app.get("/")
    async def root_check():
        return {
            "name": "arifOS Trinity",
            "status": "ok",
            "endpoints": {
                "sse": "/sse",
                "health": "/health",
                "docs": "/docs"
            }
        }

    return app

def run_sse_production():
    """Production SSE server for Railway/Render."""
    app = create_production_app()
    port = int(os.getenv("PORT", 8000))
    
    print(f"Igniting Production SSE Server on port {port}...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )

# ------------------------------------------------------------------------------
# LEGACY SERVERS (Backward Compatibility)
# ------------------------------------------------------------------------------

def run_legacy_sse():
    """Legacy Monolith SSE (for local testing)."""
    from arifos.mcp.sse import create_sse_app as legacy_create_sse_app
    port = int(os.getenv("PORT", 8000))
    app = legacy_create_sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)

# ------------------------------------------------------------------------------
# MAIN ENTRY POINT
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "default"

    # PRODUCTION: Use this for Railway/Render
    if arg in ["sse", "production"]:
        run_sse_production()
    
    # DEVELOPMENT: Use these for local testing
    elif arg == "trinity-sse":
        run_legacy_sse()
    elif arg == "trinity":
        import asyncio
        from arifos.mcp.server import main_stdio as legacy_stdio
        asyncio.run(legacy_stdio())
        
    # DEFAULT: Stdio mode (Claude Desktop local)
    else:
        from arifos.mcp.gateway import mcp
        mcp.run(transport="stdio")

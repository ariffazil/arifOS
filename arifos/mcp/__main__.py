"""
arifOS MCP Entry Point (v52.4.1-SEAL)
Authority: Antigravity (Sovereign Architect)
Ref: ADR_001_CONSTITUTIONAL_MONOLITH

Usage:
  python -m arifos.mcp sse          # Production Monolith (SSE/HTTP)
  python -m arifos.mcp trinity      # Legacy Local (Stdio)

DITEMPA BUKAN DIBERI
"""

import sys
import os
import uvicorn

def run_production_monolith():
    """
    Ignite the v52 Constitutional Monolith.
    
    Architecture:
      - Module: arifos.mcp.sse
      - Transport: SSE (Claude) + HTTP (ChatGPT)
      - Port: $PORT (default 8000)
      - Bind: 0.0.0.0 (Container)
    """
    # Import the Sealed Implementation directly
    from arifos.mcp.sse import app
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Igniting Constitutional Monolith on port {port}...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

def run_legacy_stdio():
    """Legacy Stdio mode for local testing."""
    import asyncio
    from arifos.mcp.server import main_stdio
    asyncio.run(main_stdio())

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "default"

    # PRODUCTION PATH (The Truth)
    if arg in ["sse", "production"]:
        run_production_monolith()
    
    # LEGACY PATHS
    elif arg == "trinity":
        run_legacy_stdio()
        
    # DEFAULT (Fallback to Production for Container Safety)
    else:
        # If no args, assume we might be in a container CMD that forgot args,
        # or default to production safety.
        print("No mode specified. Defaulting to Production Monolith.")
        run_production_monolith()
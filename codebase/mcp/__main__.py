"""
canonical_core MCP CLI Entry Point

Usage:
    python -m canonical_core.mcp           # stdio transport
    python -m canonical_core.mcp trinity   # stdio transport (explicit)
    python -m canonical_core.mcp sse       # SSE transport
"""

import sys

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "trinity"
    
    if mode == "sse":
        # SSE transport (Railway/Cloud)
        from codebase.mcp.sse import mcp
        print("Starting canonical_core MCP SSE server...")
        # Server will start via uvicorn externally
    else:
        # stdio transport (Claude Desktop, local)
        from codebase.mcp.server import main
        print("Starting canonical_core MCP stdio server...")
        main()

"""
codebase.mcp MCP CLI Entry Point

Usage:
    python -m codebase.mcp              # stdio transport (default)
    python -m codebase.mcp stdio        # stdio transport (explicit)
    python -m codebase.mcp sse          # SSE transport (Railway/Cloud)
    python -m codebase.mcp sse-simple   # SSE transport (minimal/reliable)
"""

import sys

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    
    if mode == "sse":
        # Full SSE transport (Railway/Cloud) - with all features
        try:
            from codebase.mcp.sse import main
            print("[BOOT] Starting codebase MCP SSE server (full)...")
            main()
        except Exception as e:
            print(f"[ERROR] Full SSE failed: {e}")
            print("[FALLBACK] Trying minimal SSE server...")
            from codebase.mcp.sse_simple import main as main_simple
            main_simple()
    
    elif mode == "sse-simple":
        # Minimal SSE transport (Railway/Cloud) - reliable fallback
        from codebase.mcp.sse_simple import main
        print("[BOOT] Starting codebase MCP SSE server (minimal)...")
        main()
    
    else:
        # stdio transport (Claude Desktop, local)
        from codebase.mcp.server import main
        print("[BOOT] Starting codebase MCP stdio server...")
        main()

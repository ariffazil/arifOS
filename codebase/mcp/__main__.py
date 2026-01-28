"""
codebase.mcp MCP CLI Entry Point

Usage:
    python -m codebase.mcp              # stdio transport (default)
    python -m codebase.mcp stdio        # stdio transport (Claude Code, Claude Desktop, Kimi, Gemini CLI)
    python -m codebase.mcp http         # Streamable HTTP transport (ChatGPT Dev Mode, Codex, Railway)
    python -m codebase.mcp sse          # Alias for http (backward compat)
    python -m codebase.mcp sse-simple   # Minimal HTTP fallback
"""

import sys

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if mode in ("http", "sse"):
        # Streamable HTTP transport (Railway/Cloud/ChatGPT/Codex)
        # "sse" is kept as alias for backward compatibility
        try:
            from codebase.mcp.sse import main
            main()
        except Exception as e:
            print(f"[ERROR] HTTP server failed: {e}")
            print("[FALLBACK] Trying minimal server...")
            from codebase.mcp.sse_simple import main as main_simple
            main_simple()

    elif mode == "sse-simple":
        # Minimal HTTP transport — reliable fallback
        from codebase.mcp.sse_simple import main
        print("[BOOT] Starting codebase MCP server (minimal fallback)...")
        main()

    else:
        # stdio transport (Claude Code, Claude Desktop, Kimi, Gemini CLI)
        from codebase.mcp.server import main
        main()

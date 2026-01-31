"""
codebase.mcp MCP CLI Entry Point (v55 Hardened)
"""

import sys

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if mode in ("http", "sse"):
        from codebase.mcp.entrypoints.sse_entry import main

        main()
    elif mode == "sse-simple":
        # Deprecated but kept for fallback if needed, or redirect to sse
        print("[WARN] sse-simple is deprecated, using sse transport.")
        from codebase.mcp.entrypoints.sse_entry import main

        main()
    else:
        from codebase.mcp.entrypoints.stdio_entry import main

        main()

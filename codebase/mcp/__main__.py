"""
codebase.mcp MCP CLI Entry Point (v55 Hardened)
"""

import sys


def main():
    """Main entry point for MCP CLI."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"

    if mode in ("http", "sse"):
        from codebase.mcp.entrypoints.sse_entry import main as sse_main

        sse_main()
    elif mode == "sse-simple":
        # Deprecated but kept for fallback if needed, or redirect to sse
        print("[WARN] sse-simple is deprecated, using sse transport.")
        from codebase.mcp.entrypoints.sse_entry import main as sse_main

        sse_main()
    else:
        from codebase.mcp.entrypoints.stdio_entry import main as stdio_main

        stdio_main()


if __name__ == "__main__":
    main()

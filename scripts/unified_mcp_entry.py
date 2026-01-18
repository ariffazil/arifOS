#!/usr/bin/env python3
"""
arifOS Unified MCP Entry Point

This is the single entry point for the unified MCP server that consolidates
all previous MCP servers into one cohesive implementation.

Usage:
    python scripts/unified_mcp_entry.py

Transport: stdio (for Claude Desktop integration)
Server: arifos_core.mcp.unified_server
Tools: 22 consolidated tools

Constitutional Authority: F1-F9 governance enforced
Version: v46.2

DITEMPA BUKAN DIBERI
"""

import sys
import asyncio
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Import unified server
from arifos.mcp.unified_server import main, print_stats

if __name__ == "__main__":
    # Print statistics on startup
    print_stats()
    print()
    print("Starting arifOS Unified MCP Server...")
    print("Transport: stdio (Claude Desktop)")
    print("Press Ctrl+C to stop.")
    print()

    # Run the server
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)

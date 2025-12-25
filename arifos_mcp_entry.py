#!/usr/bin/env python3
"""
arifOS MCP Entry Point

Constitutional stdio transport for IDE integration.
Launches the MCP server with all 15 tools (5 legacy + 10 constitutional pipeline).

Usage:
    python arifos_mcp_entry.py

Constitutional Compliance:
- F1 (Amanah): Clean session lifecycle with graceful shutdown
- F5 (Peace^2): Non-destructive termination on KeyboardInterrupt
- F9 (Anti-Hantu): Deterministic, mechanical governance

DITEMPA BUKAN DIBERI - Forged, not given.
"""

import asyncio
import sys
from pathlib import Path

# Add arifos_core to path
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root))

from arifos_core.mcp.server import mcp_server


async def main() -> None:
    """Main entry point for arifOS MCP server."""
    print("[arifOS MCP] Initializing constitutional governance pipeline...", file=sys.stderr)
    print("[arifOS MCP] 15 tools ready: 5 legacy + 10 constitutional (000->999)", file=sys.stderr)
    print("[arifOS MCP] All tools enforce the 9 Constitutional Floors (F1-F9)", file=sys.stderr)
    print("[arifOS MCP] DITEMPA BUKAN DIBERI - The server is forged.\n", file=sys.stderr)

    try:
        await mcp_server.run_stdio()
    except KeyboardInterrupt:
        # F5 (Peace^2): Graceful shutdown
        print("\n[arifOS MCP] Received shutdown signal. Closing session...", file=sys.stderr)
        print("[arifOS MCP] Session sealed. All audit trails preserved.", file=sys.stderr)
    except Exception as e:
        # F1 (Amanah): Audit all failures
        print(f"\n[arifOS MCP] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

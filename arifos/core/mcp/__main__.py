
"""
arifOS MCP Entry Point (v50.5.0)
Usage: python -m arifos.core.mcp [mode]

Modes:
  stdio (default): Run unified 16-tool server via stdio (for local Claude Desktop)
  sse: Run unified 16-tool SSE server (for remote/cloud access)
  trinity: Run 5-tool Trinity server via stdio (simplified interface)
  trinity-sse: Run 5-tool Trinity SSE server (for remote/cloud access)

Trinity Tools (5-Tool Constitutional Framework):
  000_init    → Gate (Authority + Injection + Amanah)
  agi_genius  → Mind (SENSE → THINK → ATLAS → FORGE)
  asi_act     → Heart (EVIDENCE → EMPATHY → ACT)
  apex_judge  → Soul (EUREKA → JUDGE → PROOF)
  999_vault   → Seal (Merkle + zkPC + Immutable Log)

Mnemonic: "Init the Genius, Act with Heart, Judge at Apex, seal in Vault."

DITEMPA BUKAN DIBERI
"""
import argparse
import asyncio
import sys

from arifos.core.mcp.sse import main as sse_main
from arifos.core.mcp.unified_server import main as stdio_main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="arifOS MCP Server (v50.5.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m arifos.core.mcp          # stdio (16 tools)
  python -m arifos.core.mcp sse      # SSE (16 tools)
  python -m arifos.core.mcp trinity  # stdio (5 Trinity tools)
  python -m arifos.core.mcp trinity-sse  # SSE (5 Trinity tools)
        """
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="stdio",
        choices=["stdio", "sse", "trinity", "trinity-sse"],
        help="Server mode (default: stdio)"
    )

    args = parser.parse_args()

    if args.mode == "sse":
        sse_main()
    elif args.mode == "trinity":
        from arifos.core.mcp.trinity_server import main_stdio
        asyncio.run(main_stdio())
    elif args.mode == "trinity-sse":
        from arifos.core.mcp.trinity_server import main_sse
        main_sse()
    else:
        asyncio.run(stdio_main())

"""
arifOS MCP Entry Point (v50.5.1)
Usage: python -m arifos.mcp [mode]

Modes:
  trinity (default): Run 5-tool Trinity server via stdio (for local Claude Desktop)
  trinity-sse: Run 5-tool Trinity SSE server (for Railway/cloud access)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="arifOS MCP Server (v50.5.1)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m arifos.mcp              # Trinity stdio (5 tools) - default
  python -m arifos.mcp trinity      # Trinity stdio (5 tools)
  python -m arifos.mcp trinity-sse  # Trinity SSE (5 tools) - for Railway
        """
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="trinity",
        choices=["trinity", "trinity-sse"],
        help="Server mode (default: trinity)"
    )

    args = parser.parse_args()

    if args.mode == "trinity-sse":
        from arifos.mcp.trinity_server import main_sse
        main_sse()
    else:
        from arifos.mcp.trinity_server import main_stdio
        asyncio.run(main_stdio())

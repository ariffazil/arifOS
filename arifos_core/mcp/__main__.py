
"""
arifOS MCP Entry Point
Usage: python -m arifos_core.mcp [mode]
Modes:
  stdio (default): Run standard I/O server (for local Claude Desktop)
  sse: Run SSE server (for remote/cloud access)
"""
import argparse
import asyncio
import sys

from arifos_core.mcp.sse import main as sse_main
from arifos_core.mcp.unified_server import main as stdio_main

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="arifOS MCP Server")
    parser.add_argument("mode", nargs="?", default="stdio", choices=["stdio", "sse"], help="Server mode")

    args = parser.parse_args()

    if args.mode == "sse":
        sse_main()
    else:
        asyncio.run(stdio_main())

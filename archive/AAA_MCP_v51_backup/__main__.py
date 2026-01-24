"""
AAA MCP Entry Point (v51.0.0)

Usage:
  python -m AAA_MCP              # stdio mode (default)
  python -m AAA_MCP sse          # SSE mode for Railway

DITEMPA BUKAN DIBERI
"""

import asyncio
import sys

from AAA_MCP.server import main_stdio, main_sse

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sse":
        main_sse()
    else:
        asyncio.run(main_stdio())

"""
arifOS MCP Entry Point (v52.0.0)

Usage:
  python -m arifos.mcp              # stdio mode (default)
  python -m arifos.mcp trinity-sse  # SSE mode for Railway

DITEMPA BUKAN DIBERI
"""

import asyncio
import sys
import logging

from arifos.mcp.server import main_stdio
from arifos.mcp.sse import create_sse_app

def main_sse():
    """Run SSE server."""
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    app = create_sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("sse", "trinity-sse"):
        main_sse()
    else:
        asyncio.run(main_stdio())
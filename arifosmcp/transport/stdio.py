"""
STDIO Transport Entrypoint
═══════════════════════════
Runs the arifOS MCP server over standard input/output.
"""
from __future__ import annotations

import asyncio

from arifosmcp.server import mcp


def run_stdio() -> None:
    """Run the MCP server over STDIO."""
    mcp.run(transport="stdio")


async def run_stdio_async() -> None:
    """Run the MCP server over STDIO (async)."""
    await mcp.run_stdio_async()


if __name__ == "__main__":
    run_stdio()

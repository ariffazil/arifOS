"""
arifOS MCP Server Entry Point (SSE / Streamable HTTP)
Wraps transports.sse.SSETransport for backward compatibility.
"""

import asyncio
import logging
from ..core.tool_registry import ToolRegistry
from ..transports.sse import SSETransport

logging.basicConfig(level=logging.INFO)


def main():
    """Run Streamable HTTP server."""
    registry = ToolRegistry()
    transport = SSETransport(registry)
    asyncio.run(transport.start())


if __name__ == "__main__":
    main()

# Alias for pyproject.toml entry point
main_sse = main

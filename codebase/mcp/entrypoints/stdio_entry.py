"""
arifOS MCP Server Entry Point (Stdio)
Wraps transports.stdio.StdioTransport for backward compatibility.
"""

import asyncio
import logging
from ..core.tool_registry import ToolRegistry
from ..transports.stdio import StdioTransport

logging.basicConfig(level=logging.INFO)


def main():
    """Run standard stdio server."""
    registry = ToolRegistry()
    transport = StdioTransport(registry)
    asyncio.run(transport.start())


if __name__ == "__main__":
    main()

# Alias for pyproject.toml entry point
main_stdio = main

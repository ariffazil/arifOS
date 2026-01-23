"""
arifOS MCP Entry Point - Glass-box Constitutional Governance Pipeline

This is the stdio entry point for the glass-box MCP server.
Exposes 15 tools (000?999 pipeline + legacy helpers).

Version: v1.0.0
Phase: 2A (Post-Refactoring)
"""

import asyncio

# Configure logging to stderr (MCP protocol requirement)
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='[arifOS MCP] %(message)s',
    stream=sys.stderr  # Critical: Use stderr, not stdout
)
logger = logging.getLogger(__name__)



# Updated entry point: use the unified MCP server for Kimi/ChatGPT MCP compatibility
from .unified_server import main as unified_main
from .unified_server import print_stats

if __name__ == "__main__":
    print_stats()
    print()
    print("Starting arifOS Unified MCP Server (Kimi/ChatGPT MCP entry)...")
    print("Transport: stdio (Kimi CLI/Claude Desktop)")
    print("Press Ctrl+C to stop.")
    print()
    asyncio.run(unified_main())

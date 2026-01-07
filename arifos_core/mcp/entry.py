"""
arifOS MCP Entry Point - Glass-box Constitutional Governance Pipeline

This is the stdio entry point for the glass-box MCP server.
Exposes 15 tools (000?999 pipeline + legacy helpers).

Version: v1.0.0
Phase: 2A (Post-Refactoring)
"""

import asyncio
import sys

# Configure logging to stderr (MCP protocol requirement)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[arifOS MCP] %(message)s',
    stream=sys.stderr  # Critical: Use stderr, not stdout
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for glass-box MCP server."""
    try:
        logger.info("Initializing constitutional governance pipeline...")
        
        # Import the MCP server
        from arifos_core.mcp.server import MCPServer
        
        # Create server instance
        mcp_server = MCPServer()
        
        logger.info("15 tools ready: 5 legacy + 10 constitutional (000->999)")
        logger.info("All tools enforce the 9 Constitutional Floors (F1-F9)")
        logger.info("DITEMPA BUKAN DIBERI - The server is forged.\n")
        
        # Run stdio server
        await mcp_server.run_stdio()
        
    except Exception as e:
        logger.error(f"ERROR: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

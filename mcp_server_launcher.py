#!/usr/bin/env python
"""
arifOS MCP Server Launcher (stdio mode for kimi CLI)
DITEMPA BUKAN DIBERI
"""
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import the MCP server
if __name__ == "__main__":
    import asyncio

    from arifos_core.kernel.mcp_server import main
    asyncio.run(main())

"""
arifOS MCP Server Entry Point for Claude Code
Standalone entry point that doesn't require relative imports
"""

import sys
import os
from pathlib import Path

# Add arifOS to Python path
arifos_root = Path(__file__).parent
if str(arifos_root) not in sys.path:
    sys.path.insert(0, str(arifos_root))

# Set environment variables
os.environ.setdefault("ARIFOS_ALLOW_LEGACY_SPEC", "1")
os.environ.setdefault("ARIFOS_PHYSICS_DISABLED", "1")

# Configure logging to stderr (MCP protocol requirement)
import logging
logging.basicConfig(
    level=logging.INFO,
    format='[arifOS MCP] %(message)s',
    stream=sys.stderr
)

# Import and run the unified MCP server
from arifos_core.mcp.unified_server import main as unified_main
from arifos_core.mcp.unified_server import print_stats

if __name__ == "__main__":
    import asyncio

    print_stats()
    print()
    print("Starting arifOS Constitutional Governance MCP Server...")
    print("Transport: stdio (Claude Code)")
    print("Motto: Ditempa Bukan Diberi (Forged, Not Given)")
    print()

    asyncio.run(unified_main())

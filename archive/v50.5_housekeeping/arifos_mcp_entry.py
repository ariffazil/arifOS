"""
arifOS MCP Entry Point - Shim
Restores root-level access to the unified MCP server for external agents (Kimi, ChatGPT).
"""

import asyncio
import sys
from pathlib import Path

# Add repo root to sys.path to ensure arifos package is found
repo_root = Path(__file__).parent.absolute()
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

import logging

# Set Critical Environment Variables (Bypassing boot_local.bat)
import os

# [CRITICAL] Force all logging to stderr to prevent stdout corruption (MCP Protocol)
logging.basicConfig(level=logging.WARNING, stream=sys.stderr, format='%(name)s: %(message)s')

os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"
os.environ["ARIFOS_CONSTITUTIONAL_MODE"] = "AAA"
os.environ["ARIFOS_HUMAN_SOVEREIGN"] = "Arif"

# Import the unified server main implementation
from arifos.core.mcp.unified_server import main as unified_main
from arifos.core.mcp.unified_server import print_stats

if __name__ == "__main__":
    # [CRITICAL] Windows Stdio/Proactor Fix
    # Kimi CLI uses stdio pipes to communicate. On Windows, Python default ProactorEventLoop
    # does not support pipes properly. We must force SelectorEventLoop.
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # print_stats() # Disabled to keep stdout clean for MCP stdio
    try:
        asyncio.run(unified_main())
    except Exception as e:
        # Log any crash to stderr so it can be debugged
        logging.critical(f"Server crashed: {e}", exc_info=True)
        sys.exit(1)

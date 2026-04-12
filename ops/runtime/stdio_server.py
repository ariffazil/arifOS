"""
arifOS STDIO Server - Local MCP Client Integration
═══════════════════════════════════════════════════

Minimal STDIO entry point for local AI assistants.
Uses the unified server from project root.

Usage:
    python ops/runtime/stdio_server.py

Environment:
    ARIFOS_DEPLOYMENT=local      # Forces local/stdio mode
    ARIFOS_MINIMAL_STDIO=1       # Disables HTTP overhead
"""

import os
import sys

# Force local stdio mode
os.environ["ARIFOS_DEPLOYMENT"] = "local"
os.environ["AAA_MCP_TRANSPORT"] = "stdio"
os.environ["ARIFOS_MINIMAL_STDIO"] = "1"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

# Import unified server
from server import mcp
from arifosmcp.runtime.fastmcp_ext.transports import run_server


def main():
    """Run arifOS in STDIO mode for local MCP clients."""
    print("🔥 arifOS STDIO Server starting...", file=sys.stderr)
    print("   Mode: Local (minimal)", file=sys.stderr)
    print("   Transport: STDIO", file=sys.stderr)
    print("   Server: Unified (root server.py)", file=sys.stderr)
    print("   Floors: F1-F13 (constitutional governance enabled)", file=sys.stderr)
    
    # Run unified server in stdio mode
    try:
        # Pass transport explicitly to avoid picking up bridge/HTTP defaults
        run_server(mcp, mode="stdio")
    except KeyboardInterrupt:
        print("\n👋 arifOS STDIO Server stopped", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

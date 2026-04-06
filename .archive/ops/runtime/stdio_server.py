"""
arifOS STDIO Server - Local MCP Client Integration

This is a minimal STDIO entry point for local AI assistants:
- Claude Desktop
- Cursor IDE
- Gemini CLI
- VS Code Copilot
- Any MCP-compatible client

Usage:
    # Claude Desktop config
    {
        "mcpServers": {
            "arifOS": {
                "command": "python",
                "args": ["/path/to/arifOS/stdio_server.py"]
            }
        }
    }

Environment:
    ARIFOS_DEPLOYMENT=local      # Forces local/stdio mode
    ARIFOS_MINIMAL_STDIO=1       # Disables HTTP/WebMCP/A2A overhead
"""

import os
import sys

# Force local stdio mode
os.environ["ARIFOS_DEPLOYMENT"] = "local"
os.environ["AAA_MCP_TRANSPORT"] = "stdio"
os.environ["ARIFOS_MINIMAL_STDIO"] = "1"

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from arifosmcp.runtime.server import create_aaa_mcp_server
from arifosmcp.runtime.fastmcp_ext.transports import run_server


def main():
    """Run arifOS in STDIO mode for local MCP clients."""
    print("🔥 arifOS STDIO Server starting...", file=sys.stderr)
    print("   Mode: Local (minimal)", file=sys.stderr)
    print("   Transport: STDIO", file=sys.stderr)
    print("   Floors: F1-F13 (constitutional governance enabled)", file=sys.stderr)
    
    # Create minimal MCP server (no HTTP/WebMCP/A2A)
    mcp = create_aaa_mcp_server()
    
    # Run in stdio mode
    try:
        run_server(mcp, mode="stdio", host="", port=0)
    except KeyboardInterrupt:
        print("\n👋 arifOS STDIO Server stopped", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()

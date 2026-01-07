#!/usr/bin/env python3
"""
Start AAA MCP Server for Remote Access (ChatGPT/Remote Clients)
Uses SSE (Server-Sent Events) transport instead of stdio
"""

import sys
from pathlib import Path

# Add repo root to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from arifos_mcp.server import mcp

if __name__ == "__main__":
    print("Starting AAA MCP Server (SSE mode for ChatGPT)")
    print(f"Endpoint: http://localhost:8000/sse/")
    print("Use cloudflared to expose this publicly")
    
    # Run with SSE transport on port 8000
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

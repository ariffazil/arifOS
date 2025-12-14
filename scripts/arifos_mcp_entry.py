from __future__ import annotations

"""
arifOS MCP Entry Point for Claude Desktop.

This script exposes the existing arifOS MCPServer over MCP stdio using
the official `mcp` Python SDK, so Claude Desktop can call:

- arifos_judge(query: str)
- arifos_recall(user_id: str, prompt: str, max_results: int = 5)
- arifos_audit(user_id: str, days: int = 7)

Usage (configured in Claude Desktop config):
    "mcpServers": {
      "arifos": {
        "command": "python",
        "args": [
          "C:/Users/User/OneDrive/Documents/GitHub/arifOS/scripts/arifos_mcp_entry.py"
        ]
      }
    }
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict

from mcp.server import FastMCP

# Ensure arifOS repo root is on sys.path even when launched
# from a different working directory (Claude Desktop does this).
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
  sys.path.insert(0, str(REPO_ROOT))

from arifos_core.mcp.server import MCPServer


core = MCPServer()
server = FastMCP("arifos")


@server.tool()
async def arifos_judge(query: str) -> Dict[str, Any]:
  """
  Judge a query through the arifOS governed pipeline.

  Returns a verdict and brief explanation.
  """
  return core.call_tool("arifos_judge", {"query": query})


@server.tool()
async def arifos_recall(user_id: str, prompt: str, max_results: int = 5) -> Dict[str, Any]:
  """
  Recall memories from L7 (Mem0 + Qdrant) for a user.

  Recalled memories are suggestions, not facts.
  """
  return core.call_tool(
    "arifos_recall",
    {"user_id": user_id, "prompt": prompt, "max_results": max_results},
  )


@server.tool()
async def arifos_audit(user_id: str, days: int = 7) -> Dict[str, Any]:
  """
  Retrieve audit/ledger data for a user (stubbed).
  """
  return core.call_tool("arifos_audit", {"user_id": user_id, "days": days})


async def main() -> None:
  """Run the MCP server over stdio (for Claude Desktop)."""
  await server.run_stdio_async()


if __name__ == "__main__":
  asyncio.run(main())

#!/usr/bin/env python3
"""
Kimi → arifOS MCP Bridge
Executes MCP tool calls from Kimi agent workspace.
"""

import asyncio
import json
import sys
import os

# Add arifOS to path (adjust if needed)
ARIFOS_PATH = r"C:\Users\User\arifOS"
if ARIFOS_PATH not in sys.path:
    sys.path.insert(0, ARIFOS_PATH)

from arifos.mcp.bridge import (
    bridge_init_router,
    bridge_agi_router,
    bridge_asi_router,
    bridge_apex_router,
    bridge_vault_router,
)

async def execute_tool(tool_name: str, **kwargs):
    """Execute an arifOS MCP tool."""
    
    tools = {
        "000_init": bridge_init_router,
        "agi_genius": bridge_agi_router,
        "asi_act": bridge_asi_router,
        "apex_judge": bridge_apex_router,
        "999_vault": bridge_vault_router,
    }
    
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    result = await tools[tool_name](**kwargs)
    return result

def main():
    """CLI entry point for Kimi."""
    if len(sys.argv) < 2:
        print("Usage: python kimibridge.py <tool> <args_json>")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    result = asyncio.run(execute_tool(tool_name, **args))
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()

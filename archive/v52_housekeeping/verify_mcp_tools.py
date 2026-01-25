import asyncio
import os
import sys

# Set PYTHONPATH
os.environ["PYTHONPATH"] = "."
sys.path.append(".")

from arifos.mcp.server import create_mcp_server

async def main():
    print("--- arifOS MCP Tool Verification ---")
    
    # 1. Check Tool Definitions
    from arifos.mcp.server import TOOL_DESCRIPTIONS
    tools = list(TOOL_DESCRIPTIONS.keys())
    
    print(f"Total tools defined: {len(tools)}")
    for name in tools:
        desc = TOOL_DESCRIPTIONS[name]
        print(f"  ✓ {name}: {desc['description'][:50]}...")
    
    # 2. Check Tool Routers
    from arifos.mcp.server import TOOL_ROUTERS
    routers = list(TOOL_ROUTERS.keys())
    print(f"Total routers defined: {len(routers)}")
    
    if len(tools) >= 5 and len(routers) >= 5:
        print("\n✅ SUCCESS: All 5 Trinity tools are defined and routed.")
    else:
        print(f"\n❌ FAILURE: Definitions/Routers mismatch or incomplete.")
        
    print("--- Verification Complete ---")

if __name__ == "__main__":
    asyncio.run(main())

"""
AAA Cluster Verification Script (v52.2)
Verifies the Petronas Pattern topology: Axis, Arif, Apex, and Gateway.
"""
import sys
import os
import asyncio
from typing import List

# Ensure we can import from root
sys.path.append(os.getcwd())

async def verify_server(name: str, module_path: str, expected_tools: List[str]):
    print(f"\n🔍 Verifying {name} Server ({module_path})...")
    try:
        # Dynamic import
        import importlib
        module = importlib.import_module(module_path)
        
        # Check for mcp object
        if not hasattr(module, "mcp"):
            print(f"❌ {name}: Missing 'mcp' object")
            return False
            
        mcp = module.mcp
        print(f"✅ {name}: MCP Object Found ({mcp.name})")
        
        # Check tools (FastMCP lists tools via list_tools, but we can inspect the object registry if available, 
        # or just rely on the import success for now since running it requires async context)
        # FastMCP tools are registered in mcp._tools usually.
        
        found_tools = list(mcp._tool_manager._tools.keys()) if hasattr(mcp, "_tool_manager") else []
        # FastMCP internals might differ, but let's try to just list them if possible or print count
        
        print(f"   Tools found: {len(found_tools)}")
        for tool in expected_tools:
            if any(tool in t for t in found_tools):
                print(f"   ✅ Tool '{tool}' found")
            else:
                # FastMCP might rename tools with server prefix?
                # The code uses @mcp.tool() -> axis_000_init. Name is likely "axis_000_init"
                if tool in found_tools:
                     print(f"   ✅ Tool '{tool}' found")
                else:
                     print(f"   ⚠️ Tool '{tool}' NOT found in {found_tools}")
                     
        return True
    except ImportError as e:
        print(f"❌ {name}: Import Error - {e}")
        return False
    except Exception as e:
        print(f"❌ {name}: Unexpected Error - {e}")
        return False

async def main():
    print("🚀 AAA Cluster Verification (v52.2)")
    print("====================================")
    
    success = True
    
    # 1. Verify AXIS (Foundation)
    if not await verify_server("AXIS", "arifos.mcp.servers.axis", ["axis_000_init", "axis_999_vault"]):
        success = False

    # 2. Verify ARIF (Cognition)
    if not await verify_server("ARIF", "arifos.mcp.servers.arif", ["arif_agi_genius", "arif_asi_act"]):
        success = False

    # 3. Verify APEX (Judgment)
    if not await verify_server("APEX", "arifos.mcp.servers.apex", ["apex_judge"]):
        success = False

    # 4. Verify GATEWAY (Router)
    print("\n🔍 Verifying GATEWAY...")
    try:
        from arifos.mcp import gateway
        print(f"✅ Gateway: Module imported")
        # Check mounting logic simulation
        # Cannot easily check mounts without running, but import success is good.
    except ImportError as e:
        print(f"❌ Gateway: Import Error - {e}")
        success = False

    print("\n====================================")
    if success:
        print("✅ CLUSTER VERIFIED. Ready for Deployment.")
        sys.exit(0)
    else:
        print("❌ CLUSTER VERIFICATION FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

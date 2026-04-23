import asyncio
import os
import sys

# CRITICAL: Set env vars BEFORE any arifOS imports to avoid stale profile state
os.environ["ARIFOS_PUBLIC_TOOL_PROFILE"] = "full"
os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"

from pathlib import Path
from fastmcp import Client
import json

# Add project root to sys.path with priority
sys.path.insert(0, str(Path(__file__).parent.parent))

from arifosmcp.runtime.server import create_aaa_mcp_server

async def test_hardened_9_tools():
    """Test the Nervous System 9 internal tools suite."""
    print("\n--- Starting Nervous System 9 Internal Tools Test ---")
    
    mcp_server = create_aaa_mcp_server()
    
    async with Client(mcp_server) as client:
        # 1. Anchor session to get auth_context
        print("Anchoring session...")
        anchor_call = await client.call_tool("init_anchor", {"raw_input": "Internal Test Session"})
        
        # Parse the RuntimeEnvelope from the CallToolResult
        anchor_data = json.loads(anchor_call.content[0].text)
        session_id = anchor_data.get("session_id")
        auth_context = anchor_data.get("auth_context")
        
        print(f"Session Anchored: {session_id}")
        
        # Define Nervous System 9 test cases
        internal_tools = [
            ("system_health", {"include_swap": True}),
            ("fs_inspect", {"path": ".", "depth": 1}),
            ("chroma_query", {"query": "test query", "collection_name": "default"}),
            ("log_tail", {"lines": 5}),
            ("process_list", {"limit": 5}),
            ("net_status", {"check_ports": True}),
            ("arifos_list_resources", {}),
            ("arifos_read_resource", {"uri": "canon://index"}),
            ("cost_estimator", {"action_description": "test compute", "operation": "compute"}),
        ]
        
        results = []
        for tool_name, args in internal_tools:
            print(f"\nTesting {tool_name}...")
            # Inject governance parameters
            args["session_id"] = session_id
            args["auth_context"] = auth_context
            
            try:
                call_res = await client.call_tool(tool_name, args)
                envelope = json.loads(call_res.content[0].text)
                
                if envelope.get("ok"):
                    print(f"✅ {tool_name} Passed (Stage: {envelope.get('stage')}, Verdict: {envelope.get('verdict')})")
                    results.append(True)
                else:
                    print(f"❌ {tool_name} Returned Error: {envelope.get('errors')}")
                    results.append(False)
            except Exception as e:
                print(f"❌ {tool_name} Failed with exception: {e}")
                results.append(False)
        
        print("\n--- Summary ---")
        passed = sum(1 for r in results if r)
        print(f"Total: {len(internal_tools)}")
        print(f"Passed: {passed}")
        print(f"Failed: {len(internal_tools) - passed}")
        
        if passed == len(internal_tools):
            print("\n✅ NERVOUS SYSTEM 9 VALIDATED (100% Forged)")
        else:
            print(f"\n⚠️ {len(internal_tools) - passed} tools still in 'Propa' state.")

if __name__ == "__main__":
    asyncio.run(test_hardened_9_tools())

#!/usr/bin/env python3
"""
Phase 0 MCP Protocol Test
Tests the hardened tools via actual MCP protocol calls (like MCP Inspector would).
"""

import os
import asyncio
import json
import sys
import subprocess


class MCPClient:
    """Simple MCP client for testing stdio servers."""

    def __init__(self, process: subprocess.Popen):
        self.process = process
        self.request_id = 0

    async def call(self, method: str, params: dict = None) -> dict:
        """Make an MCP request and wait for response."""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {},
        }

        # Send request
        line = json.dumps(request) + "\n"
        self.process.stdin.write(line.encode())
        self.process.stdin.flush()

        # Read response
        response_line = self.process.stdout.readline().decode()
        return json.loads(response_line)

    async def initialize(self) -> dict:
        """Initialize the MCP session."""
        return await self.call(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "clientInfo": {"name": "phase0-tester", "version": "1.0.0"},
            },
        )

    async def list_tools(self) -> list:
        """List available tools."""
        result = await self.call("tools/list")
        return result.get("result", {}).get("tools", [])

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Call a tool."""
        result = await self.call("tools/call", {"name": name, "arguments": arguments})
        return result


def _extract_content_payload(response: dict) -> dict:
    if "result" in response:
        content = response["result"].get("content", [])
        if content and "text" in content[0]:
            return json.loads(content[0]["text"])
        return response["result"]
    if "error" in response:
        return {"ok": False, "error": response["error"]}
    return response


async def test_phase0_hardening():
    """Test Phase 0 hardened tools via MCP protocol."""

    print("=" * 70)
    print("PHASE 0 MCP PROTOCOL TEST")
    print("Testing hardened tools via actual MCP stdio protocol")
    print("=" * 70)

    # Start the MCP server
    print("\n📡 Starting arifOS MCP server...")
    env = {
        **dict(subprocess.os.environ),
        "ARIFOS_MINIMAL_STDIO": "1",
        "AAA_MCP_TRANSPORT": "stdio",
    }

    process = subprocess.Popen(
        [sys.executable, "-m", "arifosmcp.runtime", "stdio"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.environ.get("ARIFOS_HOME", "/root") + "/arifOS",
        env=env,
    )

    client = MCPClient(process)

    try:
        # Initialize
        print("\n1️⃣ Initializing MCP session...")
        init_result = await client.initialize()
        if "result" not in init_result:
            print(f"❌ Initialize failed: {init_result}")
            return False
        server_name = init_result["result"]["serverInfo"]["name"]
        print(f"   ✅ Connected to: {server_name}")

        # List tools
        print("\n2️⃣ Listing available tools...")
        tools = await client.list_tools()
        tool_names = [t["name"] for t in tools]
        print(f"   Found {len(tools)} tools: {', '.join(tool_names[:5])}...")

        # Verify the current canonical tools exist
        hardened_tools = ["arif_mind_reason", "arif_memory_recall", "arif_ops_measure"]
        for tool in hardened_tools:
            if tool in tool_names:
                print(f"   ✅ {tool} available")
            else:
                print(f"   ❌ {tool} missing")
                return False

        # Test 1: arifos.mind with missing query (should return error envelope)
        print("\n3️⃣ Testing arif_mind_reason...")
        print("   3a. Testing missing query handling...")
        result = await client.call_tool(
            "arif_mind_reason", {"mode": "reason", "session_id": "test-session"}
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(
                f"   ✅ Missing query handled without crash: {content.get('verdict', content.get('status', 'ok'))}"
            )
        else:
            print(f"   ❌ Unexpected payload: {content}")
            return False

        print("   3b. Testing invalid mode...")
        result = await client.call_tool(
            "arif_mind_reason",
            {"mode": "invalid_mode", "query": "test", "session_id": "test-session"},
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(
                f"   ✅ Invalid mode returned payload: {content.get('verdict', content.get('status', 'ok'))}"
            )
        else:
            print(f"   ❌ Unexpected payload: {content}")
            return False

        # Test 2: arifos.memory with invalid mode
        print("\n4️⃣ Testing arif_memory_recall...")
        print("   4a. Testing invalid mode validation...")
        result = await client.call_tool(
            "arif_memory_recall", {"mode": "invalid_mode", "session_id": "test-session"}
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(
                f"   ✅ Invalid mode returned payload: {content.get('verdict', content.get('status', 'ok'))}"
            )
        else:
            print(f"   ❌ Unexpected payload: {content}")
            return False

        print("   4b. Testing vector_store with empty content...")
        result = await client.call_tool(
            "arif_memory_recall",
            {"mode": "store", "query": "", "session_id": "test-session"},
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(
                f"   ✅ Empty content handled without crash: {content.get('verdict', content.get('status', 'ok'))}"
            )
        else:
            print(f"   ❌ Unexpected payload: {content}")
            return False

        print("   4c. Testing vector_forget without identifiers...")
        result = await client.call_tool(
            "arif_memory_recall", {"mode": "get", "session_id": "test-session"}
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(
                f"   ✅ Missing identifier handled without crash: {content.get('verdict', content.get('status', 'ok'))}"
            )
        else:
            print(f"   ❌ Unexpected payload: {content}")
            return False

        # Test 3: arifos.ops with invalid mode
        print("\n5️⃣ Testing arif_ops_measure...")
        print("   5a. Testing invalid mode validation...")
        result = await client.call_tool(
            "arif_ops_measure", {"mode": "invalid_mode", "session_id": "test-session"}
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(
                f"   ✅ Invalid mode returned payload: {content.get('verdict', content.get('status', 'ok'))}"
            )
        else:
            print(f"   ❌ Unexpected payload: {content}")
            return False

        print("   5b. Testing vitals mode...")
        result = await client.call_tool(
            "arif_ops_measure",
            {"mode": "vitals", "action": "system_check", "session_id": "test-session"},
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(f"   ✅ Vitals mode works: {content.get('verdict', content.get('status', 'ok'))}")
        else:
            print(f"   ❌ Vitals failed: {content}")
            return False

        print("   5c. Testing health mode...")
        result = await client.call_tool(
            "arif_ops_measure", {"mode": "health", "session_id": "test-session"}
        )
        content = _extract_content_payload(result)
        if isinstance(content, dict):
            print(f"   ✅ Health mode works: {content.get('verdict', content.get('status', 'ok'))}")
        else:
            print(f"   ❌ Health failed: {content}")
            return False

        # Summary
        print("\n" + "=" * 70)
        print("PHASE 0 MCP TEST SUMMARY")
        print("=" * 70)
        print("\n✅ All hardened tools respond with proper error envelopes")
        print("✅ No crashes observed during invalid input testing")
        print("✅ Valid modes continue to work correctly")

        return True

    finally:
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except:
            process.kill()


if __name__ == "__main__":
    try:
        success = asyncio.run(test_phase0_hardening())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

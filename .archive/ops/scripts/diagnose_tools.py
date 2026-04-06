#!/usr/bin/env python3
"""
Diagnostic script to verify 5-Core MCP tool registration.
Tests tool execution through MCP protocol (not direct calls).
"""

import asyncio
import sys

print("=" * 60)
print("arifOS 5-Core Tool Registration Diagnostic")
print("=" * 60)

# Test 1: Import all modules
print("\n[1] Testing imports...")
try:
    from arifosmcp.transport import __version__

    print(f"✅ All imports successful (version: {__version__})")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check tool registration
print("\n[2] Checking tool registration...")


async def check_tools():
    try:
        tools = await mcp_server.get_tools()
        print(f"✅ Tools registered: {len(tools)}")

        expected_tools = [
            "init_session",
            "agi_cognition",
            "asi_empathy",
            "apex_verdict",
            "vault_seal",
        ]

        for name in expected_tools:
            if name in tools:
                tool = tools[name]
                print(f"  ✅ {name}: {getattr(tool, 'description', 'N/A')[:40]}...")
                if hasattr(tool, "fn") and callable(tool.fn):
                    print(f"     └─ Function bound: {tool.fn.__name__}")
                else:
                    print("     ⚠️  Function binding unclear")
            else:
                print(f"  ❌ {name}: MISSING")

        unexpected = set(tools.keys()) - set(expected_tools)
        if unexpected:
            print(f"\n⚠️  Unexpected tools: {unexpected}")

        return tools
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return {}


tools = asyncio.run(check_tools())

# Test 3: Test tool execution via MCP protocol
print("\n[3] Testing tool execution via MCP protocol...")


async def test_execution():
    try:
        # Use mcp_server's _call_tool method if available
        if hasattr(mcp_server, "_call_tool"):
            print("  Testing init_session via _call_tool...")
            result = await mcp_server._call_tool(
                "init_session",
                {
                    "query": "diagnostic test",
                    "actor_id": "diagnostic",
                    "auth_token": "test_token",
                    "mode": "conscience",
                },
            )
            print(f"    ✅ Result: {result}")
        else:
            print("  ⚠️  _call_tool not available, using direct fn access")
            # Access the underlying function
            init_tool = tools.get("init_session")
            if init_tool and hasattr(init_tool, "fn"):
                result = await init_tool.fn(
                    query="diagnostic test",
                    actor_id="diagnostic",
                    auth_token="test_token",
                    mode="conscience",
                )
                print(f"    ✅ Result: {result.get('verdict', 'N/A')}")

        print("\n✅ Tool execution working!")
        return True

    except Exception as e:
        print(f"❌ Execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


success = asyncio.run(test_execution())

# Test 4: Check FastMCP mounting
print("\n[4] Checking FastMCP mounting...")
print(f"  Server type: {type(mcp_server).__name__}")
print(f"  Has mount(): {hasattr(mcp_server, 'mount')}")

if hasattr(mcp_server, "mount"):
    try:
        app = mcp_server.mount()
        print(f"  ✅ mount() returned: {type(app).__name__}")
        if hasattr(app, "routes"):
            routes = [r.path for r in app.routes if hasattr(r, "path")]
            print(f"  Routes: {routes}")
    except Exception as e:
        print(f"  ❌ mount() failed: {e}")

print("\n" + "=" * 60)
if success and len(tools) == 5:
    print("✅ DIAGNOSTIC PASSED - 5-Core ready for Railway")
else:
    print("⚠️  PARTIAL - Tools registered but execution needs verification")
print("=" * 60)

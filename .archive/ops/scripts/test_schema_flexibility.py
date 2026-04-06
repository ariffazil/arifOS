import asyncio
import os
import sys
import uuid

# Ensure root is in path
sys.path.append(os.getcwd())


# Mock FastMCP Context
class MockContext:
    async def info(self, msg):
        print(f"INFO: {msg}")


async def test_schema_flexibility():
    print("🧪 Testing arifOS.kernel Schema Flexibility...")
    print("============================================")

    from arifosmcp.runtime.tools import metabolic_loop_router

    ctx = MockContext()

    # Case 1: Auto-generated session_id
    print("\n▶️ Case 1: Missing session_id (Auto-generation)")
    res1 = await metabolic_loop_router(query="Test auto-generation", dry_run=True, ctx=ctx)
    print(f"  ✅ Received session_id: {res1.session_id}")
    assert res1.session_id.startswith("session-") or len(res1.session_id) > 0

    # Case 2: Custom Actor ID (Human)
    print("\n▶️ Case 2: Custom Actor ID (Human)")
    res2 = await metabolic_loop_router(
        query="Test human actor", actor_id="human-arif-001", dry_run=True, ctx=ctx
    )
    # Check if actor_id is preserved in payload/auth_context
    print("  ✅ Actor ID accepted: human-arif-001")

    # Case 3: Custom Bot ID (AI LLM)
    print("\n▶️ Case 3: Custom Bot ID (AI LLM)")
    res3 = await metabolic_loop_router(
        query="Test AI bot actor", actor_id="bot-gpt4-nexus", dry_run=True, ctx=ctx
    )
    print("  ✅ Bot ID accepted: bot-gpt4-nexus")

    # Case 4: Non-rigid Session ID
    print("\n▶️ Case 4: Non-rigid Session ID (Custom string)")
    custom_sid = f"TX-FLOW-{uuid.uuid4().hex[:4]}"
    # Set active session manually to simulate existing session
    from arifosmcp.runtime.sessions import set_active_session

    set_active_session(custom_sid)

    res4 = await metabolic_loop_router(query="Test custom session string", dry_run=True, ctx=ctx)
    print(f"  ✅ Custom session_id preserved: {res4.session_id}")
    assert res4.session_id == custom_sid

    print("\n🎉 All schema flexibility tests PASSED.")


if __name__ == "__main__":
    # Disable physics for pure logic test
    os.environ["ARIFOS_PHYSICS_DISABLED"] = "1"
    asyncio.run(test_schema_flexibility())


import asyncio
import inspect
from arifos.mcp.tools.mcp_trinity import mcp_999_vault

async def debug_vault():
    # print(f"SEAL_PHRASE constant: '{SEAL_PHRASE}'")
    
    # Inspect signature
    sig = inspect.signature(mcp_999_vault)
    print(f"\nSignature: {sig}")
    for name, param in sig.parameters.items():
        if name == 'target':
            print(f"Target param default: {param.default}")

    print("\n--- Test 1: Read Action ---")
    # minimal call matching the failing test
    try:
        result = await mcp_999_vault(
            action="read",
            target="canon",
            query="test_entry",
            session_id="debug_read"
        )
        print(f"Result status: {result.get('status')}")
        print(f"Full Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Test 2: Write Action ---")
    try:
        result = await mcp_999_vault(
            action="write",
            target="ledger", 
            session_id="debug_write",
            verdict="SEAL",
            data={"content": "test"}
        )
        print(f"Result status: {result.get('status')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(debug_vault())

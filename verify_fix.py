import asyncio
import time
from arifos.mcp.tools.mcp_trinity import mcp_000_init

async def test_validate():
    print("Testing 000_init(action='validate')...")
    start = time.time()
    result = await mcp_000_init(action="validate", query="Test")
    duration = time.time() - start
    print(f"Result: {result['status']}")
    print(f"Duration: {duration:.4f}s")
    if duration > 1.0:
        print("FAIL: Validation took too long")
    else:
        print("PASS: Validation is lightweight")

async def test_init():
    print("\nTesting 000_init(action='init')...")
    start = time.time()
    # Mocking memory injection by not crashing
    try:
        result = await mcp_000_init(action="init", query="Test Init")
        duration = time.time() - start
        print(f"Result: {result['status']}")
        print(f"Duration: {duration:.4f}s")
    except Exception as e:
        print(f"Init failed (expected if dependencies missing): {e}")

if __name__ == "__main__":
    asyncio.run(test_validate())

import asyncio
import sys

import httpx

SERVICES = {
    "mcp_time": "http://mcp_time:8000/health",
    "mcp_filesystem": "http://mcp_filesystem:8000/health",
    "mcp_git": "http://mcp_git:8000/health",
    "mcp_memory": "http://mcp_memory:8000/health",
    "mcp_fetch": "http://mcp_fetch:8000/health",
    "mcp_everything": "http://mcp_everything:8000/health",
}

async def check_service(name, url):
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                print(f"🟢 {name} is READY")
                return True
        except Exception:
            pass
    print(f"🔴 {name} is NOT READY")
    return False

async def main():
    print("⏳ Waiting for substrate stack...")
    max_retries = 30
    for _i in range(max_retries):
        results = await asyncio.gather(*[check_service(n, u) for n, u in SERVICES.items()])
        if all(results):
            print("✅ All services healthy.")
            sys.exit(0)
        await asyncio.sleep(2)
    
    print("❌ Timeout waiting for services.")
    sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

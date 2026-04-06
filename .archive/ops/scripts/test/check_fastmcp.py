import asyncio
from fastmcp import Client
import sys

async def main():
    methods = [m for m in dir(Client) if not m.startswith('_')]
    print(f"Client Methods: {methods}")
    
if __name__ == "__main__":
    asyncio.run(main())

"""Scar listener entrypoint — subscribes to NATS governance events and records scars."""
import asyncio
import sys
sys.path.insert(0, "/opt/arifos")
from session_memory_bridge import get_bridge

async def main():
    bridge = get_bridge()
    await bridge.start_scar_listener()

asyncio.run(main())

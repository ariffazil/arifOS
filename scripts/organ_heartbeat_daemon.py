"""
Organ Heartbeat Daemon — Generic
Polls an organ's /health endpoint and publishes to NATS JetStream.

Usage: python organ_heartbeat_daemon.py <organ_id> <health_url> [interval_seconds]

Forged: 2026-06-14 — P0 mesh wiring
DITEMPA BUKAN DIBERI
"""

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import UTC, datetime

try:
    import httpx
    import nats
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("organ.heartbeat")

NATS_URL = "nats://127.0.0.1:4222"
DEFAULT_INTERVAL = 60


class OrganHeartbeatDaemon:
    """Polls organ health and publishes heartbeat to NATS JetStream."""

    def __init__(self, organ_id: str, health_url: str, interval: int = DEFAULT_INTERVAL):
        self.organ_id = organ_id
        self.health_url = health_url
        self.interval = interval
        self.nc: object | None = None
        self.running = False

    async def connect_nats(self) -> bool:
        if not DEPS_AVAILABLE:
            logger.error("Dependencies missing (nats, httpx)")
            return False
        try:
            self.nc = await nats.connect(NATS_URL)
            logger.info(f"[{self.organ_id}] NATS connected")
            return True
        except Exception as e:
            logger.error(f"[{self.organ_id}] NATS connection failed: {e}")
            return False

    async def disconnect(self):
        if self.nc:
            await self.nc.close()
            self.nc = None

    async def fetch_health(self) -> dict | None:
        if not DEPS_AVAILABLE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.health_url)
                if resp.status_code == 200:
                    return resp.json()
                logger.warning(f"[{self.organ_id}] health returned {resp.status_code}")
                return None
        except Exception as e:
            logger.warning(f"[{self.organ_id}] health fetch failed: {e}")
            return None

    async def publish_heartbeat(self, health_data: dict | None):
        if not self.nc:
            return

        status = (
            health_data.get("verdict")
            or health_data.get("status")
            or "UNKNOWN"
        ) if health_data else "UNREACHABLE"

        event = {
            "event": "ORGAN_HEARTBEAT",
            "organ": self.organ_id,
            "status": status,
            "health": health_data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        payload = json.dumps(event, default=str).encode()

        try:
            # JetStream publish to arifos-organs stream
            js = self.nc.jetstream()
            await js.publish(f"arifos.organ.{self.organ_id}", payload)
            logger.info(f"[{self.organ_id}] heartbeat published → status={status}")
        except Exception as e:
            logger.warning(f"[{self.organ_id}] JetStream publish failed: {e}")

    async def run_loop(self):
        logger.info(f"[{self.organ_id}] heartbeat loop started (interval={self.interval}s)")
        failures = 0
        while self.running:
            health = await self.fetch_health()
            await self.publish_heartbeat(health)
            if health:
                failures = 0
            else:
                failures += 1
                if failures >= 3:
                    logger.error(f"[{self.organ_id}] unreachable for {failures} checks")
            await asyncio.sleep(self.interval)

    async def start(self):
        logger.info(f"[{self.organ_id}] daemon starting")
        if not await self.connect_nats():
            logger.error(f"[{self.organ_id}] cannot start: NATS unreachable")
            return
        self.running = True
        await self.run_loop()

    async def stop(self):
        logger.info(f"[{self.organ_id}] daemon stopping")
        self.running = False
        await self.disconnect()


async def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <organ_id> <health_url> [interval_seconds]", file=sys.stderr)
        sys.exit(1)

    organ_id = sys.argv[1]
    health_url = sys.argv[2]
    interval = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_INTERVAL

    daemon = OrganHeartbeatDaemon(organ_id, health_url, interval)

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))

    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()


if __name__ == "__main__":
    asyncio.run(main())

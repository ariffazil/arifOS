"""
arifOS → NATS Heartbeat Sidecar
Polls arifOS health endpoint and publishes events to the NATS event bus.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import UTC, datetime
from typing import Any

try:
    import httpx
    import nats

    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("arifos-nats-heartbeat")

ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health"
NATS_URL = "nats://127.0.0.1:4222"
PUBLISH_INTERVAL = 60  # seconds


class NATSHeartbeatDaemon:
    """Polls arifOS health and publishes events to NATS."""

    def __init__(self, nats_url: str = NATS_URL, health_url: str = ARIFOS_HEALTH_URL):
        self.nats_url = nats_url
        self.health_url = health_url
        self.nc: Any | None = None
        self.running = False

    async def connect_nats(self) -> bool:
        if not DEPS_AVAILABLE:
            logger.error("Dependencies missing: pip install nats-py httpx")
            return False
        try:
            self.nc = await nats.connect(self.nats_url)
            logger.info(f"NATS connected: {self.nats_url}")
            return True
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            return False

    async def stop(self):
        """Stop the daemon gracefully."""
        self.running = False
        await self.disconnect_nats()
        logger.info("Daemon stopped")

    async def disconnect_nats(self):
        if self.nc:
            await self.nc.close()
            self.nc = None
            logger.info("NATS disconnected")

    async def fetch_health(self) -> dict | None:
        if not DEPS_AVAILABLE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.health_url)
                if resp.status_code == 200:
                    return resp.json()
                logger.warning(f"arifOS health HTTP {resp.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Health fetch error: {e}")
            return None

    async def publish(self, subject: str, payload: dict) -> bool:
        if not self.nc:
            return False
        try:
            payload["_ts"] = datetime.now(UTC).isoformat()
            await self.nc.publish(subject, json.dumps(payload, default=str).encode())
            await self.nc.flush()
            return True
        except Exception as e:
            logger.error(f"Publish failed: {e}")
            return False

    async def run(self, interval: int = PUBLISH_INTERVAL):
        consecutive_failures = 0
        logger.info(f"Heartbeat loop started (interval={interval}s)")

        while self.running:
            health = await self.fetch_health()

            if health:
                consecutive_failures = 0
                status = health.get("status", "unknown")
                organ = health.get("agent_id", "arifOS")
                ml = health.get("ml_floors", {})
                fed = health.get("federation_epistemology", {})

                # Main health event
                await self.publish(
                    "arifOS.health",
                    {
                        "event": "ARIFOS_HEALTH",
                        "organ": organ,
                        "status": status,
                        "registry_truth": health.get("registry_truth", "unknown"),
                        "runtime_drift": health.get("runtime_drift", None),
                        "contract_drift": health.get("contract_drift", None),
                        "ml_floors_enabled": ml.get("ml_floors_enabled", False),
                        "ml_runtime_ready": ml.get("ml_runtime_ready", False),
                        "ml_hold_state": ml.get("ml_hold_state", "unknown"),
                        "federation_epistemology": fed.get("status", "disabled")
                        if isinstance(fed, dict)
                        else str(fed),
                        "graphiti_enabled": health.get("graphiti_enabled", False),
                        "vault999_health": health.get("vault999_health", "unknown"),
                        "tools_loaded": health.get("tools_loaded", 0),
                        "floors_active": health.get("floors_active", 0),
                    },
                )
                logger.info(
                    f"Published health: status={status}, ml_ready={ml.get('ml_runtime_ready')}, graphiti={health.get('graphiti_enabled')}"
                )

                # Alert on degraded state
                if verdict == "DEGRADED":
                    await self.publish(
                        "arifOS.alerts",
                        {
                            "event": "ARIFOS_ALERT",
                            "alert_type": "ARIFOS_DEGRADED",
                            "message": "arifOS health degraded",
                            "severity": "high",
                        },
                    )
            else:
                consecutive_failures += 1
                logger.warning(f"Health fetch failed ({consecutive_failures}/3)")
                if consecutive_failures >= 3 and self.nc:
                    await self.publish(
                        "arifOS.alerts",
                        {
                            "event": "ARIFOS_ALERT",
                            "alert_type": "ARIFOS_UNREACHABLE",
                            "message": f"arifOS unreachable for {consecutive_failures} checks",
                            "severity": "critical",
                        },
                    )

            await asyncio.sleep(interval)


async def main():
    daemon = NATSHeartbeatDaemon()
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))

    if not await daemon.connect_nats():
        logger.error("Fatal: cannot connect to NATS")
        sys.exit(1)

    daemon.running = True
    try:
        await daemon.run()
    except asyncio.CancelledError:
        pass
    finally:
        await daemon.disconnect_nats()
        logger.info("Daemon stopped")


if __name__ == "__main__":
    asyncio.run(main())

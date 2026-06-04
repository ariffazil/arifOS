"""
arifOS → NATS Heartbeat Daemon
Sidecar that polls arifOS health and publishes events to the NATS event bus.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""
import asyncio
import json
import logging
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
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("arifOS.nats_heartbeat")

ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health"
NATS_URL = "nats://127.0.0.1:4222"
PUBLISH_INTERVAL = 60  # seconds between heartbeat publications


class NATSHeartbeatDaemon:
    """
    Polls arifOS health endpoint and publishes events to NATS.
    
    Published events:
    - arifOS.health      — heartbeat with organ status
    - arifOS.verdicts    — verdict counts from last health check
    """

    def __init__(self, nats_url: str = NATS_URL, health_url: str = ARIFOS_HEALTH_URL):
        self.nats_url = nats_url
        self.health_url = health_url
        self.nc: object | None = None
        self.running = False

    async def connect_nats(self) -> bool:
        """Connect to NATS."""
        if not DEPS_AVAILABLE:
            logger.error("Required dependencies not available (nats, httpx)")
            return False
        try:
            self.nc = await nats.connect(self.nats_url)
            logger.info(f"NATS connected: {self.nats_url}")
            return True
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            return False

    async def disconnect_nats(self):
        """Disconnect from NATS."""
        if self.nc:
            await self.nc.close()
            self.nc = None

    async def fetch_arifOS_health(self) -> dict | None:
        """Fetch arifOS health endpoint."""
        if not DEPS_AVAILABLE:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(self.health_url)
                if resp.status_code == 200:
                    return resp.json()
                else:
                    logger.warning(f"arifOS health returned {resp.status_code}")
                    return None
        except Exception as e:
            logger.warning(f"arifOS health fetch failed: {e}")
            return None

    async def publish_health_event(self, health_data: dict):
        """Publish arifOS health as NATS event."""
        if not self.nc:
            return

        verdict = health_data.get("verdict", "UNKNOWN")
        organ = health_data.get("organ", "arifOS")
        ml_floors = health_data.get("ml_floors", False)
        federation = health_data.get("federation_epistemology", "disabled")
        graphiti = health_data.get("graphiti_enabled", False)

        event = {
            "event": "ARIFOS_HEALTH",
            "organ": organ,
            "verdict": verdict,
            "ml_floors": ml_floors,
            "federation_epistemology": federation,
            "graphiti_enabled": graphiti,
            "raw_health": health_data,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self.nc.publish("arifOS.health", json.dumps(event, default=str).encode())
            await self.nc.flush()
            logger.info(f"Published health event: verdict={verdict}, ml_floors={ml_floors}")
        except Exception as e:
            logger.error(f"Failed to publish health event: {e}")

    async def publish_alert_event(self, alert_type: str, message: str, severity: str = "medium"):
        """Publish an alert to NATS."""
        if not self.nc:
            return
        event = {
            "event": "ARIFOS_ALERT",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self.nc.publish("arifOS.alerts", json.dumps(event, default=str).encode())
            await self.nc.flush()
        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")

    async def run_loop(self, interval: int = PUBLISH_INTERVAL):
        """Main heartbeat loop."""
        logger.info(f"Starting heartbeat loop (interval={interval}s)")
        consecutive_failures = 0
        while self.running:
            health = await self.fetch_arifOS_health()
            if health:
                consecutive_failures = 0
                await self.publish_health_event(health)
                # Check for critical issues
                if health.get("verdict") == "DEGRADED":
                    await self.publish_alert_event(
                        "ARIFOS_DEGRADED",
                        f"arifOS health degraded: {health}",
                        "high"
                    )
            else:
                consecutive_failures += 1
                logger.warning(f"arifOS health fetch failed ({consecutive_failures} consecutive)")
                if consecutive_failures >= 3 and self.nc:
                    await self.publish_alert_event(
                        "ARIFOS_UNREACHABLE",
                        f"arifOS unreachable for {consecutive_failures} consecutive checks",
                        "critical"
                    )

            await asyncio.sleep(interval)

    async def start(self):
        """Start the daemon."""
        logger.info("arifOS NATS Heartbeat Daemon starting")
        if not await self.connect_nats():
            logger.error("Cannot start: NATS connection failed")
            return

        self.running = True
        await self.run_loop()

    async def stop(self):
        """Stop the daemon gracefully."""
        logger.info("arifOS NATS Heartbeat Daemon stopping")
        self.running = False
        await self.disconnect_nats()


async def main():
    daemon = NATSHeartbeatDaemon()

    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(daemon.stop()))

    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()


if __name__ == "__main__":
    asyncio.run(main())

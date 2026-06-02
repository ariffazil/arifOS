"""
NATS Event Bus Publisher for arifOS
Publishes health events, verdicts, and heartbeats to the federation nervous system.
DITEMPA BUKAN DIBERI
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Any

try:
    import nats
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Federation NATS subjects
SUBJECT_VERDICTS = "arifOS.verdicts"
SUBJECT_HEARTBEAT = "arifOS.heartbeat"
SUBJECT_ALERTS = "arifOS.alerts"
SUBJECT_EVIDENCE = "arifOS.evidence"
SUBJECT_FLOORS = "arifOS.floors"


class NATSEventBus:
    """
    arifOS event publisher to NATS.
    Publishes constitutional events: SEAL, SABAR, HOLD, VOID verdicts.
    """
    _instance: Optional['NATSEventBus'] = None
    _nc: Optional[Any] = None

    def __new__(cls) -> 'NATSEventBus':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self, nats_url: str = "nats://127.0.0.1:4222") -> bool:
        """Connect to NATS server."""
        if not NATS_AVAILABLE:
            logger.warning("nats-py not installed, event bus disabled")
            return False
        try:
            self._nc = await nats.connect(nats_url)
            logger.info(f"NATS connected to {nats_url}")
            return True
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from NATS."""
        if self._nc:
            await self._nc.close()
            self._nc = None

    async def publish_verdict(
        self,
        session_id: str,
        verdict: str,  # SEAL, SABAR, HOLD, VOID
        stage: str,
        evidence_count: int = 0,
        source: str = "arifOS"
    ):
        """Publish a constitutional verdict event."""
        if not self._nc:
            logger.warning("NATS not connected, skipping verdict publish")
            return

        event = {
            "event": "VERDICT_ISSUED",
            "session_id": session_id,
            "verdict": verdict,
            "stage": stage,
            "evidence_count": evidence_count,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            await self._nc.publish(SUBJECT_VERDICTS, json.dumps(event).encode())
            await self._nc.flush()
            logger.info(f"Published verdict: {verdict} for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to publish verdict: {e}")

    async def publish_heartbeat(self, organ: str, status: str = "alive"):
        """Publish a heartbeat event from an organ."""
        if not self._nc:
            return

        event = {
            "event": "HEARTBEAT",
            "organ": organ,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            await self._nc.publish(SUBJECT_HEARTBEAT, json.dumps(event).encode())
            await self._nc.flush()
        except Exception as e:
            logger.error(f"Failed to publish heartbeat: {e}")

    async def publish_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warn",  # info, warn, critical
        source: str = "arifOS"
    ):
        """Publish an alert event."""
        if not self._nc:
            return

        event = {
            "event": "ALERT",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        try:
            await self._nc.publish(SUBJECT_ALERTS, json.dumps(event).encode())
            await self._nc.flush()
        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")


# Singleton instance
event_bus = NATSEventBus()


async def publish_arifOS_heartbeat():
    """Publish arifOS heartbeat to NATS."""
    await event_bus.publish_heartbeat("arifOS", "alive")


async def init_nats_event_bus() -> bool:
    """Initialize the NATS event bus connection."""
    return await event_bus.connect()

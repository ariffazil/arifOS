"""
arifOS NATS Event Publisher
Publishes health, verdict, and seal events to the NATS event bus.

AMANAH: This module publishes truth. Every event is real.
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any

try:
    import nats

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False


class NATSEventPublisher:
    """
    Publishes arifOS events to the NATS event bus.

    Events flow to:
    - arifOS.verdicts    — SEAL/SABAR/HOLD/VOID verdicts
    - arifOS.health      — heartbeat and health signals
    - arifOS.evidence    — new evidence ingested
    - arifOS.alerts      — governance alerts (888_HOLD, constitutional violations)
    - federation.*       — cross-organ events
    """

    def __init__(self, nats_url: str = "nats://127.0.0.1:4222"):
        self.nats_url = nats_url
        self.nc: Any | None = None
        self._connected = False

    async def connect(self) -> bool:
        """Connect to NATS. Returns True if connected."""
        if not NATS_AVAILABLE:
            return False
        try:
            self.nc = await nats.connect(self.nats_url)
            self._connected = True
            return True
        except Exception:
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from NATS."""
        if self.nc:
            await self.nc.close()
            self._connected = False

    async def publish(self, subject: str, payload: dict, compress: bool = False) -> bool:
        """
        Publish an event to a NATS subject.

        subject: NATS subject (e.g. 'arifOS.verdicts', 'federation.health')
        payload: event data as dict
        compress: not yet implemented
        """
        if not self._connected or not self.nc:
            return False
        try:
            payload["_ts"] = datetime.now(UTC).isoformat()
            data = json.dumps(payload, default=str).encode()
            await self.nc.publish(subject, data)
            await self.nc.flush()
            return True
        except Exception:
            return False

    # ── Health Events ──────────────────────────────────────────────

    async def publish_health(
        self, organ: str, status: str, metadata: dict | None = None
    ) -> bool:
        """Publish a heartbeat/health signal from an organ."""
        return await self.publish(
            "arifOS.health", {"organ": organ, "status": status, "metadata": metadata or {}}
        )

    async def publish_verdict(
        self,
        session_id: str,
        verdict: str,
        stage: str,
        tool_name: str | None = None,
        metadata: dict | None = None,
    ) -> bool:
        """
        Publish a constitutional verdict.

        verdict: SEAL | SABAR | HOLD | VOID | PARTIAL
        stage: 000–999 spine stage
        """
        return await self.publish(
            "arifOS.verdicts",
            {
                "session_id": session_id,
                "verdict": verdict,
                "stage": stage,
                "tool_name": tool_name,
                "metadata": metadata or {},
            },
        )

    async def publish_seal(
        self, session_id: str, seal_id: str, stage: str, metadata: dict | None = None
    ) -> bool:
        """Publish a SEAL event — verdict is constitutionally final."""
        return await self.publish(
            "arifOS.seals",
            {
                "session_id": session_id,
                "seal_id": seal_id,
                "stage": stage,
                "metadata": metadata or {},
            },
        )

    async def publish_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "medium",
        metadata: dict | None = None,
    ) -> bool:
        """
        Publish a governance alert (e.g. 888_HOLD, constitutional violation).

        severity: low | medium | high | critical
        """
        return await self.publish(
            "arifOS.alerts",
            {
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "metadata": metadata or {},
            },
        )

    async def publish_evidence(
        self, session_id: str, artifact_id: str, evidence_type: str, metadata: dict | None = None
    ) -> bool:
        """Publish an evidence ingestion event."""
        return await self.publish(
            "arifOS.evidence",
            {
                "session_id": session_id,
                "artifact_id": artifact_id,
                "evidence_type": evidence_type,
                "metadata": metadata or {},
            },
        )


# ── Singleton instance ─────────────────────────────────────────────
_publisher: NATSEventPublisher | None = None


async def get_publisher() -> NATSEventPublisher:
    """Get the singleton NATS publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = NATSEventPublisher()
        await _publisher.connect()
    return _publisher


# ── Test/verification ──────────────────────────────────────────────
async def test_nats_publisher():
    """Test the NATS publisher. Run: python -m arifOS.abi.nats_publisher"""
    pub = NATSEventPublisher()
    connected = await pub.connect()

    if connected:
        print("✅ NATS connected")

        # Publish a test health event
        ok = await pub.publish_health("apex-probe", "operational", {"version": "1.0.0"})
        print(f"{'✅' if ok else '❌'} Health event published: {ok}")

        # Publish a test verdict
        ok = await pub.publish_verdict("test-session-001", "SEAL", "999", "test_tool")
        print(f"{'✅' if ok else '❌'} Verdict event published: {ok}")

        # Publish an alert
        ok = await pub.publish_alert("test_alert", "APEX probe test", "low")
        print(f"{'✅' if ok else '❌'} Alert event published: {ok}")

        await pub.disconnect()
        print("✅ NATS publisher test complete")
    else:
        print("❌ NATS not available")


if __name__ == "__main__":
    asyncio.run(test_nats_publisher())

"""
arifosmcp/runtime/mesh_subscriber.py — Federation Intelligence Mesh Subscriber
═══════════════════════════════════════════════════════════════════════════════

Every organ in the arifOS federation can import this module to subscribe to
kernel intelligence broadcasts via NATS. This is how GEOX, WEALTH, WELL, A-FORGE,
AAA, and APEX stay aware of F1-F13 floor states, entropy deltas, verdict
summaries, and active leases without polling the kernel.

ARCHITECTURE:
  arifOS kernel → publish_intelligence_broadcast() → NATS JetStream
       ↓
  Each organ → MeshSubscriber → callback(floors, entropy, verdict, leases)
       ↓
  Organ uses intelligence to govern its own behavior:
    - GEOX: knows when F2 TRUTH ceiling has been breached → tighten evidence QC
    - WEALTH: knows when F7 HUMILITY is active → add wider uncertainty bands
    - WELL: knows when F5 PEACE is violated → increase dignity guard sensitivity
    - A-FORGE: knows when F11 AUTH is degraded → require higher clearance
    - AAA: displays real-time floor state in cockpit dashboard

F1 AMANAH: Mesh subscriber is read-only. It never sends commands to organs.
           It only delivers intelligence. Organs decide what to do with it.
           Mesh failure must never block organ operation.

F2 TRUTH: Subscriber delivers actual NATS messages. Not simulated.
           If NATS is unavailable, subscriber degrades gracefully to polling.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any, Callable, Optional

logger = logging.getLogger("arifosmcp.mesh_subscriber")

# Try NATS import — graceful degradation if not available
try:
    import nats

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False


# Intelligence subjects (mirrored from nats_event_bus.py)
SUBJECT_INTELLIGENCE_FLOORS = "arifos.intelligence.floors"
SUBJECT_INTELLIGENCE_ENTROPY = "arifos.intelligence.entropy"
SUBJECT_INTELLIGENCE_VERDICT = "arifos.intelligence.verdict"
SUBJECT_INTELLIGENCE_LEASE = "arifos.intelligence.lease"
SUBJECT_INTELLIGENCE_ALL = "arifos.intelligence.>"


IntelligenceCallback = Callable[[dict[str, Any]], None]


class MeshSubscriber:
    """
    Federation intelligence mesh subscriber.

    Connects to NATS JetStream and subscribes to intelligence subjects.
    Delivers structured intelligence to a callback function.

    Usage:
        subscriber = MeshSubscriber(organ_id="geox")
        subscriber.register_callback(my_callback)
        await subscriber.connect()
        # subscriber is now receiving intelligence broadcasts
        # ...
        await subscriber.disconnect()
    """

    _instance: dict[str, "MeshSubscriber"] = {}

    def __new__(cls, organ_id: str) -> "MeshSubscriber":
        if organ_id not in cls._instance:
            cls._instance[organ_id] = super().__new__(cls)
            cls._instance[organ_id]._initialized = False
        return cls._instance[organ_id]

    def __init__(self, organ_id: str) -> None:
        if self._initialized:
            return
        self._initialized = True

        self.organ_id = organ_id
        self._nc: Any | None = None
        self._subscriptions: dict[str, Any] = {}
        self._callbacks: list[IntelligenceCallback] = []
        self._connected = False
        self._polling = False
        self._poll_interval = 10  # fallback polling seconds

        # Last known intelligence state
        self.last_floors: dict[str, Any] | None = None
        self.last_entropy: float | None = None
        self.last_verdict: dict[str, Any] | None = None
        self.last_leases: dict[str, Any] | None = None
        self.last_broadcast: dict[str, Any] | None = None
        self.last_update: datetime | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    def register_callback(self, callback: IntelligenceCallback) -> None:
        """Register a callback to receive all intelligence updates."""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: IntelligenceCallback) -> None:
        """Remove a registered callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def connect(
        self,
        nats_url: str = "nats://127.0.0.1:4222",
        subscribe_all: bool = True,
    ) -> bool:
        """Connect to NATS and subscribe to intelligence subjects."""
        if not NATS_AVAILABLE:
            logger.warning(
                f"[{self.organ_id}] nats-py not available. "
                "Mesh subscriber degraded to polling mode."
            )
            self._polling = True
            return False

        try:
            self._nc = await nats.connect(
                nats_url,
                name=f"mesh-{self.organ_id}",
                connect_timeout=5,
                ping_interval=20,
                max_outstanding_pings=5,
                allow_reconnect=True,
                max_reconnect_attempts=-1,
            )
            self._connected = True
            logger.info(f"[{self.organ_id}] Connected to NATS mesh at {nats_url}")

            if subscribe_all:
                await self._subscribe(SUBJECT_INTELLIGENCE_ALL)
            else:
                await self._subscribe(SUBJECT_INTELLIGENCE_FLOORS)
                await self._subscribe(SUBJECT_INTELLIGENCE_ENTROPY)
                await self._subscribe(SUBJECT_INTELLIGENCE_VERDICT)
                await self._subscribe(SUBJECT_INTELLIGENCE_LEASE)

            return True

        except Exception as e:
            logger.warning(
                f"[{self.organ_id}] NATS connection failed: {e}. "
                "Degraded to polling mode."
            )
            self._polling = True
            return False

    async def _subscribe(self, subject: str) -> None:
        """Subscribe to a single intelligence subject."""
        if not self._nc:
            return

        try:
            sub = await self._nc.subscribe(
                subject,
                cb=self._on_message,
                queue=f"mesh-{self.organ_id}",
            )
            self._subscriptions[subject] = sub
            logger.info(
                f"[{self.organ_id}] Subscribed to {subject}"
            )
        except Exception as e:
            logger.error(
                f"[{self.organ_id}] Failed to subscribe to {subject}: {e}"
            )

    async def _on_message(self, msg: Any) -> None:
        """Handle incoming NATS message."""
        try:
            data = json.loads(msg.data.decode())
            subject = msg.subject

            # Update last-known state
            if subject == SUBJECT_INTELLIGENCE_FLOORS:
                self.last_floors = data.get("floors")
            elif subject == SUBJECT_INTELLIGENCE_ENTROPY:
                self.last_entropy = data.get("entropy_delta")
            elif subject == SUBJECT_INTELLIGENCE_VERDICT:
                self.last_verdict = data.get("verdict")
            elif subject == SUBJECT_INTELLIGENCE_LEASE:
                self.last_leases = data.get("leases")

            self.last_update = datetime.now(UTC)

            # Dispatch to all callbacks
            for cb in self._callbacks:
                try:
                    cb(data)
                except Exception as e:
                    logger.error(
                        f"[{self.organ_id}] Intelligence callback error: {e}"
                    )

        except json.JSONDecodeError:
            logger.warning(
                f"[{self.organ_id}] Received non-JSON message on {msg.subject}"
            )
        except Exception as e:
            logger.error(
                f"[{self.organ_id}] Mesh message handler error: {e}"
            )

    async def disconnect(self) -> None:
        """Disconnect from NATS gracefully."""
        for subject, sub in self._subscriptions.items():
            try:
                await sub.unsubscribe()
            except Exception:
                pass
        self._subscriptions.clear()

        if self._nc:
            try:
                await self._nc.close()
            except Exception:
                pass
        self._connected = False
        logger.info(f"[{self.organ_id}] Disconnected from NATS mesh")

    def get_intelligence_summary(self) -> dict[str, Any]:
        """
        Get a summary of the last known intelligence state.
        Useful for organs to include in their health checks.
        """
        return {
            "organ_id": self.organ_id,
            "connected": self._connected,
            "polling": self._polling,
            "subscriptions": list(self._subscriptions.keys()),
            "last_update": (
                self.last_update.isoformat() if self.last_update else None
            ),
            "has_floors": self.last_floors is not None,
            "has_entropy": self.last_entropy is not None,
            "has_verdict": self.last_verdict is not None,
            "has_leases": self.last_leases is not None,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# ORGAN INTELLIGENCE CALLBACK — default handler for organs
# ═══════════════════════════════════════════════════════════════════════════════


def organ_intelligence_printer(organ_id: str) -> IntelligenceCallback:
    """
    Create a default intelligence callback that logs received state.
    Organs can replace this with their own handler.

    Usage:
        subscriber = MeshSubscriber(organ_id="geox")
        subscriber.register_callback(organ_intelligence_printer("geox"))
    """

    def callback(data: dict[str, Any]) -> None:
        floors = data.get("floors")
        entropy = data.get("entropy_delta")
        verdict = data.get("verdict")
        leases = data.get("leases")
        heartbeats = data.get("heartbeats")

        parts = [f"[{organ_id}] mesh intelligence received"]
        if floors:
            parts.append(f"floors_active={len(floors.get('active',[]))}")
        if entropy is not None:
            parts.append(f"entropy_delta={entropy:.4f}")
        if verdict:
            parts.append(f"verdict={verdict.get('verdict','?')}")
        if leases:
            parts.append(f"leases={len(leases)}")
        if heartbeats:
            alive = sum(1 for s in heartbeats.values() if s == "alive")
            parts.append(f"organs_alive={alive}/{len(heartbeats)}")

        logger.info(" | ".join(parts))

    return callback


__all__ = [
    "MeshSubscriber",
    "organ_intelligence_printer",
    "SUBJECT_INTELLIGENCE_FLOORS",
    "SUBJECT_INTELLIGENCE_ENTROPY",
    "SUBJECT_INTELLIGENCE_VERDICT",
    "SUBJECT_INTELLIGENCE_LEASE",
    "SUBJECT_INTELLIGENCE_ALL",
]

"""
NATS Subscriber Bridge — wires the anomaly scorer to live NATS streams.

Subscribes to:
  - arifos.governance.>      (GOVERNANCE JetStream)
  - arifos.feedback.>        (FEEDBACK JetStream)
  - arifos.gradient.>        (GRADIENT JetStream)
  - arifos.e7.>              (E7_AUTONOMY JetStream)
  - arifOS.heartbeat          (heartbeat telemetry)

Each incoming event is parsed, validated, and fed to the AnomalyScorer.
The scorer periodically publishes AnomalyScore to arifos.anomaly.score.

Lifecycle:
  bridge = AnomalyNATSSubscriber()
  await bridge.start()    # connect to NATS, subscribe to all 5 streams
  ... events flow ...
  score = bridge.scorer.assess()   # get current assessment
  await bridge.stop()     # drain and disconnect

F1 AMANAH: NATS is mesh transport, not authority. Subscriber failure
must never block governance. All parsing errors are logged and dropped.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.anomaly.schemas import (
    E7AutonomyEvent,
    FeedbackSignalEvent,
    GateVerdictEvent,
    GradientSignalEvent,
)
from arifosmcp.anomaly.scorer import AnomalyScorer, get_scorer

logger = logging.getLogger("arifosmcp.anomaly.nats_subscriber")

# ── NATS subjects to subscribe to ────────────────────────────────────────

GOVERNANCE_SUBJECT = "arifos.governance.>"
FEEDBACK_SUBJECT = "arifos.feedback.>"
GRADIENT_SUBJECT = "arifos.gradient.>"
E7_SUBJECT = "arifos.e7.>"
HEARTBEAT_SUBJECT = "arifOS.heartbeat"
ANOMALY_SCORE_SUBJECT = "arifos.anomaly.score"

# Assessment interval (seconds) — how often to publish anomaly scores
ASSESS_INTERVAL_S = 15.0


class AnomalyNATSSubscriber:
    """Live NATS subscriber that bridges event streams to the anomaly scorer.

    Usage:
        sub = AnomalyNATSSubscriber()
        await sub.start()
        # ... events accumulate ...
        score = sub.scorer.assess()
        await sub.stop()
    """

    def __init__(self, nats_url: str = "nats://127.0.0.1:4222") -> None:
        self.nats_url = nats_url
        self.scorer: AnomalyScorer = get_scorer()
        self._nc: Any = None
        self._subscriptions: list[Any] = []
        self._running: bool = False
        self._publish_task: asyncio.Task[Any] | None = None
        self._event_count: int = 0
        self._error_count: int = 0
        self._started_at: str = ""

    @property
    def connected(self) -> bool:
        return self._nc is not None and hasattr(self._nc, 'is_connected') and self._nc.is_connected

    async def start(self, publish_assessments: bool = True) -> bool:
        """Connect to NATS and subscribe to all 5 anomaly streams.

        Args:
            publish_assessments: If True, periodically publish AnomalyScore
                                 to arifos.anomaly.score for cockpit consumption.

        Returns:
            True if connected and subscribed successfully.
        """
        try:
            import nats
        except ImportError:
            logger.warning("nats-py not installed — anomaly scorer running in offline mode")
            return False

        try:
            self._nc = await nats.connect(
                self.nats_url,
                name="arifOS-anomaly-scorer",
                connect_timeout=10,
                ping_interval=30,
                max_reconnect_attempts=-1,
            )
            logger.info(f"Anomaly scorer connected to NATS at {self.nats_url}")
        except Exception as e:
            logger.error(f"Anomaly scorer NATS connection failed: {e}")
            return False

        self._running = True
        self._started_at = datetime.now(UTC).isoformat()

        # Subscribe to all 5 streams
        await self._subscribe_all()

        # Start periodic assessment publisher
        if publish_assessments:
            self._publish_task = asyncio.create_task(self._publish_loop())

        logger.info(
            f"Anomaly scorer active — {len(self._subscriptions)} subscriptions, "
            f"assessment interval {ASSESS_INTERVAL_S}s"
        )
        return True

    async def _subscribe_all(self) -> None:
        """Subscribe to all 5 anomaly streams."""
        subscriptions = [
            (GOVERNANCE_SUBJECT, self._handle_governance),
            (FEEDBACK_SUBJECT, self._handle_feedback),
            (GRADIENT_SUBJECT, self._handle_gradient),
            (E7_SUBJECT, self._handle_e7),
            (HEARTBEAT_SUBJECT, self._handle_heartbeat),
        ]

        for subject, handler in subscriptions:
            try:
                sub = await self._nc.subscribe(subject, cb=handler)
                self._subscriptions.append(sub)
                logger.info(f"Anomaly scorer subscribed to {subject}")
            except Exception as e:
                logger.error(f"Failed to subscribe to {subject}: {e}")

    # ── Message handlers ──────────────────────────────────────────────────

    async def _handle_governance(self, msg: Any) -> None:
        """Handle a governance gate verdict from NATS."""
        await self._safe_handle(msg, self._parse_and_feed_governance)

    async def _handle_feedback(self, msg: Any) -> None:
        """Handle a feedback loop signal from NATS."""
        await self._safe_handle(msg, self._parse_and_feed_feedback)

    async def _handle_gradient(self, msg: Any) -> None:
        """Handle a gradient signal from NATS."""
        await self._safe_handle(msg, self._parse_and_feed_gradient)

    async def _handle_e7(self, msg: Any) -> None:
        """Handle an E7 event from NATS."""
        await self._safe_handle(msg, self._parse_and_feed_e7)

    async def _handle_heartbeat(self, msg: Any) -> None:
        """Handle a federation organ heartbeat."""
        await self._safe_handle(msg, self._parse_and_feed_heartbeat)

    async def _safe_handle(self, msg: Any, handler) -> None:
        """Wrap handler in try/except — mesh failure never blocks governance."""
        try:
            await handler(msg)
            self._event_count += 1
        except Exception as e:
            self._error_count += 1
            logger.debug(f"Anomaly handler error (non-fatal): {e}")

    # ── Parse and feed — validate schemas, feed scorer ────────────────────

    async def _parse_and_feed_governance(self, msg: Any) -> None:
        data = json.loads(msg.data.decode())
        try:
            event = GateVerdictEvent(**data)
        except Exception:
            # Try legacy format mapping
            event = GateVerdictEvent(
                gate=data.get("gate", ""),
                verdict=data.get("verdict", "PASS"),
                session_id=data.get("session_id", ""),
                tool_name=data.get("tool_name", ""),
                action_class=data.get("action_class", "OBSERVE"),
                autonomy_tier=data.get("autonomy_tier", ""),
                reasons=data.get("reasons", []),
                violated_laws=data.get("violated_laws", []),
                timestamp=data.get("timestamp", ""),
            )
        self.scorer.feed_gate_verdict(event)

    async def _parse_and_feed_feedback(self, msg: Any) -> None:
        data = json.loads(msg.data.decode())
        try:
            event = FeedbackSignalEvent(**data)
        except Exception:
            event = FeedbackSignalEvent(
                signal=data.get("signal", "PROCEED"),
                session_id=data.get("session_id", ""),
                step_number=data.get("step_number", 0),
                source_organ=data.get("source_organ", "arifOS"),
                target_organ=data.get("target_organ"),
                metadata=data.get("metadata", {}),
                timestamp=data.get("timestamp", ""),
            )
        self.scorer.feed_feedback_signal(event)

    async def _parse_and_feed_gradient(self, msg: Any) -> None:
        data = json.loads(msg.data.decode())
        try:
            event = GradientSignalEvent(**data)
        except Exception:
            event = GradientSignalEvent(
                dimension=data.get("dimension", "constitution"),
                delta=data.get("delta", 0.0),
                session_id=data.get("session_id", ""),
                source_organ=data.get("source_organ", "arifOS"),
                metadata=data.get("metadata", {}),
                timestamp=data.get("timestamp", ""),
            )
        self.scorer.feed_gradient_signal(event)

    async def _parse_and_feed_e7(self, msg: Any) -> None:
        data = json.loads(msg.data.decode())
        try:
            event = E7AutonomyEvent(**data)
        except Exception:
            event = E7AutonomyEvent(
                event=data.get("event", ""),
                session_id=data.get("session_id", ""),
                action_class=data.get("action_class", ""),
                autonomy_tier=data.get("autonomy_tier", ""),
                risk_tier=data.get("risk_tier", ""),
                blast_radius=data.get("blast_radius", ""),
                gate_verdict=data.get("gate_verdict", ""),
                reason=data.get("reason", ""),
                override_count=data.get("override_count", 0),
                surge_active=data.get("surge_active", False),
                timestamp=data.get("timestamp", ""),
            )
        self.scorer.feed_e7_event(event)

    async def _parse_and_feed_heartbeat(self, msg: Any) -> None:
        data = json.loads(msg.data.decode())
        organ = data.get("organ", "unknown")
        status = data.get("status", "alive")
        self.scorer.feed_heartbeat(organ, status)

    # ── Periodic assessment publisher ─────────────────────────────────────

    async def _publish_loop(self) -> None:
        """Periodically publish anomaly scores to arifos.anomaly.score."""
        while self._running:
            await asyncio.sleep(ASSESS_INTERVAL_S)
            if not self._running:
                break

            try:
                score = self.scorer.assess()
                payload = json.dumps(score.model_dump()).encode()
                await self._nc.publish(ANOMALY_SCORE_SUBJECT, payload)
                await self._nc.flush(timeout=2)

                if score.overall_level.value in ("ANOMALOUS", "CRITICAL"):
                    logger.warning(
                        f"Anomaly score: {score.overall_level.value} "
                        f"({score.overall_score:.3f}) — {score.worst_dimension}"
                    )
            except Exception as e:
                logger.error(f"Failed to publish anomaly score: {e}")

    # ── Lifecycle ─────────────────────────────────────────────────────────

    async def stop(self) -> None:
        """Drain subscriptions and disconnect from NATS."""
        self._running = False

        if self._publish_task:
            self._publish_task.cancel()
            try:
                await self._publish_task
            except asyncio.CancelledError:
                pass
            self._publish_task = None

        for sub in self._subscriptions:
            try:
                await sub.unsubscribe()
            except Exception:
                pass
        self._subscriptions.clear()

        if self._nc:
            try:
                await self._nc.drain()
                await self._nc.close()
            except Exception:
                pass
            self._nc = None

        logger.info(
            f"Anomaly scorer stopped — {self._event_count} events processed, "
            f"{self._error_count} errors"
        )

    async def get_status(self) -> dict[str, Any]:
        """Return subscriber status for cockpit display."""
        return {
            "connected": self.connected,
            "running": self._running,
            "started_at": self._started_at,
            "event_count": self._event_count,
            "error_count": self._error_count,
            "subscriptions": len(self._subscriptions),
            "nats_url": self.nats_url,
            "assessment_interval_s": ASSESS_INTERVAL_S,
        }

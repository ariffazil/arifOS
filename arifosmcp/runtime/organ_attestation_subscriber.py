"""
arifosmcp/runtime/organ_attestation_subscriber.py
═══════════════════════════════════════════════════════════════════════════════
Continuous NATS JetStream consumer for live organ attestation.

Subscribes to the 'arifos-organs' stream on subject 'arifos.organ.>' and
updates the in-memory heartbeat registry so that Gate 15 / institutional
evolution and the AAA cockpit see live federation liveness.

This is Forge 3 wiring: organ heartbeats were already being published; this
module makes arifOS actually listen and remember.

F1 AMANAH: NATS failure is non-fatal. The subscriber catches all exceptions,
logs them, and keeps retrying. Governance does not depend on mesh uptime.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from arifosmcp.runtime.heartbeat_registry import record_heartbeat

logger = logging.getLogger("arifosmcp.organ_attestation_subscriber")


class OrganAttestationSubscriber:
    """Continuous JetStream consumer for organ heartbeats."""

    def __init__(
        self,
        stream: str = "arifos-organs",
        subject: str = "arifos.organ.>",
        durable: str = "arifos-organ-attestation-sub",
        poll_interval: float = 5.0,
        batch_size: int = 100,
    ) -> None:
        self.stream = stream
        self.subject = subject
        self.durable = durable
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self._task: asyncio.Task[Any] | None = None
        self._stop_event = asyncio.Event()

    async def start(self, js: Any | None = None) -> bool:
        """Start the subscriber. Pass a JetStream context or let it connect."""
        try:
            import nats
        except ImportError:
            logger.warning("nats-py not installed — organ attestation subscriber offline")
            return False

        if js is None:
            try:
                nc = await nats.connect("nats://127.0.0.1:4222")
                js = nc.jetstream()
            except Exception as e:
                logger.warning("Cannot connect to NATS for organ attestation: %s", e)
                return False

        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(js))
        logger.info(
            "Organ attestation subscriber started on %s (stream=%s)",
            self.subject,
            self.stream,
        )
        return True

    async def stop(self) -> None:
        """Stop the subscriber gracefully."""
        self._stop_event.set()
        if self._task is not None:
            try:
                self._task.cancel()
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Organ attestation subscriber stopped")

    async def _run(self, js: Any) -> None:
        """Main loop: create durable pull subscriber and ingest messages."""
        from arifosmcp.abi.attestation_verifier import AttestationRecord

        sub: Any | None = None
        while not self._stop_event.is_set():
            try:
                if sub is None:
                    sub = await js.pull_subscribe(
                        self.subject,
                        durable=self.durable,
                        stream=self.stream,
                        config={"ack_wait": 30},
                    )
                    logger.debug(
                        "Pull subscriber created on %s (stream=%s)",
                        self.subject,
                        self.stream,
                    )

                msgs = await sub.fetch(self.batch_size, timeout=self.poll_interval)
                for msg in msgs:
                    try:
                        record = AttestationRecord.from_nats_message(msg.data)
                        if record is None:
                            await msg.ack()
                            continue

                        # Update the live heartbeat registry
                        record_heartbeat(
                            organ_id=record.organ,
                            status=record.verdict,
                            tool_count=record.tool_count,
                            degraded=record.verdict.upper()
                            not in {"ALIVE", "HEALTHY", "OK", "PASS", "READY", "SERVING"},
                            reason=f"registry_truth={record.registry_truth}",
                            load=record.raw,
                        )
                        await msg.ack()
                        logger.debug(
                            "Ingested organ heartbeat: %s (verdict=%s, tools=%s)",
                            record.organ,
                            record.verdict,
                            record.tool_count,
                        )
                    except Exception as e:
                        logger.warning("Failed to process organ heartbeat: %s", e)
                        try:
                            await msg.nak()
                        except Exception:
                            pass
            except TimeoutError:
                # No messages in poll_interval seconds — normal, loop back
                continue
            except Exception as e:
                logger.warning("Organ attestation subscriber error: %s", e)
                sub = None
                await asyncio.sleep(self.poll_interval)


# Singleton for server lifecycle management
_subscriber: OrganAttestationSubscriber | None = None


async def start_organ_attestation_subscriber(js: Any | None = None) -> bool:
    """Idempotent start of the live organ attestation subscriber."""
    global _subscriber
    if _subscriber is not None:
        return True
    _subscriber = OrganAttestationSubscriber()
    return await _subscriber.start(js)


async def stop_organ_attestation_subscriber() -> None:
    """Idempotent stop."""
    global _subscriber
    if _subscriber is not None:
        await _subscriber.stop()
        _subscriber = None

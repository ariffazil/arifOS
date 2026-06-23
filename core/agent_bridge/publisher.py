"""Publisher: agents call this to broadcast telemetry into the swarm cortex."""

from __future__ import annotations

import logging

from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

from agent_bridge.models import AgentTelemetry

logger = logging.getLogger(__name__)

STREAM_NAME = "agent_memory"
SUBJECT_PREFIX = "agent.memory."


class TelemetryPublisher:
    """Publish agent telemetry to NATS JetStream.

    Usage (from any agent process):
        pub = await TelemetryPublisher.connect()
        await pub.publish(AgentTelemetry(...))
    """

    def __init__(self, nc: NATS, js) -> None:
        self.nc = nc
        self.js = js

    @classmethod
    async def connect(cls, servers: list[str] | None = None) -> "TelemetryPublisher":
        servers = servers or ["nats://localhost:4222"]
        nc = NATS()
        await nc.connect(servers=servers)
        js = nc.jetstream()

        # Idempotent stream creation
        try:
            await js.add_stream(
                StreamConfig(
                    name=STREAM_NAME,
                    subjects=[f"{SUBJECT_PREFIX}*"],
                    retention="workqueue",
                    max_msgs=-1,
                    max_bytes=-1,
                )
            )
            logger.info("Created JetStream stream: %s", STREAM_NAME)
        except Exception as exc:
            if (
                "already in use" in str(exc).lower()
                or "stream name already in use" in str(exc).lower()
            ):
                logger.debug("Stream %s already exists", STREAM_NAME)
            else:
                raise

        return cls(nc, js)

    async def publish(self, telemetry: AgentTelemetry) -> None:
        subject = telemetry.to_nats_subject()
        payload = telemetry.model_dump_json().encode("utf-8")
        await self.js.publish(subject, payload)
        logger.debug("Published telemetry to %s | outcome=%s", subject, telemetry.outcome)

    async def close(self) -> None:
        await self.nc.close()

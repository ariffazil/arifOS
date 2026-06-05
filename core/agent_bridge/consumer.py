"""Consumer: arifOS ingests telemetry into L3 (Qdrant) and L5 (Graphiti)."""

from __future__ import annotations

import json
import logging

from nats.aio.client import Client as NATS
from nats.js.api import ConsumerConfig

from agent_bridge.models import AgentTelemetry

logger = logging.getLogger(__name__)

STREAM_NAME = "agent_memory"
CONSUMER_NAME = "arifos_bridge_consumer"


class TelemetryConsumer:
    """Consume agent telemetry and persist to federation memory layers.

    Usage:
        consumer = await TelemetryConsumer.connect()
        await consumer.run(handler)
    """

    def __init__(self, nc: NATS, js, sub) -> None:
        self.nc = nc
        self.js = js
        self.sub = sub

    @classmethod
    async def connect(cls, servers: list[str] | None = None, durable: str = CONSUMER_NAME) -> "TelemetryConsumer":
        servers = servers or ["nats://localhost:4222"]
        nc = NATS()
        await nc.connect(servers=servers)
        js = nc.jetstream()

        sub = await js.pull_subscribe(
            subject="agent.memory.*",
            durable=durable,
            stream=STREAM_NAME,
            config=ConsumerConfig(durable_name=durable),
        )
        return cls(nc, js, sub)

    async def fetch_one(self, timeout: float = 5.0) -> AgentTelemetry | None:
        """Pull one message from the stream."""
        msgs = await self.sub.fetch(1, timeout=timeout)
        if not msgs:
            return None
        msg = msgs[0]
        data = json.loads(msg.data.decode("utf-8"))
        telemetry = AgentTelemetry(**data)
        await msg.ack()
        return telemetry

    async def run(self, handler, batch_size: int = 10) -> None:
        """Blocking loop: fetch, handle, ack."""
        logger.info("TelemetryConsumer started | stream=%s", STREAM_NAME)
        while True:
            try:
                msgs = await self.sub.fetch(batch_size, timeout=10.0)
                for msg in msgs:
                    data = json.loads(msg.data.decode("utf-8"))
                    telemetry = AgentTelemetry(**data)
                    await handler(telemetry)
                    await msg.ack()
            except Exception as exc:
                logger.exception("Consumer loop error: %s", exc)

    async def close(self) -> None:
        await self.sub.unsubscribe()
        await self.nc.close()

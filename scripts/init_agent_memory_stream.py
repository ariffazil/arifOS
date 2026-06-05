#!/usr/bin/env python3
"""Idempotently create the NATS JetStream 'agent_memory' stream.

Run once after NATS restart or on fresh install.
"""

from __future__ import annotations

import asyncio
import logging

from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

STREAM_NAME = "agent_memory"
SUBJECTS = ["agent.memory.*"]


async def main() -> int:
    nc = NATS()
    await nc.connect(servers=["nats://localhost:4222"])
    js = nc.jetstream()

    try:
        info = await js.add_stream(
            StreamConfig(
                name=STREAM_NAME,
                subjects=SUBJECTS,
                retention="workqueue",
                max_msgs=-1,
                max_bytes=-1,
            )
        )
        logger.info("Created stream: %s | subjects=%s", info.config.name, info.config.subjects)
    except Exception as exc:
        if "already in use" in str(exc).lower():
            logger.info("Stream %s already exists — no action needed.", STREAM_NAME)
        else:
            logger.error("Failed to create stream: %s", exc)
            return 1
    finally:
        await nc.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

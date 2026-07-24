"""Kabarkan Worker — constitutional observability processor.

Subscribes to NATS JetStream (kabarkan.ingest.>), processes observations,
and writes enriched records to Postgres + MinIO.

Part of Fork B: the sovereign arifOS observability plane.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import signal
import sys
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("kabarkan-worker")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NATS_URL = os.getenv("KABARKAN_NATS_URL", "nats://127.0.0.1:4222")
STREAM_NAME = os.getenv("KABARKAN_STREAM", "kabarkan-ingest")
SUBJECTS = os.getenv("KABARKAN_SUBJECTS", "kabarkan.ingest.>")
CONSUMER_NAME = os.getenv("KABARKAN_CONSUMER", "kabarkan-worker-v1")
BATCH_SIZE = int(os.getenv("KABARKAN_BATCH_SIZE", "10"))
POLL_INTERVAL_S = float(os.getenv("KABARKAN_POLL_INTERVAL", "1.0"))
MAX_CONCURRENT = int(os.getenv("KABARKAN_MAX_CONCURRENT", "5"))

# Postgres — prefer POSTGRES_URL, fall back to individual vars
import urllib.parse as _up

_PG_URL = os.getenv("POSTGRES_URL", "")
if _PG_URL:
    _parsed = _up.urlparse(_PG_URL)
    PG_HOST = _parsed.hostname or "localhost"
    PG_PORT = _parsed.port or 5432
    PG_DB = _parsed.path.lstrip("/") or "vault999"
    PG_USER = _up.unquote(_parsed.username or "") or "arifos_admin"
    PG_PASSWORD = _up.unquote(_parsed.password or "") or ""
else:
    PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
    PG_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
    PG_DB = os.getenv("POSTGRES_DB", "vault999")
    PG_USER = os.getenv("POSTGRES_USER", "arifos_admin")
    PG_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# MinIO (optional archiving)
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "")
S3_BUCKET = os.getenv("KABARKAN_S3_BUCKET", "kabarkan-archive")


async def _pg_connect() -> Any:
    """Create async Postgres connection."""
    import asyncpg

    dsn = f"postgresql://{PG_USER}"
    if PG_PASSWORD:
        dsn += f":{PG_PASSWORD}"
    dsn += f"@{PG_HOST}:{PG_PORT}/{PG_DB}"

    return await asyncpg.connect(dsn, timeout=5)


async def _nats_connect() -> tuple[Any, Any]:
    """Connect to NATS and bind to JetStream consumer."""
    import nats
    from nats.js.api import ConsumerConfig, AckPolicy, DeliverPolicy

    nc = await nats.connect(NATS_URL)
    js = nc.jetstream()

    try:
        await js.add_consumer(
            STREAM_NAME,
            config=ConsumerConfig(
                name=CONSUMER_NAME,
                deliver_policy=DeliverPolicy.ALL,
                ack_policy=AckPolicy.EXPLICIT,
                max_deliver=3,
                ack_wait=30,
            ),
        )
        logger.info(f"Consumer {CONSUMER_NAME} created on {STREAM_NAME}")
    except Exception as e:
        logger.info(f"Consumer {CONSUMER_NAME} already exists on {STREAM_NAME}: {e}")

    return nc, js


async def _store_observation(pg: Any, record: dict[str, Any]) -> bool:
    """Write a single observation to Postgres."""
    try:
        import uuid as _uuid

        def _parse_dt(val: Any) -> datetime | None:
            if val is None:
                return None
            if isinstance(val, datetime):
                return val
            try:
                return datetime.fromisoformat(str(val))
            except (ValueError, TypeError):
                return None

        obs_id = _uuid.UUID(str(record.get("observation_id") or _uuid.uuid4()))
        trace_id = _uuid.UUID(str(record.get("trace_id") or _uuid.uuid4()))
        span_id = _uuid.UUID(str(record.get("span_id") or _uuid.uuid4()))

        await pg.execute(
            """
            INSERT INTO observability.observations (
                id, trace_id, span_id, parent_span_id,
                session_id, actor_id, tool_name, organ_id,
                verdict_class, delta_s, reasons, next_safe_action,
                uncertainty_tag, input_hash, output_hash, vault_receipt,
                cost_usd, model_name, latency_ms,
                start_time, end_time, metadata, created_at
            ) VALUES (
                $1, $2, $3, $4,
                $5, $6, $7, $8,
                $9, $10, $11::jsonb, $12,
                $13, $14, $15, $16,
                $17, $18, $19,
                $20, $21, $22::jsonb, $23
            ) ON CONFLICT (id) DO NOTHING
            """,
            obs_id,
            trace_id,
            span_id,
            record.get("parent_span_id"),
            record.get("session_id"),
            record.get("actor_id", "unknown"),
            record.get("tool_name", ""),
            record.get("organ_id"),
            record.get("verdict_class", "OK"),
            record.get("delta_s", 0.0),
            json.dumps(record.get("reasons", [])),
            record.get("next_safe_action")
            if isinstance(record.get("next_safe_action"), str)
            else (
                record.get("next_safe_action", {}).get("action")
                if isinstance(record.get("next_safe_action"), dict)
                else str(record.get("next_safe_action", "")) or None
            ),
            record.get("uncertainty_tag"),
            record.get("input_hash"),
            record.get("output_hash"),
            record.get("vault_receipt"),
            record.get("cost_usd"),
            record.get("model_name"),
            record.get("latency_ms"),
            _parse_dt(record.get("start_time")) or datetime.now(timezone.utc),
            _parse_dt(record.get("end_time")),
            json.dumps(record.get("metadata", {})),
            datetime.now(timezone.utc),
        )
        return True
    except Exception as e:
        logger.warning(f"Store failed: {e}")
        return False


async def _archive_to_s3(record: dict[str, Any]) -> None:
    """Optionally archive raw observations to MinIO.

    Not yet implemented — requires aioboto3 or minio-py.
    """
    pass


async def process_observation(pg: Any, record: dict[str, Any]) -> bool:
    """Process a single observation: store + archive + enrich.

    Returns True if processed successfully.
    """
    # Store to Postgres
    ok = await _store_observation(pg, record)

    # Optionally archive
    if S3_ENDPOINT:
        await _archive_to_s3(record)

    return ok


async def consumer_loop() -> None:
    """Main consumer loop — pull messages from NATS, process, ack."""
    nc = None
    pg = None

    try:
        nc, js = await _nats_connect()
        pg = await _pg_connect()
        logger.info(f"Kabarkan Worker v1 connected — NATS={NATS_URL} PG={PG_HOST}/{PG_DB}")

        sub = await js.pull_subscribe(SUBJECTS, CONSUMER_NAME, stream=STREAM_NAME)

        while True:
            try:
                msgs = await sub.fetch(BATCH_SIZE, timeout=POLL_INTERVAL_S)
            except Exception:
                # Timeout with no messages is normal
                continue

            sem = asyncio.Semaphore(MAX_CONCURRENT)
            pg_lock = asyncio.Lock()

            def _msg_seq(msg) -> str:
                try:
                    return str(msg.metadata.sequence.stream)
                except Exception:
                    try:
                        return str(msg.metadata.sequence.consumer)
                    except Exception:
                        return "?"

            async def handle_one(msg) -> None:
                async with sem:
                    seq = _msg_seq(msg)
                    try:
                        data = json.loads(msg.data.decode())
                        async with pg_lock:
                            ok = await process_observation(pg, data)
                        if ok:
                            await msg.ack()
                        else:
                            logger.warning(f"Nak msg {seq}: store failed")
                            await msg.nak()
                    except json.JSONDecodeError:
                        logger.warning(f"Nak msg {seq}: invalid JSON")
                        await msg.nak()
                    except Exception as e:
                        logger.error(f"Nak msg {seq}: {e}")
                        await msg.nak()

            await asyncio.gather(*[handle_one(m) for m in msgs])

    except asyncio.CancelledError:
        logger.info("Worker shutting down")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        if pg:
            await pg.close()
        if nc:
            try:
                await asyncio.wait_for(nc.drain(), timeout=3.0)
            except (asyncio.TimeoutError, Exception):
                pass
            await nc.close()


def main() -> None:
    """Entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    logger.info("Starting Kabarkan Worker v1")
    logger.info(f"  NATS:     {NATS_URL}")
    logger.info(f"  Stream:   {STREAM_NAME}")
    logger.info(f"  Subjects: {SUBJECTS}")
    logger.info(f"  Postgres: {PG_HOST}:{PG_PORT}/{PG_DB}")
    logger.info(f"  Batch:    {BATCH_SIZE}")
    logger.info(f"  Workers:  {MAX_CONCURRENT}")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task = loop.create_task(consumer_loop())

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: task.cancel())

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()
        logger.info("Kabarkan Worker stopped")


if __name__ == "__main__":
    main()

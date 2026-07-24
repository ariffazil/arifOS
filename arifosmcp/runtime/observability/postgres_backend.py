"""Postgres backend for arifOS observability — replaces Langfuse v4 SDK.

Architecture:
    Telemetry.record_tool_call() → PostgresBackend.store()
        → INSERT INTO observability_observations
        → optionally enqueue to Redis for the ingestion worker

Thread-safety:
    Uses a connection pool (asyncpg or psycopg2 pool).
    Falls back to a simple synchronous connection if pool is unavailable.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from .models import ObservationRecord

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Connection helpers
# ---------------------------------------------------------------------------

_PG_POOL: Any = None
_PG_LOCK = threading.Lock()
_PG_DSN: str | None = None
_REDIS_CONN: Any = None


def _get_pg_dsn() -> str | None:
    """Build Postgres DSN from vault.env variables or defaults.

    Checks in order:
    1. POSTGRES_URL (full connection string — our canonical env var)
    2. Individual POSTGRES_HOST/PORT/DB/USER/PASSWORD
    """
    global _PG_DSN
    if _PG_DSN:
        return _PG_DSN

    # Prefer the full connection string if present
    full_url = os.getenv("POSTGRES_URL")
    if full_url:
        # Quick health check — if URL fails, fall back to explicit params
        try:
            import psycopg2
            test_conn = psycopg2.connect(full_url, connect_timeout=2)
            test_conn.close()
            _PG_DSN = full_url
            return _PG_DSN
        except Exception:
            logger.debug(f"[Observe] POSTGRES_URL connection failed, falling back to explicit params")
            # Fall through to explicit params below

    host = os.getenv("POSTGRES_HOST", "127.0.0.1")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "vault999")
    user = os.getenv("POSTGRES_USER", "arifos_admin")
    password = os.getenv("POSTGRES_PASSWORD", "")

    if password:
        dsn = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    else:
        dsn = f"postgresql://{user}@{host}:{port}/{db}"

    _PG_DSN = dsn
    return dsn


def _get_connection():
    """Get a synchronous psycopg2 connection (simple, no pool for MVP).

    Production: swap for asyncpg pool or SQLAlchemy engine.
    """
    global _PG_POOL

    if _PG_POOL is not None:
        try:
            # Check if still alive
            _PG_POOL.cursor().execute("SELECT 1")
            return _PG_POOL
        except Exception:
            logger.debug("[Observe] Postgres connection lost, reconnecting")
            _PG_POOL = None

    try:
        import psycopg2

        dsn = _get_pg_dsn()
        if not dsn:
            logger.warning("[Observe] No Postgres DSN configured")
            return None

        conn = psycopg2.connect(dsn, connect_timeout=3)
        conn.autocommit = True
        _PG_POOL = conn
        logger.info(f"[Observe] Connected to Postgres at {dsn}")
        return conn
    except ImportError:
        logger.debug("[Observe] psycopg2 not installed; cannot store observations")
        return None
    except Exception as e:
        logger.warning(f"[Observe] Postgres connection failed: {e}")
        return None


def _ensure_schema(conn) -> bool:
    """Create the observability schema and table if they don't exist.

    Idempotent — safe to call on every startup.
    """
    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS observability;
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS observability.observations (
                id              UUID PRIMARY KEY,
                trace_id        UUID NOT NULL,
                span_id         UUID NOT NULL,
                parent_span_id  UUID,
                session_id      TEXT,
                actor_id        TEXT NOT NULL DEFAULT 'unknown',
                tool_name       TEXT NOT NULL DEFAULT '',
                organ_id        TEXT,
                verdict_class   TEXT NOT NULL DEFAULT 'OK',
                delta_s         DOUBLE PRECISION DEFAULT 0,
                reasons         JSONB,
                next_safe_action TEXT,
                uncertainty_tag TEXT,
                input_hash      TEXT,
                output_hash     TEXT,
                vault_receipt   TEXT,
                cost_usd        DOUBLE PRECISION,
                model_name      TEXT,
                latency_ms      DOUBLE PRECISION,
                start_time      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                end_time        TIMESTAMPTZ,
                metadata        JSONB,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        # Indexes for common query patterns
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_trace_id
            ON observability.observations (trace_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_actor_id
            ON observability.observations (actor_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_tool_name
            ON observability.observations (tool_name);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_created_at
            ON observability.observations (created_at DESC);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_session_id
            ON observability.observations (session_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_obs_verdict
            ON observability.observations (verdict_class);
        """)
        cur.close()
        return True
    except Exception as e:
        logger.warning(f"[Observe] Schema init failed: {e}")
        return False


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------


class PostgresBackend:
    """Stores telemetry observations to local Postgres.

    Thread-safe singleton. Falls back gracefully if Postgres is unavailable.
    """

    _instance: PostgresBackend | None = None
    _lock = threading.Lock()

    def __new__(cls) -> PostgresBackend:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._conn = None
        self._schema_ok = False
        self._enabled = True
        self._init()
        self._initialized = True

    def _init(self) -> None:
        self._conn = _get_connection()
        if self._conn:
            self._schema_ok = _ensure_schema(self._conn)
            if self._schema_ok:
                logger.info("[Observe] PostgresBackend ready — schema OK")
            else:
                logger.warning("[Observe] Schema init failed — will retry on write")
        else:
            logger.warning("[Observe] No Postgres connection — observations will be dropped")

    def store(self, record: ObservationRecord) -> bool:
        """Store a single observation.

        Args:
            record: Fully populated ObservationRecord from Telemetry.

        Returns:
            True if stored successfully, False on failure.
        """
        if not self._enabled:
            return False

        # Retry connection if lost
        if not self._conn:
            self._conn = _get_connection()
            if self._conn and not self._schema_ok:
                self._schema_ok = _ensure_schema(self._conn)

        if not self._conn or not self._schema_ok:
            return False

        try:
            cur = self._conn.cursor()
            cur.execute(
                """
                INSERT INTO observability.observations (
                    id, trace_id, span_id, parent_span_id,
                    session_id, actor_id, tool_name, organ_id,
                    verdict_class, delta_s, reasons, next_safe_action,
                    uncertainty_tag, input_hash, output_hash, vault_receipt,
                    cost_usd, model_name, latency_ms,
                    start_time, end_time, metadata, created_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s, %s
                )
                """,
                (
                    str(record.observation_id),
                    str(record.trace_id),
                    str(record.span_id),
                    str(record.parent_span_id) if record.parent_span_id else None,
                    record.session_id,
                    record.actor_id,
                    record.tool_name,
                    record.organ_id,
                    record.verdict_class,
                    record.delta_s,
                    json.dumps(record.reasons) if record.reasons else None,
                    record.next_safe_action,
                    record.uncertainty_tag,
                    record.input_hash,
                    record.output_hash,
                    record.vault_receipt,
                    record.cost_usd,
                    record.model_name,
                    record.latency_ms,
                    record.start_time,
                    record.end_time,
                    json.dumps(record.metadata) if record.metadata else None,
                    record.created_at,
                ),
            )
            cur.close()
            return True
        except Exception as e:
            logger.debug(f"[Observe] Write failed: {e}")
            # Connection might be dead — clear for retry
            self._conn = None
            self._schema_ok = False
            return False

    def store_batch(self, records: list[ObservationRecord]) -> int:
        """Store multiple observations.

        Args:
            records: List of ObservationRecord.

        Returns:
            Count of successfully stored records.
        """
        count = 0
        for r in records:
            if self.store(r):
                count += 1
        return count

    def flush(self) -> None:
        """No-op for Postgres (writes are synchronous).

        Compat shim for Langfuse SDK's flush().
        """
        pass

    def close(self) -> None:
        """Close the connection."""
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            self._conn = None

    @property
    def healthy(self) -> bool:
        """Check if backend is operational."""
        if not self._conn:
            return False
        try:
            cur = self._conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            return True
        except Exception:
            return False

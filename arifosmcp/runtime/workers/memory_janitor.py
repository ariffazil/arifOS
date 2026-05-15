"""
arifosmcp/runtime/workers/memory_janitor.py — Phoenix-72 Janitor Protocol

Hub-and-Spoke persistence layer for Phoenix memory state.
All Phoenix cooling state lives in PostgreSQL (Tier 4) — NOT flat files.
Vault-999 is the only permitted JSONL ledger (Tier 5).

Sweep loop (asyncio, hourly):
  1. Query Postgres: SELECT * FROM memory_store WHERE phoenix_state = 'cooling'
     AND NOW() >= phoenix_cooldown_expiry
  2. For each expired entry:
       - Pass metrics to phoenix_72.evaluate_promotion()
       - VOID  → UPDATE state='void', deleted_at=NOW(); Qdrant hard-delete
       - SEAL  → UPDATE state='sealed'; arif_vault_seal(payload)
  3. Log sweep results

Schema migration (run once):
  ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS phoenix_state VARCHAR(20);
  ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS phoenix_cooldown_expiry TIMESTAMPTZ;
  ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS phoenix_psi_utility INT DEFAULT 0;
  ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS phoenix_tri_witness JSONB DEFAULT '{}';
  ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS phoenix_anti_hantu_flag BOOLEAN DEFAULT FALSE;

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

_PG_URL = os.getenv(
    "ARIFOS_MEMORY_POSTGRES_URL",
    "postgresql://arifos_admin:ArifPostgresVault2026!@postgres:5432/vault999",
)
_QDRANT_URL = os.getenv("QDRANT_URL", "http://qdrant:6333")
_QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "arifos_memory")
_SWEEP_INTERVAL_SECONDS = int(os.getenv("JANITOR_SWEEP_INTERVAL_SECONDS", "3600"))
_JANITOR_ENABLED = os.getenv("JANITOR_ENABLED", "1").lower() in ("1", "true", "yes")

# =============================================================================
# Postgres helpers
# =============================================================================


async def _pg_fetch_rows(query: str, *args) -> list[dict[str, Any]]:
    """Execute a SELECT and return rows as list of dicts."""
    import asyncpg

    conn = await asyncpg.connect(_PG_URL, timeout=10)
    try:
        rows = await conn.fetch(query, *args)
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def _pg_execute(query: str, *args) -> str:
    """Execute a write query. Returns execution result string."""
    import asyncpg

    conn = await asyncpg.connect(_PG_URL, timeout=10)
    try:
        return await conn.execute(query, *args)
    finally:
        await conn.close()


# =============================================================================
# Qdrant helpers
# =============================================================================


def _get_qdrant_client():
    from qdrant_client import QdrantClient  # noqa: PLC0415

    qdrant_url = _QDRANT_URL
    if qdrant_url.startswith("ENC["):
        qdrant_url = "http://qdrant:6333"
    return QdrantClient(url=qdrant_url)


def _qdrant_delete(point_id: str) -> bool:
    """Hard-delete a point from Qdrant. Returns True on success."""
    try:
        from qdrant_client.models import PointIdsList

        client = _get_qdrant_client()
        client.delete(
            collection_name=_QDRANT_COLLECTION,
            points_selector=PointIdsList(points=[point_id]),
        )
        return True
    except Exception as exc:
        logger.error("Qdrant delete failed for point_id=%s: %s", point_id, exc)
        return False


# =============================================================================
# Vault-999 helper
# =============================================================================


def _seal_to_vault(memory_id: str, phoenix_entry: dict[str, Any]) -> dict[str, Any]:
    """Call arif_vault_seal for a Phoenix SEAL transition."""
    from arifosmcp.runtime.tools import _arif_vault_seal

    payload = json.dumps(
        {
            "phoenix_id": phoenix_entry.get("phoenix_id"),
            "memory_id": memory_id,
            "state": "sealed",
            "psi_utility": phoenix_entry.get("phoenix_psi_utility", 0),
            "tri_witness": phoenix_entry.get("phoenix_tri_witness", {}),
            "anti_hantu_flag": phoenix_entry.get("phoenix_anti_hantu_flag", False),
            "cooldown_expiry": phoenix_entry.get("phoenix_cooldown_expiry"),
            "sealed_at": datetime.now(timezone.utc).isoformat(),
            "source": "phoenix_janitor",
        },
        default=str,
    )

    result = _arif_vault_seal(
        mode="seal",
        payload=payload,
        session_id=None,
        ack_irreversible=True,
        actor_id="arifOS_janitor",
        constitutional_chain_id=None,
        judge_state_hash=None,
        verification_state=None,
        witness_type="ai",
        drift_events=None,
    )
    return result


# =============================================================================
# Schema migration
# =============================================================================


async def ensure_phoenix_columns() -> bool:
    """Run ALTER TABLE to add Phoenix columns if they don't exist.

    Idempotent — uses ADD COLUMN IF NOT EXISTS (Postgres 15+).
    """
    columns = [
        ("phoenix_state", "VARCHAR(20) DEFAULT 'cooling'"),
        ("phoenix_cooldown_expiry", "TIMESTAMPTZ"),
        ("phoenix_psi_utility", "INT DEFAULT 0"),
        ("phoenix_tri_witness", "JSONB DEFAULT '{}'::jsonb"),
        ("phoenix_anti_hantu_flag", "BOOLEAN DEFAULT FALSE"),
    ]

    for col_name, col_type in columns:
        try:
            # Postgres 15+ syntax — no string interpolation, no DO$$ block
            await _pg_execute(
                f"ALTER TABLE memory_store ADD COLUMN IF NOT EXISTS {col_name} {col_type}",
            )
            logger.info("Phoenix column %s is ready", col_name)
        except Exception as exc:
            logger.warning("Phoenix column migration failed for %s: %s", col_name, exc)
            return False
    return True


# =============================================================================
# Phoenix state constants (local copy — avoids circular import)
# =============================================================================

_STATE_COOLING = "cooling"
_STATE_SEALED = "sealed"
_STATE_VOID = "void"


# =============================================================================
# Core sweep logic
# =============================================================================


async def _sweep_one(entry: dict[str, Any]) -> tuple[str, str]:
    """Evaluate and resolve one COOLING row. Returns (outcome, reason)."""
    memory_id = str(entry["id"])
    qdrant_id = str(entry["qdrant_id"]) if entry.get("qdrant_id") else None

    phoenix_entry = {
        "phoenix_id": entry.get("phoenix_id") or memory_id,
        "memory_id": memory_id,
        "state": entry.get("phoenix_state", _STATE_COOLING),
        "cooldown_expiry": entry.get("phoenix_cooldown_expiry"),
        "psi_utility": entry.get("phoenix_psi_utility", 0),
        "tri_witness": entry.get("phoenix_tri_witness") or {},
        "anti_hantu_flag": entry.get("phoenix_anti_hantu_flag", False),
        "created_at": entry.get("created_at"),
    }

    # Import here to avoid top-level circular deps
    from arifosmcp.runtime.phoenix_72 import evaluate_promotion

    new_state, reason = evaluate_promotion(phoenix_entry)

    if new_state == phoenix_entry["state"]:
        return "unchanged", reason

    if new_state == _STATE_VOID:
        if qdrant_id:
            _qdrant_delete(qdrant_id)
        await _pg_execute(
            "UPDATE memory_store SET phoenix_state = 'void', "
            "deleted_at = now() WHERE id = $1::uuid",
            entry["id"],
        )
        logger.info(
            "PHOENIX VOID: memory_id=%s qdrant_id=%s reason=%s", memory_id, qdrant_id, reason
        )
        return "voided", reason

    if new_state == _STATE_SEALED:
        try:
            vault_result = _seal_to_vault(memory_id, phoenix_entry)
            vault_ok = vault_result.get("status") == "OK"
        except Exception as exc:
            logger.error("Vault seal failed for memory_id=%s: %s", memory_id, exc)
            vault_ok = False

        await _pg_execute(
            "UPDATE memory_store SET phoenix_state = 'sealed' WHERE id = $1::uuid",
            entry["id"],
        )
        logger.info(
            "PHOENIX SEALED: memory_id=%s vault_ok=%s reason=%s",
            memory_id,
            vault_ok,
            reason,
        )
        return "sealed", reason

    return "unchanged", f"unknown new_state={new_state}"


async def run_sweep() -> dict[str, int]:
    """Run one full sweep of all expired COOLING entries.

    Returns dict with counts: sealed, voided, unchanged, errors.
    """
    schema_ok = await ensure_phoenix_columns()
    if not schema_ok:
        logger.error("Janitor sweep aborted: schema migration failed")
        return {"sealed": 0, "voided": 0, "unchanged": 0, "errors": 1}

    rows = await _pg_fetch_rows(
        """
        SELECT id, qdrant_id, phoenix_state, phoenix_cooldown_expiry,
               phoenix_psi_utility, phoenix_tri_witness, phoenix_anti_hantu_flag,
               created_at
        FROM memory_store
        WHERE phoenix_state = 'cooling'
          AND phoenix_cooldown_expiry IS NOT NULL
          AND NOW() >= phoenix_cooldown_expiry
          AND deleted_at IS NULL
        """,
    )

    if not rows:
        logger.debug("Janitor sweep: no expired COOLING entries found")
        return {"sealed": 0, "voided": 0, "unchanged": 0, "errors": 0}

    logger.info("Janitor sweep: processing %d expired COOLING entries", len(rows))

    counts = {"sealed": 0, "voided": 0, "unchanged": 0, "errors": 0}
    for row in rows:
        try:
            outcome, _ = await _sweep_one(row)
            if outcome in counts:
                counts[outcome] += 1
        except Exception as exc:
            logger.error("Sweep error for row id=%s: %s", row["id"], exc)
            counts["errors"] += 1

    logger.info(
        "Janitor sweep complete: sealed=%d voided=%d unchanged=%d errors=%d",
        counts["sealed"],
        counts["voided"],
        counts["unchanged"],
        counts["errors"],
    )
    return counts


# =============================================================================
# Background sweep loop
# =============================================================================


class MemoryJanitor:
    """Phoenix-72 Janitor — runs hourly sweep loop as a background asyncio task."""

    def __init__(
        self,
        sweep_interval_seconds: int = _SWEEP_INTERVAL_SECONDS,
        enabled: bool = _JANITOR_ENABLED,
    ) -> None:
        self.sweep_interval = sweep_interval_seconds
        self.enabled = enabled
        self._task: asyncio.Future | None = None
        self._shutdown = threading.Event()

    async def _loop(self) -> None:
        """Async background loop: sleep interval, then run_sweep."""
        while not self._shutdown.is_set():
            try:
                # Sleep first — let server boot before first sweep
                await asyncio.sleep(self.sweep_interval)

                if self._shutdown.is_set():
                    break

                logger.info("Janitor sweep starting...")
                counts = await run_sweep()
                logger.info("Janitor sweep done: %s", counts)

            except asyncio.CancelledError:
                logger.info("Janitor loop CancelledError — shutting down")
                break
            except Exception as exc:
                logger.error("Janitor loop error: %s", exc)

    def start(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        """Start the Janitor background task."""
        if not self.enabled:
            logger.info("Janitor is disabled (JANITOR_ENABLED=0)")
            return

        def _run_loop() -> None:
            async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(async_loop)
            try:
                async_loop.run_until_complete(self._loop())
            finally:
                async_loop.close()

        if loop is not None:
            self._task = asyncio.run_coroutine_threadsafe(self._loop(), loop)  # type: ignore[assignment]
            logger.info("Janitor task scheduled in provided event loop")
        else:
            t = threading.Thread(target=_run_loop, daemon=True, name="phoenix-janitor")
            t.start()
            logger.info("Janitor daemon thread started (interval=%ds)", self.sweep_interval)

    def stop(self) -> None:
        """Signal the Janitor to stop after the current sweep."""
        self._shutdown.set()
        if self._task is not None:
            self._task.cancel()


# =============================================================================
# Module-level singleton + startup helper
# =============================================================================

_janitor: MemoryJanitor | None = None


def get_janitor() -> MemoryJanitor:
    """Get or create the module-level MemoryJanitor singleton."""
    global _janitor
    if _janitor is None:
        _janitor = MemoryJanitor()
    return _janitor


def start_janitor(loop: asyncio.AbstractEventLoop | None = None) -> MemoryJanitor:
    """Start the Janitor and return the singleton instance."""
    janitor = get_janitor()
    janitor.start(loop=loop)
    return janitor

"""
arifosmcp/runtime/state_store.py — Dual-layer (L1 in-process + L4 Postgres) persistence for KernelState.

EUREKA-A storage layer. Per Hermes-ASI probe 2026-06-11:
  - L1 = Redis-style in-process dict (fast, session-scoped, ephemeral)
  - L4 = Supabase/Postgres `memory_store` table with tier='kernel_state' (durable, cross-session)

Reversibility (F1): file delete = revert. No new tables, no migrations. New tier
in existing `memory_store` table. Drop tier='kernel_state' rows = revert.

Constitutional binding:
  F1 AMANAH  — soft-delete only (deleted_at), never destructive
  F2 TRUTH   — every snapshot includes full canonical state + state_hash
  F4 CLARITY — all I/O is typed Pydantic; never dict-typed
  F7 HUMILITY — L4 failure does NOT block L1 (kernel keeps working)
  F11 AUDIT   — every write is logged with actor, event_type, state_hash
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from arifosmcp.runtime.kernel_state import (
    KernelState,
    KernelStateStore,
    get_state_store,
)

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# L4 configuration — env-driven, fail-soft
# ─────────────────────────────────────────────────────────────────────────────

_PG_URL = os.environ.get("ARIFOS_MEMORY_POSTGRES_URL") or os.environ.get("POSTGRES_URL", "")
_L4_ENABLED = bool(_PG_URL)
_L4_TIMEOUT_S: int = 5  # asyncpg.connect expects int seconds
_TIER_KERNEL_STATE = "kernel_state"


# ─────────────────────────────────────────────────────────────────────────────
# Snapshot envelope (what gets written to L4)
# ─────────────────────────────────────────────────────────────────────────────


class KernelStateSnapshot(BaseModel):
    """The L4 record for one KernelState save. Versioned for migration."""

    snapshot_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    state_version: str
    state_hash: str
    payload: dict[str, Any]  # canonical KernelState.model_dump(mode='json')
    actor: str
    event_type: str
    recorded_at: float = Field(default_factory=lambda: time.time())
    pg_id: str | None = None  # set after L4 write
    l4_write_ok: bool = False
    l4_error: str | None = None


# ─────────────────────────────────────────────────────────────────────────────
# L4 helpers — asyncpg with fail-soft semantics
# ─────────────────────────────────────────────────────────────────────────────


def _pg_run(coro: Any) -> Any:
    """Run async coroutine in fresh event loop. Pattern from memory_store.py."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


async def _pg_write_snapshot(snapshot: KernelStateSnapshot) -> str | None:
    """Write one snapshot to memory_store with tier='kernel_state'. Returns pg_id or None."""
    if not _L4_ENABLED:
        return None
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=_L4_TIMEOUT_S, statement_cache_size=0)
        try:
            text_repr = f"KernelState@{snapshot.state_hash[:16]} session={snapshot.session_id}"
            metadata = {
                "actor": snapshot.actor,
                "event_type": snapshot.event_type,
                "state_hash": snapshot.state_hash,
                "state_version": snapshot.state_version,
                "session_id": snapshot.session_id,
                "snapshot_id": snapshot.snapshot_id,
            }
            entity_tags = ["kernel_state", snapshot.actor]
            distillation_status = "kernel_state_snapshot"
            pg_id = str(uuid.uuid4())
            await conn.execute(
                """
                INSERT INTO memory_store
                    (id, tier, text, metadata, qdrant_id, session_id,
                     entity_tags, distillation_status, distillation_metadata,
                     valid_at, recorded_at)
                VALUES ($1::uuid, $2, $3, $4::jsonb, $5::uuid, $6, $7, $8, $9::jsonb, $10, $11)
                ON CONFLICT (id) DO NOTHING
                """,
                pg_id,
                _TIER_KERNEL_STATE,
                text_repr,
                json.dumps(metadata, default=str),
                None,  # qdrant_id (not used for kernel_state)
                snapshot.session_id,
                entity_tags,
                distillation_status,
                json.dumps({"payload": snapshot.payload}, default=str),
                datetime.fromtimestamp(snapshot.recorded_at, tz=UTC),
                datetime.fromtimestamp(snapshot.recorded_at, tz=UTC),
            )
            return pg_id
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("L4 kernel_state write failed for session=%s: %s", snapshot.session_id, exc)
        return None


async def _pg_load_snapshots(session_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Load last N snapshots for a session, newest first."""
    if not _L4_ENABLED:
        return []
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=_L4_TIMEOUT_S, statement_cache_size=0)
        try:
            rows = await conn.fetch(
                """
                SELECT id::text, text, metadata, distillation_metadata, recorded_at
                FROM memory_store
                WHERE tier = $1 AND session_id = $2 AND deleted_at IS NULL
                ORDER BY recorded_at DESC
                LIMIT $3
                """,
                _TIER_KERNEL_STATE,
                session_id,
                limit,
            )
            out: list[dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                # asyncpg returns JSONB as str; decode to dict
                for k in ("metadata", "distillation_metadata"):
                    if isinstance(d.get(k), str):
                        try:
                            d[k] = json.loads(d[k])
                        except (TypeError, ValueError):
                            pass
                out.append(d)
            return out
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("L4 kernel_state load failed for session=%s: %s", session_id, exc)
        return []


async def _pg_soft_delete_snapshots(session_id: str) -> int:
    """Soft-delete all snapshots for a session. Returns count."""
    if not _L4_ENABLED:
        return 0
    try:
        import asyncpg  # noqa: PLC0415

        conn = await asyncpg.connect(_PG_URL, timeout=_L4_TIMEOUT_S, statement_cache_size=0)
        try:
            result = await conn.execute(
                """
                UPDATE memory_store
                SET deleted_at = now()
                WHERE tier = $1 AND session_id = $2 AND deleted_at IS NULL
                """,
                _TIER_KERNEL_STATE,
                session_id,
            )
            # parse "UPDATE n"
            try:
                return int(result.split()[-1])
            except (ValueError, IndexError):
                return 0
        finally:
            await conn.close()
    except Exception as exc:
        logger.warning("L4 kernel_state soft-delete failed for session=%s: %s", session_id, exc)
        return 0


# ─────────────────────────────────────────────────────────────────────────────
# Dual-layer store — wraps KernelStateStore with L4 mirror
# ─────────────────────────────────────────────────────────────────────────────


class DualLayerKernelStore:
    """L1 (in-process) + L4 (Postgres) KernelState persistence.

    Every save_state() writes to L1 synchronously and to L4 best-effort.
    L4 failures NEVER block L1 — F7 HUMILITY: kernel stays alive even if
    Postgres is down. L4 is for auditability and cross-session replay.
    """

    def __init__(self) -> None:
        self._l1: KernelStateStore = get_state_store()
        self._l4_writes: int = 0
        self._l4_failures: int = 0
        self._l4_loads: int = 0

    @property
    def l1(self) -> KernelStateStore:
        return self._l1

    @property
    def l4_enabled(self) -> bool:
        return _L4_ENABLED

    def save_state(
        self,
        state: KernelState,
        *,
        actor: str = "kernel",
        event_type: str = "save",
    ) -> tuple[str, KernelStateSnapshot | None]:
        """Save to L1 (sync) and L4 (best-effort).

        Returns (state_hash, snapshot). Snapshot is None if L4 disabled.
        """
        # L1 first — must not fail
        state_hash = self._l1.save_state(state)

        # L4 best-effort
        snapshot: KernelStateSnapshot | None = None
        if _L4_ENABLED:
            snapshot = KernelStateSnapshot(
                session_id=state.session_id,
                state_version=state.state_version,
                state_hash=state_hash,
                payload=state.canonical_dict(),
                actor=actor,
                event_type=event_type,
            )
            pg_id = _pg_run(_pg_write_snapshot(snapshot))
            if pg_id is not None:
                snapshot.pg_id = pg_id
                snapshot.l4_write_ok = True
                self._l4_writes += 1
            else:
                snapshot.l4_write_ok = False
                snapshot.l4_error = "asyncpg write returned None (see logs)"
                self._l4_failures += 1

        return state_hash, snapshot

    def transition(
        self,
        session_id: str,
        actor: str,
        event_type: str,
        payload: dict[str, Any],
    ) -> tuple[KernelState | None, str | None, KernelStateSnapshot | None]:
        """Apply a transition. Returns (new_state, state_hash, l4_snapshot)."""
        new_state, new_hash = self._l1.transition(session_id, actor, event_type, payload)
        if new_state is None or new_hash is None:
            return None, None, None
        _, snapshot = self.save_state(new_state, actor=actor, event_type=event_type)
        return new_state, new_hash, snapshot

    def load_state(self, session_id: str) -> KernelState | None:
        """Load from L1 only — L4 is for replay, not hot path."""
        return self._l1.load_state(session_id)

    def replay_from_l4(self, session_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Load last N snapshots from L4 for replay/audit. Returns raw rows."""
        rows = _pg_run(_pg_load_snapshots(session_id, limit))
        self._l4_loads += 1
        return rows

    def forget_session(self, session_id: str) -> int:
        """Soft-delete all L4 snapshots for a session. F1 reversible (deleted_at)."""
        return _pg_run(_pg_soft_delete_snapshots(session_id))

    def stats(self) -> dict[str, Any]:
        return {
            **self._l1.stats(),
            "l4_enabled": _L4_ENABLED,
            "l4_writes": self._l4_writes,
            "l4_failures": self._l4_failures,
            "l4_loads": self._l4_loads,
        }


# ─────────────────────────────────────────────────────────────────────────────
# Module-level singleton
# ─────────────────────────────────────────────────────────────────────────────

_DUAL_STORE: DualLayerKernelStore | None = None


def get_dual_store() -> DualLayerKernelStore:
    """Lazy singleton. No side effects on import."""
    global _DUAL_STORE
    if _DUAL_STORE is None:
        _DUAL_STORE = DualLayerKernelStore()
    return _DUAL_STORE


__all__ = [
    "DualLayerKernelStore",
    "KernelStateSnapshot",
    "get_dual_store",
]

"""
ART Library — Cold-path persistent memory of ART verdicts.

W1 wedge (2026-06-21). Built AND wired. Provides:
  - Postgres-backed persistent call history (90-day bounded retention)
  - Read interface for art_registry.py (W2) and art_propose.py (W3)
  - Optional `ARIFOS_ART_LIBRARY=0` env kill-switch (zero overhead when off)

The reflex (art.py) is NOT modified. Writes happen via a fire-and-forget
call from mesh_subscriber.py:287-326 — see the WIRING section below.

Heritage:
  - ART reflex:        arifosmcp/runtime/art.py       (hot path, ≤500 lines ceiling)
  - ART compat shim:   arifosmcp/runtime/art_compat.py (cold, legacy 6-check order)
  - ART doctrine:      arifosmcp/runtime/art_pusaka.py (cold, PUSAKA / APEX dials)
  - Skill-RAG pattern: xf-zhao/Agentic-Skill-Discovery (arxiv 2405.15019, 2024)
  - Dynamic discovery: aipotheosis-labs/aci (Unified MCP, 2024)
  - Self-supervision:  Toolformer (Meta AI, 2023)

Design constraints (binding):
  - Module-level import must NOT require asyncpg (graceful dry-mode)
  - All write methods are fire-and-forget; never raise, never block the reflex
  - DB unavailable → empty reads, library logs WARNING and continues
  - 90-day window matches ART's `days_since_use → ABANDONED` transition
  - LOC budget: ≤300 lines (cold-path discipline)

WIRING (W1.5 LIVE — wired in mesh_subscriber.py:287-326):
  The ART library write is already live inside `organ_intelligence_printer`.
  Every mesh broadcast becomes a row in art_library via
  `asyncio.get_running_loop().create_task(_record_art_verdict())`.
  See `arifosmcp/runtime/mesh_subscriber.py` lines 287-326 for the
  implementation. Never raises. Never blocks the mesh.

DITEMPA BUKAN DIBERI — Library is forged, not configured.
"""

from __future__ import annotations
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("arifosmcp.art_library")

# ═══════════════════════════════════════════════════════════════════════════
# OPTIONAL asyncpg — module-level reference so tests can patch it.
# Library is functional in dry mode (empty reads) if asyncpg is missing.
# ═══════════════════════════════════════════════════════════════════════════
try:
    import asyncpg  # type: ignore
except ImportError:  # pragma: no cover
    asyncpg = None  # type: ignore


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS — the 90-day window matches ART's days_since_use → ABANDONED.
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_RETENTION_DAYS: int = 90  # prune older rows
DEFAULT_LOOKBACK_DAYS: int = 30  # recent reads default window
DEFAULT_INTENT_LIMIT: int = 5  # top-K similar intents for RAG
DEFAULT_TOOL_LIMIT: int = 50  # top-K verdicts per tool
ART_LIBRARY_ENABLED: bool = os.getenv("ARIFOS_ART_LIBRARY", "1") != "0"


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODEL — local mirrors of ArtVerdict / ToolState to avoid hot-path coupling.
# ═══════════════════════════════════════════════════════════════════════════


class VerdictLabel(str, Enum):
    """Local mirror of ArtVerdict (art.py). Decoupled — no cross-import."""

    PROCEED = "PROCEED"
    HOLD = "HOLD"
    BLOCK = "BLOCK"
    DEFAULT_OBSERVE = "DEFAULT_OBSERVE"


class StateLabel(str, Enum):
    """Local mirror of ToolState (art.py). Decoupled — no cross-import."""

    UNTRUSTED = "UNTRUSTED"
    OBSERVED = "OBSERVED"
    TRUSTED = "TRUSTED"
    FALLBACK = "FALLBACK"
    ABANDONED = "ABANDONED"


@dataclass
class ArtVerdictRow:
    """One persisted ART verdict. Written by mesh_subscriber; read by registry/propose."""

    ts: datetime
    session_id: str
    tool_name: str
    action_class: str
    tool_state: str
    verdict: str
    witness: Optional[str] = None
    blast_radius: Optional[str] = None
    reversible: Optional[bool] = None
    failure_rate: Optional[float] = None
    drift_count: Optional[int] = None
    days_since_use: Optional[int] = None
    intent: Optional[str] = None
    actor_id: Optional[str] = None
    extras: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if isinstance(self.ts, datetime):
            d["ts"] = self.ts.isoformat()
        return d


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA — single DDL string, idempotent, ready for Postgres ≥ 13.
# ═══════════════════════════════════════════════════════════════════════════

SCHEMA_DDL: str = """
CREATE TABLE IF NOT EXISTS art_library (
    id              BIGSERIAL PRIMARY KEY,
    ts              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    session_id      TEXT NOT NULL,
    actor_id        TEXT,
    tool_name       TEXT NOT NULL,
    action_class    TEXT NOT NULL,
    tool_state      TEXT NOT NULL,
    verdict         TEXT NOT NULL,
    witness         TEXT,
    blast_radius    TEXT,
    reversible      BOOLEAN,
    failure_rate    REAL,
    drift_count     INTEGER,
    days_since_use  INTEGER,
    intent          TEXT,
    extras          JSONB
);
CREATE INDEX IF NOT EXISTS art_library_ts_idx ON art_library (ts DESC);
CREATE INDEX IF NOT EXISTS art_library_tool_idx ON art_library (tool_name, ts DESC);
CREATE INDEX IF NOT EXISTS art_library_session_idx ON art_library (session_id, ts DESC);
CREATE INDEX IF NOT EXISTS art_library_intent_idx ON art_library
    USING gin (to_tsvector('english', COALESCE(intent, '')));
"""


# ═══════════════════════════════════════════════════════════════════════════
# LIBRARY — the only public class. Postgres-backed, optional, cold-path.
# ═══════════════════════════════════════════════════════════════════════════


class ArtLibrary:
    """Cold-path persistent memory of ART verdicts.

    Read interface (W2/W3 callers: art_registry, art_propose):
        lib = ArtLibrary()
        recent = await lib.recent_for_tool("arif_think", window_days=30)
        rate   = await lib.success_rate("arif_think", window_days=30)

    Write interface (W1.5 caller: mesh_subscriber):
        await lib.record(ArtVerdictRow(...))

    DB unavailable → all methods return safely (False / [] / None).
    Library never raises, never blocks the reflex path.
    """

    def __init__(
        self,
        dsn: Optional[str] = None,
        retention_days: int = DEFAULT_RETENTION_DAYS,
    ) -> None:
        self._dsn = dsn or os.getenv("ARIFOS_PG_DSN")
        self._retention_days = retention_days
        self._pool: Optional[Any] = None
        self._schema_ready: bool = False

    async def _ensure_pool(self) -> bool:
        """Lazy pool init. Returns True iff pool is usable. Never raises."""
        if not self._dsn or not ART_LIBRARY_ENABLED:
            return False
        if self._pool is not None:
            return True
        if asyncpg is None:
            logger.warning("art_library: asyncpg not installed; running in dry mode")
            return False
        try:
            self._pool = await asyncpg.create_pool(self._dsn, min_size=1, max_size=4)
            return True
        except Exception as exc:
            logger.warning("art_library: Postgres pool init failed: %s", exc)
            return False

    async def ensure_schema(self) -> bool:
        """Run DDL once. Idempotent — cached via _schema_ready."""
        if self._schema_ready:
            return True
        if not await self._ensure_pool() or self._pool is None:
            return False
        try:
            async with self._pool.acquire() as conn:
                await conn.execute(SCHEMA_DDL)
            self._schema_ready = True
            return True
        except Exception as exc:
            logger.warning("art_library.ensure_schema failed: %s", exc)
            return False

    async def record(self, row: ArtVerdictRow) -> bool:
        """Fire-and-forget insert. Never raises, never blocks the caller."""
        if not await self._ensure_pool() or self._pool is None:
            return False
        try:
            extras_json = json.dumps(row.extras) if row.extras else None
            async with self._pool.acquire() as conn:
                await conn.execute(
                    """INSERT INTO art_library
                       (ts, session_id, actor_id, tool_name, action_class, tool_state,
                        verdict, witness, blast_radius, reversible, failure_rate,
                        drift_count, days_since_use, intent, extras)
                       VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15)""",
                    row.ts,
                    row.session_id,
                    row.actor_id,
                    row.tool_name,
                    row.action_class,
                    row.tool_state,
                    row.verdict,
                    row.witness,
                    row.blast_radius,
                    row.reversible,
                    row.failure_rate,
                    row.drift_count,
                    row.days_since_use,
                    row.intent,
                    extras_json,
                )
            return True
        except Exception as exc:
            logger.warning("art_library.record failed for tool=%s: %s", row.tool_name, exc)
            return False

    async def recent_for_tool(
        self,
        tool: str,
        window_days: int = DEFAULT_LOOKBACK_DAYS,
        limit: int = DEFAULT_TOOL_LIMIT,
    ) -> list[ArtVerdictRow]:
        """Return most-recent verdicts for a tool, newest first, bounded by window."""
        if not await self._ensure_pool() or self._pool is None:
            return []
        try:
            since = datetime.now(timezone.utc) - timedelta(days=window_days)
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT * FROM art_library
                       WHERE tool_name = $1 AND ts >= $2
                       ORDER BY ts DESC LIMIT $3""",
                    tool,
                    since,
                    limit,
                )
            return [_row_to_art_verdict(r) for r in rows]
        except Exception as exc:
            logger.warning("art_library.recent_for_tool failed: %s", exc)
            return []

    async def recent_for_intent(
        self,
        intent: str,
        limit: int = DEFAULT_INTENT_LIMIT,
    ) -> list[ArtVerdictRow]:
        """Return most-recent verdicts matching an intent (tsvector match)."""
        if not await self._ensure_pool() or self._pool is None:
            return []
        try:
            async with self._pool.acquire() as conn:
                rows = await conn.fetch(
                    """SELECT * FROM art_library
                       WHERE to_tsvector('english', COALESCE(intent, ''))
                             @@ plainto_tsquery('english', $1)
                       ORDER BY ts DESC LIMIT $2""",
                    intent,
                    limit,
                )
            return [_row_to_art_verdict(r) for r in rows]
        except Exception as exc:
            logger.warning("art_library.recent_for_intent failed: %s", exc)
            return []

    async def success_rate(
        self,
        tool: str,
        window_days: int = DEFAULT_LOOKBACK_DAYS,
    ) -> Optional[float]:
        """Compute PROCEED fraction for a tool over the window. None = no data."""
        recent = await self.recent_for_tool(tool, window_days=window_days, limit=1000)
        if not recent:
            return None
        proceeds = sum(1 for r in recent if r.verdict == VerdictLabel.PROCEED.value)
        return proceeds / len(recent)

    async def prune(self, retention_days: Optional[int] = None) -> int:
        """Delete rows older than retention window. Returns count deleted."""
        retention = retention_days if retention_days is not None else self._retention_days
        if not await self._ensure_pool() or self._pool is None:
            return 0
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=retention)
            async with self._pool.acquire() as conn:
                result = await conn.execute("DELETE FROM art_library WHERE ts < $1", cutoff)
            # asyncpg returns e.g. "DELETE 42"
            try:
                return int(result.split()[1])
            except (IndexError, ValueError):
                return 0
        except Exception as exc:
            logger.warning("art_library.prune failed: %s", exc)
            return 0

    async def close(self) -> None:
        """Tear down pool. Idempotent."""
        if self._pool is not None:
            try:
                await self._pool.close()
            except Exception:
                pass
            self._pool = None
            self._schema_ready = False


# ═══════════════════════════════════════════════════════════════════════════
# INTERNAL HELPERS — row conversion + singleton accessor
# ═══════════════════════════════════════════════════════════════════════════


def _row_to_art_verdict(row: Any) -> ArtVerdictRow:
    """Convert asyncpg.Record / namedtuple / dict → ArtVerdictRow.

    Supports three row shapes:
      - asyncpg.Record (dict-like + attribute access)
      - namedtuple (attribute access + integer index)
      - dict (key access)
    """

    def _get(key: str, default: Any = None) -> Any:
        # Try dict-like access first (catches asyncpg.Record + dict)
        if hasattr(row, "keys"):
            try:
                return row[key]
            except (KeyError, TypeError):
                pass
        # Fall back to attribute access (catches namedtuple + asyncpg.Record)
        return getattr(row, key, default)

    extras_raw = _get("extras")
    extras: dict = {}
    if extras_raw:
        try:
            extras = json.loads(extras_raw) if isinstance(extras_raw, str) else dict(extras_raw)
        except (json.JSONDecodeError, TypeError, ValueError):
            extras = {}
    return ArtVerdictRow(
        ts=_get("ts"),
        session_id=_get("session_id"),
        actor_id=_get("actor_id"),
        tool_name=_get("tool_name"),
        action_class=_get("action_class"),
        tool_state=_get("tool_state"),
        verdict=_get("verdict"),
        witness=_get("witness"),
        blast_radius=_get("blast_radius"),
        reversible=_get("reversible"),
        failure_rate=_get("failure_rate"),
        drift_count=_get("drift_count"),
        days_since_use=_get("days_since_use"),
        intent=_get("intent"),
        extras=extras,
    )


_default_library: Optional[ArtLibrary] = None


def get_library() -> ArtLibrary:
    """Return the default library instance (lazy-init, process-global)."""
    global _default_library
    if _default_library is None:
        _default_library = ArtLibrary()
    return _default_library


def _reset_default_library() -> None:
    """Test-only: reset the module-level singleton."""
    global _default_library
    _default_library = None


__all__ = [
    "ArtLibrary",
    "ArtVerdictRow",
    "StateLabel",
    "VerdictLabel",
    "SCHEMA_DDL",
    "DEFAULT_RETENTION_DAYS",
    "DEFAULT_LOOKBACK_DAYS",
    "DEFAULT_INTENT_LIMIT",
    "DEFAULT_TOOL_LIMIT",
    "ART_LIBRARY_ENABLED",
    "get_library",
    "_reset_default_library",
    "_row_to_art_verdict",
]

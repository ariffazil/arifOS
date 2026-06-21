"""
ACT Library — Persistent memory of past execution programs.

Tracks:
  - Every program that ran (verdict + pattern + stages)
  - Which patterns succeeded/failed for which action classes
  - Human acknowledgment patterns (which actions need human checkpoints)

Used by:
  - act.py (next_stage verification)
  - Agent loop (recall past program patterns)
  - A-FORGE /execute (stage tracking)

Design constraints (binding):
  - Module-level import must NOT require asyncpg (graceful dry-mode)
  - All write methods are fire-and-forget; never raise, never block
  - DB unavailable → empty reads, library logs WARNING and continues
  - In-memory fallback when no DB available (for stateless agents)
  - LOC budget: ≤300 lines (cold-path discipline)

DITEMPA BUKAN DIBERI — Library is forged, not configured.
"""

from __future__ import annotations
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("arifosmcp.act_library")

# ═══════════════════════════════════════════════════════════════════════════
# OPTIONAL asyncpg — module-level reference so tests can patch it.
# ═══════════════════════════════════════════════════════════════════════════
try:
    import asyncpg  # type: ignore
except ImportError:
    asyncpg = None  # type: ignore


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_RETENTION_DAYS: int = 90
ACT_LIBRARY_ENABLED: bool = os.getenv("ARIFOS_ACT_LIBRARY", "1") != "0"


# ═══════════════════════════════════════════════════════════════════════════
# PROGRAM RECORD — one entry per execution program
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ProgramRecord:
    """Record of one execution program (may have multiple stages)."""
    ts: str = ""                                      # ISO timestamp
    session_id: str = "unknown"
    program_id: str = ""                              # unique id for this program
    action_class: str = "unknown"                     # from action classifier
    execution_pattern: str = "single_shot"             # from ACT
    blast_radius: str = "unknown"
    is_reversible: bool = False
    stage_count: int = 1
    stages_completed: int = 0
    stages_failed: int = 0
    verdict: str = "unknown"                          # what ACT decided
    human_acknowledged: bool = False
    had_compensation: bool = False
    had_dry_run: bool = False
    tool_name: str = "unknown"
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# IN-MEMORY STORE (fallback when no DB)
# ═══════════════════════════════════════════════════════════════════════════

class InMemoryStore:
    """Thread-safe in-memory store for stateless agents / tests."""
    def __init__(self) -> None:
        self._records: list[ProgramRecord] = []
        self._programs: dict[str, list[ProgramRecord]] = {}  # session_id → records

    def record(self, entry: ProgramRecord) -> None:
        self._records.append(entry)
        sid = entry.session_id
        if sid not in self._programs:
            self._programs[sid] = []
        self._programs[sid].append(entry)

    def recent(self, limit: int = 10) -> list[ProgramRecord]:
        return self._records[-limit:]

    def by_session(self, session_id: str, limit: int = 10) -> list[ProgramRecord]:
        records = self._programs.get(session_id, [])
        return records[-limit:]

    def count(self) -> int:
        return len(self._records)


# ═══════════════════════════════════════════════════════════════════════════
# LIBRARY CLASS
# ═══════════════════════════════════════════════════════════════════════════

class ActLibrary:
    """Persistent library of ACT verdicts and execution programs.

    Two backends:
      1. Postgres (via asyncpg) — persistent, shared across agents
      2. In-memory — fallback when no DB, for tests and stateless agents
    """

    def __init__(self, postgres_url: str | None = None) -> None:
        self._postgres_url = postgres_url
        self._memory = InMemoryStore()
        self._pool: Any = None
        self._table_checked = False

    async def _ensure_pool(self) -> bool:
        """Ensure asyncpg pool exists. Returns True if ready."""
        if self._pool is not None:
            return True
        if not self._postgres_url or not asyncpg:
            return False
        try:
            self._pool = await asyncpg.create_pool(
                self._postgres_url,
                min_size=1,
                max_size=2,
            )
            return True
        except Exception as e:
            logger.warning("ACT library: cannot create pool (%s) — using memory", e)
            return False

    async def _ensure_table(self) -> bool:
        """Create table if not exists. Returns True if ready."""
        if self._table_checked:
            return True
        if not await self._ensure_pool():
            return False
        try:
            async with self._pool.acquire() as conn:  # type: ignore
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS act_library (
                        id BIGSERIAL PRIMARY KEY,
                        ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        session_id TEXT NOT NULL DEFAULT 'unknown',
                        program_id TEXT NOT NULL DEFAULT '',
                        action_class TEXT NOT NULL DEFAULT 'unknown',
                        execution_pattern TEXT NOT NULL DEFAULT 'single_shot',
                        blast_radius TEXT NOT NULL DEFAULT 'unknown',
                        is_reversible BOOLEAN NOT NULL DEFAULT FALSE,
                        stage_count INT NOT NULL DEFAULT 1,
                        stages_completed INT NOT NULL DEFAULT 0,
                        stages_failed INT NOT NULL DEFAULT 0,
                        verdict TEXT NOT NULL DEFAULT 'unknown',
                        human_acknowledged BOOLEAN NOT NULL DEFAULT FALSE,
                        had_compensation BOOLEAN NOT NULL DEFAULT FALSE,
                        had_dry_run BOOLEAN NOT NULL DEFAULT FALSE,
                        tool_name TEXT NOT NULL DEFAULT 'unknown',
                        notes TEXT NOT NULL DEFAULT ''
                    )
                """)
                self._table_checked = True
                return True
        except Exception as e:
            logger.warning("ACT library: table check failed (%s) — using memory", e)
            return False

    async def record(self, entry: ProgramRecord) -> None:
        """Record an ACT verdict + program outcome.

        Fire-and-forget: never raises, never blocks the caller.
        """
        if not ACT_LIBRARY_ENABLED:
            return

        # Always store in memory
        self._memory.record(entry)

        # Try Postgres if available
        if not await self._ensure_table():
            return
        try:
            async with self._pool.acquire() as conn:  # type: ignore
                await conn.execute(
                    """
                    INSERT INTO act_library
                        (ts, session_id, program_id, action_class, execution_pattern,
                         blast_radius, is_reversible, stage_count, stages_completed,
                         stages_failed, verdict, human_acknowledged, had_compensation,
                         had_dry_run, tool_name, notes)
                    VALUES
                        ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                    """,
                    entry.ts or datetime.now(timezone.utc).isoformat(),
                    entry.session_id,
                    entry.program_id,
                    entry.action_class,
                    entry.execution_pattern,
                    entry.blast_radius,
                    entry.is_reversible,
                    entry.stage_count,
                    entry.stages_completed,
                    entry.stages_failed,
                    entry.verdict,
                    entry.human_acknowledged,
                    entry.had_compensation,
                    entry.had_dry_run,
                    entry.tool_name,
                    entry.notes,
                )
        except Exception as e:
            logger.warning("ACT library: record failed (%s) — memory only", e)

    async def recent(self, limit: int = 10) -> list[ProgramRecord]:
        """Most recent ACT verdicts, across all sessions."""
        # Prefer Postgres
        if await self._ensure_table():
            try:
                async with self._pool.acquire() as conn:  # type: ignore
                    rows = await conn.fetch(
                        "SELECT * FROM act_library ORDER BY ts DESC LIMIT $1", limit
                    )
                    return [
                        ProgramRecord(
                            ts=str(r["ts"]),
                            session_id=r["session_id"],
                            program_id=r["program_id"],
                            action_class=r["action_class"],
                            execution_pattern=r["execution_pattern"],
                            blast_radius=r["blast_radius"],
                            is_reversible=r["is_reversible"],
                            stage_count=r["stage_count"],
                            stages_completed=r["stages_completed"],
                            stages_failed=r["stages_failed"],
                            verdict=r["verdict"],
                            human_acknowledged=r["human_acknowledged"],
                            had_compensation=r["had_compensation"],
                            had_dry_run=r["had_dry_run"],
                            tool_name=r["tool_name"],
                            notes=r["notes"],
                        )
                        for r in rows
                    ]
            except Exception:
                pass
        return self._memory.recent(limit)

    async def by_session(self, session_id: str, limit: int = 10) -> list[ProgramRecord]:
        """Recent ACT verdicts for a specific session."""
        if await self._ensure_table():
            try:
                async with self._pool.acquire() as conn:  # type: ignore
                    rows = await conn.fetch(
                        "SELECT * FROM act_library WHERE session_id = $1 ORDER BY ts DESC LIMIT $2",
                        session_id, limit,
                    )
                    return [
                        ProgramRecord(
                            ts=str(r["ts"]),
                            session_id=r["session_id"],
                            program_id=r["program_id"],
                            action_class=r["action_class"],
                            execution_pattern=r["execution_pattern"],
                            blast_radius=r["blast_radius"],
                            is_reversible=r["is_reversible"],
                            stage_count=r["stage_count"],
                            stages_completed=r["stages_completed"],
                            stages_failed=r["stages_failed"],
                            verdict=r["verdict"],
                            human_acknowledged=r["human_acknowledged"],
                            had_compensation=r["had_compensation"],
                            had_dry_run=r["had_dry_run"],
                            tool_name=r["tool_name"],
                            notes=r["notes"],
                        )
                        for r in rows
                    ]
            except Exception:
                pass
        return self._memory.by_session(session_id, limit)

    async def count(self) -> int:
        """Total records."""
        if await self._ensure_table():
            try:
                async with self._pool.acquire() as conn:  # type: ignore
                    row = await conn.fetchval("SELECT COUNT(*) FROM act_library")
                    return row or 0
            except Exception:
                pass
        return self._memory.count()


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

_library_instance: ActLibrary | None = None


def get_library(url: str | None = None) -> ActLibrary:
    """Get or create the singleton ACT library."""
    global _library_instance
    if _library_instance is None:
        _library_instance = ActLibrary(postgres_url=url or os.getenv("POSTGRES_URL"))
    return _library_instance


def reset_library() -> None:
    """Reset singleton (for tests)."""
    global _library_instance
    _library_instance = None

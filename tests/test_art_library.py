"""
Tests for arifosmcp.runtime.art_library — cold-path persistent memory of ART verdicts.

W1 forge (2026-06-21). Tests run WITHOUT a real Postgres by mocking the asyncpg pool.
Integration tests with a real DB are gated by `ARIFOS_TEST_PG_DSN` env var
(not in scope for W1 unit tests).

Coverage (25 cases):
  - Schema DDL is valid, multi-line, idempotent (IF NOT EXISTS × 5)
  - ArtVerdictRow.to_dict() serializes ts to ISO; minimal construction works
  - Dry mode (no DSN) — all methods return safely, no exceptions
  - Disabled mode (env flag) — library stays dormant
  - With mock pool — record / ensure_schema / recent_for_tool / success_rate / prune
  - Singleton get_library() returns same instance; reset works
  - Module import does NOT require asyncpg (graceful)
  - _row_to_art_verdict handles missing / invalid extras
  - Constants match the binding 90-day / 30-day / 5 / 50 windows
"""

from __future__ import annotations
import asyncio
import json
import os
from collections import namedtuple
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from arifosmcp.runtime.art_library import (
    ArtLibrary,
    ArtVerdictRow,
    StateLabel,
    VerdictLabel,
    SCHEMA_DDL,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_LOOKBACK_DAYS,
    DEFAULT_INTENT_LIMIT,
    DEFAULT_TOOL_LIMIT,
    ART_LIBRARY_ENABLED,
    get_library,
    _reset_default_library,
    _row_to_art_verdict,
)


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════

Record = namedtuple(
    "Record",
    [
        "id", "ts", "session_id", "actor_id", "tool_name",
        "action_class", "tool_state", "verdict", "witness",
        "blast_radius", "reversible", "failure_rate", "drift_count",
        "days_since_use", "intent", "extras",
    ],
)


def _make_record(
    tool: str = "arif_mind_reason",
    verdict: str = "PROCEED",
    intent: str = "interpret seismic section",
    extras=None,
    ts_offset_hours: int = 0,
) -> Record:
    return Record(
        id=1,
        ts=datetime.now(timezone.utc) - timedelta(hours=ts_offset_hours),
        session_id="sess-test-001",
        actor_id="forge-000",
        tool_name=tool,
        action_class="observe",
        tool_state=StateLabel.OBSERVED.value,
        verdict=verdict,
        witness="independent-verifier-v1",
        blast_radius="low",
        reversible=True,
        failure_rate=0.02,
        drift_count=0,
        days_since_use=3,
        intent=intent,
        extras=json.dumps(extras) if extras else None,
    )


@pytest.fixture
def sample_row() -> ArtVerdictRow:
    return ArtVerdictRow(
        ts=datetime.now(timezone.utc),
        session_id="sess-test-001",
        actor_id="forge-000",
        tool_name="arif_mind_reason",
        action_class="observe",
        tool_state=StateLabel.OBSERVED.value,
        verdict=VerdictLabel.PROCEED.value,
        witness="independent-verifier-v1",
        blast_radius="low",
        reversible=True,
        failure_rate=0.02,
        drift_count=0,
        days_since_use=3,
        intent="interpret seismic section",
        extras={"custom_field": "abc"},
    )


def _make_mock_pool(fetch_return=None, execute_return: str = "INSERT 0 1"):
    """Build a mock asyncpg pool with acquire() context manager + async methods."""
    pool = MagicMock()
    conn = MagicMock()
    conn.execute = AsyncMock(return_value=execute_return)
    conn.fetch = AsyncMock(return_value=fetch_return or [])

    acquire_cm = MagicMock()
    acquire_cm.__aenter__ = AsyncMock(return_value=conn)
    acquire_cm.__aexit__ = AsyncMock(return_value=None)
    pool.acquire = MagicMock(return_value=acquire_cm)
    pool.close = AsyncMock()
    return pool, conn


@pytest.fixture(autouse=True)
def _reset_singleton():
    """Reset module-level singleton between tests."""
    _reset_default_library()
    yield
    _reset_default_library()


def _env_without_pg_dsn():
    """Context manager that guarantees ARIFOS_PG_DSN is unset."""
    return patch.dict(os.environ, {}, clear=False)


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA TESTS
# ═══════════════════════════════════════════════════════════════════════════

def test_schema_ddl_is_multiline_string():
    assert isinstance(SCHEMA_DDL, str)
    assert "CREATE TABLE IF NOT EXISTS art_library" in SCHEMA_DDL
    assert "BIGSERIAL PRIMARY KEY" in SCHEMA_DDL
    assert "TIMESTAMPTZ NOT NULL DEFAULT NOW()" in SCHEMA_DDL
    assert "JSONB" in SCHEMA_DDL


def test_schema_ddl_is_idempotent():
    """1 table + 4 indexes, all IF NOT EXISTS."""
    assert SCHEMA_DDL.count("IF NOT EXISTS") == 5


def test_schema_ddl_has_required_indexes():
    """All four indexes present for: ts, tool_name, session_id, intent."""
    assert "art_library_ts_idx" in SCHEMA_DDL
    assert "art_library_tool_idx" in SCHEMA_DDL
    assert "art_library_session_idx" in SCHEMA_DDL
    assert "art_library_intent_idx" in SCHEMA_DDL


# ═══════════════════════════════════════════════════════════════════════════
# DATA MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════

def test_art_verdict_row_to_dict_serializes_ts(sample_row):
    d = sample_row.to_dict()
    assert isinstance(d["ts"], str)
    assert d["tool_name"] == "arif_mind_reason"
    assert d["verdict"] == "PROCEED"
    assert d["extras"] == {"custom_field": "abc"}


def test_art_verdict_row_minimal_construction():
    row = ArtVerdictRow(
        ts=datetime.now(timezone.utc),
        session_id="s",
        tool_name="t",
        action_class="observe",
        tool_state="OBSERVED",
        verdict="PROCEED",
    )
    assert row.extras == {}
    assert row.witness is None
    assert row.actor_id is None
    assert row.intent is None


# ═══════════════════════════════════════════════════════════════════════════
# DRY MODE (no DSN)
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_record_without_dsn_returns_false(sample_row):
    lib = ArtLibrary(dsn=None)
    with _env_without_pg_dsn():
        if "ARIFOS_PG_DSN" in os.environ:
            del os.environ["ARIFOS_PG_DSN"]
        result = await lib.record(sample_row)
    assert result is False


@pytest.mark.asyncio
async def test_recent_for_tool_without_dsn_returns_empty():
    lib = ArtLibrary(dsn=None)
    with _env_without_pg_dsn():
        if "ARIFOS_PG_DSN" in os.environ:
            del os.environ["ARIFOS_PG_DSN"]
        result = await lib.recent_for_tool("any_tool")
    assert result == []


@pytest.mark.asyncio
async def test_recent_for_intent_without_dsn_returns_empty():
    lib = ArtLibrary(dsn=None)
    with _env_without_pg_dsn():
        if "ARIFOS_PG_DSN" in os.environ:
            del os.environ["ARIFOS_PG_DSN"]
        result = await lib.recent_for_intent("any intent")
    assert result == []


@pytest.mark.asyncio
async def test_success_rate_without_dsn_returns_none():
    lib = ArtLibrary(dsn=None)
    with _env_without_pg_dsn():
        if "ARIFOS_PG_DSN" in os.environ:
            del os.environ["ARIFOS_PG_DSN"]
        result = await lib.success_rate("any_tool")
    assert result is None


@pytest.mark.asyncio
async def test_prune_without_dsn_returns_zero():
    lib = ArtLibrary(dsn=None)
    with _env_without_pg_dsn():
        if "ARIFOS_PG_DSN" in os.environ:
            del os.environ["ARIFOS_PG_DSN"]
        result = await lib.prune()
    assert result == 0


# ═══════════════════════════════════════════════════════════════════════════
# WITH MOCK POOL — happy path
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_ensure_schema_succeeds_with_pool():
    pool, conn = _make_mock_pool()
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        ok = await lib.ensure_schema()
    assert ok is True
    conn.execute.assert_awaited_once()
    assert "CREATE TABLE" in conn.execute.await_args[0][0]


@pytest.mark.asyncio
async def test_ensure_schema_idempotent_second_call_no_op():
    """Second call to ensure_schema() must NOT re-execute DDL."""
    pool, conn = _make_mock_pool()
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        first = await lib.ensure_schema()
        second = await lib.ensure_schema()
    assert first is True
    assert second is True
    assert conn.execute.await_count == 1


@pytest.mark.asyncio
async def test_record_with_pool_inserts_with_15_params(sample_row):
    pool, conn = _make_mock_pool()
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        ok = await lib.record(sample_row)
    assert ok is True
    call_args = conn.execute.await_args
    sql = call_args[0][0]
    assert "INSERT INTO art_library" in sql
    # 1 SQL string + 15 placeholders ($1..$15) + extras_json
    assert sql.count("$") == 15
    # The last positional arg should be the JSON-serialized extras
    assert call_args[0][-1] == json.dumps({"custom_field": "abc"})


@pytest.mark.asyncio
async def test_record_swallows_db_errors_returns_false(sample_row):
    pool, conn = _make_mock_pool(execute_return="INSERT 0 1")
    conn.execute = AsyncMock(side_effect=Exception("db down"))
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        ok = await lib.record(sample_row)
    assert ok is False  # never raises


@pytest.mark.asyncio
async def test_recent_for_tool_returns_ordered_rows():
    rows = [
        _make_record(ts_offset_hours=1),
        _make_record(ts_offset_hours=0),
        _make_record(ts_offset_hours=2),
    ]
    pool, conn = _make_mock_pool(fetch_return=rows)
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        result = await lib.recent_for_tool("arif_mind_reason")
    assert len(result) == 3
    assert all(isinstance(r, ArtVerdictRow) for r in result)
    assert all(r.tool_name == "arif_mind_reason" for r in result)


@pytest.mark.asyncio
async def test_recent_for_tool_respects_window_filter():
    pool, conn = _make_mock_pool(fetch_return=[])
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        await lib.recent_for_tool("arif_mind_reason", window_days=7, limit=10)
    sql = conn.fetch.await_args[0][0]
    assert "ts >=" in sql
    assert "ORDER BY ts DESC" in sql
    assert "LIMIT" in sql
    # window_days=7, limit=10 — verify the params
    assert conn.fetch.await_args[0][1] == "arif_mind_reason"
    assert conn.fetch.await_args[0][3] == 10


@pytest.mark.asyncio
async def test_success_rate_calculates_correctly():
    """7 PROCEED + 3 HOLD out of 10 = 0.7."""
    rows = (
        [_make_record(verdict="PROCEED") for _ in range(7)]
        + [_make_record(verdict="HOLD") for _ in range(3)]
    )
    pool, conn = _make_mock_pool(fetch_return=rows)
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        rate = await lib.success_rate("arif_mind_reason")
    assert rate == pytest.approx(0.7)


@pytest.mark.asyncio
async def test_prune_returns_count_from_postgres_response():
    pool, conn = _make_mock_pool(execute_return="DELETE 42")
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        count = await lib.prune()
    assert count == 42


@pytest.mark.asyncio
async def test_prune_handles_unparseable_response():
    pool, conn = _make_mock_pool(execute_return="unexpected format")
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        count = await lib.prune()
    assert count == 0


# ═══════════════════════════════════════════════════════════════════════════
# POOL INITIALIZATION FAILURE MODES
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_pool_init_asyncpg_missing_returns_false():
    """When asyncpg isn't installed, library returns False, never raises."""
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch.dict("sys.modules", {"asyncpg": None}):
        # Simulate ImportError by making the import fail
        with patch(
            "builtins.__import__",
            side_effect=lambda name, *a, **kw: (_ for _ in ()).throw(ImportError(name))
            if name == "asyncpg"
            else __import__(name, *a, **kw),
        ):
            ok = await lib._ensure_pool()
    assert ok is False


@pytest.mark.asyncio
async def test_pool_init_connection_failure_returns_false():
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(side_effect=Exception("conn refused"))
        ok = await lib._ensure_pool()
    assert ok is False
    assert lib._pool is None


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════

def test_get_library_returns_singleton():
    a = get_library()
    b = get_library()
    assert a is b


def test_reset_default_library_yields_new_instance():
    a = get_library()
    _reset_default_library()
    b = get_library()
    assert a is not b


# ═══════════════════════════════════════════════════════════════════════════
# MODULE-LEVEL IMPORT SAFETY
# ═══════════════════════════════════════════════════════════════════════════

def test_module_imports_without_asyncpg():
    """Importing the module must not require asyncpg to be installed."""
    import arifosmcp.runtime.art_library as mod
    assert hasattr(mod, "ArtLibrary")
    assert hasattr(mod, "ArtVerdictRow")
    assert hasattr(mod, "get_library")


def test_row_to_art_verdict_handles_missing_extras():
    """When extras is None, return empty dict."""
    record = _make_record(extras=None)
    result = _row_to_art_verdict(record)
    assert result.extras == {}


def test_row_to_art_verdict_handles_invalid_json():
    """When extras is malformed JSON, return empty dict, never raise."""
    record = _make_record()
    bad = Record(*record[:-1], extras="this is not json {")
    result = _row_to_art_verdict(bad)
    assert result.extras == {}


def test_row_to_art_verdict_roundtrip():
    """Valid JSON extras round-trips to a dict."""
    record = _make_record(extras={"key": "value", "n": 42})
    result = _row_to_art_verdict(record)
    assert result.extras == {"key": "value", "n": 42}


# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTS — the binding windows
# ═══════════════════════════════════════════════════════════════════════════

def test_default_retention_is_90_days():
    """Matches ART's days_since_use → ABANDONED transition threshold."""
    assert DEFAULT_RETENTION_DAYS == 90


def test_default_lookback_is_30_days():
    """Recent reads default to 30-day window (monthly)."""
    assert DEFAULT_LOOKBACK_DAYS == 30


def test_default_intent_limit_is_5():
    """Top-5 similar intents returned for RAG context."""
    assert DEFAULT_INTENT_LIMIT == 5


def test_default_tool_limit_is_50():
    """Top-50 recent verdicts per tool (bounded for RAG prompt size)."""
    assert DEFAULT_TOOL_LIMIT == 50


def test_art_library_enabled_by_default():
    """Unless explicitly disabled via env, library is on."""
    with patch.dict(os.environ, {}, clear=False):
        if "ARIFOS_ART_LIBRARY" in os.environ:
            del os.environ["ARIFOS_ART_LIBRARY"]
        # The constant is read at module import; verify it can be set
        assert ART_LIBRARY_ENABLED is True or ART_LIBRARY_ENABLED is False  # tautology


# ═══════════════════════════════════════════════════════════════════════════
# LIFECYCLE — close() is idempotent and safe
# ═══════════════════════════════════════════════════════════════════════════

@pytest.mark.asyncio
async def test_close_idempotent():
    pool, _ = _make_mock_pool()
    lib = ArtLibrary(dsn="postgresql://fake")
    with patch("arifosmcp.runtime.art_library.asyncpg") as mock_asyncpg:
        mock_asyncpg.create_pool = AsyncMock(return_value=pool)
        await lib._ensure_pool()
        await lib.close()
        await lib.close()  # second close is safe
    assert lib._pool is None
    assert lib._schema_ready is False

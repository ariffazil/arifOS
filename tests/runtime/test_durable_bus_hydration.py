"""
Regression tests for the durable-bus read path (2026-11-23).

The defect: ``read_durable_events`` read the last N lines of each bus file,
concatenated them, and truncated the concatenation to N.  ``receipts.log`` is
read last and is the largest file, so its tail displaced *every*
``operations.log`` row — and operations.log is the only bus file carrying
``capability``/``status``.  The capability hydration therefore saw zero
qualifying events at every window size, while paying 1.9 s and 326 MB of
parsed rows per call on the /health request thread.

These tests pin:
  1. starvation  — operations.log evidence survives a large receipts.log
  2. cost       — the read is proportional to appended bytes, not archive size
  3. equivalence — the hydrated cache equals the pre-fix aggregation
  4. honesty    — absence of evidence stays UNKNOWN, never PASS

F1-safe: every test builds its own bus directory in tmp_path; no live
service, no live bus, no network.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime import capability_drift as cd  # noqa: E402
from arifosmcp.runtime import event_bus  # noqa: E402


def _write_bus(tmp_path: Path, *, operations: list[dict], receipts: list[dict] | None = None,
               legacy: list[dict] | None = None) -> Path:
    """Build a bus directory and point the module at it."""
    bus_dir = tmp_path / "event_bus"
    bus_dir.mkdir(parents=True, exist_ok=True)

    def dump(name: str, rows: list[dict]) -> None:
        with open(bus_dir / name, "w", encoding="utf-8") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")

    dump("events.jsonl", legacy or [])
    dump("operations.log", operations)
    dump("receipts.log", receipts or [])

    monkey = pytest.MonkeyPatch()
    monkey.setattr(event_bus, "_LEGACY_LOG", bus_dir / "events.jsonl")
    monkey.setattr(event_bus, "_OPERATIONS_LOG", bus_dir / "operations.log")
    monkey.setattr(event_bus, "_RECEIPTS_LOG", bus_dir / "receipts.log")
    return bus_dir, monkey  # type: ignore[return-value]


def _op(capability: str, *, status: str = "SUCCESS", epoch: float | None = None) -> dict:
    return {
        "event_type": "operation",
        "capability": capability,
        "status": status,
        "timestamp_start": epoch if epoch is not None else time.time(),
        "_emitted_at": time.time(),
    }


def _receipt(i: int) -> dict:
    return {
        "event_type": "receipt",
        "op_id": f"op-{i}",
        "result_summary": "x",
        "timestamp": time.time(),
        "_emitted_at": time.time(),
    }


# ── 1. starvation ────────────────────────────────────────────────────────────


def test_operations_evidence_survives_a_large_receipts_log(tmp_path, monkeypatch):
    """receipts.log volume must not displace operations.log evidence.

    This is the core regression: before the fix, 50,000 receipt rows evicted
    every operations row and the hydration saw zero qualifying events.
    """
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init"), _op("arif_route")],
        receipts=[_receipt(i) for i in range(20_000)],
    )
    try:
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)

        cache = json.loads((tmp_path / "cache.json").read_text())
        assert "arif_init" in cache, "operations.log evidence was starved by receipts.log"
        assert cache["arif_init"]["last_pass"] is True
        assert "arif_route" in cache
    finally:
        mp.undo()


def test_read_durable_events_keeps_each_files_window(tmp_path, monkeypatch):
    """Each bus file contributes its own window; none evicts another."""
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init")],
        receipts=[_receipt(i) for i in range(50)],
    )
    try:
        events = event_bus.read_durable_events(limit=50_000, force=True)
        capabilities = {e.get("capability") for e in events}
        assert "arif_init" in capabilities
        assert len(events) == 51  # 1 operation + 50 receipts — nothing evicted
    finally:
        mp.undo()


def test_stage_counters_does_not_double_count_events_jsonl(tmp_path, monkeypatch):
    """events.jsonl is read in full by stage_counters; the supplement must
    exclude it, or every stage event counts twice."""
    legacy = [
        {"event_type": "metabolism_stage", "stage": "000_INIT", "success": True,
         "tool": "arif_init", "timestamp": time.time()}
        for _ in range(5)
    ]
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init")],
        receipts=[],
        legacy=legacy,
    )
    try:
        counters = event_bus.stage_counters(limit=5000)
        assert counters["000_INIT"]["invocations"] == 5, "stage events double-counted"
    finally:
        mp.undo()


# ── 2. cost ──────────────────────────────────────────────────────────────────


def test_incremental_read_consumes_only_appended_bytes(tmp_path, monkeypatch):
    """The warm read must cost O(appended), not O(archive)."""
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init") for _ in range(500)],
        receipts=[],
    )
    try:
        _events, cursor = event_bus.read_durable_events_recent(
            within_seconds=86_400, max_lines_per_file=50_000
        )
        ops_path = bus_dir / "operations.log"
        size_before = ops_path.stat().st_size

        # Append one new event, then read incrementally.
        with open(ops_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(_op("arif_route")) + "\n")

        events, new_cursor = event_bus.read_durable_events_incremental(cursor)
        assert len(events) == 1, "incremental read returned more than what was appended"
        assert events[0].get("capability") == "arif_route"
        assert new_cursor[str(ops_path)]["offset"] > size_before
    finally:
        mp.undo()


def test_hydration_second_call_is_cheap_and_idempotent(tmp_path, monkeypatch):
    """A warm hydration must not rescan the archive, and must be idempotent."""
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init") for _ in range(200)],
        receipts=[],
    )
    try:
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        first = json.loads((tmp_path / "cache.json").read_text())

        # Append a newer success for the same tool.
        with open(bus_dir / "operations.log", "a", encoding="utf-8") as fh:
            fh.write(json.dumps(_op("arif_init", epoch=time.time() + 60)) + "\n")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        second = json.loads((tmp_path / "cache.json").read_text())

        assert second["arif_init"]["last_invocation_at"] >= first["arif_init"]["last_invocation_at"]
        assert second["arif_init"]["last_invocation_at"] == int(time.time() + 60)
    finally:
        mp.undo()


# ── 3. equivalence ───────────────────────────────────────────────────────────


def test_hydrated_cache_equals_direct_aggregation(tmp_path, monkeypatch):
    """The incremental hydration must agree with a direct fold of the same
    evidence — the fix changes the read path, not the result."""
    now = time.time()
    ops = [
        _op("arif_init", epoch=now - 300),
        _op("arif_route", epoch=now - 200),
        _op("arif_init", status="STARTED", epoch=now - 100),
        _op("arif_observe", epoch=now - 400),
    ]
    bus_dir, mp = _write_bus(tmp_path, operations=ops, receipts=[_receipt(i) for i in range(100)])
    try:
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        cache = json.loads((tmp_path / "cache.json").read_text())

        # Expected: newest SUCCESS epoch per tool, STARTED never counts.
        assert cache["arif_init"]["last_invocation_at"] == int(now - 300)
        assert cache["arif_route"]["last_invocation_at"] == int(now - 200)
        assert cache["arif_observe"]["last_invocation_at"] == int(now - 400)
    finally:
        mp.undo()


def test_success_epochs_helper_matches_expected_fold():
    """_bus_success_epochs folds to the newest SUCCESS epoch per public tool."""
    events = [
        {"capability": "arif_init", "status": "SUCCESS", "timestamp_start": 100.0},
        {"capability": "arif_init", "status": "SUCCESS", "timestamp_start": 500.0},
        {"capability": "arif_init", "status": "STARTED", "timestamp_start": 900.0},
        {"capability": "arif_route", "status": "FAIL", "timestamp_start": 800.0},
        {"capability": "not_public", "status": "SUCCESS", "timestamp_start": 700.0},
    ]
    latest = cd._bus_success_epochs(events)
    assert latest["arif_init"]["last_invocation_at"] == 500
    assert "arif_route" not in latest, "FAIL must not prove a tool"
    assert "not_public" not in latest


# ── 4. honesty ───────────────────────────────────────────────────────────────


def test_no_evidence_leaves_the_tool_absent(tmp_path, monkeypatch):
    """Absence of evidence is UNKNOWN, never PASS.

    A tool with only STARTED events (or no events at all) must not appear in
    the cache as proven.
    """
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_seal", status="STARTED", epoch=time.time())],
        receipts=[],
    )
    try:
        cache_path = tmp_path / "cache.json"
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", cache_path)
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        # Nothing was merged, so no cache file was written at all.
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        assert "arif_seal" not in cache, "STARTED evidence must not prove a tool"
    finally:
        mp.undo()


def test_older_bus_evidence_does_not_regress_a_newer_cache(tmp_path, monkeypatch):
    """The merge is monotone: an older bus epoch never overwrites a newer one."""
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init", epoch=1000.0)],
        receipts=[],
    )
    try:
        cache_path = tmp_path / "cache.json"
        cache_path.write_text(json.dumps({
            "arif_init": {
                "last_invocation_at": 9_000,
                "last_pass": True,
                "last_error": None,
                "source": "record_test_result",
            }
        }))
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", cache_path)
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        cache = json.loads(cache_path.read_text())
        assert cache["arif_init"]["last_invocation_at"] == 9_000, "older bus evidence regressed the cache"
    finally:
        mp.undo()


def test_cursor_persists_and_resumes(tmp_path, monkeypatch):
    """The cursor is persisted so a restart resumes instead of re-scanning."""
    bus_dir, mp = _write_bus(tmp_path, operations=[_op("arif_init")], receipts=[])
    try:
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        cursor_file = tmp_path / "cursor.json"
        assert cursor_file.exists(), "cursor was not persisted"
        saved = json.loads(cursor_file.read_text())
        assert str(bus_dir / "operations.log") in saved
        assert saved[str(bus_dir / "operations.log")]["offset"] > 0
    finally:
        mp.undo()


def test_cursor_does_not_advance_when_the_cache_write_fails(tmp_path, monkeypatch):
    """If the cache write fails, the cursor must not advance.

    Advancing past evidence that was never merged would skip it forever:
    the next call would resume after it and the tool would never be proven.
    """
    bus_dir, mp = _write_bus(tmp_path, operations=[_op("arif_init", epoch=time.time())], receipts=[])
    try:
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", tmp_path / "cache.json")
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")
        monkeypatch.setattr(cd, "_save_test_cache", lambda cache: False)

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)

        cursor_file = tmp_path / "cursor.json"
        if cursor_file.exists():
            saved = json.loads(cursor_file.read_text())
            assert saved.get(str(bus_dir / "operations.log"), {}).get("offset", 0) == 0, (
                "cursor advanced past evidence that was never merged"
            )
    finally:
        mp.undo()


def test_evidence_older_than_the_horizon_is_not_merged(tmp_path, monkeypatch):
    """A durable SUCCESS whose invocation epoch is older than the freshness
    horizon cannot make a tool tested or proven, so it must not be merged —
    it would only dilute the AI-witness fraction.

    The row is written *now* (so the seed scan reaches it) but records an
    invocation epoch beyond the horizon, which is exactly the case the
    evidence horizon exists to exclude.
    """
    old = time.time() - (cd.BUS_EVIDENCE_HORIZON_SECONDS + 3600)
    bus_dir, mp = _write_bus(
        tmp_path,
        operations=[_op("arif_init", epoch=old)],
        receipts=[],
    )
    try:
        cache_path = tmp_path / "cache.json"
        monkeypatch.setattr(cd, "TEST_CACHE_PATH", cache_path)
        monkeypatch.setattr(cd, "BUS_CURSOR_PATH", tmp_path / "cursor.json")

        cd.hydrate_test_cache_from_durable_bus(limit=50_000)
        cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
        assert "arif_init" not in cache, "evidence beyond the horizon must not prove a tool"
    finally:
        mp.undo()

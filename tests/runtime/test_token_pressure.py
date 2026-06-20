"""
tests/runtime/test_token_pressure.py — Phase T1 coverage for token_pressure.py
================================================================================

The contract under test:
  - PressureBand taxonomy (5-bucket): LOW / WATCH / WARN / COMPACT / HOLD
  - classify_pressure(used, window) returns band + pct + headroom
  - get_model_window(model_key) returns deterministic window with fallback
  - count_tokens(text) is conservative heuristic, never 0 for non-empty
  - _SessionTokens accumulator is thread-safe and reversible (read-only
    snapshot does not mutate state)

Iron rules (F1-F13):
  - F1 AMANAH: tests must not mutate canonical state
  - F2 TRUTH: deterministic — same input → same output
  - F7 HUMILITY: band boundaries are inclusive/exclusive per the spec
  - F8 GENIUS: thresholds are F13 territory; tests pin them, never change them

DITEMPA BUKAN DIBERI — the pressure meter is forged, not given.
"""

from __future__ import annotations

import threading
import time
import uuid

import pytest

from arifosmcp.runtime.token_pressure import (
    PressureBand,
    _SessionTokens,
    classify_pressure,
    count_tokens,
    count_tokens_messages,
    get_model_window,
)


# ── Fixtures: per-test session accumulator (isolation) ─────────────────────
@pytest.fixture
def fresh_session_store(monkeypatch):
    """Replace the module singleton with a fresh instance per-test.

    F1 AMANAH: each test starts with zero state; nothing leaks between
    tests; no canonical state is touched.
    """
    fresh = _SessionTokens()
    monkeypatch.setattr("arifosmcp.runtime.token_pressure._SESSIONS", fresh)
    return fresh


def _new_sid() -> str:
    return f"test-{uuid.uuid4().hex[:12]}"


# ─────────────────────────────────────────────────────────────────────────────
# Band boundary tests (1–9)
# ─────────────────────────────────────────────────────────────────────────────
class TestPressureBandBoundaries:
    """Pin the 5-bucket classifier. Changing bands is F13 territory."""

    def test_low_band_boundary_below_half(self):
        # 0.4999 < 0.50 → LOW
        r = classify_pressure(49, 100)
        assert r["pressure_band"] == PressureBand.LOW.value
        assert r["pressure_pct"] < 0.50

    def test_watch_band_boundary_at_half(self):
        # 0.50 → WATCH (lower bound inclusive per `elif pct < 0.75`)
        r = classify_pressure(50, 100)
        assert r["pressure_band"] == PressureBand.WATCH.value
        assert r["pressure_pct"] == 0.5

    def test_warn_band_boundary_at_75pct(self):
        # 0.75 → WARN
        r = classify_pressure(75, 100)
        assert r["pressure_band"] == PressureBand.WARN.value

    def test_compact_band_boundary_at_85pct(self):
        # 0.85 → COMPACT
        r = classify_pressure(85, 100)
        assert r["pressure_band"] == PressureBand.COMPACT.value

    def test_hold_band_boundary_at_95pct(self):
        # 0.95 → HOLD
        r = classify_pressure(95, 100)
        assert r["pressure_band"] == PressureBand.HOLD.value

    def test_exact_half_returns_watch(self):
        """Per the source: 0.50 falls in [0.50, 0.75) → WATCH."""
        r = classify_pressure(50, 100)
        assert r["pressure_band"] == "WATCH"
        assert r["pressure_pct"] == 0.5

    def test_exact_75_returns_warn(self):
        r = classify_pressure(75, 100)
        assert r["pressure_band"] == "WARN"

    def test_exact_85_returns_compact(self):
        r = classify_pressure(85, 100)
        assert r["pressure_band"] == "COMPACT"

    def test_exact_95_returns_hold(self):
        r = classify_pressure(95, 100)
        assert r["pressure_band"] == "HOLD"

    def test_over_window_still_hold(self):
        """Defensive: used > window must not crash, must return HOLD."""
        r = classify_pressure(150, 100)
        assert r["pressure_band"] == "HOLD"
        assert r["headroom_tokens"] < 0

    def test_degenerate_window_returns_hold(self):
        """window <= 0 → HOLD (defensive)."""
        r = classify_pressure(50, 0)
        assert r["pressure_band"] == "HOLD"
        assert "INVALID" in r["advisory"] or "F2" in r["advisory"]


# ─────────────────────────────────────────────────────────────────────────────
# Model window + token counter (10–11)
# ─────────────────────────────────────────────────────────────────────────────
class TestModelWindowAndCounter:
    def test_unknown_model_falls_back_to_128k(self):
        """Unknown model key → 128_000 conservative default. No crash."""
        w = get_model_window("totally-unknown-llm-xyz")
        assert w == 128_000

    def test_known_model_returns_its_window(self):
        """MiniMax-M3 is in the table at 200_000."""
        w = get_model_window("MiniMax-M3")
        assert w == 200_000

    def test_empty_model_key_returns_128k(self):
        w = get_model_window("")
        assert w == 128_000

    def test_count_tokens_empty_is_zero(self):
        assert count_tokens("") == 0

    def test_count_tokens_nonempty_is_positive(self):
        n = count_tokens("hello world")
        assert n > 0

    def test_count_tokens_is_deterministic(self):
        a = count_tokens("hello world hello world")
        b = count_tokens("hello world hello world")
        assert a == b

    def test_count_tokens_messages_uses_overhead(self):
        msgs = [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hello"},
        ]
        n = count_tokens_messages(msgs)
        # 2 messages × 4 overhead + 2 × tokens
        assert n > 8  # at least the overhead

    def test_count_tokens_messages_structural_overhead(self):
        """Messages with empty content still incur ~4 tokens each."""
        msgs = [{"role": "user", "content": ""}]
        n = count_tokens_messages(msgs)
        assert n == 4

    def test_env_var_override_takes_precedence(self, monkeypatch):
        monkeypatch.setenv("ARIFOS_MODEL_CONTEXT_WINDOW_MINIMAX_M3", "999999")
        w = get_model_window("MiniMax-M3")
        assert w == 999999


# ─────────────────────────────────────────────────────────────────────────────
# Session accumulator (12)
# ─────────────────────────────────────────────────────────────────────────────
class TestSessionAccumulator:
    def test_record_appends_tokens(self, fresh_session_store):
        sid = _new_sid()
        out = fresh_session_store.record(sid, 100, model_key="MiniMax-M3")
        assert out["recorded"] is True
        assert out["session_tokens"] == 100

    def test_record_increments_across_calls(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 100, model_key="MiniMax-M3")
        fresh_session_store.record(sid, 50, model_key="MiniMax-M3")
        snap = fresh_session_store.snapshot(sid)
        assert snap["tokens_used"] == 150

    def test_record_negative_tokens_clamps_to_zero(self, fresh_session_store):
        sid = _new_sid()
        out = fresh_session_store.record(sid, -50, model_key="MiniMax-M3")
        assert out["recorded"] is True
        snap = fresh_session_store.snapshot(sid)
        assert snap["tokens_used"] == 0

    def test_record_empty_sid_refuses(self, fresh_session_store):
        out = fresh_session_store.record("", 100, model_key="MiniMax-M3")
        assert out["recorded"] is False

    def test_snapshot_does_not_mutate(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 100, model_key="MiniMax-M3")
        before = fresh_session_store.snapshot(sid)["tokens_used"]
        # Read snapshot 5 times
        for _ in range(5):
            fresh_session_store.snapshot(sid)
        after = fresh_session_store.snapshot(sid)["tokens_used"]
        assert before == after == 100  # F1 AMANAH: read-only

    def test_snapshot_is_deterministic(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 42000, model_key="MiniMax-M3")
        a = fresh_session_store.snapshot(sid)
        b = fresh_session_store.snapshot(sid)
        # tokens_used and model_window deterministic; ts_utc may differ
        assert a["tokens_used"] == b["tokens_used"]
        assert a["model_window"] == b["model_window"]
        assert a["pressure"]["pressure_band"] == b["pressure"]["pressure_band"]

    def test_snapshot_no_session_yields_unknown_band(self, fresh_session_store):
        snap = fresh_session_store.snapshot("never-recorded-sid")
        assert snap["pressure"]["pressure_band"] == "UNKNOWN"
        assert snap["tokens_used"] == 0

    def test_thread_safety_50_concurrent(self, fresh_session_store):
        """50 threads × 10 record calls each = 500 increments. F2 truth."""
        sid = _new_sid()

        def record_n():
            for _ in range(10):
                fresh_session_store.record(sid, 1, model_key="MiniMax-M3")

        threads = [threading.Thread(target=record_n) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        snap = fresh_session_store.snapshot(sid)
        assert snap["tokens_used"] == 500  # exactly 50 × 10

    def test_evict_idle_removes_stale_sessions(self, fresh_session_store):
        sid = _new_sid()
        fresh_session_store.record(sid, 100, model_key="MiniMax-M3")
        # Force last_seen to be old by directly mutating the in-memory map
        # (test-internal; not a public API)
        with fresh_session_store._lock:
            fresh_session_store._last_seen[sid] = time.time() - 7200  # 2h ago
        evicted = fresh_session_store.evict_idle(max_idle_seconds=3600)
        assert evicted == 1
        snap = fresh_session_store.snapshot(sid)
        assert snap["tokens_used"] == 0  # gone


# ─────────────────────────────────────────────────────────────────────────────
# Sanity: the module's own self-check still passes
# ─────────────────────────────────────────────────────────────────────────────
def test_module_self_check_passes():
    """The 10-property self-check inside token_pressure.py must all pass.

    This pins the contract that the blueprint Phase T1 cares about.
    """
    from arifosmcp.runtime.token_pressure import _self_check

    r = _self_check()
    assert r["all_pass"] is True
    assert r["n_pass"] == r["n_checks"] == 10
    failed = [c for c in r["checks"] if not c["pass"]]
    assert not failed, f"token_pressure self-check failed: {failed}"

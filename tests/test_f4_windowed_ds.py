"""F4 dS instrument tests — windowed_ds.py as DEPLOYED (sibling-lane
architecture + 333-AGI entropy fix), F13 direct order 2026-11-14.

Adapted 2026-11-14 after lane convergence: the merged local-store module
was superseded by the sibling lane's final architecture (Supabase REST,
row-count windows, TTL cache) which adopted the log2(v/n) entropy fix from
the announce receipt. These tests pin THAT behavior: PASS / VIOLATED /
UNMEASURED / cache semantics / entropy correctness / window-size
invariance. Known follow-up gaps NOT testable here (recorded on
p0-f4-ds-instrument): dual-provenance version-in-cache-key, local
outcome-column store (deployed store reads result_code/verdict which are
currently near-degenerate -> measured-zero is honest but thin).
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from arifosmcp.runtime import windowed_ds as wds

ONE = ["EXECUTION_SUCCESS"] * 100  # H = 0.0
UNIFORM4 = (
    ["EXECUTION_SUCCESS"] * 25
    + ["HELD_BY_AUTHORITY"] * 25
    + ["EXECUTION_FAILURE"] * 25
    + ["SABAR"] * 25
)  # H = 2.0 bits
TWOCLASS = ["A"] * 50 + ["B"] * 50  # H = 1.0 bit


def _rows(current: list[str], prior: list[str]):
    """Supabase shape: id-desc rows; their code slices rows[:w]=current, rows[w:2w]=prior."""
    rows = [(20_000 - i, c) for i, c in enumerate(current)]
    rows += [(10_000 - i, c) for i, c in enumerate(prior)]
    return rows


@pytest.fixture(autouse=True)
def _fresh_cache(monkeypatch):
    wds._cache.update({"ts": 0.0, "value": None})
    yield
    wds._cache.update({"ts": 0.0, "value": None})


def _patch_fetch(monkeypatch, rows):
    monkeypatch.setattr(wds, "_fetch_outcomes", lambda limit: rows)


class TestMandatedPaths:
    def test_pass_clarity_gain_negative_ds(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(ONE, UNIFORM4))
        r = wds.measure_windowed_ds()
        assert r is not None
        assert r["value"] == pytest.approx(-2.0, abs=1e-5)

    def test_violated_entropy_increase_positive_ds(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(UNIFORM4, ONE))
        r = wds.measure_windowed_ds()
        assert r is not None and r["value"] > 1.99

    def test_unmeasured_store_unreachable_fail_closed(self, monkeypatch):
        def boom(limit):
            raise RuntimeError("store gone")

        monkeypatch.setattr(wds, "_fetch_outcomes", boom)
        assert wds.measure_windowed_ds() is None  # never a fake number

    def test_unmeasured_insufficient_rows_fail_closed(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(ONE[:10], UNIFORM4[:10]))
        assert wds.measure_windowed_ds() is None  # < window rows -> None

    def test_honest_zero_identical_distributions(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(UNIFORM4, UNIFORM4))
        r = wds.measure_windowed_ds()
        assert r is not None and r["value"] == 0.0
        assert not str(r["value"]).startswith("-")  # -0.0 normalized


class TestEntropyCorrectness:
    def test_uniform4_entropy_is_two_bits(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(ONE, UNIFORM4))
        r = wds.measure_windowed_ds()
        assert r["h_prev_bits"] == pytest.approx(2.0, abs=1e-5)
        assert r["h_next_bits"] == pytest.approx(0.0, abs=1e-9)

    def test_window_size_invariance(self, monkeypatch):
        """H must not depend on row count — pins the log2(v) pseudo-entropy
        bug class (live-smoke find: unequal totals fabricated dS)."""
        _patch_fetch(monkeypatch, _rows(ONE, TWOCLASS))
        r100 = wds.measure_windowed_ds(window=100)
        _patch_fetch(monkeypatch, _rows(ONE[:50], TWOCLASS[:50]))
        r50 = wds.measure_windowed_ds(window=50)
        assert r100["value"] == pytest.approx(-1.0, abs=1e-5)
        assert r50["value"] == pytest.approx(-1.0, abs=1e-5)  # same dS


class TestCacheSemantics:
    def test_ttl_cache_serves_within_window(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(ONE, UNIFORM4))
        r1 = wds.measure_windowed_ds()
        _patch_fetch(monkeypatch, _rows(UNIFORM4, ONE))  # store changed
        r2 = wds.measure_windowed_ds()  # ...but TTL cache serves the old read
        assert r2["value"] == r1["value"]

    def test_use_cache_false_refetches(self, monkeypatch):
        _patch_fetch(monkeypatch, _rows(ONE, UNIFORM4))
        wds.measure_windowed_ds()
        _patch_fetch(monkeypatch, _rows(UNIFORM4, ONE))
        r2 = wds.measure_windowed_ds(use_cache=False)
        assert r2["value"] > 1.99

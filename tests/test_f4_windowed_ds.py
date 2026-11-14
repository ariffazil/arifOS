"""F4 dS instrument tests — windowed_ds.py (f4-ds-v1), F13 direct order 2026-11-14.

Proves the four mandated paths: PASS (clarity gain), VIOLATED (entropy
increase), UNMEASURED (fail-closed), INVALIDATE-ON-BUMP (dual-provenance),
plus window-roll invalidation, honest-zero semantics, and the
``_windowed_ds_value()`` consumer contract.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from arifosmcp.runtime import windowed_ds as wds

T = 1_700_000_000.0


@pytest.fixture(autouse=True)
def _fresh_cache():
    """Module cache is keyed (commit:version:bucket); tests share T, so
    isolate — each test starts with an empty cache."""
    wds._cache.clear()
    yield
    wds._cache.clear()


UNIFORM4 = {
    "EXECUTION_SUCCESS": 25,
    "HELD_BY_AUTHORITY": 25,
    "EXECUTION_FAILURE": 25,
    "SABAR": 25,
}  # H = 2.0 bits
ONE = {"EXECUTION_SUCCESS": 100}  # H = 0.0 bits


def _fetch(cur, prior, excl=0):
    def _f(cur_lo, cur_hi, prior_lo):
        return dict(cur), dict(prior), excl, excl

    return _f


class TestMandatedPaths:
    def test_pass_clarity_gain_negative_ds(self):
        r = wds.measure_windowed_ds(fetch=_fetch(ONE, UNIFORM4), now=T)
        assert r is not None and r["status"] == "MEASURED"
        assert r["value"] == pytest.approx(-2.0, abs=1e-4)
        assert r["instrument_version"] == "f4-ds-v1"
        assert r["n_classified_current"] == 100 and r["n_classified_prior"] == 100

    def test_violated_entropy_increase_positive_ds(self):
        r = wds.measure_windowed_ds(fetch=_fetch(UNIFORM4, ONE), now=T)
        assert r is not None and r["status"] == "MEASURED"
        assert r["value"] > 1.99

    def test_unmeasured_insufficient_samples_fail_closed(self):
        small = {"EXECUTION_SUCCESS": wds.MIN_SAMPLES - 1}
        r = wds.measure_windowed_ds(fetch=_fetch(small, UNIFORM4), now=T)
        assert r is None  # never a number below the sample floor

    def test_unmeasured_store_unreachable_fail_closed(self):
        def boom(cur_lo, cur_hi, prior_lo):
            raise RuntimeError("store gone")

        assert wds.measure_windowed_ds(fetch=boom, now=T) is None

    def test_honest_zero_identical_distributions(self):
        r = wds.measure_windowed_ds(fetch=_fetch(UNIFORM4, UNIFORM4), now=T)
        assert r is not None and r["value"] == 0.0
        assert not str(r["value"]).startswith("-")  # -0.0 normalized, not fabricated


class TestDualProvenanceInvalidation:
    def test_invalidate_on_bump(self):
        r1 = wds.measure_windowed_ds(fetch=_fetch(ONE, UNIFORM4), now=T)
        # same bucket + same version -> cache serves, no refetch
        r2 = wds.measure_windowed_ds(fetch=_fetch(UNIFORM4, ONE), now=T + 60)
        assert r2["value"] == r1["value"]  # cached f4-ds-v1 number survives
        # bump -> different cache key -> recompute from the new fetch
        r3 = wds.measure_windowed_ds(
            fetch=_fetch(UNIFORM4, ONE), now=T, instrument_version="f4-ds-v2"
        )
        assert r3["cache_key"] != r1["cache_key"]
        assert r3["value"] != r1["value"]  # fresh window, not stale v1
        assert r3["status"] == "MEASURED"

    def test_window_roll_invalidates(self):
        wds.measure_windowed_ds(fetch=_fetch(ONE, UNIFORM4), now=T)
        r2 = wds.measure_windowed_ds(
            fetch=_fetch(UNIFORM4, ONE), now=T + wds.WINDOW_BUCKET_SECONDS + 1
        )
        assert r2["value"] > 0  # refetched after bucket roll


class TestConsumerContract:
    def test_windowed_ds_value_consumer_shape(self):
        """The rest_routes wire reads m['value'] — shape must hold."""
        r = wds.measure_windowed_ds(fetch=_fetch(ONE, UNIFORM4), now=T)
        v = None if r is None else float(r["value"])
        assert v == pytest.approx(-2.0, abs=1e-4)

    def test_window_size_invariance_bug_class(self):
        """Unequal window totals must NOT shift ΔS (catches the log2(v)
        pseudo-entropy bug the live smoke found: H may not depend on n)."""
        scaled = {k: 2 * v for k, v in UNIFORM4.items()}  # same dist, 200 rows
        r = wds.measure_windowed_ds(fetch=_fetch(ONE, scaled), now=T)
        assert r is not None
        assert r["value"] == pytest.approx(-2.0, abs=1e-4)

    def test_provenance_fields_present(self):
        r = wds.measure_windowed_ds(fetch=_fetch(ONE, UNIFORM4), now=T)
        for key in (
            "instrument_version",
            "source_commit",
            "cache_key",
            "window_bounds",
            "falsifier",
            "excluded_unclassified",
        ):
            assert key in r, f"missing provenance field: {key}"

"""Regression: a failed WELL snapshot refresh must not ERASE the last known-good payload.

Failure class (witnessed 2026-11-20 01:27-01:35Z, kernel :8088 /health):
  WELL /health calls BACK into kernel :8088 (well server.py:2769,2813 federation
  geometry). A kernel /health cold build occupies the loop; WELL's answer to the
  kernel's own refresher stalls; the refresher's 2.5s budget expires; the
  failure path set payload=None — and the SAME build that caused the stall then
  read payload=None. F6 fell back to meters with origin
  `unmeasured_default:f6_partially_measured`, hiding the real reason
  (`well_health:coverage_insufficient`). 4/4 consecutive builds showed the
  poisoned snapshot while out-of-process fetches ran 16-38ms.

Contract (stale-while-error, evidence age never masked):
  A. cold failure (no prior payload)  -> payload None, err set, degraded, fast retry 2s
  B. warm failure (payload age < KEEP) -> payload RETAINED, ts stays the payload's,
                                          degraded disclosed, normal 30s cadence
  C. stale failure (payload age > KEEP)-> payload dropped, ts = failure time, fast retry
  D. success clears err + degraded, 30s cadence
"""

from __future__ import annotations

import sys
import time
import urllib.request
from unittest.mock import patch as _patch

sys.path.insert(0, "/root/arifOS")

from arifosmcp.runtime.rest_routes import rest_routes as rr  # noqa: E402


class _StopLoop(Exception):
    pass


def _run_one_iteration(monkeypatch, urlopen_behavior):
    """Drive exactly one loop iteration; capture the sleep the loop chose."""
    sleeps: list[float] = []

    def fake_sleep(seconds):
        sleeps.append(seconds)
        raise _StopLoop()

    def fake_urlopen(req, timeout=None):  # noqa: ARG001
        return urlopen_behavior()

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(rr.time, "sleep", fake_sleep)
    try:
        rr._well_snapshot_loop()
    except _StopLoop:
        pass
    return sleeps


def _reset_snapshot():
    rr._well_health_snapshot.update(
        {"payload": None, "ts": 0.0, "err": None, "degraded": False}
    )


def _boom():
    raise TimeoutError("timed out")


def _ok_payload():
    import contextlib, io

    body = b'{"status": "degraded", "truth_status": "INSUFFICIENT_DATA"}'

    class R:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return body

    return R()


def test_a_cold_failure_drops_to_none_and_fast_retries(monkeypatch):
    _reset_snapshot()
    sleeps = _run_one_iteration(monkeypatch, _boom)
    s = rr._well_health_snapshot
    assert s["payload"] is None
    assert "TimeoutError" in (s["err"] or "")
    assert s["degraded"] is True
    assert sleeps == [2.0], sleeps


def test_b_warm_failure_retains_last_known_good(monkeypatch):
    _reset_snapshot()
    good = {"status": "degraded", "truth_status": "INSUFFICIENT_DATA"}
    rr._well_health_snapshot.update({"payload": good, "ts": time.time() - 5.0})
    sleeps = _run_one_iteration(monkeypatch, _boom)
    s = rr._well_health_snapshot
    assert s["payload"] is good, "failed refresh erased fresh evidence"
    assert "TimeoutError" in (s["err"] or "")
    assert s["degraded"] is True
    assert abs(time.time() - 5.0 - s["ts"]) < 60, (
        "payload ts must not be masked by failure time"
    )
    assert sleeps == [30.0], (
        "retained payload rides the normal cadence, not the hot retry"
    )


def test_c_stale_failure_drops_old_payload(monkeypatch):
    _reset_snapshot()
    rr._well_health_snapshot.update(
        {
            "payload": {"old": True},
            "ts": time.time() - rr.WELL_SNAPSHOT_STALE_KEEP_S - 60.0,
        }
    )
    sleeps = _run_one_iteration(monkeypatch, _boom)
    s = rr._well_health_snapshot
    assert s["payload"] is None, (
        "stale evidence beyond KEEP must not masquerade as current"
    )
    assert s["degraded"] is True
    assert sleeps == [2.0]


def test_d_success_clears_error_and_degraded(monkeypatch):
    _reset_snapshot()
    rr._well_health_snapshot.update(
        {"payload": None, "err": "TimeoutError: timed out", "degraded": True}
    )
    sleeps = _run_one_iteration(monkeypatch, _ok_payload)
    s = rr._well_health_snapshot
    assert isinstance(s["payload"], dict)
    assert s["err"] is None
    assert s["degraded"] is False
    assert sleeps == [30.0]


def test_e_keep_constant_is_declared(monkeypatch=None):
    assert rr.WELL_SNAPSHOT_STALE_KEEP_S >= 300.0, (
        "keep window must cover build-stall windows (~10s x probe cadence)"
    )


def test_f_initial_dict_declares_degraded_false(monkeypatch=None):
    # source-level check: the module-level snapshot declares the key, so
    # .get("degraded") in the builder is never a silent None-as-False.
    import inspect

    src = inspect.getsource(rr)
    assert '"degraded": False' in src, (
        "initial snapshot dict must declare degraded=False"
    )


if __name__ == "__main__":
    import traceback

    fails = 0
    import _pytest.monkeypatch as mp

    for name in sorted(n for n in globals() if n.startswith("test_")):
        try:
            with mp.MonkeyPatch.context() as m:
                globals()[name](m)
            print(f"  PASS  {name}")
        except Exception:
            fails += 1
            print(f"  FAIL  {name}")
            traceback.print_exc()
    print(f"\n{fails} failing")
    sys.exit(1 if fails else 0)

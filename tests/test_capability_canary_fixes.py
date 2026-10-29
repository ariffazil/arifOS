"""
tests/test_capability_canary_fixes.py — F13-authorized canary fixes 1, 2, 4
(2026-10-30: "F13 AUTHORIZE CANARY FIX 1-4"; fix 3 is the systemd timer,
installed separately on the host).

Fences are mutation-testable both directions (Rule 3p): each asserts the
load-bearing behavior that dies if the fix is removed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime.capability_drift import record_test_result
from arifosmcp.runtime.witness_producers import probe_ai_witness


# ── FIX 2: outcome semantics in record_test_result ─────────────────────────


def test_held_by_authority_is_not_failed(tmp_path):
    cache = tmp_path / "cache.json"
    import arifosmcp.runtime.capability_drift as cd
    orig = cd.TEST_CACHE_PATH
    cd.TEST_CACHE_PATH = cache
    try:
        record_test_result("arif_think", passed=True, error=None,
                           outcome="HELD_BY_AUTHORITY", invoked_at=1_800_000_000)
        row = json.loads(cache.read_text())["arif_think"]
        assert row["outcome"] == "HELD_BY_AUTHORITY"
        assert row["last_pass"] is True  # the tool worked — it answered
    finally:
        cd.TEST_CACHE_PATH = orig


def test_falsifier_passed_false_cannot_wear_outcome_passed(tmp_path):
    import arifosmcp.runtime.capability_drift as cd
    orig = cd.TEST_CACHE_PATH
    cd.TEST_CACHE_PATH = tmp_path / "cache.json"
    try:
        with pytest.raises(ValueError):
            record_test_result("arif_think", passed=False, outcome="PASSED")
        with pytest.raises(ValueError):
            record_test_result("arif_think", passed=True, outcome="MAYBE")
    finally:
        cd.TEST_CACHE_PATH = orig


def test_legacy_rows_without_outcome_still_count_as_before(tmp_path):
    # backward compatibility: pre-fix rows (no outcome field) must not crash
    # the witness and must count by last_pass as they always did
    cache = tmp_path / "cache.json"
    cache.write_text(json.dumps({
        "arif_init": {"last_invocation_at": 9_999_999_999, "last_pass": True},
    }))
    value, reason = probe_ai_witness(fresh_seconds=86400, cache_path=str(cache))
    assert value == 1.0


# ── FIX 4: witness counts decisive only; held-fresh transparent ────────────


def _cache(tmp_path, rows):
    p = tmp_path / "cache.json"
    p.write_text(json.dumps(rows))
    return str(p)


def test_held_rows_are_fresh_but_not_decisive(tmp_path):
    now = 9_999_999_999  # far future relative to rows → all fresh
    rows = {}
    for i in range(3):
        rows[f"t_pass_{i}"] = {"last_invocation_at": now - 100, "last_pass": True,
                               "outcome": "PASSED"}
    for i in range(3):
        rows[f"t_hold_{i}"] = {"last_invocation_at": now - 100, "last_pass": True,
                               "outcome": "HELD_BY_AUTHORITY"}
    value, reason = probe_ai_witness(fresh_seconds=86400, cache_path=_cache(tmp_path, rows))
    assert value == 0.5, "3 decisive of 6 — held answers must NOT inflate the witness"
    assert "3 held-by-authority fresh" in reason


def test_falsifier_counting_held_as_decisive_inflates_witness(tmp_path):
    # mutation direction: if fix 4 were removed (held counted as passed),
    # the same cache would read 1.0 — the exact W3 overshoot refused 2026-10-29
    now = 9_999_999_999
    rows = {
        "a": {"last_invocation_at": now - 100, "last_pass": True, "outcome": "PASSED"},
        "b": {"last_invocation_at": now - 100, "last_pass": True, "outcome": "HELD_BY_AUTHORITY"},
    }
    value, _ = probe_ai_witness(fresh_seconds=86400, cache_path=_cache(tmp_path, rows))
    assert value == 0.5  # NOT 1.0


def test_stale_rows_still_excluded(tmp_path):
    rows = {
        "fresh": {"last_invocation_at": 9_999_999_999 - 10, "last_pass": True, "outcome": "PASSED"},
        "stale": {"last_invocation_at": 1_000, "last_pass": True, "outcome": "PASSED"},
    }
    value, reason = probe_ai_witness(fresh_seconds=86400, cache_path=_cache(tmp_path, rows))
    assert value == 0.5
    assert "1 stale excluded" in reason


# ── FIX 1: entry-point guard refuses the source-tree shadow ────────────────


def test_entrypoint_refuses_source_tree_cwd():
    # run the module from INSIDE the repo: the guard must exit 3 BEFORE any
    # tool call. (Under -m from inside /root/arifOS, arifosmcp resolves to the
    # source tree — exactly the shadow the guard exists to refuse.)
    r = subprocess.run(
        [sys.executable, "-m", "arifosmcp.runtime.capability_smoke_test"],
        cwd="/root/arifOS",
        capture_output=True, text=True, timeout=60,
        env={"PATH": "/usr/bin:/bin", "ARIFOS_CANARY_ALLOW_SOURCE": ""},
    )
    assert r.returncode == 3, f"expected refusal exit 3, got {r.returncode}: {r.stdout[:200]}"
    payload = json.loads(r.stdout.strip().splitlines()[-1])
    assert payload["refused"] == "source_tree_shadow"
    assert payload["resolved"].startswith("/root/arifOS")


def test_falsifier_guard_dies_if_shadow_restore(tmp_path):
    # mutation direction: if the sys.path.insert were restored (or the guard
    # removed), the same invocation would NOT exit 3 — proven by the assert
    # above. Here we additionally pin the guard text exists in source.
    src = (Path(__file__).resolve().parents[1]
           / "arifosmcp/runtime/capability_smoke_test.py").read_text()
    assert "sys.path.insert(0" not in src, "shadow restored into the canary"
    assert "source_tree_shadow" in src, "resolution guard removed"

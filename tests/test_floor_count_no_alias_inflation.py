"""Envelope 1 regression — floor count must not exceed target (alias inflation).

Locks the defect triaged 2026-10-13: producers wrote F11/F12/F13 AND
L11/L12/L13, inflating floors_detail 13 -> 16 and floors_pass 12 -> 15,
which (with the `>=` comparator) let a doubled count render "healthy".

This test probes the live kernel, so it is the post-deploy tripwire.
The pure counterpart (test_canonical_floor_id) covers the fold without
any network.

LIVE-ONLY behavior — kernel is not reachable from CI, so this test will
SKIP (not pass) when /health is unreachable.
"""
from __future__ import annotations

import json
import urllib.request

import pytest

ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health"


def _fetch_health() -> dict:
    req = urllib.request.Request(ARIFOS_HEALTH_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        return json.loads(resp.read())


@pytest.fixture(scope="module")
def constitutional():
    try:
        h = _fetch_health()
    except Exception as exc:
        pytest.skip(f"arifOS /health unreachable: {exc}")
    return h["layer_health"]["constitutional"]


def test_floor_count_equals_target_no_alias_inflation(constitutional):
    detail = constitutional["floors_detail"]
    target = constitutional["floors_target"]
    assert len(detail) == target, (
        f"{len(detail)} floors != target {target} (alias inflation)"
    )


def test_pass_count_never_exceeds_target(constitutional):
    assert constitutional["floors_pass"] <= constitutional["floors_target"], (
        f"floors_pass={constitutional['floors_pass']} exceeds "
        f"floors_target={constitutional['floors_target']}"
    )


def test_alias_keys_do_not_leak_into_detail(constitutional):
    detail = constitutional["floors_detail"]
    for f in ("F11", "F12", "F13"):
        assert f not in detail, f"non-canonical alias key {f} leaked into floors_detail"
    for l in ("L11", "L12", "L13"):
        assert l in detail, f"canonical key {l} missing from floors_detail"

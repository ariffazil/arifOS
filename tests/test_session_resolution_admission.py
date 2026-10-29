"""
tests/test_session_resolution_admission.py — PACKET-AB Changeset A (2026-10-29)

Tests 1-5 and 8 of the packet matrix: session_resolution admission over the
gate telemetry store, and the hook drift fence. Admission logic is imported
from the SHIPPED module (report_lane) — never re-implemented here (Rule 3p:
a test that carries its own copy of the control is ceremony).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arifosmcp.runtime.report_lane import (
    SESSION_RESOLUTION_VOCAB,
    admit_for_readiness,
    classify_session,
    readiness_counts,
    resolve_row_resolution,
)

HOOK = Path("/root/.arifos/agents/kimi/hooks/aaa-completion-check.sh")
CONFIG = Path("/root/.kimi-code/config.toml")


def _row(session="session_dff10dca-94f5-4257-990a-0d9f9f28a1b3", **kw):
    r = {"session": session, "event": "Stop", "verdict": "OBSERVE"}
    r.update(kw)
    return r


# ── test 1: real session accepted ───────────────────────────────────────────


def test_real_session_admitted():
    assert classify_session("session_dff10dca-94f5-4257") == "real"
    assert admit_for_readiness(_row(session_resolution="real")) is True


def test_falsifier_real_requires_session_shape():
    # mutation direction: loosen the regex and a fixture id passes as real
    assert classify_session("fx") == "synthetic"
    assert classify_session("gold-test") == "synthetic"
    assert classify_session("") == "synthetic"


# ── test 2: synthetic only in designated test scope ─────────────────────────


def test_synthetic_admitted_only_in_test_scope():
    row = _row(session="synthetic-probe-1", session_resolution="synthetic")
    assert admit_for_readiness(row, test_scope=False) is False
    assert admit_for_readiness(row, test_scope=True) is True


# ── test 3: missing session_resolution fails closed (row still exists) ──────


def test_missing_resolution_fails_closed_at_admissibility():
    row = _row()  # no session_resolution field — the legacy shape
    assert resolve_row_resolution(row) == "legacy_unclassified"
    assert admit_for_readiness(row) is False
    assert admit_for_readiness(row, test_scope=True) is False  # legacy never counts


def test_falsifier_fail_closed_is_load_bearing():
    # mutation direction: if admission defaulted open, a fieldless row would
    # count toward readiness. Assert the closed default mechanically.
    counts = readiness_counts([_row(), _row()])  # two fieldless rows
    assert counts["admitted_real"] == 0
    assert counts["readiness"] == "UNMEASURED"


# ── test 4: invalid session_resolution rejected ─────────────────────────────


def test_invalid_resolution_rejected():
    row = _row(session_resolution="maybe")
    assert resolve_row_resolution(row) == "__invalid__"
    assert admit_for_readiness(row) is False
    assert "maybe" not in SESSION_RESOLUTION_VOCAB


def test_falsifier_vocabulary_is_closed():
    for tok in ("real", "synthetic", "legacy_unclassified"):
        assert tok in SESSION_RESOLUTION_VOCAB
    assert len(SESSION_RESOLUTION_VOCAB) == 3  # no silent widening


# ── test 5: synthetic cannot satisfy production readiness ───────────────────


def test_fixture_store_is_never_green():
    rows = [_row(session=f"synthetic-{i}", session_resolution="synthetic") for i in range(100)]
    counts = readiness_counts(rows)
    assert counts["admitted_real"] == 0
    assert counts["readiness"] == "UNMEASURED"


def test_mixed_store_counts_real_only():
    rows = (
        [_row(session_resolution="real")]
        + [_row(session=f"synthetic-{i}", session_resolution="synthetic") for i in range(5)]
        + [_row()]  # legacy, no field
    )
    counts = readiness_counts(rows)
    assert counts["admitted_real"] == 1
    assert counts["synthetic"] == 5
    assert counts["legacy_unclassified"] == 1
    assert counts["readiness"] == "MEASURED"


# ── test 8: gate still enforces via its real hook (drift fence) ─────────────


def test_fence_hook_registered_and_stamping():
    cfg = CONFIG.read_text()
    assert "aaa-completion-check.sh" in cfg, "hook no longer registered in kimi config"
    hook = HOOK.read_text()
    assert "session_resolution" in hook, "hook lost its session_resolution stamping"
    assert 'SESSION_RESOLUTION=' in hook, "hook classification variable removed"


def test_fence_hook_content_pin():
    # drift detector: the hook must still match the manifest-pinned sha or,
    # if intentionally changed by a later authorized run, that run's receipt
    # must exist. Here we pin the structural contract only.
    hook = HOOK.read_text()
    assert hook.count('"session_resolution":"$SESSION_RESOLUTION"') == 3, (
        "expected the stamp on all three telemetry write sites"
    )

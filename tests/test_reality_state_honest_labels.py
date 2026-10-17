"""Regression: honest epistemic labels for WELL biological state (F2).

Born from F13 chat directive 2026-10-14: ``arifos://reality/state`` relayed
a WELL payload that self-declares ``environment=TEST`` /
"Mocked healthy state for test session" (dated 2026-04-30) as
``epistemic=OBSERVED`` while WELL's own ``freshness=FRESH`` claim rode
inside it — a truth-labeling defect (F2), not a data defect.

Contract after fix:
  - mock/test payload      -> epistemic ``DECLARED_TEST_MOCK`` + degraded
  - payload timestamp >48h -> ``data_freshness=STALE`` + degraded
  - WELL's self-claims stay verbatim inside ``data`` (causality contract:
    two disagreeing values are both returned, each with its label)
"""

from __future__ import annotations

import json
import time

from arifosmcp.resources.reality_state import _probe_biological


def _write(path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_mock_test_state_labeled_declared_test_mock(tmp_path):
    state = tmp_path / "state.json"
    _write(
        state,
        {
            "environment": "TEST",
            "reason": "Mocked healthy state for test session",
            "timestamp": "2026-04-30T00:00:00+00:00",
            "freshness": "FRESH",  # WELL's own claim — must survive verbatim
            "metrics": {"cognitive": {"clarity": 10}},
        },
    )
    out = _probe_biological(candidates=[str(state)])
    ws = out["well_state"]
    assert ws["epistemic"] == "DECLARED_TEST_MOCK", "mock must not be OBSERVED (F2)"
    assert "mock_warning" in ws
    assert out["degraded"] is True
    # WELL self-claim preserved — kernel label disagrees, visibly
    assert ws["data"]["freshness"] == "FRESH"
    # 2026-04-30 is months old -> stale regardless of mock status
    assert ws["data_age_hours"] > 48
    assert ws["data_freshness"] == "STALE"


def test_stale_but_real_state_labeled_observed_stale(tmp_path):
    state = tmp_path / "state.json"
    _write(
        state,
        {
            "environment": "PROD",
            "timestamp": "2026-10-10T00:00:00+00:00",
            "metrics": {"cognitive": {"clarity": 7}},
        },
    )
    out = _probe_biological(candidates=[str(state)])
    ws = out["well_state"]
    assert ws["epistemic"] == "OBSERVED"
    assert ws["data_freshness"] == "STALE"
    assert out["degraded"] is True


def test_fresh_real_state_healthy(tmp_path):
    state = tmp_path / "state.json"
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime())
    _write(state, {"environment": "PROD", "timestamp": now_iso, "metrics": {}})
    out = _probe_biological(candidates=[str(state)])
    ws = out["well_state"]
    assert ws["epistemic"] == "OBSERVED"
    assert "data_freshness" not in ws
    assert out["degraded"] is False


def test_mock_reason_alone_triggers_label(tmp_path):
    state = tmp_path / "state.json"
    _write(
        state,
        {"reason": "mocked for pytest", "timestamp": "2026-10-14T00:00:00+00:00"},
    )
    out = _probe_biological(candidates=[str(state)])
    assert out["well_state"]["epistemic"] == "DECLARED_TEST_MOCK"

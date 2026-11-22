"""Unit test for Bridge PR-0a: signal_cognitive_pressure must never mutate well_score."""

from __future__ import annotations

import json
from pathlib import Path

from arifosmcp.runtime import well_bridge


def test_signal_cognitive_pressure_does_not_mutate_well_score(tmp_path: Path, monkeypatch) -> None:
    state_file = tmp_path / "well_state.json"
    initial = {
        "well_score": 88,
        "metrics": {"cognitive": {"clarity": 10, "decision_fatigue": 1.0}},
        "floors_violated": [],
    }
    state_file.write_text(json.dumps(initial), encoding="utf-8")
    monkeypatch.setattr(well_bridge, "WELL_STATE_PATH", state_file)

    ok = well_bridge.signal_cognitive_pressure(load_delta=3.0, source="forge")
    assert ok is True

    after = json.loads(state_file.read_text(encoding="utf-8"))
    assert after["well_score"] == 88, "PR-0a violation: machine load_delta mutated H-WELL well_score"
    assert after["metrics"]["cognitive"]["decision_fatigue"] == 4.0
    assert "W6_METABOLIC_PAUSE" in after["floors_violated"]

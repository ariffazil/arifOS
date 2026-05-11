"""
tests/runtime/test_well_bridge.py — WELL Biological Substrate Bridge Tests
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

from arifosmcp.runtime import well_bridge as wb


@pytest.fixture
def mock_well_state(monkeypatch):
    """Provide a temporary WELL state.json and patch the bridge path."""
    tmpdir = tempfile.mkdtemp()
    state_path = Path(tmpdir) / "state.json"
    base_state = {
        "timestamp": "2026-05-11T00:00:00+00:00",
        "well_score": 85,
        "floors_violated": [],
        "metrics": {"cognitive": {"clarity": 10, "decision_fatigue": 0}},
    }
    state_path.write_text(json.dumps(base_state))
    monkeypatch.setattr(wb, "WELL_STATE_PATH", state_path)
    yield state_path
    # cleanup
    state_path.unlink(missing_ok=True)
    os.rmdir(tmpdir)


@pytest.fixture
def degraded_well_state(mock_well_state):
    """Return path to a degraded WELL state."""
    state = json.loads(mock_well_state.read_text())
    state["well_score"] = 45
    state["floors_violated"] = ["W6_METABOLIC_PAUSE"]
    mock_well_state.write_text(json.dumps(state))
    return mock_well_state


class TestBiologicalReadiness:
    """F06 EMPATHY + F07 HUMILITY: Biological readiness scoring."""

    def test_optimal_state(self, mock_well_state):
        r = wb.get_biological_readiness()
        assert r["ok"] is True
        assert r["verdict"] == "OPTIMAL"
        assert r["bandwidth"] == "FULL"
        assert r["sabar_advisory"] is False
        assert r["well_score"] == 85

    def test_functional_state(self, mock_well_state):
        state = json.loads(mock_well_state.read_text())
        state["well_score"] = 65
        mock_well_state.write_text(json.dumps(state))
        r = wb.get_biological_readiness()
        assert r["verdict"] == "FUNCTIONAL"
        assert r["bandwidth"] == "NORMAL"

    def test_low_capacity_state(self, mock_well_state):
        state = json.loads(mock_well_state.read_text())
        state["well_score"] = 30
        mock_well_state.write_text(json.dumps(state))
        r = wb.get_biological_readiness()
        assert r["verdict"] == "LOW_CAPACITY"
        assert r["bandwidth"] == "REDUCED"
        assert r["sabar_advisory"] is True

    def test_degraded_with_violations(self, degraded_well_state):
        r = wb.get_biological_readiness()
        assert r["verdict"] == "DEGRADED"
        assert r["bandwidth"] == "RESTRICTED"
        assert r["sabar_advisory"] is True
        assert "W6_METABOLIC_PAUSE" in r["violations"]

    def test_missing_state_file(self, monkeypatch):
        monkeypatch.setattr(wb, "WELL_STATE_PATH", Path("/nonexistent/well/state.json"))
        r = wb.get_biological_readiness()
        assert r["ok"] is False
        assert r["verdict"] == "UNKNOWN"

    def test_corrupt_json(self, mock_well_state):
        mock_well_state.write_text("not-json{")
        r = wb.get_biological_readiness()
        assert r["ok"] is False
        assert r["verdict"] == "ERROR"


class TestInjectBiologicalContext:
    """F06 EMPATHY: Inject WELL context into governance state."""

    def test_injects_telemetry(self, mock_well_state):
        gs = {"verdict": "SEAL", "message": "All good", "telemetry": {}}
        result = wb.inject_biological_context(gs)
        assert result["telemetry"]["well_score"] == 85
        assert result["telemetry"]["well_verdict"] == "OPTIMAL"
        assert "sabar_advisory" not in result or result["sabar_advisory"] is False
        assert result["verdict"] == "SEAL"  # not downgraded

    def test_downgrades_seal_when_degraded(self, degraded_well_state):
        gs = {"verdict": "SEAL", "message": "All good", "telemetry": {}}
        result = wb.inject_biological_context(gs)
        assert result["verdict"] == "HOLD"
        assert "[WELL-HOLD]" in result["message"]

    def test_no_downgrade_if_not_seal(self, degraded_well_state):
        gs = {"verdict": "QUALIFY", "message": "Maybe", "telemetry": {}}
        result = wb.inject_biological_context(gs)
        assert result["verdict"] == "QUALIFY"


class TestCognitivePressure:
    """F06 EMPATHY: Cognitive load tracking and metabolic pause triggers."""

    def test_increments_decision_fatigue(self, mock_well_state):
        ok = wb.signal_cognitive_pressure(1.5, source="forge")
        assert ok is True
        state = json.loads(mock_well_state.read_text())
        assert state["metrics"]["cognitive"]["decision_fatigue"] == 1.5

    def test_caps_fatigue_at_10(self, mock_well_state):
        wb.signal_cognitive_pressure(6.0)
        wb.signal_cognitive_pressure(6.0)
        state = json.loads(mock_well_state.read_text())
        assert state["metrics"]["cognitive"]["decision_fatigue"] == 10.0

    def test_w6_metabolic_pause_trigger(self, mock_well_state):
        wb.signal_cognitive_pressure(3.0)
        state = json.loads(mock_well_state.read_text())
        assert "W6_METABOLIC_PAUSE" in state["floors_violated"]

    def test_reduces_well_score(self, mock_well_state):
        initial = json.loads(mock_well_state.read_text())["well_score"]
        wb.signal_cognitive_pressure(5.0)
        state = json.loads(mock_well_state.read_text())
        assert state["well_score"] == initial - 10.0

    def test_returns_false_when_state_missing(self, monkeypatch):
        monkeypatch.setattr(wb, "WELL_STATE_PATH", Path("/nonexistent"))
        assert wb.signal_cognitive_pressure(1.0) is False

"""
Test suite for arifOS WELL Bridge — Biological Substrate Connector
═══════════════════════════════════════════════════════════════════

Tests get_biological_readiness, inject_biological_context,
signal_cognitive_pressure, and anchor_well_to_vault.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from arifosmcp.runtime.well_bridge import (
    get_biological_readiness,
    inject_biological_context,
    signal_cognitive_pressure,
)


@pytest.fixture(autouse=True)
def _mock_well_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect WELL_STATE_PATH to a temp file for every test."""
    mock_path = tmp_path / "well_state.json"
    monkeypatch.setattr(
        "arifosmcp.runtime.well_bridge.WELL_STATE_PATH", mock_path
    )
    return mock_path


class TestGetBiologicalReadiness:
    def test_missing_state_returns_unknown(self, _mock_well_path: Path) -> None:
        readiness = get_biological_readiness()
        assert readiness["ok"] is False
        assert readiness["verdict"] == "UNKNOWN"
        assert readiness["well_score"] == 50.0
        assert readiness["bandwidth"] == "NORMAL"
        assert readiness["sabar_advisory"] is False

    def test_optimal_state(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=85, floors_violated=[])
        readiness = get_biological_readiness()
        assert readiness["ok"] is True
        assert readiness["verdict"] == "OPTIMAL"
        assert readiness["bandwidth"] == "FULL"
        assert readiness["sabar_advisory"] is False
        assert readiness["well_score"] == 85

    def test_functional_state(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=65, floors_violated=[])
        readiness = get_biological_readiness()
        assert readiness["verdict"] == "FUNCTIONAL"
        assert readiness["bandwidth"] == "NORMAL"
        assert readiness["sabar_advisory"] is False

    def test_low_capacity_state(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=40, floors_violated=[])
        readiness = get_biological_readiness()
        assert readiness["verdict"] == "LOW_CAPACITY"
        assert readiness["bandwidth"] == "REDUCED"
        assert readiness["sabar_advisory"] is True

    def test_degraded_state_with_violations(self, _mock_well_path: Path) -> None:
        _write_state(
            _mock_well_path, well_score=90, floors_violated=["W6_METABOLIC_PAUSE"]
        )
        readiness = get_biological_readiness()
        assert readiness["verdict"] == "DEGRADED"
        assert readiness["bandwidth"] == "RESTRICTED"
        assert readiness["sabar_advisory"] is True
        assert "W6_METABOLIC_PAUSE" in readiness["violations"]

    def test_malformed_state_returns_error(self, _mock_well_path: Path) -> None:
        _mock_well_path.write_text("not-json", encoding="utf-8")
        readiness = get_biological_readiness()
        assert readiness["ok"] is False
        assert readiness["verdict"] == "ERROR"
        assert readiness["well_score"] == 0.0
        assert readiness["bandwidth"] == "RESTRICTED"
        assert readiness["sabar_advisory"] is True


class TestInjectBiologicalContext:
    def test_injects_telemetry(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=72)
        state: dict[str, Any] = {"verdict": "SEAL", "telemetry": {}, "message": ""}
        injected = inject_biological_context(state)
        assert injected["telemetry"]["well_score"] == 72
        assert injected["telemetry"]["well_verdict"] == "FUNCTIONAL"
        assert injected["telemetry"]["well_bandwidth"] == "NORMAL"

    def test_degraded_downgrades_seal_to_hold(self, _mock_well_path: Path) -> None:
        _write_state(
            _mock_well_path, well_score=90, floors_violated=["W6_METABOLIC_PAUSE"]
        )
        state: dict[str, Any] = {"verdict": "SEAL", "telemetry": {}, "message": ""}
        injected = inject_biological_context(state)
        assert injected["verdict"] == "HOLD"
        assert "[WELL-HOLD]" in injected["message"]

    def test_does_not_downgrade_non_seal(self, _mock_well_path: Path) -> None:
        _write_state(
            _mock_well_path, well_score=90, floors_violated=["W6_METABOLIC_PAUSE"]
        )
        state: dict[str, Any] = {"verdict": "HOLD", "telemetry": {}, "message": ""}
        injected = inject_biological_context(state)
        assert injected["verdict"] == "HOLD"

    def test_sets_sabar_advisory_when_low(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=30)
        state: dict[str, Any] = {"verdict": "SEAL", "telemetry": {}, "message": ""}
        injected = inject_biological_context(state)
        assert injected["sabar_advisory"] is True

    def test_no_sabar_when_optimal(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=90)
        state: dict[str, Any] = {"verdict": "SEAL", "telemetry": {}, "message": ""}
        injected = inject_biological_context(state)
        assert injected.get("sabar_advisory") is not True


class TestSignalCognitivePressure:
    def test_updates_fatigue(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=80, metrics={"cognitive": {"clarity": 10, "decision_fatigue": 2}})
        ok = signal_cognitive_pressure(load_delta=1.5, source="forge")
        assert ok is True
        state = _read_state(_mock_well_path)
        assert state["metrics"]["cognitive"]["decision_fatigue"] == 3.5

    def test_caps_fatigue_at_10(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=80, metrics={"cognitive": {"clarity": 10, "decision_fatigue": 9}})
        ok = signal_cognitive_pressure(load_delta=5.0, source="forge")
        assert ok is True
        state = _read_state(_mock_well_path)
        assert state["metrics"]["cognitive"]["decision_fatigue"] == 10.0

    def test_adds_w6_violation_on_high_load(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=80, floors_violated=[])
        ok = signal_cognitive_pressure(load_delta=3.0, source="forge")
        assert ok is True
        state = _read_state(_mock_well_path)
        assert "W6_METABOLIC_PAUSE" in state["floors_violated"]

    def test_returns_false_when_state_missing(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        missing_path = tmp_path / "no_well_here.json"
        monkeypatch.setattr(
            "arifosmcp.runtime.well_bridge.WELL_STATE_PATH", missing_path
        )
        ok = signal_cognitive_pressure(load_delta=1.0)
        assert ok is False

    def test_decreases_well_score(self, _mock_well_path: Path) -> None:
        _write_state(_mock_well_path, well_score=60)
        signal_cognitive_pressure(load_delta=2.0)
        state = _read_state(_mock_well_path)
        assert state["well_score"] == 56


def _write_state(path: Path, well_score: float = 50, floors_violated: list[str] | None = None, metrics: dict[str, Any] | None = None) -> None:
    state: dict[str, Any] = {
        "well_score": well_score,
        "floors_violated": floors_violated or [],
        "timestamp": "2026-05-11T12:00:00Z",
    }
    if metrics is not None:
        state["metrics"] = metrics
    path.write_text(json.dumps(state), encoding="utf-8")


def _read_state(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

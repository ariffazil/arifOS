"""Regression tests for transport module exports."""

from __future__ import annotations

from arifosmcp.transport import conformance
from arifosmcp.transport import run_conformance_spine


def test_transport_run_conformance_spine_points_to_v2_module() -> None:
    assert run_conformance_spine.__module__ == "arifosmcp.transport.conformance_spine"


def test_legacy_conformance_path_delegates_to_v2(monkeypatch) -> None:
    called = {}

    def _fake_run_spine():
        called["yes"] = True
        return {"spine": "ARIF Conformance Spine v0.2"}

    monkeypatch.setattr("arifosmcp.transport.conformance_spine.run_spine", _fake_run_spine)
    report = conformance.run_conformance_spine()

    assert called["yes"] is True
    assert report["spine"] == "ARIF Conformance Spine v0.2"

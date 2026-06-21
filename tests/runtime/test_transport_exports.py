"""Regression tests for transport module exports."""

from __future__ import annotations

from arifosmcp.transport import run_conformance_spine


def test_transport_run_conformance_spine_points_to_v2_module() -> None:
    assert run_conformance_spine.__module__ == "arifosmcp.transport.conformance_spine"

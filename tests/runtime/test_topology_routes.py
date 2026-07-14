"""
Tests for arifosmcp.runtime.rest_routes.topology_routes
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.rest_routes.topology_routes import (  # noqa: E402
    compose_topology,
    _tool_drift_diff,
)


def test_topology_shape() -> None:
    t = compose_topology()
    assert "snapshot_id" in t
    assert "observed_at" in t
    assert "tool_drift" in t
    assert "organs" in t


def test_tool_drift_diff_surfaces_arif_measure() -> None:
    d = _tool_drift_diff()
    abr = d["advertised_but_unregistered"]
    assert any("arif_measure" in s for s in abr)


def test_organs_have_ontology() -> None:
    t = compose_topology()
    layers = {o.get("ontology") for o in t["organs"]}
    # Per audit: SOUL/MIND/BODY/ORGANS/MUSCLE/MEMORY/NERVES — we expose 8 organs w/ layers.
    assert "MIND" in layers or any("mind" in str(x).lower() for x in layers)
    assert "MEMORY" in layers
    assert "MUSCLE" in layers

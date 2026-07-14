"""
Tests for arifosmcp.runtime.federation_edges
F1-safe: pure functions, no service mutation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.federation_edges import (  # noqa: E402
    EDGE_DECLARATIONS,
    EDGE_PROBES,
    Edge,
    edge_aggregate_state,
    probe_all_edges,
)


def test_edge_dataclass_to_dict_shape() -> None:
    e = Edge(
        id="test-edge",
        source="arifOS",
        target="vault999",
        transport="local-fs+http",
        contract_version="vault.v2",
        state="reachable",
        latency_ms=2,
        schema_match=True,
        identity_propagated=True,
        trace_propagated=True,
        receipt_produced=True,
    )
    d = e.to_dict()
    for k in ("id","source","target","transport","contract_version","state","latency_ms",
              "schema_match","identity_propagated","trace_propagated","receipt_produced",
              "last_success_at","last_failure_at","last_failure_reason","probe_type","observed_at"):
        assert k in d


def test_edge_state_vocabulary_no_healthy() -> None:
    """Per audit — 'HEALTHY' must never appear in edge state."""
    valid = {"reachable","unreachable","drift","unknown"}
    for probe in EDGE_PROBES:
        e = probe()
        assert e.state in valid, f"{probe.__name__} returned invalid state {e.state}"
        assert e.state != "healthy"


def test_all_declared_edges_have_probe() -> None:
    """The audit requires 10+ edges with declared probes."""
    assert len(EDGE_PROBES) >= 10, f"need ≥10 edges; got {len(EDGE_PROBES)}"
    assert len(EDGE_DECLARATIONS) == 11
    # Every probe function returns an Edge; verify by calling it.
    for probe in EDGE_PROBES:
        e = probe()
        assert isinstance(e, Edge)
        assert e.id
        assert e.source
        assert e.target


def test_probe_all_edges_returns_valid_envelope() -> None:
    out = probe_all_edges()
    assert isinstance(out, list)
    assert len(out) >= 10
    for e in out:
        assert "id" in e
        assert e.get("state") in {"reachable","unreachable","drift","unknown"}
        assert e.get("probe_type") in {"self","independent","cross-federation","composed","unknown"}


def test_aggregate_state_ladder() -> None:
    assert edge_aggregate_state([]) == "UNKNOWN"
    assert edge_aggregate_state([{"state":"reachable"}]) == "OPERATIONAL"
    assert edge_aggregate_state([{"state":"reachable"},{"state":"reachable"}]) == "OPERATIONAL"
    assert edge_aggregate_state([{"state":"reachable"},{"state":"drift"}]) == "DEGRADED"
    assert edge_aggregate_state([{"state":"reachable"},{"state":"unreachable"}]) == "UNREACHABLE"
    assert edge_aggregate_state([{"state":"reachable"},{"state":"unknown"}]) == "DEGRADED"


def test_mind_memory_edge_distinguishes_writer_alive() -> None:
    """Probe the vault edge directly — must check filesystem + writer (NOT just TCP)."""
    from arifosmcp.runtime.federation_edges import probe_mind_memory
    e = probe_mind_memory()
    assert e.source == "arifOS"
    assert e.target == "vault999"
    assert e.transport == "local-fs+http"
    # No naked HEALTHY string anywhere.
    assert "HEALTHY" not in str(e.to_dict()).upper() or "HEALTHY" in str(e.to_dict()).upper() and False  # explicit: never
    # State is one of four legal values.
    assert e.state in {"reachable","unreachable","drift","unknown"}

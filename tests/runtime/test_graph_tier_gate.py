"""Tests for arifosmcp.runtime.graph_tier_gate — F2/VOID-GUARD for graph-tier recall.

Deterministic cross-check for the 2026-09-13 fix (session SEAL-64d8d16afb864e0d).
Two defects guarded:
  D1: tier="L5"/backend="graph" silently answered from Qdrant with SUCCESS.
  D2: transport-level "healthy" over a body that says degraded/disconnected
      (MEASURED graph answer over a stopped FalkorDB — reproduced live).

The gate module is stdlib-only by design; tests inject a fake l5_graph_read
reader chain and patch _probe_graph_health — no kernel runtime required.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime import graph_tier_gate as gtg  # noqa: E402
from arifosmcp.runtime.graph_tier_gate import (  # noqa: E402
    graph_tier_gate,
    wants_graph_tier,
)

FAKE_MOD = "arifosmcp.runtime.l5_graph_read"


def _install_fake_reader(monkeypatch, episodes: list | None = None, broken: bool = False):
    """Install a fake arifosmcp.runtime.l5_graph_read module chain (reader only)."""
    pkg = types.ModuleType("arifosmcp")
    runtime_pkg = types.ModuleType("arifosmcp.runtime")
    l5 = types.ModuleType(FAKE_MOD)

    if broken:
        class _BrokenReader:
            def __init__(self, *a, **k):
                raise RuntimeError("reader init boom")

        l5.L5GraphReader = _BrokenReader  # type: ignore[attr-defined]
    else:

        class _FakeReader:
            def __init__(self, *a, **k):
                pass

            def find_similar_tasks(self, goal, top_k=5):
                return (episodes or [])[:top_k]

        l5.L5GraphReader = _FakeReader  # type: ignore[attr-defined]

    pkg.runtime = runtime_pkg
    monkeypatch.setitem(sys.modules, "arifosmcp", pkg)
    monkeypatch.setitem(sys.modules, "arifosmcp.runtime", runtime_pkg)
    monkeypatch.setitem(sys.modules, FAKE_MOD, l5)


def _set_health(monkeypatch, health):
    monkeypatch.setattr(gtg, "_probe_graph_health", lambda: health)


# ── wants_graph_tier ─────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "payload,expected",
    [
        ({"tier_hint": "L5"}, True),
        ({"tier": "L5"}, True),
        ({"tier": "l5"}, True),          # case-insensitive
        ({"backend": "graph"}, True),
        ({"backend": "FalkorDB"}, True),  # case-insensitive
        ({"backend": "falkordb"}, True),
        ({"tier": "L3"}, False),
        ({"tier": "L4"}, False),
        ({"backend": "qdrant"}, False),
        ({}, False),
        (None, False),
        ("not-a-dict", False),
    ],
)
def test_wants_graph_tier(payload, expected):
    assert wants_graph_tier(payload) is expected


# ── gate: backend DOWN → UNMEASURED, never vector ────────────────────────────


def test_gate_body_says_degraded_returns_unmeasured(monkeypatch):
    """D2 regression: transport OK, body degraded → UNMEASURED."""
    _install_fake_reader(monkeypatch, episodes=[{"task_id": "t1"}])
    _set_health(monkeypatch, {"status": "degraded", "falkordb": "disconnected"})
    res = graph_tier_gate("query", {"tier_hint": "L5", "query": "PETRONAS"})
    assert res["intercepted"] is True and res["hold"] is True
    p = res["payload"]
    assert p["error"] == "GRAPH_BACKEND_UNAVAILABLE"
    assert p["measurement_status"] == "UNMEASURED"
    assert "results" not in p  # never vector results wearing graph's clothes
    assert p["graph_health"]["falkordb"] == "disconnected"


def test_gate_probe_unreachable_returns_unmeasured(monkeypatch):
    _install_fake_reader(monkeypatch)
    _set_health(monkeypatch, {"status": "degraded", "error": "connection refused"})
    res = graph_tier_gate("query", {"backend": "graph"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["measurement_status"] == "UNMEASURED"


def test_gate_reader_import_failure_returns_unmeasured(monkeypatch):
    _set_health(monkeypatch, {"status": "healthy"})
    monkeypatch.setitem(sys.modules, FAKE_MOD, None)  # forces ImportError
    res = graph_tier_gate("query", {"backend": "graph"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["measurement_status"] == "UNMEASURED"


def test_gate_string_shaped_degraded_returns_unmeasured(monkeypatch):
    _install_fake_reader(monkeypatch)
    _set_health(monkeypatch, "degraded")
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is True


# ── gate: backend UP → graph-backed answer with provenance ───────────────────


def test_gate_healthy_body_serves_graph_results(monkeypatch):
    episodes = [
        {"task_id": "t1", "goal": "revive falkordb", "provenance": "graphiti_l5"},
        {"task_id": "t2", "goal": "fix memory gate", "provenance": "graphiti_l5"},
    ]
    _install_fake_reader(monkeypatch, episodes=episodes)
    _set_health(monkeypatch, {"status": "healthy", "falkordb": "connected"})
    res = graph_tier_gate("query", {"tier_hint": "L5", "query": "falkordb"})
    assert res["intercepted"] is True and res["hold"] is False
    p = res["payload"]
    assert p["backend"] == "falkordb-graph"
    assert p["measurement_status"] == "MEASURED"
    assert p["count"] == 2
    assert all(r.get("provenance") for r in p["results"])


def test_gate_healthy_string_shape_serves_graph(monkeypatch):
    _install_fake_reader(monkeypatch, episodes=[{"task_id": "t9", "provenance": "g"}])
    _set_health(monkeypatch, "healthy")
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["hold"] is False and res["payload"]["measurement_status"] == "MEASURED"


def test_gate_healthy_but_reader_raises_returns_unmeasured(monkeypatch):
    _install_fake_reader(monkeypatch, broken=True)
    _set_health(monkeypatch, {"status": "healthy"})
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["error"] == "GRAPH_QUERY_FAILED"


# ── regression: normal path untouched ────────────────────────────────────────


def test_vector_payload_not_intercepted():
    assert wants_graph_tier({"tier_hint": None, "backend": None}) is False
    assert wants_graph_tier({"query": "plain vector recall"}) is False

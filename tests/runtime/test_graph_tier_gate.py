"""Tests for arifosmcp.runtime.graph_tier_gate — F2/VOID-GUARD for graph-tier recall.

Deterministic cross-check for the 2026-09-13 fix (session SEAL-64d8d16afb864e0d).
The gate module is dependency-light by design; these tests inject a fake
l5_graph_read module chain into sys.modules so no kernel runtime is required.

Defect being guarded: tier="L5"/backend="graph" silently answered from Qdrant
with SUCCESS. Law: "no data" ≠ "all clear".
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.graph_tier_gate import (  # noqa: E402
    graph_tier_gate,
    wants_graph_tier,
)

FAKE_MOD = "arifosmcp.runtime.l5_graph_read"


def _install_fake_l5(monkeypatch, health: str, episodes: list | None = None):
    """Install a fake arifosmcp.runtime.l5_graph_read module chain."""
    pkg = types.ModuleType("arifospkg")  # placeholder name, replaced below
    pkg = types.ModuleType("arifosmcp")
    runtime_pkg = types.ModuleType("arifosmcp.runtime")
    l5 = types.ModuleType(FAKE_MOD)

    class _FakeReader:
        def __init__(self, *a, **k):
            pass

        def find_similar_tasks(self, goal, top_k=5):
            return (episodes or [])[:top_k]

    l5.L5GraphReader = _FakeReader  # type: ignore[attr-defined]
    l5.l5_health_check = lambda: health  # type: ignore[attr-defined]
    pkg.runtime = runtime_pkg
    monkeypatch.setitem(sys.modules, "arifosmcp", pkg)
    monkeypatch.setitem(sys.modules, "arifosmcp.runtime", runtime_pkg)
    monkeypatch.setitem(sys.modules, FAKE_MOD, l5)


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


def test_gate_down_returns_unmeasured_hold(monkeypatch):
    _install_fake_l5(monkeypatch, health="degraded")
    res = graph_tier_gate("query", {"tier_hint": "L5", "query": "PETRONAS"})
    assert res["intercepted"] is True
    assert res["hold"] is True
    p = res["payload"]
    assert p["error"] == "GRAPH_BACKEND_UNAVAILABLE"
    assert p["measurement_status"] == "UNMEASURED"
    assert "results" not in p  # never vector results wearing graph's clothes
    assert p["graph_health"] == "degraded"


def test_gate_import_failure_returns_unmeasured(monkeypatch):
    monkeypatch.setitem(sys.modules, FAKE_MOD, None)  # forces ImportError
    res = graph_tier_gate("query", {"backend": "graph"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["measurement_status"] == "UNMEASURED"


def test_gate_health_probe_exception_returns_unmeasured(monkeypatch):
    _install_fake_l5(monkeypatch, health="healthy")
    import arifosmcp.runtime.l5_graph_read as l5mod  # the fake

    def boom():
        raise RuntimeError("probe crashed")

    l5mod.l5_health_check = boom  # type: ignore[attr-defined]
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["measurement_status"] == "UNMEASURED"


# ── gate: backend UP → graph-backed answer with provenance ───────────────────


def test_gate_healthy_dict_shaped_health_serves_graph(monkeypatch):
    """Live-observed 2026-09-13: l5_health_check() returns a dict, not a str.
    A naive string compare failed closed on a HEALTHY backend."""
    episodes = [{"task_id": "t9", "goal": "x", "provenance": "graphiti_l5"}]
    _install_fake_l5(monkeypatch, health="irrelevant-unused", episodes=episodes)
    import arifosmcp.runtime.l5_graph_read as l5mod  # the fake

    l5mod.l5_health_check = lambda: {"status": "healthy", "l5_enabled": True}  # type: ignore[attr-defined]
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is False
    assert res["payload"]["measurement_status"] == "MEASURED"
    assert res["payload"]["count"] == 1


def test_gate_healthy_serves_graph_results(monkeypatch):
    episodes = [
        {
            "task_id": "t1",
            "goal": "revive falkordb",
            "domain": "infra",
            "provenance": "graphiti_l5",
            "similarity_score": 0.91,
        },
        {
            "task_id": "t2",
            "goal": "fix memory gate",
            "domain": "kernel",
            "provenance": "graphiti_l5",
            "similarity_score": 0.72,
        },
    ]
    _install_fake_l5(monkeypatch, health="healthy", episodes=episodes)
    res = graph_tier_gate("query", {"tier_hint": "L5", "query": "falkordb"})
    assert res["intercepted"] is True
    assert res["hold"] is False
    p = res["payload"]
    assert p["backend"] == "falkordb-graph"
    assert p["measurement_status"] == "MEASURED"
    assert p["count"] == 2
    assert all(r.get("provenance") for r in p["results"])


def test_gate_healthy_but_query_raises_returns_unmeasured(monkeypatch):
    _install_fake_l5(monkeypatch, health="healthy")
    import arifosmcp.runtime.l5_graph_read as l5mod  # the fake

    class _BrokenReader:
        def __init__(self, *a, **k):
            raise RuntimeError("reader init boom")

    l5mod.L5GraphReader = _BrokenReader  # type: ignore[attr-defined]
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["error"] == "GRAPH_QUERY_FAILED"


# ── regression: normal path untouched ────────────────────────────────────────


def test_vector_payload_not_intercepted():
    assert wants_graph_tier({"tier_hint": None, "backend": None}) is False
    assert wants_graph_tier({"query": "plain vector recall"}) is False

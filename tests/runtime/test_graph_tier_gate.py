"""Tests for arifosmcp.runtime.graph_tier_gate — F2/VOID-GUARD for graph-tier recall.

Deterministic cross-check for the 2026-09-13 fixes (session SEAL-64d8d16afb864e0d).
Three defects guarded:
  D1: tier="L5"/backend="graph" silently answered from Qdrant with SUCCESS.
  D2: transport-level "healthy" over a body that says degraded/disconnected
      (MEASURED graph answer over a stopped FalkorDB — reproduced live).
  D3: write-only graph — reader searched Task nodes only; every forge-written
      Episode invisible to graph recall (found by external hostile re-probe).

The gate module is stdlib-only by design; tests patch _probe_graph_health and
_graph_recall — no kernel runtime required.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime import graph_tier_gate as gtg  # noqa: E402
from arifosmcp.runtime.graph_tier_gate import (  # noqa: E402
    graph_tier_gate,
    wants_graph_tier,
)


def _set_health(monkeypatch, health):
    monkeypatch.setattr(gtg, "_probe_graph_health", lambda: health)


def _set_recall(monkeypatch, results):
    monkeypatch.setattr(gtg, "_graph_recall", lambda q, k=5: results)


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
    _set_health(monkeypatch, {"status": "degraded", "falkordb": "disconnected"})
    res = graph_tier_gate("query", {"tier_hint": "L5", "query": "PETRONAS"})
    assert res["intercepted"] is True and res["hold"] is True
    p = res["payload"]
    assert p["error"] == "GRAPH_BACKEND_UNAVAILABLE"
    assert p["measurement_status"] == "UNMEASURED"
    assert "results" not in p  # never vector results wearing graph's clothes
    assert p["graph_health"]["falkordb"] == "disconnected"


def test_gate_probe_unreachable_returns_unmeasured(monkeypatch):
    _set_health(monkeypatch, {"status": "degraded", "error": "connection refused"})
    res = graph_tier_gate("query", {"backend": "graph"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["measurement_status"] == "UNMEASURED"


def test_gate_string_shaped_degraded_returns_unmeasured(monkeypatch):
    _set_health(monkeypatch, "degraded")
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is True


# ── gate: backend UP → graph-backed EPISODE recall with provenance ───────────


def test_gate_healthy_body_serves_episode_recall(monkeypatch):
    """D3 regression: forged episodes must be retrievable, with provenance."""
    episodes = [
        {
            "name": "L5 Reality Graph Outage",
            "summary": "falkordb.service misconfigured...",
            "memory_id": "boundary-l5-outage-2026-09",
            "actor_id": "kimi-code/FI-008",
            "session_id": "SEAL-64d8d16afb864e0d",
            "created_at": "2026-09-13T01:10:44Z",
            "score": 0.671,
            "provenance": "falkordb-graph",
        },
        {
            "name": "Void-guard fix",
            "summary": "gate added...",
            "memory_id": "m2",
            "actor_id": "kimi-code/FI-008",
            "session_id": "SEAL-64d8d16afb864e0d",
            "created_at": "2026-09-13T00:58:18Z",
            "score": 0.44,
            "provenance": "falkordb-graph",
        },
    ]
    _set_health(monkeypatch, {"status": "healthy", "falkordb": "connected"})
    _set_recall(monkeypatch, episodes)
    res = graph_tier_gate("query", {"tier_hint": "L5", "query": "boundary marker FalkorDB recovery"})
    assert res["intercepted"] is True and res["hold"] is False
    p = res["payload"]
    assert p["backend"] == "falkordb-graph"
    assert p["measurement_status"] == "MEASURED"
    assert p["count"] == 2
    top = p["results"][0]
    assert top["name"] == "L5 Reality Graph Outage"
    # provenance contract: actor + session + memory_id + created_at on every hit
    assert all(
        r.get("actor_id") and r.get("session_id") and r.get("memory_id") and r.get("created_at")
        for r in p["results"]
    )
    assert all(r.get("provenance") == "falkordb-graph" for r in p["results"])


def test_gate_healthy_string_shape_serves_graph(monkeypatch):
    _set_health(monkeypatch, "healthy")
    _set_recall(monkeypatch, [])
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["hold"] is False
    assert res["payload"]["measurement_status"] == "MEASURED"
    assert res["payload"]["count"] == 0  # honest empty, not an error


def test_gate_healthy_but_recall_raises_returns_unmeasured(monkeypatch):
    _set_health(monkeypatch, {"status": "healthy"})

    def boom(q, k=5):
        raise RuntimeError("search api 500")

    monkeypatch.setattr(gtg, "_graph_recall", boom)
    res = graph_tier_gate("query", {"tier": "L5"})
    assert res["intercepted"] is True and res["hold"] is True
    assert res["payload"]["error"] == "GRAPH_QUERY_FAILED"
    assert res["payload"]["measurement_status"] == "UNMEASURED"


# ── regression: normal path untouched ────────────────────────────────────────


def test_vector_payload_not_intercepted():
    assert wants_graph_tier({"tier_hint": None, "backend": None}) is False
    assert wants_graph_tier({"query": "plain vector recall"}) is False

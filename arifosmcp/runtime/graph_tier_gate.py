"""
arifosmcp/runtime/graph_tier_gate.py
═══════════════════════════════════════════════════════════════════════════
F2/VOID-GUARD for graph-tier memory recall (2026-09-13)

DEFECT (reproduced twice — external Claude probe + FI-008, same session):
  arif_memory called with tier="L5" / payload.backend="graph" accepted the
  parameters, then silently answered from the Qdrant vector store and reported
  SUCCESS. Two silent-failure paths in one surface.

DEFECT-2 (reproduced live 2026-09-13, down-branch test):
  l5_graph_read.l5_health_check() reports "healthy" when the HTTP transport to
  l5-search-api succeeds — even when the body says
  {'status':'degraded','falkordb':'disconnected'}. The gate then answered
  MEASURED over a stopped FalkorDB. A measurement surface reporting success
  over a store it didn't query. The gate therefore probes the /health BODY
  itself and requires body.status == 'healthy'.

LAW (Witness-First / Void Guard):
  "No data" ≠ "All clear". "No data" = "Cannot witness."
  A graph-tier request whose backend is down must return UNMEASURED — never
  vector results wearing graph's clothes.

CONTRACT:
  wants_graph_tier(payload) -> bool
      Pure detection. True if the caller asked for the graph tier.

  graph_tier_gate(mode, payload) -> dict
      Keys: intercepted (bool), hold (bool), payload (dict).
        intercepted=False            → proceed on normal (vector) path.
        intercepted=True, hold=True  → return UNMEASURED HOLD envelope.
        intercepted=True, hold=False → serve graph-backed results.

  Deliberately stdlib-only (urllib probe + urllib recall) so it stays
  unit-testable in complete isolation — no arifosmcp imports at all.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import urllib.request
from typing import Any

logger = logging.getLogger(__name__)

# Values that mean "the caller asked for the graph tier".
_GRAPH_TIERS = {"L5"}
_GRAPH_BACKENDS = {"graph", "falkordb", "falkor", "l5-graph"}

_UNMEASURED_NOTE = (
    "Graph tier (L5) requested but the graph backend (FalkorDB via "
    "l5-search-api :8001) is not available. Vector fallback suppressed — "
    "'no data' is not 'all clear' (F2 void-guard, 2026-09-13, "
    "session SEAL-64d8d16afb864e0d)."
)


def wants_graph_tier(payload: Any) -> bool:
    """Pure detection — did the caller ask for the graph tier?"""
    if not isinstance(payload, dict):
        return False
    tier = str(payload.get("tier_hint") or payload.get("tier") or "").strip().upper()
    backend = str(payload.get("backend") or "").strip().lower()
    return tier in _GRAPH_TIERS or backend in _GRAPH_BACKENDS


def _probe_graph_health() -> dict[str, Any]:
    """Probe the l5-search-api /health BODY — transport success is not health.

    Returns the parsed body dict on HTTP success, or a degraded dict on any
    failure. Callers decide health via _health_ok().
    """
    base = os.environ.get("GRAPHITI_MCP_URL", "http://localhost:8001").rstrip("/")
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=3) as resp:
            body = json.loads(resp.read().decode())
        return body if isinstance(body, dict) else {"status": "degraded", "error": "non-dict body"}
    except Exception as exc:
        return {"status": "degraded", "error": str(exc)}


def _health_ok(health: Any) -> bool:
    """Accept both str ('healthy'/'degraded') and dict ({'status': ...}) shapes."""
    if isinstance(health, dict):
        return str(health.get("status", "")).strip().lower() == "healthy"
    return str(health).strip().lower() == "healthy"


def _graph_recall(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    """Episode recall via l5-search-api /search/semantic.

    R1 (2026-09-13): replaces L5GraphReader.find_similar_tasks, which searched
    Task nodes only — every forge-written Episode was invisible to graph
    recall. Returns episodes incl. provenance (actor_id, session_id,
    memory_id, created_at). min_score floor kept low (0.3): the gate wants
    recall + ranking; relevance ordering comes back in `score`.
    """
    base = os.environ.get("GRAPHITI_MCP_URL", "http://localhost:8001").rstrip("/")
    body = json.dumps({"query": query, "max_results": top_k, "min_score": 0.3}).encode()
    req = urllib.request.Request(
        f"{base}/search/semantic",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        payload = json.loads(resp.read().decode())
    out = []
    for r in payload.get("results", []):
        if not isinstance(r, dict):
            continue
        out.append(
            {
                "name": r.get("name", ""),
                "summary": r.get("summary", ""),
                "memory_id": r.get("memory_id", ""),
                "actor_id": r.get("actor_id", ""),
                "session_id": r.get("session_id", ""),
                "created_at": r.get("created_at", ""),
                "score": r.get("score"),
                "provenance": "falkordb-graph",
            }
        )
    return out


def graph_tier_gate(mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Gate a graph-tier memory request. See module docstring for contract."""
    base = {"mode": mode}

    health = _probe_graph_health()
    if not _health_ok(health):
        return {
            "intercepted": True,
            "hold": True,
            "payload": {
                **base,
                "error": "GRAPH_BACKEND_UNAVAILABLE",
                "measurement_status": "UNMEASURED",
                "message": _UNMEASURED_NOTE,
                "graph_health": health,
            },
        }

    # Backend healthy → serve graph-backed episode recall with provenance.
    query_text = str(payload.get("query") or payload.get("goal") or "")
    try:
        top_k = int(payload.get("top_k") or 5)
    except (TypeError, ValueError):
        top_k = 5
    try:
        results = _graph_recall(query_text, top_k)
        return {
            "intercepted": True,
            "hold": False,
            "payload": {
                **base,
                "backend": "falkordb-graph",
                "measurement_status": "MEASURED",
                "graph_health": health,
                "message": "Graph tier (L5) served from FalkorDB via l5-search-api.",
                "results": results,
                "count": len(results),
            },
        }
    except Exception as exc:
        # Healthy probe but query failed → still loud, still UNMEASURED.
        return {
            "intercepted": True,
            "hold": True,
            "payload": {
                **base,
                "error": "GRAPH_QUERY_FAILED",
                "measurement_status": "UNMEASURED",
                "message": f"Graph backend reported healthy but the query raised: {exc}.",
            },
        }

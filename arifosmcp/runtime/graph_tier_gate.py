"""
arifosmcp/runtime/graph_tier_gate.py
═══════════════════════════════════════════════════════════════════════════
F2/VOID-GUARD for graph-tier memory recall (2026-09-13)

DEFECT (reproduced twice — external Claude probe + FI-008, same session):
  arif_memory called with tier="L5" / payload.backend="graph" accepted the
  parameters, then silently answered from the Qdrant vector store and reported
  SUCCESS. Two silent-failure paths in one surface.

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

  This module is deliberately dependency-light (stdlib only at import time;
  l5_graph_read imported lazily) so it stays unit-testable in isolation.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
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


def _health_ok(health: Any) -> bool:
    """l5_health_check() returns either a string ('healthy'/'degraded') or a
    dict ({'status': 'healthy', 'l5_enabled': ...}). Observed live 2026-09-13:
    dict shape — a naive `!= 'healthy'` string compare failed CLOSED even when
    the backend was up (safe direction, wrong behaviour). Normalize both."""
    if isinstance(health, dict):
        return str(health.get("status", "")).strip().lower() == "healthy"
    return str(health).strip().lower() == "healthy"


def graph_tier_gate(mode: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Gate a graph-tier memory request. See module docstring for contract."""
    base = {"mode": mode}

    # Lazy import: keeps this module unit-testable and import-cycle-free.
    try:
        from arifosmcp.runtime.l5_graph_read import L5GraphReader, l5_health_check
    except Exception as exc:  # ImportError or anything the module raises on load
        return {
            "intercepted": True,
            "hold": True,
            "payload": {
                **base,
                "error": "GRAPH_BACKEND_UNAVAILABLE",
                "measurement_status": "UNMEASURED",
                "message": f"Graph read module failed to import: {exc}. {_UNMEASURED_NOTE}",
            },
        }

    try:
        health = l5_health_check()
    except Exception as exc:
        return {
            "intercepted": True,
            "hold": True,
            "payload": {
                **base,
                "error": "GRAPH_BACKEND_UNAVAILABLE",
                "measurement_status": "UNMEASURED",
                "message": f"Graph health probe raised: {exc}. {_UNMEASURED_NOTE}",
            },
        }

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

    # Backend healthy → serve graph-backed results with provenance.
    try:
        reader = L5GraphReader()
        goal = str(payload.get("query") or payload.get("goal") or "")
        try:
            top_k = int(payload.get("top_k") or 5)
        except (TypeError, ValueError):
            top_k = 5
        results = reader.find_similar_tasks(goal=goal or "*", top_k=top_k)
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

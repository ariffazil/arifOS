"""
arifosmcp/runtime/l5_graph_read.py — L5 Graphiti READ Path v1
════════════════════════════════════════════════════════════════════

THE READ COUNTERPART to l5_graphiti_bridge.py (write-only).

L5 Graphiti stores episodic knowledge as entity graphs in FalkorDB.
l5_graphiti_bridge.py writes episodes (fire-and-forget).
THIS file reads them back — enabling:

  1. find_similar_tasks(goal)    → "Have we done this before?"
  2. get_capability_subgraph()   → "What tools/paths exist for this domain?"
  3. get_prior_path(signature)   → "What was the last plan for this task?"
  4. get_mind_state(context_id)  → "Restore a checkpointed MIND state"

ARCHITECTURE
────────────
  l5_graphiti_bridge.py  →  WRITE  →  Graphiti  →  FalkorDB
  l5_graph_read.py       →  READ   ←  Graphiti  ←  FalkorDB
  feedback_loop.py       →  uses both for closed-loop reasoning

FAILURE MODE
────────────
  F1 AMANAH: Graphiti read failure must NEVER block reasoning.
  If Graphiti is down, return empty/fresh defaults. Reasoning continues
  with Qdrant-only memory. L5 is enrichment, not requirement.

FLOOR BINDING
─────────────
  F02 (TRUTH)  — all retrieved episodes tagged with provenance
  F08 (GENIUS) — query timeout cap prevents stalling
  F09 (ANTIHANTU) — retrieved content is factual, not simulated memory

AUTHORITY: 555_MEMORY, 333_MIND
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
_GRAPHITI_URL = os.getenv("GRAPHITI_MCP_URL", "http://localhost:8001")  # L5 Search API
_GRAPHITI_GROUP_ID = os.getenv("GRAPHITI_GROUP_ID", "af_forge")
_GRAPHITI_TIMEOUT_S = float(os.getenv("GRAPHITI_READ_TIMEOUT_S", "3.0"))
_GRAPHITI_ENABLED = os.getenv("GRAPHITI_L5_ENABLED", "true").lower() == "true"
_MAX_RESULTS = int(os.getenv("GRAPHITI_READ_MAX_RESULTS", "10"))


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP CLIENT (zero external deps — urllib only)
# ═══════════════════════════════════════════════════════════════════════════════


def _graphiti_get(path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
    """GET from Graphiti MCP, with timeout and error handling."""
    if not _GRAPHITI_ENABLED:
        return {"error": "L5 disabled", "results": []}

    import urllib.error
    import urllib.parse
    import urllib.request

    url = f"{_GRAPHITI_URL.rstrip('/')}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)

    try:
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=_GRAPHITI_TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.URLError as e:
        logger.warning("l5_graph_read: Graphiti unreachable — %s", e)
        return {"error": str(e), "results": []}
    except json.JSONDecodeError:
        logger.warning("l5_graph_read: Graphiti returned non-JSON")
        return {"error": "non-JSON response", "results": []}
    except Exception as e:
        logger.warning("l5_graph_read: unexpected — %s", e)
        return {"error": str(e), "results": []}


def _graphiti_post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    """POST to Graphiti MCP, with timeout and error handling."""
    if not _GRAPHITI_ENABLED:
        return {"error": "L5 disabled", "results": []}

    import urllib.error
    import urllib.request

    url = f"{_GRAPHITI_URL.rstrip('/')}{path}"
    data = json.dumps(body).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        with urllib.request.urlopen(req, timeout=_GRAPHITI_TIMEOUT_S) as resp:
            resp_body = resp.read().decode("utf-8")
            return json.loads(resp_body) if resp_body else {}
    except urllib.error.URLError as e:
        logger.warning("l5_graph_read: POST to Graphiti failed — %s", e)
        return {"error": str(e), "results": []}
    except Exception as e:
        logger.warning("l5_graph_read: POST unexpected — %s", e)
        return {"error": str(e), "results": []}


# ═══════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════════════════


def find_similar_tasks(
    goal: str,
    top_k: int = 5,
    domain: str | None = None,
) -> list[dict[str, Any]]:
    """Find prior tasks similar to the given goal.

    Queries Graphiti entity graph for episodes with similar goals.
    Returns ranked list of {task_id, goal, domain, steps_count,
    outcome, epistemic_band, timestamp, similarity_score}.

    Used by: feedback_loop.py to bootstrap plan skeletons.

    F2 TRUTH: every result tagged with provenance = "graphiti_l5".
    """
    if not _GRAPHITI_ENABLED:
        return []

    # Build search query
    query = {
        "query": goal,
        "group_id": _GRAPHITI_GROUP_ID,
        "max_results": min(top_k, _MAX_RESULTS),
    }
    if domain:
        query["filter"] = {"domain": domain}

    resp = _graphiti_post("/search/episodes", query)

    if "error" in resp:
        logger.info("l5_graph_read: find_similar_tasks returned error — %s", resp["error"])
        return []

    results = resp.get("results", resp.get("episodes", []))
    return [
        {
            "task_id": r.get("uuid", r.get("episode_id", "")),
            "goal": r.get("goal", r.get("summary", "")),
            "domain": r.get("domain", "unknown"),
            "steps_count": r.get("total_steps", 0),
            "outcome": r.get("plan_status", "unknown"),
            "epistemic_band": r.get("epistemic_band", 0.5),
            "timestamp": r.get("created_at", r.get("timestamp", "")),
            "similarity_score": r.get("score", r.get("similarity", 0.0)),
            "provenance": "graphiti_l5",
        }
        for r in results[:top_k]
    ]


def get_capability_subgraph(
    domain: str = "general",
    tools: list[str] | None = None,
) -> dict[str, Any]:
    """Retrieve the capability subgraph for a domain.

    Returns {nodes: [...], edges: [...]} where nodes are tools/operations
    and edges are data flow / dependency relationships.

    Used by: graph-based planner to constrain what tools are considered.

    F2 TRUTH: returns empty subgraph + provenance if L5 unavailable.
    """
    if not _GRAPHITI_ENABLED:
        return {
            "nodes": [],
            "edges": [],
            "provenance": "l5_disabled",
            "domain": domain,
        }

    query: dict[str, Any] = {
        "group_id": _GRAPHITI_GROUP_ID,
        "domain": domain,
    }
    if tools:
        query["tools"] = tools

    resp = _graphiti_post("/graph/capability", query)

    if "error" in resp:
        logger.info("l5_graph_read: get_capability_subgraph error — %s", resp["error"])
        return {
            "nodes": [],
            "edges": [],
            "provenance": "l5_error",
            "domain": domain,
            "error": resp["error"],
        }

    return {
        "nodes": resp.get("nodes", []),
        "edges": resp.get("edges", []),
        "provenance": "graphiti_l5",
        "domain": domain,
        "retrieved_at": datetime.now(UTC).isoformat(),
    }


def get_prior_path(
    task_signature: str,
) -> list[dict[str, Any]] | None:
    """Retrieve the most recent reasoning path for a task signature.

    A "task signature" is a stable hash of goal + domain + constraints.
    Returns the step sequence from the most recent successful execution,
    or None if no prior path exists.

    Used by: Sequential Thinking to adapt prior plans instead of
    starting from zero.
    """
    if not _GRAPHITI_ENABLED:
        return None

    sig_hash = hashlib.sha256(task_signature.encode()).hexdigest()[:16]

    resp = _graphiti_get(
        "/episodes/path",
        params={"signature": sig_hash, "group_id": _GRAPHITI_GROUP_ID},
    )

    if "error" in resp or not resp.get("steps"):
        return None

    return resp.get("steps", [])


def get_mind_state_checkpoint(
    context_id: str,
) -> dict[str, Any] | None:
    """Retrieve a checkpointed MIND state from Graphiti.

    Returns the full MINDState snapshot dict, or None if not found.
    Used to resume reasoning across sessions.
    """
    if not _GRAPHITI_ENABLED:
        return None

    resp = _graphiti_get(
        "/episodes/checkpoint",
        params={"context_id": context_id, "group_id": _GRAPHITI_GROUP_ID},
    )

    if "error" in resp or not resp.get("snapshot"):
        return None

    snapshot = resp["snapshot"]
    snapshot["provenance"] = "graphiti_l5_checkpoint"
    snapshot["retrieved_at"] = datetime.now(UTC).isoformat()
    return snapshot


def search_by_embedding(
    query_text: str,
    top_k: int = 5,
    threshold: float = 0.6,
) -> list[dict[str, Any]]:
    """Semantic search over L5 episodes using embedding similarity.

    This is the "don't start from zero" function — given a new task
    description, find prior episodes with similar semantic content.

    Falls back to keyword search if embedding not available.
    """
    if not _GRAPHITI_ENABLED:
        return []

    resp = _graphiti_post(
        "/search/semantic",
        {
            "query": query_text,
            "group_id": _GRAPHITI_GROUP_ID,
            "max_results": min(top_k, _MAX_RESULTS),
            "min_score": threshold,
        },
    )

    if "error" in resp:
        logger.info("l5_graph_read: semantic search error — %s", resp["error"])
        return []

    results = resp.get("results", resp.get("episodes", []))
    return [
        {
            "episode_id": r.get("uuid", r.get("episode_id", "")),
            "content": r.get("summary", r.get("content", ""))[:500],
            "score": r.get("score", r.get("similarity", 0.0)),
            "timestamp": r.get("created_at", r.get("timestamp", "")),
            "provenance": "graphiti_l5_semantic",
        }
        for r in results[:top_k]
    ]


def l5_health_check() -> dict[str, Any]:
    """Quick health probe for the L5 read path."""
    if not _GRAPHITI_ENABLED:
        return {"status": "disabled", "l5_enabled": False}

    start = time.monotonic()
    resp = _graphiti_get("/health")
    latency = time.monotonic() - start

    return {
        "status": "healthy" if "error" not in resp else "degraded",
        "l5_enabled": True,
        "url": _GRAPHITI_URL,
        "latency_s": round(latency, 3),
        "error": resp.get("error"),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH READER ADAPTER (implements GraphReader protocol from feedback_loop.py)
# ═══════════════════════════════════════════════════════════════════════════════


class L5GraphReader:
    """Adapter: wraps l5_graph_read functions as GraphReader protocol.

    Implements the GraphReader protocol from feedback_loop.py.
    Drop-in replacement for NoOpGraphReader when L5 is available.
    """

    def find_similar_tasks(
        self,
        goal: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        return find_similar_tasks(goal=goal, top_k=top_k)

    def get_capability_subgraph(
        self,
        domain: str,
        tools: list[str] | None = None,
    ) -> dict[str, Any]:
        return get_capability_subgraph(domain=domain, tools=tools)

    def get_prior_path(
        self,
        task_signature: str,
    ) -> list[dict[str, Any]] | None:
        return get_prior_path(task_signature=task_signature)


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH WRITER ADAPTER (implements GraphWriter protocol from feedback_loop.py)
# ═══════════════════════════════════════════════════════════════════════════════


class L5GraphWriter:
    """Adapter: writes feedback signals to L5 Graphiti.

    Implements the GraphWriter protocol from feedback_loop.py.
    Drop-in replacement for NoOpGraphWriter when L5 is available.
    """

    def update_edge_weight(
        self,
        source_node: str,
        target_node: str,
        delta: float,
        reason: str = "",
    ) -> bool:
        """Update an edge weight in the capability graph."""
        if not _GRAPHITI_ENABLED:
            return False
        resp = _graphiti_post(
            "/graph/edge/weight",
            {
                "source": source_node,
                "target": target_node,
                "delta": delta,
                "reason": reason,
                "group_id": _GRAPHITI_GROUP_ID,
            },
        )
        return "error" not in resp

    def annotate_path(
        self,
        path_nodes: list[str],
        annotation: dict[str, Any],
    ) -> bool:
        """Annotate a path in the capability graph."""
        if not _GRAPHITI_ENABLED:
            return False
        resp = _graphiti_post(
            "/graph/path/annotate",
            {
                "nodes": path_nodes,
                "annotation": annotation,
                "group_id": _GRAPHITI_GROUP_ID,
            },
        )
        return "error" not in resp

    def record_episode(
        self,
        state,
        signal,
        metadata=None,
    ) -> str | None:
        """Record a completed reasoning episode in Graphiti."""
        if not _GRAPHITI_ENABLED:
            return None
        from arifosmcp.runtime.mind_state import MINDState

        if not isinstance(state, MINDState):
            return None

        body = {
            "memory_id": f"mind_{state.context_id}",
            "session_id": state.session_id,
            "goal": state.goal,
            "domain": state.domain,
            "total_steps": len(state.plan_steps),
            "total_revisions": state.total_revisions,
            "plan_status": state.plan_status.value,
            "epistemic_band": state.epistemic_band,
            "malu_index": state.malu_index,
            "final_signal": signal.value if hasattr(signal, "value") else str(signal),
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        resp = _graphiti_post(
            "/episodes",
            {
                "group_id": _GRAPHITI_GROUP_ID,
                "name": f"mind_episode_{state.context_id[:8]}",
                "episode_body": json.dumps(body, default=str),
                "source": "feedback_loop",
                "source_description": "arifOS MIND feedback loop",
            },
        )
        return resp.get("uuid") if "error" not in resp else None


__all__ = [
    "find_similar_tasks",
    "get_capability_subgraph",
    "get_prior_path",
    "get_mind_state_checkpoint",
    "search_by_embedding",
    "l5_health_check",
    "L5GraphReader",
    "L5GraphWriter",
]

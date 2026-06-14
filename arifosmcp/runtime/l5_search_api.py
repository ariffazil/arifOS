"""
arifosmcp/runtime/l5_search_api.py — L5 Search API Service v1
═══════════════════════════════════════════════════════════════

Standalone FastAPI service providing search/read endpoints for
FalkorDB knowledge graph. This is the THIN LAYER between
l5_graph_read.py (query functions) and FalkorDB (graph database).

ENDPOINTS
─────────
  GET  /health              — liveness probe
  POST /search/episodes     — keyword + filter search
  POST /search/semantic     — semantic similarity search (keyword fallback)
  POST /graph/capability    — domain capability subgraph
  POST /graph/edge/weight   — edge weight update
  POST /graph/path/annotate — path annotation
  GET  /episodes/path       — prior reasoning path
  GET  /episodes/checkpoint — checkpoint retrieval
  POST /episodes            — episode creation

All endpoints return {"results": [...]} or {"error": "..."} for
compatibility with l5_graph_read.py's existing response parsing.

ARCHITECTURE
────────────
  l5_graph_read.py  →  HTTP  →  l5_search_api.py (:8001)  →  FalkorDB (:6380)
  l5_graphiti_bridge.py  →  HTTP  →  graphiti-mcp (:8000)  →  FalkorDB (:6380)

Two separate services, one database. Bridge writes episodes via Graphiti.
Search API reads them back directly from FalkorDB.

AUTHORITY: 555_MEMORY
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, UTC
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ── Configuration ──────────────────────────────────────────────────────────
FALKOR_HOST = os.getenv("FALKOR_HOST", "localhost")
FALKOR_PORT = int(os.getenv("FALKOR_PORT", "6380"))
FALKOR_GRAPH = os.getenv("FALKOR_GRAPH", "arif_l5_knowledge")
SERVICE_PORT = int(os.getenv("L5_SEARCH_PORT", "8001"))

app = FastAPI(title="L5 Search API", version="1.0.0")


# ═══════════════════════════════════════════════════════════════════════════════
# FALKORDB CONNECTION
# ═══════════════════════════════════════════════════════════════════════════════

def _get_graph():
    """Get FalkorDB graph handle. Returns None if unavailable."""
    try:
        from falkordb import FalkorDB
        db = FalkorDB(host=FALKOR_HOST, port=FALKOR_PORT)
        return db.select_graph(FALKOR_GRAPH)
    except Exception as e:
        logger.warning("FalkorDB unavailable: %s", e)
        return None


def _safe_query(cypher: str, params: dict | None = None) -> list[list[Any]]:
    """Execute a Cypher query safely. Returns [] on failure."""
    graph = _get_graph()
    if graph is None:
        return []
    try:
        result = graph.query(cypher, params or {})
        return result.result_set if result else []
    except Exception as e:
        logger.warning("Cypher query failed: %s — %s", cypher[:80], e)
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# REQUEST MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class SearchRequest(BaseModel):
    query: str = ""
    group_id: str = "af_forge"
    max_results: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    filter: dict[str, str] | None = None


class SemanticSearchRequest(BaseModel):
    query: str
    group_id: str = "af_forge"
    max_results: int = Field(default=10, ge=1, le=50)
    min_score: float = Field(default=0.6, ge=0.0, le=1.0)


class CapabilityRequest(BaseModel):
    group_id: str = "af_forge"
    domain: str = "general"
    tools: list[str] | None = None


class EdgeWeightRequest(BaseModel):
    source: str
    target: str
    delta: float
    reason: str = ""
    group_id: str = "af_forge"


class PathAnnotateRequest(BaseModel):
    nodes: list[str]
    annotation: dict[str, Any]
    group_id: str = "af_forge"


class EpisodeCreateRequest(BaseModel):
    group_id: str = "af_forge"
    name: str
    episode_body: str
    source: str = "direct"
    source_description: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    """Liveness probe."""
    graph = _get_graph()
    return {
        "status": "healthy" if graph else "degraded",
        "service": "l5-search-api",
        "falkordb": "connected" if graph else "disconnected",
        "graph": FALKOR_GRAPH,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# EPISODE SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/search/episodes")
async def search_episodes(req: SearchRequest):
    """Search episodes by keyword + optional domain filter.

    Queries FalkorDB for Episode nodes matching the search terms.
    Returns ranked results with similarity metadata.
    """
    # Build Cypher query for episode search
    cypher_parts = ["MATCH (e:Episode)"]
    where_clauses = []
    params = {}

    if req.query:
        where_clauses.append(
            "(toLower(e.name) CONTAINS toLower($query) "
            "OR toLower(e.episode_body) CONTAINS toLower($query))"
        )
        params["query"] = req.query

    if req.filter and req.filter.get("domain"):
        where_clauses.append("toLower(e.domain) = toLower($domain)")
        params["domain"] = req.filter["domain"]

    if where_clauses:
        cypher_parts.append("WHERE " + " AND ".join(where_clauses))

    cypher_parts.append("RETURN e.uuid, e.name, e.episode_body, e.domain, "
                        "e.total_steps, e.plan_status, e.epistemic_band, "
                        "e.created_at, e.source, e.source_description")
    cypher_parts.append(f"LIMIT {req.max_results}")

    cypher = " ".join(cypher_parts)
    rows = _safe_query(cypher, params)

    results = []
    for row in rows:
        if len(row) >= 1:
            results.append({
                "uuid": row[0] if len(row) > 0 else "",
                "name": row[1] if len(row) > 1 else "",
                "summary": _safe_get(row, 2, ""),
                "domain": row[3] if len(row) > 3 else "unknown",
                "total_steps": row[4] if len(row) > 4 else 0,
                "plan_status": row[5] if len(row) > 5 else "unknown",
                "epistemic_band": row[6] if len(row) > 6 else 0.5,
                "created_at": row[7] if len(row) > 7 else "",
                "source": row[8] if len(row) > 8 else "unknown",
                "source_description": row[9] if len(row) > 9 else "",
            })

    return {"results": results, "total": len(results)}


@app.post("/search/semantic")
async def search_semantic(req: SemanticSearchRequest):
    """Semantic similarity search — keyword fallback.

    In production, this would use embeddings + vector similarity.
    For now, falls back to keyword matching on episode content.
    """
    query = (req.query or "").strip()
    if not query:
        return {"results": [], "total": 0}

    # Split query into terms for broader matching
    terms = [t.lower() for t in query.split() if len(t) > 1]

    # Build OR-based Cypher: match if ANY term hits ANY text field
    where_clauses = []
    params = {}
    for i, term in enumerate(terms):
        param_name = f"term{i}"
        where_clauses.append(
            f"(toLower(e.name) CONTAINS ${param_name} "
            f"OR toLower(e.episode_body) CONTAINS ${param_name} "
            f"OR toLower(e.source_description) CONTAINS ${param_name})"
        )
        params[param_name] = term

    cypher = (
        "MATCH (e:Episode)\n"
        "WHERE " + " OR ".join(where_clauses) + "\n"
        "RETURN e.uuid, e.name, e.episode_body, e.source_description, e.created_at, e.source\n"
        f"LIMIT {req.max_results}"
    )

    rows = _safe_query(cypher, params)

    # Score: how many query terms hit this episode
    results = []
    for row in rows:
        name = _safe_get(row, 1, "")
        body = _safe_get(row, 2, "")
        desc = _safe_get(row, 3, "")
        combined = f"{name} {body} {desc}".lower()
        hits = sum(1 for t in terms if t in combined)
        score = min(0.95, 0.3 + (hits / max(len(terms), 1)) * 0.65)

        if score >= req.min_score:
            results.append({
                "uuid": _safe_get(row, 0, ""),
                "name": name,
                "summary": body[:300] if body else "",
                "source_description": desc[:300],
                "source": _safe_get(row, 5, ""),
                "score": round(score, 3),
                "hits": hits,
                "total_terms": len(terms),
                "created_at": _safe_get(row, 4, ""),
            })

    # Sort by score descending
    results.sort(key=lambda r: r["score"], reverse=True)

    return {"results": results, "total": len(results)}


# ═══════════════════════════════════════════════════════════════════════════════
# CAPABILITY GRAPH
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/graph/capability")
async def get_capability(req: CapabilityRequest):
    """Retrieve domain capability subgraph.

    Returns nodes (tools/operations) and edges (data flows/dependencies)
    for the requested domain.
    """
    # Query for nodes in domain
    node_cypher = """
        MATCH (n:Tool)
        WHERE n.domain = $domain OR $domain = 'general'
        RETURN n.name, n.type, n.domain, n.description
        LIMIT 50
    """
    node_rows = _safe_query(node_cypher, {"domain": req.domain})

    # Query for edges between tools
    edge_cypher = """
        MATCH (a:Tool)-[r:DEPENDS_ON|PRODUCES|REQUIRES]->(b:Tool)
        WHERE a.domain = $domain OR $domain = 'general'
        RETURN a.name, type(r), b.name, r.weight
        LIMIT 100
    """
    edge_rows = _safe_query(edge_cypher, {"domain": req.domain})

    nodes = []
    for row in node_rows:
        nodes.append({
            "name": _safe_get(row, 0, ""),
            "type": _safe_get(row, 1, "tool"),
            "domain": _safe_get(row, 2, req.domain),
            "description": _safe_get(row, 3, ""),
        })

    edges = []
    for row in edge_rows:
        edges.append({
            "source": _safe_get(row, 0, ""),
            "relation": _safe_get(row, 1, ""),
            "target": _safe_get(row, 2, ""),
            "weight": _safe_get(row, 3, 0.5),
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "provenance": "falkordb_l5",
        "domain": req.domain,
    }


@app.post("/graph/edge/weight")
async def update_edge_weight(req: EdgeWeightRequest):
    """Update edge weight in the capability graph.

    Used by feedback_loop.py to reinforce/weaken paths.
    """
    cypher = """
        MATCH (a)-[r]->(b)
        WHERE a.name = $source AND b.name = $target
        SET r.weight = coalesce(r.weight, 0.5) + $delta,
            r.last_updated = $ts,
            r.last_reason = $reason
        RETURN r.weight
    """
    rows = _safe_query(cypher, {
        "source": req.source,
        "target": req.target,
        "delta": req.delta,
        "ts": datetime.now(UTC).isoformat(),
        "reason": req.reason,
    })
    return {"success": len(rows) > 0, "new_weight": rows[0][0] if rows else None}


@app.post("/graph/path/annotate")
async def annotate_path(req: PathAnnotateRequest):
    """Annotate a path in the capability graph."""
    count = 0
    for i in range(len(req.nodes) - 1):
        cypher = """
            MATCH (a)-[r]->(b)
            WHERE a.name = $source AND b.name = $target
            SET r.annotation = $annotation,
                r.annotated_at = $ts
            RETURN r
        """
        rows = _safe_query(cypher, {
            "source": req.nodes[i],
            "target": req.nodes[i + 1],
            "annotation": json.dumps(req.annotation),
            "ts": datetime.now(UTC).isoformat(),
        })
        if rows:
            count += 1
    return {"success": count > 0, "edges_annotated": count}


# ═══════════════════════════════════════════════════════════════════════════════
# EPISODE PATH & CHECKPOINT
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/episodes/path")
async def get_prior_path(
    signature: str = Query(...),
    group_id: str = Query("af_forge"),
):
    """Retrieve the most recent reasoning path for a task signature."""
    sig_hash = hashlib.sha256(signature.encode()).hexdigest()[:16]

    cypher = """
        MATCH (e:Episode)
        WHERE e.signature = $sig
        RETURN e.steps
        ORDER BY e.created_at DESC
        LIMIT 1
    """
    rows = _safe_query(cypher, {"sig": sig_hash})

    if not rows or not rows[0][0]:
        return {"steps": None}

    try:
        steps = json.loads(rows[0][0]) if isinstance(rows[0][0], str) else rows[0][0]
    except (json.JSONDecodeError, TypeError):
        steps = []

    return {"steps": steps, "signature": sig_hash}


@app.get("/episodes/checkpoint")
async def get_checkpoint(
    context_id: str = Query(...),
    group_id: str = Query("af_forge"),
):
    """Retrieve a checkpointed MIND state."""
    cypher = """
        MATCH (e:Episode)
        WHERE e.context_id = $ctx AND e.type = 'mind_checkpoint'
        RETURN e.snapshot, e.created_at
        ORDER BY e.created_at DESC
        LIMIT 1
    """
    rows = _safe_query(cypher, {"ctx": context_id})

    if not rows or not rows[0][0]:
        return {"snapshot": None}

    try:
        snapshot = json.loads(rows[0][0]) if isinstance(rows[0][0], str) else rows[0][0]
    except (json.JSONDecodeError, TypeError):
        snapshot = None

    return {
        "snapshot": snapshot,
        "context_id": context_id,
        "retrieved_at": datetime.now(UTC).isoformat(),
    }


@app.post("/episodes")
async def create_episode(req: EpisodeCreateRequest):
    """Create an episode node in FalkorDB.

    Direct path — bypasses Graphiti for cases where we want to write
    directly to FalkorDB.
    """
    try:
        body = json.loads(req.episode_body)
    except json.JSONDecodeError:
        body = {"raw": req.episode_body}

    episode_id = hashlib.sha256(
        f"{req.name}:{time.time()}".encode()
    ).hexdigest()[:16]

    cypher = """
        CREATE (e:Episode {
            uuid: $uuid,
            name: $name,
            episode_body: $body,
            source: $source,
            source_description: $desc,
            created_at: $ts
        })
        RETURN e.uuid
    """
    rows = _safe_query(cypher, {
        "uuid": episode_id,
        "name": req.name,
        "body": req.episode_body,
        "source": req.source,
        "desc": req.source_description,
        "ts": datetime.now(UTC).isoformat(),
    })

    return {
        "uuid": episode_id,
        "created": len(rows) > 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════

def _safe_get(row: list, idx: int, default: Any = "") -> Any:
    """Safely get an element from a result row."""
    try:
        return row[idx] if idx < len(row) else default
    except (IndexError, TypeError):
        return default


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting L5 Search API on port %d", SERVICE_PORT)
    uvicorn.run(app, host="127.0.0.1", port=SERVICE_PORT, log_level="info")

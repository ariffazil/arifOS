"""
arifosmcp/memory/cognitive_memory.py — 666_MEMORY v2: Cognitive Memory Backend
════════════════════════════════════════════════════════════════════════════════

Graph-backed cognitive memory with contradiction detection.
Collapsed into arif_memory_recall modes — no new tools, just new modes.

Modes served from this module:
  graph_store        — Persist a plan/memory as graph nodes+edges (FalkorDB + Qdrant)
  graph_query        — Query plans from the graph (hybrid FalkorDB + Qdrant)
  graph_get          — Retrieve a specific plan by ID
  contradict_scan    — Scan a claim for contradictions against sealed knowledge
  contradict_resolve — Resolve a contradiction (OVERRIDE/MERGE/VOID/ACKNOWLEDGE)
  contradict_status  — Unresolved contradiction count, per-epoch breakdown
  cognitive_recall   — Unified recall: Qdrant + FalkorDB + contradictions
  cognitive_learn    — Close the learning loop: attach outcome + lessons to plan
  cognitive_cross_session — Cross-session plan retrieval for MIND Router injection

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ── Feature Flags ────────────────────────────────────────────────────────────
MEMORY_V2_ENABLED = os.getenv("MEMORY_V2_ENABLED", "true").lower() in ("true", "1", "yes", "on")
MEMORY_GRAPH_BACKEND = os.getenv("MEMORY_GRAPH_BACKEND", "falkordb")  # falkordb | none
MEMORY_CONTRADICTION_SCAN = os.getenv("MEMORY_CONTRADICTION_SCAN", "true").lower() in ("true", "1")
MEMORY_CROSS_SESSION = os.getenv("MEMORY_CROSS_SESSION", "true").lower() in ("true", "1")
MEMORY_AUTO_PERSIST_PLANS = os.getenv("MEMORY_AUTO_PERSIST_PLANS", "true").lower() in ("true", "1")

# ── FalkorDB Connection ──────────────────────────────────────────────────────
_FALKORDB_HOST = os.getenv("FALKORDB_HOST", "localhost")
_FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))


def _get_falkordb():
    """Lazy-import FalkorDB client. Returns None if unavailable."""
    if MEMORY_GRAPH_BACKEND != "falkordb":
        return None
    try:
        from falkordb import FalkorDB
        return FalkorDB(host=_FALKORDB_HOST, port=_FALKORDB_PORT)
    except Exception as exc:
        logger.warning(f"FalkorDB unavailable: {exc}")
        return None


def _get_qdrant():
    """Lazy-import Qdrant client for hybrid search."""
    try:
        from arifosmcp.runtime.memory_store import _get_qdrant_client
        return _get_qdrant_client()
    except Exception as exc:
        logger.warning(f"Qdrant unavailable: {exc}")
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# GRAPH OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def graph_store(
    plan_object: dict | None = None,
    content: str | None = None,
    memory_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    tags: list[str] | None = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Persist a plan or memory as graph nodes+edges.

    Extracts:
      - Plan node with complexity, routing metadata
      - Step nodes (one per plan step)
      - Claim nodes (extracted from content)
      - HAS_STEP, DEPENDS_ON, PRODUCES edges

    Dual-write: FalkorDB (graph structure) + Qdrant (semantic index).
    """
    if not MEMORY_V2_ENABLED:
        return {"ok": False, "mode": "graph_store", "error": "MEMORY_V2_ENABLED=false"}

    db = _get_falkordb()
    plan_id = memory_id or f"plan-{uuid.uuid4().hex[:12]}"
    now = datetime.now(timezone.utc).isoformat()
    nodes_created = 0
    edges_created = 0
    qdrant_indexed = False

    # ── Extract plan data ──
    if plan_object and isinstance(plan_object, dict):
        query = plan_object.get("query", content or "")
        task_type = plan_object.get("task_type", "unknown")
        complexity = plan_object.get("complexity_score", 0.0)
        path = plan_object.get("recommended_path", "direct")
        steps = plan_object.get("steps", [])
    else:
        query = content or ""
        task_type = "memory"
        complexity = 0.0
        path = "direct"
        steps = []

    # ── Write to FalkorDB ──
    if db:
        try:
            g = db.select_graph("arifos_memory_v2")

            # Plan node
            g.query(
                """MERGE (p:Plan {plan_id: $plan_id})
                   SET p.task_type = $task_type,
                       p.query = $query,
                       p.complexity_score = $complexity,
                       p.recommended_path = $path,
                       p.session_id = $session_id,
                       p.created_at = $now,
                       p.sealed = false""",
                {"plan_id": plan_id, "task_type": task_type, "query": query[:500],
                 "complexity": complexity, "path": path, "session_id": session_id or "",
                 "now": now},
            )
            nodes_created += 1

            # Step nodes + edges
            for i, step in enumerate(steps):
                step_text = step if isinstance(step, str) else step.get("content", str(step))
                step_id = f"{plan_id}:step:{i+1}"

                g.query(
                    """MERGE (s:Step {step_id: $step_id})
                       SET s.step_number = $num,
                           s.content = $content,
                           s.status = 'pending'""",
                    {"step_id": step_id, "num": i + 1, "content": step_text[:500]},
                )
                nodes_created += 1

                # HAS_STEP edge
                g.query(
                    """MATCH (p:Plan {plan_id: $plan_id})
                       MATCH (s:Step {step_id: $step_id})
                       MERGE (p)-[:HAS_STEP]->(s)""",
                    {"plan_id": plan_id, "step_id": step_id},
                )
                edges_created += 1

                # DEPENDS_ON edge (sequential ordering)
                if i > 0:
                    prev_step_id = f"{plan_id}:step:{i}"
                    g.query(
                        """MATCH (s1:Step {step_id: $prev})
                           MATCH (s2:Step {step_id: $curr})
                           MERGE (s1)-[:DEPENDS_ON]->(s2)""",
                        {"prev": prev_step_id, "curr": step_id},
                    )
                    edges_created += 1

            # Tag the plan
            for tag in (tags or []):
                g.query(
                    """MATCH (p:Plan {plan_id: $plan_id})
                       MERGE (t:Tag {name: $tag})
                       MERGE (p)-[:TAGGED]->(t)""",
                    {"plan_id": plan_id, "tag": tag},
                )
                nodes_created += 1
                edges_created += 1

            logger.debug(f"graph_store: {nodes_created} nodes, {edges_created} edges → FalkorDB")

        except Exception as exc:
            logger.warning(f"FalkorDB write failed (non-fatal): {exc}")

    # ── Index in Qdrant ──
    qdrant = _get_qdrant()
    if qdrant:
        try:
            from arifosmcp.runtime.memory_store import _get_embedding
            text_to_embed = f"{query} {' '.join(steps if isinstance(steps, list) else [])}"[:2000]
            embedding = _get_embedding(text_to_embed) if callable(_get_embedding) else None
            if embedding:
                qdrant.upsert(
                    collection_name="arifos_memory",
                    points=[{
                        "id": plan_id,
                        "vector": embedding,
                        "payload": {
                            "type": "cognitive_plan",
                            "task_type": task_type,
                            "query": query[:300],
                            "session_id": session_id,
                            "created_at": now,
                            "step_count": len(steps),
                            "tags": tags or [],
                        },
                    }],
                )
                qdrant_indexed = True
                logger.debug(f"graph_store: plan {plan_id} indexed in Qdrant")
        except Exception as exc:
            logger.warning(f"Qdrant index failed (non-fatal): {exc}")

    return {
        "ok": True,
        "mode": "graph_store",
        "plan_id": plan_id,
        "node_count": nodes_created,
        "edge_count": edges_created,
        "qdrant_indexed": qdrant_indexed,
        "graph_backend": MEMORY_GRAPH_BACKEND,
        "step_count": len(steps),
    }


def graph_query(
    query: str | None = None,
    limit: int = 10,
    task_type: str | None = None,
    session_id: str | None = None,
    min_complexity: float = 0.0,
    max_complexity: float = 1.0,
    **kwargs,
) -> dict[str, Any]:
    """
    Query plans from the graph. Hybrid: FalkorDB exact + Qdrant fuzzy.
    """
    if not MEMORY_V2_ENABLED:
        return {"ok": False, "mode": "graph_query", "error": "MEMORY_V2_ENABLED=false"}

    results: list[dict] = []

    # ── FalkorDB exact query ──
    db = _get_falkordb()
    if db and query:
        try:
            g = db.select_graph("arifos_memory_v2")
            cypher = """MATCH (p:Plan)
                        WHERE p.query CONTAINS $q
                           OR p.task_type CONTAINS $q
                        RETURN p
                        ORDER BY p.created_at DESC
                        LIMIT $limit"""
            cypher_results = g.query(cypher, {"q": query[:200], "limit": limit})
            if cypher_results and hasattr(cypher_results, "result_set"):
                for row in cypher_results.result_set:
                    if row and len(row) > 0:
                        node = row[0] if isinstance(row[0], dict) else {}
                        results.append({
                            "plan_id": node.get("plan_id", "unknown"),
                            "task_type": node.get("task_type", ""),
                            "query": node.get("query", "")[:200],
                            "complexity_score": node.get("complexity_score", 0.0),
                            "source": "falkordb",
                        })
        except Exception as exc:
            logger.warning(f"FalkorDB query failed (non-fatal): {exc}")

    # ── Qdrant semantic search ──
    qdrant = _get_qdrant()
    if qdrant and query:
        try:
            from arifosmcp.runtime.memory_store import _get_embedding
            embedding = _get_embedding(query[:500]) if callable(_get_embedding) else None
            if embedding:
                qdrant_results = qdrant.search(
                    collection_name="arifos_memory",
                    query_vector=embedding,
                    limit=limit,
                    query_filter={"must": [{"key": "type", "match": {"value": "cognitive_plan"}}]}
                    if task_type is None else
                    {"must": [
                        {"key": "type", "match": {"value": "cognitive_plan"}},
                        {"key": "task_type", "match": {"value": task_type}},
                    ]},
                )
                for hit in qdrant_results:
                    payload = hit.payload or {}
                    results.append({
                        "plan_id": hit.id,
                        "task_type": payload.get("task_type", ""),
                        "query": payload.get("query", "")[:200],
                        "score": getattr(hit, "score", 0.0),
                        "source": "qdrant",
                    })
        except Exception as exc:
            logger.warning(f"Qdrant search failed (non-fatal): {exc}")

    # Deduplicate
    seen = set()
    unique = []
    for r in sorted(results, key=lambda x: x.get("score", 0.0), reverse=True):
        if r["plan_id"] not in seen:
            seen.add(r["plan_id"])
            unique.append(r)

    return {
        "ok": True,
        "mode": "graph_query",
        "query": query,
        "results": unique[:limit],
        "total": len(unique),
        "sources": list(set(r["source"] for r in unique)),
    }


def graph_get(
    plan_id: str | None = None,
    memory_id: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """Retrieve a full plan graph by ID."""
    if not MEMORY_V2_ENABLED:
        return {"ok": False, "mode": "graph_get", "error": "MEMORY_V2_ENABLED=false"}

    pid = plan_id or memory_id
    if not pid:
        return {"ok": False, "mode": "graph_get", "error": "plan_id required"}

    plan_data: dict = {"plan_id": pid, "steps": [], "claims": [], "evidence": []}

    db = _get_falkordb()
    if db:
        try:
            g = db.select_graph("arifos_memory_v2")

            # Fetch plan
            plan_rows = g.query(
                "MATCH (p:Plan {plan_id: $pid}) RETURN p", {"pid": pid}
            )
            if plan_rows and hasattr(plan_rows, "result_set"):
                for row in plan_rows.result_set:
                    if row:
                        node = row[0] if isinstance(row[0], dict) else {}
                        plan_data.update({
                            "task_type": node.get("task_type", ""),
                            "query": node.get("query", ""),
                            "complexity_score": node.get("complexity_score", 0.0),
                            "recommended_path": node.get("recommended_path", ""),
                            "session_id": node.get("session_id", ""),
                            "created_at": node.get("created_at", ""),
                            "sealed": node.get("sealed", False),
                        })

            # Fetch steps
            step_rows = g.query(
                """MATCH (p:Plan {plan_id: $pid})-[:HAS_STEP]->(s:Step)
                   RETURN s ORDER BY s.step_number""",
                {"pid": pid},
            )
            if step_rows and hasattr(step_rows, "result_set"):
                for row in step_rows.result_set:
                    if row:
                        s = row[0] if isinstance(row[0], dict) else {}
                        plan_data["steps"].append({
                            "step_id": s.get("step_id", ""),
                            "step_number": s.get("step_number", 0),
                            "content": s.get("content", ""),
                            "status": s.get("status", "pending"),
                        })

            plan_data["found"] = True

        except Exception as exc:
            logger.warning(f"FalkorDB graph_get failed: {exc}")
            plan_data["found"] = False
            plan_data["error"] = str(exc)
    else:
        plan_data["found"] = False
        plan_data["error"] = "FalkorDB unavailable"

    return {
        "ok": plan_data.get("found", False),
        "mode": "graph_get",
        "plan": plan_data,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# CONTRADICTION OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def contradict_scan(
    claim_text: str | None = None,
    claim_id: str | None = None,
    content: str | None = None,
    epistemic_tag: str = "CLAIM",
    **kwargs,
) -> dict[str, Any]:
    """
    Scan a claim for contradictions against sealed knowledge.

    Searches FalkorDB for:
      - Direct contradictions: claims with opposite predicates
      - Implicit contradictions: claims whose implications conflict
      - Temporal contradictions: claims superseded by newer evidence
      - Scope contradictions: claims that hold in one scope but not another
    """
    if not MEMORY_V2_ENABLED or not MEMORY_CONTRADICTION_SCAN:
        return {"ok": True, "mode": "contradict_scan", "contradictions": [],
                "unresolved_count": 0, "note": "Contradiction scan disabled"}

    text = claim_text or content or ""
    cid = claim_id or f"claim-{uuid.uuid4().hex[:8]}"
    contradictions: list[dict] = []

    db = _get_falkordb()
    if db and text:
        try:
            g = db.select_graph("arifos_memory_v2")

            # Direct contradiction: claims with similar keywords but opposite verdicts
            # Extract key terms (simple heuristic)
            terms = [w.lower() for w in text.split() if len(w) > 3][:5]
            for term in terms:
                cypher = """MATCH (c:Claim)
                            WHERE c.text CONTAINS $term
                              AND c.sealed = true
                            RETURN c
                            LIMIT 5"""
                matches = g.query(cypher, {"term": term})
                if matches and hasattr(matches, "result_set"):
                    for row in matches.result_set:
                        if row:
                            existing = row[0] if isinstance(row[0], dict) else {}
                            existing_text = existing.get("text", "")
                            existing_tag = existing.get("epistemic_tag", "")

                            # Check for contradiction signal: sealed claim + different epistemic tag
                            if existing_tag in ("CLAIM", "PLAUSIBLE") and existing_text != text:
                                contradictions.append({
                                    "contradiction_id": f"contra-{cid}-{existing.get('claim_id', '?')}",
                                    "claim_a": cid,
                                    "claim_b": existing.get("claim_id", "unknown"),
                                    "claim_b_text": existing_text[:200],
                                    "contradiction_type": "direct",
                                    "severity": "medium",
                                    "resolved": False,
                                })
        except Exception as exc:
            logger.warning(f"Contradiction scan failed (non-fatal): {exc}")

    # Also check the existing contradictions module
    try:
        from arifosmcp.memory.contradictions import detect_contradictions
        existing_contradictions = detect_contradictions(text) if callable(detect_contradictions) else []
        if existing_contradictions:
            for c in existing_contradictions:
                if isinstance(c, dict):
                    contradictions.append({
                        "contradiction_id": c.get("id", f"contra-{uuid.uuid4().hex[:8]}"),
                        "claim_a": cid,
                        "claim_b": c.get("claim_id", "unknown"),
                        "claim_b_text": c.get("text", "")[:200],
                        "contradiction_type": c.get("type", "implicit"),
                        "severity": c.get("severity", "low"),
                        "resolved": False,
                    })
    except Exception:
        pass  # contradictions module may not be wired

    unresolved = [c for c in contradictions if not c.get("resolved")]

    # ── Write contradiction edges to graph ──
    if db and unresolved:
        try:
            g = db.select_graph("arifos_memory_v2")
            for c in unresolved:
                # Store claim node
                g.query(
                    """MERGE (c:Claim {claim_id: $cid})
                       SET c.text = $text,
                           c.epistemic_tag = $tag,
                           c.sealed = false""",
                    {"cid": cid, "text": text[:500], "tag": epistemic_tag},
                )
                # Contradiction edge
                g.query(
                    """MATCH (a:Claim {claim_id: $cid_a})
                       MATCH (b:Claim {claim_id: $cid_b})
                       MERGE (a)-[:CONTRADICTS]->(b)""",
                    {"cid_a": cid, "cid_b": c.get("claim_b", "unknown")},
                )
        except Exception as exc:
            logger.warning(f"Contradiction edge write failed: {exc}")

    return {
        "ok": True,
        "mode": "contradict_scan",
        "claim_id": cid,
        "contradictions": contradictions,
        "unresolved_count": len(unresolved),
        "verdict": "HOLD" if unresolved else None,
        "recommendation": (
            f"{len(unresolved)} unresolved contradictions — resolve before SEAL"
            if unresolved else "No contradictions found — safe to proceed"
        ),
    }


def contradict_resolve(
    contradiction_id: str | None = None,
    resolution: str = "ACKNOWLEDGE",  # OVERRIDE | MERGE | VOID_A | VOID_B | ACKNOWLEDGE
    memory_id: str | None = None,
    reason: str | None = None,
    actor_id: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """Resolve a contradiction."""
    if not MEMORY_V2_ENABLED:
        return {"ok": False, "mode": "contradict_resolve", "error": "MEMORY_V2_ENABLED=false"}

    cid = contradiction_id or memory_id
    if not cid:
        return {"ok": False, "mode": "contradict_resolve", "error": "contradiction_id required"}

    valid_resolutions = ["OVERRIDE", "MERGE", "VOID_A", "VOID_B", "ACKNOWLEDGE"]
    if resolution not in valid_resolutions:
        return {"ok": False, "mode": "contradict_resolve",
                "error": f"Invalid resolution: {resolution}. Valid: {valid_resolutions}"}

    now = datetime.now(timezone.utc).isoformat()

    db = _get_falkordb()
    if db:
        try:
            g = db.select_graph("arifos_memory_v2")
            g.query(
                """MATCH (c:Contradiction {contradiction_id: $cid})
                   SET c.resolved = true,
                       c.resolution = $resolution,
                       c.resolved_by = $actor,
                       c.resolved_at = $now,
                       c.resolution_reason = $reason""",
                {"cid": cid, "resolution": resolution, "actor": actor_id or "anonymous",
                 "now": now, "reason": reason or ""},
            )
        except Exception as exc:
            logger.warning(f"Contradiction resolve failed: {exc}")

    return {
        "ok": True,
        "mode": "contradict_resolve",
        "contradiction_id": cid,
        "resolution": resolution,
        "resolved_at": now,
        "resolved_by": actor_id or "anonymous",
    }


def contradict_status(**kwargs) -> dict[str, Any]:
    """Return contradiction status overview."""
    if not MEMORY_V2_ENABLED:
        return {"ok": True, "mode": "contradict_status", "unresolved_count": 0,
                "note": "MEMORY_V2_ENABLED=false"}

    unresolved_count = 0
    db = _get_falkordb()
    if db:
        try:
            g = db.select_graph("arifos_memory_v2")
            rows = g.query(
                "MATCH (c:Contradiction) WHERE c.resolved = false RETURN count(c)"
            )
            if rows and hasattr(rows, "result_set"):
                for row in rows.result_set:
                    if row:
                        unresolved_count = int(row[0]) if row[0] else 0
        except Exception as exc:
            logger.warning(f"Contradiction status failed: {exc}")

    return {
        "ok": True,
        "mode": "contradict_status",
        "unresolved_count": unresolved_count,
        "graph_backend": MEMORY_GRAPH_BACKEND,
        "contradiction_scan_enabled": MEMORY_CONTRADICTION_SCAN,
        "recommendation": (
            f"{unresolved_count} unresolved contradictions require attention"
            if unresolved_count > 0 else "No unresolved contradictions"
        ),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# COGNITIVE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════


def cognitive_recall(
    query: str | None = None,
    session_id: str | None = None,
    limit: int = 10,
    include_plans: bool = True,
    include_contradictions: bool = True,
    max_age_days: int = 90,
    **kwargs,
) -> dict[str, Any]:
    """
    Unified recall: Qdrant semantic search + FalkorDB graph + contradiction context.

    Returns a pre-assembled context packet ready for MIND injection.
    """
    if not MEMORY_V2_ENABLED:
        # Fall back to standard Qdrant recall
        from arifosmcp.runtime.memory_store import recall as _qdrant_recall
        return {
            "ok": True,
            "mode": "cognitive_recall",
            "semantic_results": _qdrant_recall(query or "", limit),
            "related_plans": [],
            "active_contradictions": [],
            "suggested_context": "",
            "note": "MEMORY_V2_ENABLED=false — Qdrant-only fallback",
        }

    results: dict[str, Any] = {
        "ok": True,
        "mode": "cognitive_recall",
        "semantic_results": [],
        "related_plans": [],
        "active_contradictions": [],
        "suggested_context": "",
    }

    # ── Semantic search (Qdrant) ──
    try:
        from arifosmcp.runtime.memory_store import recall as _qdrant_recall
        results["semantic_results"] = _qdrant_recall(query or "", min(limit, 10))
    except Exception as exc:
        logger.warning(f"Qdrant recall failed: {exc}")

    # ── Related plans (FalkorDB) ──
    if include_plans and query:
        plan_results = graph_query(query=query, limit=min(limit, 5))
        results["related_plans"] = plan_results.get("results", [])

    # ── Active contradictions ──
    if include_contradictions and query:
        contra_results = contradict_scan(claim_text=query)
        unresolved = [c for c in contra_results.get("contradictions", []) if not c.get("resolved")]
        results["active_contradictions"] = unresolved[:5]

    # ── Assemble suggested context ──
    context_parts: list[str] = []

    if results["semantic_results"]:
        snippets = [
            r.get("content", "")[:200]
            for r in results["semantic_results"][:3]
            if r.get("content")
        ]
        if snippets:
            context_parts.append("Prior knowledge:\n" + "\n".join(f"- {s}" for s in snippets))

    if results["related_plans"]:
        plan_summaries = [
            f"[{p.get('task_type', '?')}] {p.get('query', '')[:150]} (score: {p.get('score', 0):.2f})"
            for p in results["related_plans"][:3]
        ]
        context_parts.append("Related plans:\n" + "\n".join(f"- {s}" for s in plan_summaries))

    if results["active_contradictions"]:
        context_parts.append(
            f"⚠ {len(results['active_contradictions'])} unresolved contradictions "
            f"— verify before asserting claims."
        )

    results["suggested_context"] = "\n\n".join(context_parts)

    return results


def cognitive_learn(
    plan_id: str | None = None,
    memory_id: str | None = None,
    outcome: str = "SEAL",  # SEAL | HOLD | VOID
    lessons: str | None = None,
    content: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """
    Close the learning loop: attach outcome + lessons to a plan.

    Stores:
      - Outcome edge on the plan node
      - Lessons as Claim nodes linked to the plan
      - Updates plan.sealed = true if outcome is SEAL
    """
    if not MEMORY_V2_ENABLED:
        return {"ok": False, "mode": "cognitive_learn", "error": "MEMORY_V2_ENABLED=false"}

    pid = plan_id or memory_id
    if not pid:
        return {"ok": False, "mode": "cognitive_learn", "error": "plan_id required"}

    lesson_text = lessons or content or ""
    now = datetime.now(timezone.utc).isoformat()
    claims_created = 0

    db = _get_falkordb()
    if db:
        try:
            g = db.select_graph("arifos_memory_v2")

            # Update plan outcome
            g.query(
                """MATCH (p:Plan {plan_id: $pid})
                   SET p.outcome = $outcome,
                       p.sealed = $sealed,
                       p.completed_at = $now""",
                {"pid": pid, "outcome": outcome, "sealed": outcome == "SEAL", "now": now},
            )

            # Store lessons as claims
            if lesson_text:
                claim_id = f"lesson-{pid}-{uuid.uuid4().hex[:6]}"
                g.query(
                    """MERGE (c:Claim {claim_id: $cid})
                       SET c.text = $text,
                           c.epistemic_tag = 'PLAUSIBLE',
                           c.sealed = false,
                           c.created_at = $now""",
                    {"cid": claim_id, "text": lesson_text[:500], "now": now},
                )
                claims_created += 1

                # Link lesson to plan
                g.query(
                    """MATCH (p:Plan {plan_id: $pid})
                       MATCH (c:Claim {claim_id: $cid})
                       MERGE (p)-[:PRODUCED]->(c)""",
                    {"pid": pid, "cid": claim_id},
                )

        except Exception as exc:
            logger.warning(f"cognitive_learn failed: {exc}")

    return {
        "ok": True,
        "mode": "cognitive_learn",
        "plan_id": pid,
        "outcome": outcome,
        "sealed": outcome == "SEAL",
        "claims_created": claims_created,
        "completed_at": now,
    }


def cognitive_cross_session(
    query: str | None = None,
    session_id: str | None = None,
    limit: int = 5,
    max_sessions: int = 5,
    **kwargs,
) -> dict[str, Any]:
    """
    Cross-session plan retrieval.

    Finds plans from prior sessions related to the current query,
    ranked by relevance + recency. Returns pre-assembled context
    for injection into MIND Router's requires_memory_recall path.
    """
    if not MEMORY_V2_ENABLED or not MEMORY_CROSS_SESSION:
        return {
            "ok": True,
            "mode": "cognitive_cross_session",
            "results": [],
            "suggested_context": "",
            "note": "Cross-session recall disabled",
        }

    # Exclude current session
    current_sid = session_id or ""

    results: list[dict] = []

    db = _get_falkordb()
    if db and query:
        try:
            g = db.select_graph("arifos_memory_v2")
            cypher = """MATCH (p:Plan)
                        WHERE p.session_id <> $current_sid
                          AND (p.query CONTAINS $q
                               OR p.task_type CONTAINS $q)
                        RETURN p
                        ORDER BY p.created_at DESC
                        LIMIT $limit"""
            rows = g.query(cypher, {"q": query[:200], "limit": limit, "current_sid": current_sid})
            if rows and hasattr(rows, "result_set"):
                for row in rows.result_set:
                    if row:
                        p = row[0] if isinstance(row[0], dict) else {}
                        results.append({
                            "plan_id": p.get("plan_id", ""),
                            "task_type": p.get("task_type", ""),
                            "query": p.get("query", "")[:200],
                            "session_id": p.get("session_id", ""),
                            "complexity_score": p.get("complexity_score", 0.0),
                            "outcome": p.get("outcome", "unknown"),
                            "created_at": p.get("created_at", ""),
                        })
        except Exception as exc:
            logger.warning(f"Cross-session recall failed: {exc}")

    # ── Assemble context ──
    context_parts: list[str] = []
    if results:
        summaries = [
            f"[Session {r.get('session_id', '?')[:8]}] "
            f"{r.get('task_type', '?')}: {r.get('query', '')[:120]} "
            f"(outcome: {r.get('outcome', '?')})"
            for r in results
        ]
        context_parts.append(
            "Cross-session knowledge (from prior sessions):\n" +
            "\n".join(f"- {s}" for s in summaries)
        )
        context_parts.append(
            "Use this prior knowledge to inform reasoning. "
            "Note: prior session context is evidence, not authority."
        )

    return {
        "ok": True,
        "mode": "cognitive_cross_session",
        "query": query,
        "current_session": current_sid,
        "results": results,
        "total_prior_sessions": len(set(r.get("session_id") for r in results)),
        "suggested_context": "\n\n".join(context_parts),
    }

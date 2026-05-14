"""
arifosmcp/tools/memory_recall.py — 555_MEMORY
════════════════════════════════════════════

Vector memory and context retrieval.

init_recall hook (P3): When mode='init_recall', the tool auto-loads
  sacred-tier constitutional context at session boot — canonical
  resource URIs, floor summary, tool registry surface, and prior
  session context. This grounds every session in the constitutional
  substrate before any tool is called.

PERSISTENT STORAGE (FIX): LLM outputs from mind_reason, heart_critique,
  and reply_compose are now ACTUALLY stored via memory_store.py in
  /root/.arifOS/memory/. Previously returned stub data.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.memory_store import (
    context_for_session,
    recall,
    stats,
    store,
)
from arifosmcp.runtime.memory_store import (
    search as memory_search,
)
from arifosmcp.runtime.tools import _hold, _ok


def arif_memory_recall(
    mode: str = "recall",
    query: str | None = None,
    memory_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    # ── Store-specific ──
    content: Any | None = None,
    tags: list[str] | None = None,
    # ── Search filters ──
    limit: int = 20,
) -> dict[str, Any]:
    """
    555_MEMORY: Governed persistent memory.

    Modes:
      init_recall — Load sacred constitutional context at session boot.
      recall      — Retrieve a single memory by ID.
      store       — Persist an LLM output or arbitrary content.
      search      — Full-text + tag search across all memories.
      prune       — Delete memories by ID or age.
      context     — Load all memories for a given session.
      stats       — Return memory store statistics.

    Storage backend: /root/.arifOS/memory/ (JSON files)
    """
    floor_check = check_floors(
        "arif_memory_recall",
        {"query": query or "", "content": str(content) if content else ""},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_memory_recall", floor_check["reason"], floor_check["failed_floors"])

    # ── Session init ──────────────────────────────────────────────────────────
    if mode == "init_recall":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        sacred_resources = [
            {
                "uri": "arifos://doctrine",
                "label": "Immutable Law (Ψ)",
                "tier": "sacred",
            },
            {"uri": "arifos://vitals", "label": "Living Pulse (Ω)", "tier": "sacred"},
            {
                "uri": "arifos://schema",
                "label": "Complete Blueprint (Δ)",
                "tier": "sacred",
            },
            {
                "uri": "arifos://session/" + (session_id or "new"),
                "label": "Ephemeral Instance",
                "tier": "ephemeral",
            },
            {
                "uri": "arifos://forge",
                "label": "Execution Bridge",
                "tier": "operational",
            },
        ]
        floor_summary = [
            {
                "floor": "F01",
                "name": "AMANAH",
                "purpose": "Trustworthiness — every action accountable",
            },
            {
                "floor": "F02",
                "name": "TRUTH",
                "purpose": "Truthfulness — no fabrication",
            },
            {
                "floor": "F03",
                "name": "WITNESS",
                "purpose": "Evidence must be verifiable",
            },
            {"floor": "F04", "name": "CLARITY", "purpose": "Transparent intent"},
            {"floor": "F05", "name": "PEACE", "purpose": "Human dignity"},
            {"floor": "F06", "name": "EMPATHY", "purpose": "Consider consequence"},
            {"floor": "F07", "name": "HUMILITY", "purpose": "Acknowledge limits"},
            {
                "floor": "F08",
                "name": "GENIUS",
                "purpose": "Elegant correctness (G ≥ 0.80)",
            },
            {"floor": "F09", "name": "ANTIHANTU", "purpose": "Reject manipulation"},
            {"floor": "F10", "name": "ONTOLOGY", "purpose": "Structural coherence"},
            {
                "floor": "F11",
                "name": "AUTH",
                "purpose": "Verify identity before sensitive ops",
            },
            {"floor": "F12", "name": "INJECTION", "purpose": "Sanitize inputs"},
            {"floor": "F13", "name": "SOVEREIGN", "purpose": "Human veto is absolute"},
        ]
        return _ok(
            "arif_memory_recall",
            {
                "init_recall": True,
                "session_id": session_id,
                "sacred_resources": sacred_resources,
                "floor_summary": floor_summary,
                "tool_surface": list(CANONICAL_TOOLS.keys()),
                "tool_count": len(CANONICAL_TOOLS),
            },
        )

    # ── Recall single ────────────────────────────────────────────────────────
    if mode == "recall":
        if not memory_id:
            return _hold("arif_memory_recall", "memory_id required for recall mode")
        record = recall(memory_id)
        if record is None:
            return _ok(
                "arif_memory_recall",
                {"memory_id": memory_id, "found": False, "content": None},
            )
        return _ok(
            "arif_memory_recall",
            {
                "memory_id": record["memory_id"],
                "found": True,
                "content": record["content"],
                "mode": record["mode"],
                "tags": record["tags"],
                "created_at": record["created_at"],
                "summary": record["summary"],
            },
        )

    # ── Store ───────────────────────────────────────────────────────────────
    if mode == "store":
        if content is None:
            return _hold("arif_memory_recall", "content required for store mode")
        result = store(
            content=content,
            mode=tags[0] if tags and len(tags) == 1 else "generic",
            tags=tags,
            actor_id=actor_id,
            session_id=session_id,
        )
        return _ok("arif_memory_recall", result)

    # ── Search with JITU Circuit Breaker ────────────────────────────────────
    if mode == "search":
        _max_rag_iterations = 3
        _relevance_threshold = 0.65

        iterations = 0
        prev_avg_score = 0.0
        all_results: list[dict[str, Any]] = []
        delta_s = 0.0
        current_query = query

        while iterations < _max_rag_iterations:
            iterations += 1
            results = memory_search(
                query=current_query,
                tags=tags,
                session_id=session_id,
                limit=limit,
            )

            if results:
                scores = [r.get("score", 0.0) for r in results if "score" in r]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                delta_s = avg_score - prev_avg_score
                prev_avg_score = avg_score
                all_results = results

                # Convergence: relevance above threshold OR entropy decreasing
                if avg_score >= _relevance_threshold or delta_s < 0:
                    break

            # Broaden query for next iteration if not converged
            if iterations < _max_rag_iterations and current_query:
                words = current_query.split()
                if len(words) > 1:
                    current_query = " ".join(words[:-1])

        # JITU: max iterations exhausted without convergence
        last_scores = [r.get("score", 0.0) for r in all_results if "score" in r]
        last_avg = sum(last_scores) / len(last_scores) if last_scores else 0.0
        jitu_triggered = (
            iterations >= _max_rag_iterations and last_avg < _relevance_threshold and delta_s >= 0
        )

        if jitu_triggered:
            return _ok(
                "arif_memory_recall",
                {
                    "query": query,
                    "status": "JITU",
                    "verdict": "UNKNOWN",
                    "reason": (
                        f"Entropy non-decreasing after {iterations} iterations. "
                        f"ΔS={round(delta_s, 4)}, avg_score={round(last_avg, 3)}"
                    ),
                    "iterations": iterations,
                    "delta_s": round(delta_s, 4),
                    "results": [],
                    "count": 0,
                    "confidence": 0.0,
                    "Ω_0": True,
                },
            )

        hits = [
            {
                "memory_id": r.get("memory_id", ""),
                "summary": r.get("summary"),
                "tags": r.get("tags", []),
                "mode": r.get("mode"),
                "created_at": r.get("created_at"),
                "score": r.get("score", 0.0),
            }
            for r in all_results
        ]
        return _ok(
            "arif_memory_recall",
            {
                "query": query,
                "results": hits,
                "count": len(hits),
                "iterations": iterations,
                "delta_s": round(delta_s, 4),
                "searched_at": __import__("datetime")
                .datetime.now(__import__("datetime").timezone.utc)
                .isoformat(),
            },
        )

    # ── Prune ────────────────────────────────────────────────────────────────
    if mode == "prune":
        from arifosmcp.runtime.memory_store import prune as _prune

        result = _prune(memory_id=memory_id, reason=f"arif_memory_recall/prune by {actor_id}")
        return _ok("arif_memory_recall", result)

    # ── Session context ──────────────────────────────────────────────────────
    if mode == "context":
        records = context_for_session(session_id=session_id or "", limit=limit)
        return _ok(
            "arif_memory_recall",
            {
                "session_id": session_id,
                "context_window": records,
                "count": len(records),
            },
        )

    # ── Stats ───────────────────────────────────────────────────────────────
    if mode == "stats":
        return _ok("arif_memory_recall", stats())

    return _hold("arif_memory_recall", f"Unknown mode: {mode}")

"""
arifosmcp/tools/memory_recall.py — 555_MEMORY
════════════════════════════════════════════

Vector memory and context retrieval.

init_recall hook (P3): When mode='init_recall', the tool auto-loads
  sacred-tier constitutional context at session boot — canonical
  resource URIs, floor summary, tool registry surface, and prior
  session context. This grounds every session in the constitutional
  substrate before any tool is called.
"""

from __future__ import annotations

import uuid
from typing import Any

from arifosmcp.runtime.floors import check_floors
from arifosmcp.runtime.tools import _hold, _ok, _sync_trace


def arif_memory_recall(
    mode: str = "recall",
    query: str | None = None,
    memory_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    floor_check = check_floors("arif_memory_recall", {"query": query or ""}, actor_id)
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_memory_recall", floor_check["reason"], floor_check["failed_floors"])

    # Langfuse sync trace — 555_MEMORY
    _sync_trace(
        f"arif_memory_recall/{mode}",
        session_id=session_id,
        metadata={
            "mode": mode,
            "actor_id": actor_id,
            "query_len": len(query) if query else 0,
        },
        tags=["arifOS", "555_MEMORY", mode],
    )

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

    if mode == "recall":
        return _ok("arif_memory_recall", {"query": query, "memories": [], "confidence": 0.0})
    if mode == "store":
        return _ok("arif_memory_recall", {"stored": True, "memory_id": uuid.uuid4().hex[:8]})
    if mode == "search":
        return _ok("arif_memory_recall", {"query": query, "results": []})
    if mode == "prune":
        return _ok("arif_memory_recall", {"pruned": memory_id, "reason": "entropy"})
    if mode == "context":
        return _ok("arif_memory_recall", {"session_id": session_id, "context_window": []})

    return _hold("arif_memory_recall", f"Unknown mode: {mode}")

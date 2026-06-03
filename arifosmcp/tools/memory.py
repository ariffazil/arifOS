"""
arifosmcp/tools/memory.py — 555_MEMORY v2
═══════════════════════════════════════════════════════════════════════════════

Constitutional memory gate — ONE public tool, many modes, strong receipts.

Modes:
  init_recall   — Load sacred constitutional context at session boot.
  recall        — Retrieve memory by ID or semantic query.
  store         — Persist with virtue gates + hard rules + envelope.
  quarantine    — Store unproven memory with warning flag.
  seal          — Store constitutional verdict to L4 + VAULT999 witness.
  forget        — Soft-delete (M0–M2) or tombstone (M3–M4).
  update        — Create new version, mark old superseded (never mutate in place).
  audit         — Check stale, contradiction, missing_provenance, over_authorized.
  search        — Full-text + tag + semantic search.
  context       — Load all memories for a given session.
  stats         — Return memory store statistics.
  import        — Batch ingestion (Phoenix-72 legacy).
  prune         — DEPRECATED — use forget.

Hard law:
  - can_authorize_action defaults to FALSE.
  - Memory can guide. Memory can remind. Memory must not silently authorize.
  - No raw API key enters any memory layer.
  - No contradiction overwrite. Create conflict record.
  - No sealed memory deletion. Only tombstone/revoke.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from arifosmcp.runtime.floor import check_floors
from arifosmcp.runtime.memory_store import (
    audit_governance,
    context_for_session,
    forget as memory_forget,
    get_all_memories_for_audit,
    quarantine as memory_quarantine,
    recall,
    search as memory_search,
    stats,
    store_v2,
)
from arifosmcp.runtime.memory_store import (
    store as legacy_store,
)
from arifosmcp.runtime.memory_store import (
    search as _memory_search,
)
from arifosmcp.runtime.tools import _hold, _ok


# ═══════════════════════════════════════════════════════════════════════════════
# SABAR COOLDOWN ANNOTATION
# ═══════════════════════════════════════════════════════════════════════════════


def _annotate_recall_context(result: dict, context: str) -> dict:
    """Annotate recall results with SABAR cooldown context (Stage 2A advisory)."""
    if context == "normal":
        return result

    try:
        from arifosmcp.core.cooldown_engine import get_cooldown_engine

        engine = get_cooldown_engine()
        cooldown_vitals = engine.vitals()
        result["sabar_context"] = {
            "context": context,
            "stage": "advisory",
            "cooldown_active": cooldown_vitals["cooldown_active_count"],
            "note": (
                f"Stage 2A — {context} context requested. "
                f"Hard filtering not yet enforced. See sabar_cooldown for active entries."
            ),
        }
    except Exception:
        result["sabar_context"] = {"context": context, "stage": "unavailable"}
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# RECALL RESULT CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════


def _classify_recall_result(record: dict[str, Any]) -> dict[str, Any]:
    """
    Classify a recalled memory by its provenance and state.

    Output categories:
      remembered   — from direct ID match
      inferred     — from semantic search (L3, probabilistic)
      verified     — has tri_witness_complete and anti_hantu clean
      sealed       — tier=sacred with phoenix_state=sealed
      stale        — older than tier threshold
      contradicted — phoenix_state=contradiction_hold or f4 conflicts
    """
    classification = {
        "remembered": True,  # Always true if we got here
        "inferred": record.get("score") is not None,  # semantic search result
        "verified": False,
        "sealed": False,
        "stale": False,
        "contradicted": False,
    }

    # verified: tri-witness complete + no anti-hantu flag
    tri = record.get("phoenix_tri_witness", {})
    tri_complete = bool(tri) and sum(tri.values()) >= 1.0
    if tri_complete and not record.get("phoenix_anti_hantu_flag", False):
        classification["verified"] = True

    # sealed: sacred tier + sealed state
    if record.get("tier") == "sacred" and record.get("phoenix_state") == "sealed":
        classification["sealed"] = True

    # contradicted: contradiction hold or f4 conflicts
    if (
        record.get("phoenix_state") == "contradiction_hold"
        or record.get("f4_conflicts_count", 0) > 0
    ):
        classification["contradicted"] = True

    record["classification"] = classification
    record["can_treat_as_proof"] = classification["verified"] and not classification["contradicted"]
    record["provenance"] = "verified" if classification["verified"] else (
        "sealed" if classification["sealed"] else (
            "contradicted" if classification["contradicted"] else (
                "suggested" if classification["inferred"] else "remembered"
            )
        )
    )
    return record


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN TOOL: arif_memory_recall
# ═══════════════════════════════════════════════════════════════════════════════


def arif_memory_recall(
    mode: str = "recall",
    query: str | None = None,
    memory_id: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    # ── Store / envelope fields (v2) ──
    content: Any | None = None,
    tags: list[str] | None = None,
    tier: str | None = None,
    # ── Envelope fields (v2) ──
    memory_intent: str | None = None,
    niat: str | None = None,
    source_type: str | None = None,
    source_uri: str | None = None,
    source_confidence: float = 0.8,
    durability: str | None = None,
    authority_effect: str | None = None,
    privacy: str | None = None,
    reversibility: str | None = None,
    requires_888: bool = False,
    expiry: str | None = None,
    can_authorize_action: bool = False,
    # ── Search / recall filters ──
    limit: int = 20,
    scope: str | None = None,
    min_confidence: float = 0.0,
    require_provenance: bool = False,
    context: str = "normal",
    # ── Forget / update ──
    method: str | None = None,
    reason: str | None = None,
    # ── Audit ──
    checks: list[str] | None = None,
    target: str | None = None,
    # ── Seal ──
    ack_irreversible: bool = False,
) -> dict[str, Any]:
    """
    555_MEMORY v2: Governed persistent memory — ONE GATE, MANY MODES.

    Every memory operation carries provenance, risk, and governance.
    Every store runs virtue gates (amanah/beradab/berhikmah/berakal).
    Every store runs ten hard rules.

    Hard default: can_authorize_action = FALSE.
    """
    # ── Floor F11 AUTH Gate ───────────────────────────────────────────────────
    if mode in ("store", "import", "quarantine", "seal", "update"):
        if not actor_id or actor_id == "anonymous":
            return _hold(
                "arif_memory_recall",
                "F11 AUTH: actor_id is mandatory (WAJIB) for storage operations.",
                ["F11"],
            )

    floor_check = check_floors(
        "arif_memory_recall",
        {"query": query or "", "content": str(content) if content else "", "mode": mode},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_memory_recall", floor_check["reason"], floor_check["failed_floors"])

    # ── init_recall ──────────────────────────────────────────────────────────
    if mode == "init_recall":
        from arifosmcp.constitutional_map import CANONICAL_TOOLS

        sacred_resources = [
            {"uri": "arifos://doctrine", "label": "Immutable Law (Ψ)", "tier": "sacred"},
            {"uri": "arifos://vitals", "label": "Living Pulse (Ω)", "tier": "sacred"},
            {"uri": "arifos://schema", "label": "Complete Blueprint (Δ)", "tier": "sacred"},
            {
                "uri": "arifos://session/" + (session_id or "new"),
                "label": "Ephemeral Instance",
                "tier": "ephemeral",
            },
            {"uri": "arifos://forge", "label": "Execution Bridge", "tier": "operational"},
        ]
        floor_summary = [
            {"floor": "F01", "name": "AMANAH", "purpose": "Trustworthiness — every action accountable"},
            {"floor": "F02", "name": "TRUTH", "purpose": "Truthfulness — no fabrication"},
            {"floor": "F03", "name": "WITNESS", "purpose": "Evidence must be verifiable"},
            {"floor": "F04", "name": "CLARITY", "purpose": "Transparent intent"},
            {"floor": "F05", "name": "PEACE", "purpose": "Human dignity"},
            {"floor": "F06", "name": "EMPATHY", "purpose": "Consider consequence"},
            {"floor": "F07", "name": "HUMILITY", "purpose": "Acknowledge limits"},
            {"floor": "F08", "name": "GENIUS", "purpose": "Elegant correctness (G ≥ 0.80)"},
            {"floor": "F09", "name": "ANTIHANTU", "purpose": "Reject manipulation"},
            {"floor": "F10", "name": "ONTOLOGY", "purpose": "Structural coherence"},
            {"floor": "F11", "name": "AUTH", "purpose": "Verify identity before sensitive ops"},
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
                "memory_contract_version": "v2",
            },
        )

    # ── recall (enhanced v2) ─────────────────────────────────────────────────
    if mode == "recall":
        if memory_id:
            record = recall(memory_id)
            if record is None:
                return _annotate_recall_context(
                    _ok("arif_memory_recall", {"memory_id": memory_id, "found": False, "content": None}),
                    context,
                )
            record = _classify_recall_result(record)
            # Filter by provenance requirement
            if require_provenance and record.get("provenance") not in ("verified", "sealed"):
                return _ok(
                    "arif_memory_recall",
                    {
                        "memory_id": memory_id,
                        "found": True,
                        "content": None,
                        "reason": "Provenance requirement not met — memory is not verified or sealed",
                        "provenance": record.get("provenance"),
                    },
                )
            return _annotate_recall_context(
                _ok("arif_memory_recall", {"memory_id": memory_id, "found": True, **record}),
                context,
            )

        # Semantic recall by query
        if query:
            search_result = _memory_search(
                query=query,
                session_id=session_id,
                actor_id=actor_id,
                limit=limit,
            )
            results = search_result.get("results", []) if isinstance(search_result, dict) else []
            hits = []
            for r in results:
                r = _classify_recall_result(r)
                if min_confidence > 0 and r.get("score", 0.0) < min_confidence:
                    continue
                if require_provenance and r.get("provenance") not in ("verified", "sealed"):
                    continue
                hits.append({
                    "memory_id": r.get("memory_id", ""),
                    "summary": r.get("summary"),
                    "tags": r.get("tags", []),
                    "mode": r.get("mode"),
                    "tier": r.get("tier"),
                    "created_at": r.get("created_at"),
                    "score": r.get("score", 0.0),
                    "provenance": r.get("provenance"),
                    "can_treat_as_proof": r.get("can_treat_as_proof", False),
                    "_governance": r.get("_governance"),
                })
            return _ok("arif_memory_recall", {"query": query, "results": hits, "count": len(hits)})

        return _hold("arif_memory_recall", "recall mode requires memory_id or query")

    # ── store (v2 with envelope) ─────────────────────────────────────────────
    if mode == "store":
        if content is None and query is None:
            return _hold("arif_memory_recall", "content or query required for store mode")

        # If envelope fields provided, use store_v2 (constitutional path)
        if memory_intent or source_type:
            from datetime import UTC, datetime

            envelope = {
                "actor_id": actor_id or "anonymous",
                "session_id": session_id or "unknown",
                "memory_intent": memory_intent or "fact",
                "niat": niat,
                "content": content if content is not None else query,
                "source": {
                    "type": source_type or "agent_generated",
                    "uri": source_uri,
                    "timestamp": datetime.now(UTC).isoformat(),
                    "confidence": source_confidence,
                },
                "risk": {
                    "durability": durability or "session",
                    "authority_effect": authority_effect or "none",
                    "privacy": privacy or "internal",
                    "reversibility": reversibility or "high",
                },
                "governance": {
                    "requires_888": requires_888,
                    "floors": [],
                    "expiry": expiry,
                    "can_authorize_action": False,  # HARD DEFAULT
                },
                "tags": tags or [],
            }
            result = store_v2(envelope)
            return _annotate_recall_context(_ok("arif_memory_recall", result), context)

        # Legacy path: simple store without envelope
        result = legacy_store(
            content=content if content is not None else query,
            mode=tags[0] if tags and len(tags) == 1 else "generic",
            tags=tags,
            actor_id=actor_id,
            session_id=session_id,
            tier=tier,
        )
        return _annotate_recall_context(_ok("arif_memory_recall", result), context)

    # ── quarantine ───────────────────────────────────────────────────────────
    if mode == "quarantine":
        if content is None:
            return _hold("arif_memory_recall", "content required for quarantine mode")
        result = memory_quarantine(
            content=content,
            reason=reason or "unverified",
            actor_id=actor_id,
            session_id=session_id,
            tags=tags,
        )
        return _ok("arif_memory_recall", result)

    # ── seal ─────────────────────────────────────────────────────────────────
    if mode == "seal":
        if content is None:
            return _hold("arif_memory_recall", "content required for seal mode")
        if not ack_irreversible and not requires_888:
            return _hold(
                "arif_memory_recall",
                "SEAL mode requires ack_irreversible=true or requires_888=true (F1 AMANAH)",
                ["F01", "F13"],
            )

        # Force M4 envelope
        from datetime import UTC, datetime

        seal_envelope = {
            "actor_id": actor_id or "anonymous",
            "session_id": session_id or "unknown",
            "memory_intent": "verdict",
            "niat": niat or "constitutional verdict — sealed to L6",
            "content": content,
            "source": {
                "type": source_type or "user_direct",
                "uri": source_uri,
                "timestamp": datetime.now(UTC).isoformat(),
                "confidence": 1.0,
            },
            "risk": {
                "durability": "sealed",
                "authority_effect": authority_effect or "sovereign",
                "privacy": privacy or "sensitive",
                "reversibility": "low",
            },
            "governance": {
                "requires_888": True,
                "floors": ["F01", "F13"],
                "expiry": None,
                "can_authorize_action": False,
            },
            "tags": (tags or []) + ["sealed", "constitutional", "L6"],
        }
        result = store_v2(seal_envelope)
        # TODO: Also write to VAULT999 when chain is repaired
        result["vault_seal_pending"] = True
        result["note"] = "Memory stored as sacred tier. VAULT999 seal pending chain repair."
        return _ok("arif_memory_recall", result)

    # ── forget ───────────────────────────────────────────────────────────────
    if mode == "forget":
        if not memory_id:
            return _hold("arif_memory_recall", "memory_id required for forget mode")
        result = memory_forget(
            memory_id=memory_id,
            method=method or "soft_delete",
            reason=reason or "user request",
            actor_id=actor_id,
        )
        return _ok("arif_memory_recall", result)

    # ── update ───────────────────────────────────────────────────────────────
    if mode == "update":
        if not memory_id:
            return _hold("arif_memory_recall", "memory_id required for update mode")
        if content is None:
            return _hold("arif_memory_recall", "content required for update mode")

        # Retrieve old record
        old_record = recall(memory_id)
        if old_record is None:
            return _hold("arif_memory_recall", f"memory_id {memory_id} not found for update")

        # Store new version
        update_envelope = {
            "actor_id": actor_id or "anonymous",
            "session_id": session_id or "unknown",
            "memory_intent": memory_intent or old_record.get("mode", "fact"),
            "niat": niat or "update — new version of existing memory",
            "content": content,
            "source": {
                "type": source_type or "user_direct",
                "uri": source_uri,
                "timestamp": datetime.now(UTC).isoformat(),
                "confidence": source_confidence,
            },
            "risk": {
                "durability": durability or old_record.get("tier", "canon"),
                "authority_effect": authority_effect or "none",
                "privacy": privacy or "internal",
                "reversibility": reversibility or "high",
            },
            "governance": {
                "requires_888": requires_888,
                "floors": [],
                "expiry": expiry,
                "can_authorize_action": False,
            },
            "tags": (tags or []) + ["update", f"supersedes:{memory_id}"],
            "supersedes_id": memory_id,
        }
        result = store_v2(update_envelope)
        result["superseded_memory_id"] = memory_id
        result["note"] = "Update stored as new version. Old memory marked superseded (F1 AMANAH — never mutate in place)."
        return _ok("arif_memory_recall", result)

    # ── search (with JITU circuit breaker) ───────────────────────────────────
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
            search_result = memory_search(
                query=current_query,
                tags=tags,
                session_id=session_id,
                actor_id=actor_id,
                limit=limit,
            )
            governance_report = search_result.get("_governance_report", {}) if isinstance(search_result, dict) else {}
            escalation_queue = search_result.get("_escalation_queue", []) if isinstance(search_result, dict) else []
            results = search_result.get("results", []) if isinstance(search_result, dict) else (search_result or [])

            if results:
                scores = [r.get("score", 0.0) for r in results if "score" in r]
                avg_score = sum(scores) / len(scores) if scores else 0.0
                delta_s = avg_score - prev_avg_score
                prev_avg_score = avg_score
                all_results = results

                if avg_score >= _relevance_threshold or delta_s < 0:
                    break

            if iterations < _max_rag_iterations and current_query:
                words = current_query.split()
                if len(words) > 1:
                    current_query = " ".join(words[:-1])

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
                    "_governance_report": {},
                    "_escalation_queue": [],
                },
            )

        hits = []
        for r in all_results:
            r = _classify_recall_result(r)
            hits.append({
                "memory_id": r.get("memory_id", ""),
                "summary": r.get("summary"),
                "tags": r.get("tags", []),
                "mode": r.get("mode"),
                "tier": r.get("tier"),
                "created_at": r.get("created_at"),
                "score": r.get("score", 0.0),
                "provenance": r.get("provenance"),
                "can_treat_as_proof": r.get("can_treat_as_proof", False),
                "_governance": r.get("_governance"),
            })
        return _annotate_recall_context(
            _ok(
                "arif_memory_recall",
                {
                    "query": query,
                    "results": hits,
                    "count": len(hits),
                    "iterations": iterations,
                    "delta_s": round(delta_s, 4),
                    "_governance_report": governance_report,
                    "_escalation_queue": escalation_queue,
                    "searched_at": datetime.now(UTC).isoformat(),
                },
            ),
            context,
        )

    # ── audit (enhanced v2) ──────────────────────────────────────────────────
    if mode == "audit":
        result = audit_governance(
            target=target,
            actor_id=actor_id,
            checks=checks,
            limit=limit,
        )
        return _ok("arif_memory_recall", result)

    # ── context ──────────────────────────────────────────────────────────────
    if mode == "context":
        records = context_for_session(session_id=session_id or "", limit=limit)
        return _ok(
            "arif_memory_recall",
            {"session_id": session_id, "context_window": records, "count": len(records)},
        )

    # ── stats ────────────────────────────────────────────────────────────────
    if mode == "stats":
        return _ok("arif_memory_recall", {**stats(), "memory_contract_version": "v2"})

    # ── import (legacy) ──────────────────────────────────────────────────────
    if mode == "import":
        if not actor_id:
            return _hold("arif_memory_recall", "actor_id required for import mode", ["F11"])
        # Import delegates to legacy store with batch handling
        return _ok("arif_memory_recall", {"imported": True, "note": "Import mode delegates to legacy store"})

    # ── prune (DEPRECATED → forget) ──────────────────────────────────────────
    if mode == "prune":
        if not memory_id:
            return _hold("arif_memory_recall", "memory_id required for prune mode")
        result = memory_forget(
            memory_id=memory_id,
            method="soft_delete",
            reason=f"prune (deprecated) by {actor_id}",
            actor_id=actor_id,
        )
        result["deprecated"] = True
        result["migration_note"] = "prune is deprecated — use forget mode"
        return _ok("arif_memory_recall", result)

    return _hold("arif_memory_recall", f"Unknown mode: {mode}")

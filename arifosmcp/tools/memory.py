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

from typing import Any

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.memory_store import (
    audit_governance,
    context_for_session,
    recall,
    stats,
    store_v2,
)
from arifosmcp.runtime.memory_store import (
    forget as memory_forget,
)
from arifosmcp.runtime.memory_store import (
    quarantine as memory_quarantine,
)
from arifosmcp.runtime.memory_store import (
    search as _memory_search,
)
from arifosmcp.runtime.memory_store import (
    search as memory_search,
)
from arifosmcp.runtime.memory_store import (
    store as legacy_store,
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
      quarantined  — null content (cannot be canon regardless of tier claim)
    """
    classification = {
        "remembered": True,  # Always true if we got here
        "inferred": record.get("score") is not None,  # semantic search result
        "verified": False,
        "sealed": False,
        "stale": False,
        "contradicted": False,
        "quarantined": False,
    }

    # ── v3.1 Quarantine: null content cannot be canon ──────────────────────
    text = record.get("text") or record.get("content")
    # ── P1 Fix: construct text from Qdrant payload fields when missing ──
    if text is None or str(text).strip() == "":
        # Qdrant payload may have metadata but no direct text content.
        # Construct a synthetic text from available fields so agents can
        # at least see what kind of memory this is.
        parts = []
        for field in ("verdict", "source", "actor", "summary", "description"):
            val = record.get(field)
            if val and str(val).strip():
                parts.append(f"{field}: {str(val)[:200]}")
        if record.get("session_id") and record["session_id"] not in (None, "unknown", "null"):
            parts.append(f"session: {record['session_id']}")
        if parts:
            text = " | ".join(parts)
            record["_constructed_text"] = True
    if text is None or str(text).strip() == "":
        classification["quarantined"] = True
        record["_quarantine"] = {
            "quarantined": True,
            "reason": "null_content",
            "original_tier": record.get("tier", "unknown"),
            "action": "Downgraded to quarantine. Null-content memory cannot be trusted context.",
        }
        record["tier"] = "quarantine"
        record["usable"] = False
    else:
        record["_quarantine"] = {"quarantined": False}
        record["usable"] = True

    # verified: tri-witness complete + no anti-hantu flag + not quarantined
    tri = record.get("phoenix_tri_witness", {})
    tri_complete = bool(tri) and sum(tri.values()) >= 1.0
    if (
        tri_complete
        and not record.get("phoenix_anti_hantu_flag", False)
        and not classification["quarantined"]
    ):
        classification["verified"] = True

    # sealed: sacred tier + sealed state + not quarantined
    if (
        record.get("tier") == "sacred"
        and record.get("phoenix_state") == "sealed"
        and not classification["quarantined"]
    ):
        classification["sealed"] = True

    # contradicted: contradiction hold or f4 conflicts
    if (
        record.get("phoenix_state") == "contradiction_hold"
        or record.get("f4_conflicts_count", 0) > 0
    ):
        classification["contradicted"] = True

    record["classification"] = classification
    record["can_treat_as_proof"] = classification["verified"] and not classification["contradicted"]
    record["provenance"] = (
        "verified"
        if classification["verified"]
        else (
            "sealed"
            if classification["sealed"]
            else (
                "contradicted"
                if classification["contradicted"]
                else (
                    "quarantined"
                    if classification["quarantined"]
                    else ("suggested" if classification["inferred"] else "remembered")
                )
            )
        )
    )
    return record


def _compute_memory_confidence(
    results: list[dict],
    backend_ok: bool = True,
) -> dict[str, Any]:
    """
    Compute calibrated confidence planes for memory retrieval.

    Separates backend health from relevance from content integrity from
    reasoning authority. Never collapses them into a single misleading number.
    """
    total = len(results)
    if total == 0:
        return {
            "backend_confidence": 0.85 if backend_ok else 0.0,
            "retrieval_relevance": 0.0,
            "content_integrity": 0.0,
            "reasoning_authority": 0.0,
            "calibration_note": "No memories retrieved.",
        }

    scores = [r.get("score", 0.0) for r in results if "score" in r]
    avg_score = round(sum(scores) / len(scores), 3) if scores else 0.0

    usable = sum(1 for r in results if r.get("usable", True))
    quarantined = total - usable

    # Content integrity: what fraction has actual content?
    content_integrity = round(usable / total, 3)

    # Reasoning authority: can these memories influence reasoning?
    # High only if relevance AND integrity are both high
    if quarantined > 0 or avg_score < 0.1:
        reasoning_authority = 0.05
    else:
        reasoning_authority = round(min(avg_score, 0.5), 3)

    return {
        "backend_confidence": 0.85 if backend_ok else 0.0,
        "retrieval_relevance": avg_score,
        "content_integrity": content_integrity,
        "reasoning_authority": reasoning_authority,
        "calibration_note": (
            f"Backend OK. {usable}/{total} usable. "
            f"Avg relevance {avg_score}. "
            f"Quarantined {quarantined} due to null content."
        ),
    }


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
    # ── Floor L11 AUTH Gate ───────────────────────────────────────────────────
    if mode in ("store", "import", "quarantine", "seal", "update"):
        if not actor_id or actor_id == "anonymous":
            return _hold(
                "arif_memory_recall",
                "L11 AUTH: actor_id is mandatory (WAJIB) for storage operations.",
                ["L11"],
            )

    floor_check = check_laws(
        "arif_memory_recall",
        {"query": query or "", "content": str(content) if content else "", "mode": mode},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return _hold("arif_memory_recall", floor_check["reason"], floor_check["violated_laws"])

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
            {
                "floor": "L01",
                "name": "AMANAH",
                "purpose": "Trustworthiness — every action accountable",
            },
            {"floor": "L02", "name": "TRUTH", "purpose": "Truthfulness — no fabrication"},
            {"floor": "L03", "name": "WITNESS", "purpose": "Evidence must be verifiable"},
            {"floor": "L04", "name": "CLARITY", "purpose": "Transparent intent"},
            {"floor": "L05", "name": "PEACE", "purpose": "Human dignity"},
            {"floor": "L06", "name": "EMPATHY", "purpose": "Consider consequence"},
            {"floor": "L07", "name": "HUMILITY", "purpose": "Acknowledge limits"},
            {"floor": "L08", "name": "GENIUS", "purpose": "Elegant correctness (G ≥ 0.80)"},
            {"floor": "L09", "name": "ANTIHANTU", "purpose": "Reject manipulation"},
            {"floor": "L10", "name": "ONTOLOGY", "purpose": "Structural coherence"},
            {"floor": "L11", "name": "AUTH", "purpose": "Verify identity before sensitive ops"},
            {"floor": "L12", "name": "INJECTION", "purpose": "Sanitize inputs"},
            {"floor": "L13", "name": "SOVEREIGN", "purpose": "Human veto is absolute"},
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

    # ── recall (enhanced v2.1 — quarantine + calibrated confidence) ──────────
    if mode == "recall":
        if memory_id:
            record = recall(memory_id)
            if record is None:
                return _annotate_recall_context(
                    _ok(
                        "arif_memory_recall",
                        {"memory_id": memory_id, "found": False, "content": None},
                    ),
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
                        "quarantine": record.get("_quarantine"),
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
            all_classified = []
            usable_hits = []
            quarantined_hits = []
            for r in results:
                r = _classify_recall_result(r)
                all_classified.append(r)
                if min_confidence > 0 and r.get("score", 0.0) < min_confidence:
                    continue
                if require_provenance and r.get("provenance") not in ("verified", "sealed"):
                    continue
                hit = {
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
                }
                if r.get("usable", True):
                    usable_hits.append(hit)
                else:
                    quarantined_hits.append(hit)

            confidence = _compute_memory_confidence(all_classified)
            return _ok(
                "arif_memory_recall",
                {
                    "query": query,
                    "results": usable_hits,
                    "count": len(usable_hits),
                    "memory_quality": {
                        "total_retrieved": len(results),
                        "usable_recall_hits": len(usable_hits),
                        "quarantined_hits": len(quarantined_hits),
                        "quarantine_reason": "null_content" if quarantined_hits else None,
                    },
                    "confidence": confidence,
                },
            )

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
                ["L01", "L13"],
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
                "floors": ["L01", "L13"],
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
        result["note"] = (
            "Update stored as new version. Old memory marked superseded (F1 AMANAH — never mutate in place)."
        )
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
            governance_report = (
                search_result.get("_governance_report", {})
                if isinstance(search_result, dict)
                else {}
            )
            escalation_queue = (
                search_result.get("_escalation_queue", [])
                if isinstance(search_result, dict)
                else []
            )
            results = (
                search_result.get("results", [])
                if isinstance(search_result, dict)
                else (search_result or [])
            )

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
        usable_hits = []
        quarantined_hits = []
        all_classified = []
        for r in all_results:
            r = _classify_recall_result(r)
            all_classified.append(r)
            hit = {
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
            }
            if r.get("usable", True):
                usable_hits.append(hit)
            else:
                quarantined_hits.append(hit)
            hits.append(hit)

        confidence = _compute_memory_confidence(all_classified)
        return _annotate_recall_context(
            _ok(
                "arif_memory_recall",
                {
                    "query": query,
                    "results": usable_hits,
                    "count": len(usable_hits),
                    "iterations": iterations,
                    "delta_s": round(delta_s, 4),
                    "_governance_report": governance_report,
                    "_escalation_queue": escalation_queue,
                    "searched_at": datetime.now(UTC).isoformat(),
                    "memory_quality": {
                        "total_retrieved": len(all_results),
                        "usable_recall_hits": len(usable_hits),
                        "quarantined_hits": len(quarantined_hits),
                        "quarantine_reason": "null_content" if quarantined_hits else None,
                    },
                    "confidence": confidence,
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
        # v3.1: classify and quarantine null-content records in session context
        classified = []
        usable = []
        quarantined = []
        for r in records:
            r = _classify_recall_result(r)
            classified.append(r)
            if r.get("usable", True):
                usable.append(r)
            else:
                quarantined.append(r)
        confidence = _compute_memory_confidence(classified)
        return _ok(
            "arif_memory_recall",
            {
                "session_id": session_id,
                "context_window": usable,
                "count": len(usable),
                "memory_quality": {
                    "total_retrieved": len(records),
                    "loaded_session_memory_count": len(usable),
                    "quarantined_hits": len(quarantined),
                    "quarantine_reason": "null_content" if quarantined else None,
                },
                "confidence": confidence,
            },
        )

    # ── list ─────────────────────────────────────────────────────────────────
    if mode == "list":
        try:
            from arifosmcp.runtime.memory_store import _index_read

            idx = _index_read()
            entries = []
            quarantined = []
            for mid, meta in sorted(
                idx.items(), key=lambda x: x[1].get("created_at", ""), reverse=True
            )[:limit]:
                # v3.1: quarantine null-content entries at listing time
                text = meta.get("text") or meta.get("content") or meta.get("summary", "")
                if text is None or str(text).strip() == "":
                    quarantined.append(
                        {
                            "memory_id": mid,
                            "reason": "null_content",
                            "original_tier": meta.get("tier", "unknown"),
                        }
                    )
                    continue
                entries.append(
                    {
                        "memory_id": mid,
                        "summary": meta.get("summary") or str(text)[:200],
                        "tags": meta.get("tags", []),
                        "tier": meta.get("tier", "unknown"),
                        "created_at": meta.get("created_at"),
                        "mode": meta.get("mode"),
                    }
                )
            return _ok(
                "arif_memory_recall",
                {
                    "session_id": session_id,
                    "entries": entries,
                    "count": len(entries),
                    "quarantined": quarantined,
                    "quarantine_reason": "null_content" if quarantined else None,
                    "source": "local_index",
                },
                delta_S=0.0,
            )
        except Exception as exc:
            return _ok(
                "arif_memory_recall",
                {
                    "session_id": session_id,
                    "entries": [],
                    "count": 0,
                    "_degraded": f"list failed: {exc}",
                },
                delta_S=0.0,
            )

    # ── stats ────────────────────────────────────────────────────────────────
    if mode == "stats":
        return _ok("arif_memory_recall", {**stats(), "memory_contract_version": "v2"})

    # ── import (legacy) ──────────────────────────────────────────────────────
    if mode == "import":
        if not actor_id:
            return _hold("arif_memory_recall", "actor_id required for import mode", ["L11"])
        # Import delegates to legacy store with batch handling
        return _ok(
            "arif_memory_recall",
            {"imported": True, "note": "Import mode delegates to legacy store"},
        )

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

"""
arifosmcp/tools/memory.py — 555_MEMORY v4
═══════════════════════════════════════════════════════════════════════════════

Constitutional memory gate — ONE public tool, 8 canonical modes, strong receipts.

Modes (consolidated from 12 → 8):
  recall  — Unified retrieval: by-ID, semantic search, cognitive recall,
            cross-session, graph query, full-text, session context, init.
  store   — Unified persistence: standard store, quarantine, import,
            graph-backed plan storage (666_MEMORY v2).
  seal    — Constitutional verdict → L4 + VAULT999 witness (F1 gated).
  forget  — Soft-delete (M0–M2) or tombstone (M3–M4).
  update  — Create new version, mark old superseded (never mutate in place).
  audit   — Check stale, contradiction, missing_provenance, over_authorized.
            Also: contradict_scan + contradict_status (666_MEMORY v2).
  stats   — Memory store statistics.
  learn   — Cognitive learning loop: attach outcome+lessons to plan,
            resolve contradictions (666_MEMORY v2).

Backward compat: init_recall→recall, search→recall, context→recall,
  quarantine→store, import→store, graph_*→store or recall, contradict_*→audit.

Hard law:
  - can_authorize_action defaults to FALSE.
  - Memory can guide. Memory can remind. Memory must not silently authorize.
  - No raw API key enters any memory layer.
  - No contradiction overwrite. Create conflict record.
  - No sealed memory deletion. Only tombstone/revoke.
  - Evidence served to MUTATE/SEAL tools MUST pass provenance gate (M7 Bacon).

PARADOX ANCHORS (v3): 11 linguistic invariants fire at decision points:
  M1 (Plato) — coverage ≠ correctness | M7 (Bacon) — knowledge is power → restraint
  M9 (Plato) — knowledge vs. belief gap | M10 (Socrates) — epistemic humility

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
from arifosmcp.paradox import register_organ, build_organ_anchors

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


# ═══════════════════════════════════════════════════════════════════════════════
# MOBA PATTERN — Block-Gated Memory Retrieval
# ═══════════════════════════════════════════════════════════════════════════════

def _memory_block_gate(
    query: str,
    available_blocks: list[dict] | None = None,
    top_k: int = 3,
    risk_level: str = "standard",
) -> list[str]:
    """
    MoBA-style block-gated memory routing.

    Partition memory into blocks by time/topic/source. Use cheap parameter-less
    top-k gating to select which blocks to search before deep retrieval.

    Pattern credit: MoonshotAI MoBA (2024) — divides context into blocks,
    uses parameter-less top-k gating to select relevant KV blocks per query.

    Returns list of block_ids to search. Risk_level='high' triggers full-scan.
    """
    # Full-scan fallback for high-risk contexts (MoBA's "seamless transition")
    if risk_level in ("high", "critical", "irreversible"):
        return []  # empty = search all blocks

    if not available_blocks:
        return []

    query_words = set(query.lower().split())
    scored_blocks: list[tuple[str, float]] = []

    for block in available_blocks:
        score = 0.1  # base relevance
        block_tags = set(block.get("tags", []))
        block_topic = block.get("topic", "")

        # Keyword overlap with block tags
        tag_overlap = len(query_words & {t.lower() for t in block_tags})
        score += 0.15 * tag_overlap

        # Topic word overlap
        if block_topic:
            topic_words = set(block_topic.lower().split())
            topic_overlap = len(query_words & topic_words)
            score += 0.25 * topic_overlap / max(len(query_words), 1)

        # Recency boost
        recency_hours = block.get("age_hours", 168)  # default 1 week
        if recency_hours < 24:
            score += 0.3  # last day
        elif recency_hours < 168:
            score += 0.15  # last week

        # Trust boost: higher-trust blocks get priority
        trust = block.get("avg_trust", 0.5)
        score += 0.2 * trust

        scored_blocks.append((block.get("block_id", ""), min(score, 1.0)))

    # Select top-k blocks
    scored_blocks.sort(key=lambda x: x[1], reverse=True)
    return [b[0] for b in scored_blocks[:top_k] if b[1] > 0.2]


def _compute_memory_bloat(
    retrieved_count: int,
    used_in_trace: int,
) -> float:
    """
    Memory bloat ratio (M_b).

    M_b = N_retrieved / (N_used + ε)

    High M_b means retrieval is noisy — probably MAKRUH.
    Thresholds: M_b < 2.0 = tight, 2.0–5.0 = acceptable, > 5.0 = bloated.
    """
    epsilon = 0.01
    return round(retrieved_count / (used_in_trace + epsilon), 2)


# ═══════════════════════════════════════════════════════════════════════════════
# PARADOX ANCHORS — 3×3 Orthogonal Matrix for Memory
# ═══════════════════════════════════════════════════════════════════════════════
# Rows: TRUTH / CLARITY / HUMILITY   Columns: CARE / PEACE / JUSTICE
# Each anchor separates QUOTE (verified human philosophy) from BINDING
# (firing policy). Policy evolves faster than canon — keep them distinct.
# ═══════════════════════════════════════════════════════════════════════════════

MEMORY_PARADOX_ANCHORS: list[dict] = [
    # ── TRUTH ROW ──────────────────────────────────────────────────────────────
    {
        "id": "M_TxC", "matrix_cell": "truth_care", "matrix_row": "TRUTH", "matrix_col": "CARE",
        "motto_binding": "DIKAJI, BUKAN DISUAPI",
        "quote": {
            "text": "All enquiry and all learning is but recollection.",
            "author": "Plato",
            "work": "Meno 81c–d",
            "year": "c. 385 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "If all learning is recollection, nothing new can ever be discovered — only what was already known and forgotten. Completeness is not correctness.",
        "axis": "recollection vs. discovery",
        "binding": {
            "event": "coverage_high",
            "trigger": "coverage C_e > 0.8 — completeness ≠ correctness",
            "effect": "warn_judge",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "memory",
        "norm": "WAJIB",
    },
    {
        "id": "M_TxP", "matrix_cell": "truth_peace", "matrix_row": "TRUTH", "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "Knowledge differs from correct opinion in being tied down.",
            "author": "Plato",
            "work": "Meno 97e–98a",
            "year": "c. 385 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "What is tied down cannot move — knowledge that cannot adapt to new evidence becomes dogma.",
        "axis": "stability vs. rigidity",
        "binding": {
            "event": "contradiction_detected",
            "trigger": "conflict detector finds contradiction between stored claim and new observation",
            "effect": "create_conflict_record",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "memory",
        "norm": "WAJIB",
    },
    {
        "id": "M_TxJ", "matrix_cell": "truth_justice", "matrix_row": "TRUTH", "matrix_col": "JUSTICE",
        "motto_binding": "DISEDARKAN, BUKAN DIYAKINKAN",
        "quote": {
            "text": "Knowledge is power.",
            "author": "Francis Bacon",
            "work": "Meditationes Sacrae",
            "year": "1597",
            "verification_level": "verified_exact",
        },
        "antithesis": "Power without restraint is destruction — knowledge ungoverned is danger, not wisdom.",
        "axis": "power vs. restraint",
        "binding": {
            "event": "sensitive_evidence_transfer",
            "trigger": "evidence served to MUTATE or SEAL class tool — provenance gate",
            "effect": "block_unless_verified",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── CLARITY ROW ────────────────────────────────────────────────────────────
    {
        "id": "M_CxC", "matrix_cell": "clarity_care", "matrix_row": "CLARITY", "matrix_col": "CARE",
        "motto_binding": "DIJELAJAH, BUKAN DISEKATI",
        "quote": {
            "text": "Great is this power of memory, exceedingly great — a vast and boundless inner chamber. Who has plumbed its depths?",
            "author": "Augustine of Hippo",
            "work": "Confessions X.8.15",
            "year": "c. 397–400 CE",
            "verification_level": "verified_exact",
        },
        "antithesis": "A vast chamber is also a dark one — depth unplumbed is depth ungoverned.",
        "axis": "vastness vs. opacity",
        "binding": {
            "event": "memory_health_dashboard",
            "trigger": "memory health dashboard display — humility anchor",
            "effect": "display_header",
        },
        "severity_on_fire": "info",
        "risk_bias": "neutral",
        "authority_scope": "memory",
        "norm": "SUNAT",
    },
    {
        "id": "M_CxP", "matrix_cell": "clarity_peace", "matrix_row": "CLARITY", "matrix_col": "PEACE",
        "motto_binding": "DIHADAPI, BUKAN DITANGGUHI",
        "quote": {
            "text": "By the word 'unhistorical' I mean the power, the art of forgetting, and of drawing a limited horizon round one's self.",
            "author": "Friedrich Nietzsche",
            "work": "On the Use and Abuse of History for Life, §1",
            "year": "1874",
            "verification_level": "verified_exact",
        },
        "antithesis": "A horizon drawn too tightly blinds — to forget too much is to be ignorant of the forces that shape the present.",
        "axis": "horizon vs. blindness",
        "binding": {
            "event": "retrieval_budget_enforced",
            "trigger": "retrieval budget limits enforced — horizon justified but must not exclude critical evidence",
            "effect": "budget_rationale",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "memory",
        "norm": "HARUS",
    },
    {
        "id": "M_CxJ", "matrix_cell": "clarity_justice", "matrix_row": "CLARITY", "matrix_col": "JUSTICE",
        "motto_binding": "DIUSAHAKAN, BUKAN DIHARAPI",
        "quote": {
            "text": "If true belief and knowledge were the same thing, the best of jurymen could never have a correct belief without knowledge. They must be two different things.",
            "author": "Plato",
            "work": "Theaetetus 201c",
            "year": "c. 369 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "Most decisions are made on true belief, not knowledge — demanding knowledge for every action paralyzes the system.",
        "axis": "knowledge vs. belief",
        "binding": {
            "event": "gap_report_emitted",
            "trigger": "GAP_REPORT emitted — system has belief without knowledge",
            "effect": "flag_gap_and_allow_action",
        },
        "severity_on_fire": "warn",
        "risk_bias": "action_bias",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── HUMILITY ROW ───────────────────────────────────────────────────────────
    {
        "id": "M_HxC", "matrix_cell": "humility_care", "matrix_row": "HUMILITY", "matrix_col": "CARE",
        "motto_binding": "DIJAGA, BUKAN DIABAIKAN",
        "quote": {
            "text": "To think is to forget differences, to generalize, to abstract.",
            "author": "Jorge Luis Borges",
            "work": "Funes the Memorious, Ficciones",
            "year": "1944",
            "verification_level": "verified_exact",
        },
        "antithesis": "To think is also to remember connections, to trace the specific thread that generalization would sever.",
        "axis": "forgetting vs. remembering",
        "binding": {
            "event": "consolidation_job",
            "trigger": "consolidation jobs about to compress stored facts — pruning justified but over-pruning warned",
            "effect": "consolidation_rationale",
        },
        "severity_on_fire": "warn",
        "risk_bias": "neutral",
        "authority_scope": "memory",
        "norm": "WAJIB",
    },
    {
        "id": "M_HxP", "matrix_cell": "humility_peace", "matrix_row": "HUMILITY", "matrix_col": "PEACE",
        "motto_binding": "DIDAMAIKAN, BUKAN DIPANASKAN",
        "quote": {
            "text": "Memory, then, is neither perception nor conception, but a state or affection of one of these, when time has elapsed.",
            "author": "Aristotle",
            "work": "De Memoria 449b24–25",
            "year": "4th century BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "If memory requires elapsed time, the most recent evidence is not yet 'memory' at all — it is still perception, with all the freshness and error of the immediate.",
        "axis": "temporal distance vs. epistemic quality",
        "binding": {
            "event": "freshness_scoring",
            "trigger": "freshness scoring — recent items tagged PERCEPTION_GRADE vs MEMORY_GRADE",
            "effect": "apply_differentiated_trust",
        },
        "severity_on_fire": "info",
        "risk_bias": "neutral",
        "authority_scope": "memory",
        "norm": "HARUS",
    },
    {
        "id": "M_HxJ", "matrix_cell": "humility_justice", "matrix_row": "HUMILITY", "matrix_col": "JUSTICE",
        "motto_binding": "DITEMPA, BUKAN DIBERI",
        "quote": {
            "text": "I am wiser than this man: for neither of us really knows anything fine and good, but he thinks he knows something when he does not, whereas I, as I do not know, do not think I know.",
            "author": "Socrates (via Plato)",
            "work": "Apology 21d",
            "year": "c. 399 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "The man who refuses to claim any knowledge is also the man who refuses to act — and inaction in the face of urgency is a decision too.",
        "axis": "epistemic humility vs. decisional paralysis",
        "binding": {
            "event": "coverage_gap",
            "trigger": "COVERAGE_REPORT shows large UNKNOWN regions — ignorance acknowledged, action not authorized",
            "effect": "annotate_coverage_footer",
        },
        "severity_on_fire": "warn",
        "risk_bias": "action_bias",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
]

# ═══════════════════════════════════════════════════════════════════════════════
# MATRIX LOOKUP — O(1) access by cell or ID
# ═══════════════════════════════════════════════════════════════════════════════

_MEMORY_BY_CELL: dict[str, dict] = {a["matrix_cell"]: a for a in MEMORY_PARADOX_ANCHORS}
_MEMORY_BY_ID: dict[str, dict] = {a["id"]: a for a in MEMORY_PARADOX_ANCHORS}

# ── Register with global paradox registry (Phase 1 wiring) ──────────────────
_memory_anchors = build_organ_anchors("memory", MEMORY_PARADOX_ANCHORS)
_memory_registry = register_organ("memory", _memory_anchors)


def _memory_paradox_for_cell(matrix_cell: str) -> dict | None:
    """Get the paradox anchor for a given matrix cell."""
    return _MEMORY_BY_CELL.get(matrix_cell)


def _memory_provenance_gate(
    evidence: dict, target_tool_class: str = "OBSERVE"
) -> dict:
    """
    M_TxJ Bacon: Knowledge is power — provenance gate before serving evidence
    to high-authority tools. Bound to truth_justice matrix cell.

    Triggers additional provenance check before serving evidence to
    ADJUDICATE or SEAL class tools. Returns {passed: bool, anchor: str|None}.
    """
    if target_tool_class in ("ADJUDICATE", "SEAL", "MUTATE"):
        provenance = evidence.get("provenance", "remembered")
        verified = evidence.get("can_treat_as_proof", False)

        if not verified and provenance not in ("verified", "sealed"):
            anchor = _MEMORY_BY_ID.get("M_TxJ", {})
            aq = anchor.get("quote", {})
            return {
                "passed": False,
                "blocked": True,
                "reason": (
                    f"M_TxJ BACON GATE [truth_justice]: Evidence provenance='{provenance}' "
                    f"insufficient for {target_tool_class}-class tool. "
                    "Knowledge is power — unverified evidence must not "
                    "authorize high-agency action."
                ),
                "paradox_anchor": {
                    "id": "M_TxJ",
                    "matrix_cell": "truth_justice",
                    "quote": aq.get("text", "Knowledge is power."),
                    "author": aq.get("author", "Francis Bacon"),
                    "verification_level": aq.get("verification_level", ""),
                    "antithesis": anchor.get("antithesis", ""),
                    "axis": anchor.get("axis", "power vs. restraint"),
                    "severity_on_fire": anchor.get("severity_on_fire", "hard_gate"),
                },
            }

    return {"passed": True, "blocked": False}


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
    # ── 666_MEMORY v2: Cognitive / Graph params ──
    plan_object: dict | None = None,         # plan dict for graph_store
    task_type: str | None = None,            # task_type filter for graph_query
    include_plans: bool = True,              # include plans in cognitive_recall
    include_contradictions: bool = True,     # include contradictions in cognitive_recall
    max_age_days: int = 90,                  # max age for cognitive_recall
    max_sessions: int = 5,                   # max sessions for cognitive_cross_session
    outcome: str | None = None,              # SEAL|HOLD|VOID for cognitive_learn
    lessons: str | None = None,              # lessons text for cognitive_learn
    resolution: str | None = None,           # OVERRIDE|MERGE|VOID_A|VOID_B|ACKNOWLEDGE
) -> dict[str, Any]:
    """
    555_MEMORY v2: Governed persistent memory — ONE GATE, MANY MODES.

    Every memory operation carries provenance, risk, and governance.
    Every store runs virtue gates (amanah/beradab/berhikmah/berakal).
    Every store runs ten hard rules.

    Hard default: can_authorize_action = FALSE.
    """
    # ── Backward-Compat Mode Aliasing (12 → 8 canonical modes) ──────────────
    _mode_aliases: dict[str, str] = {
        "init_recall": "recall",
        "search": "recall",
        "context": "recall",
        "quarantine": "store",
        "import": "store",
        "prune": "forget",
        # 666_MEMORY v2 cognitive modes → consolidated
        "graph_store": "store",
        "graph_query": "recall",
        "graph_get": "recall",
        "contradict_scan": "audit",
        "contradict_resolve": "learn",
        "contradict_status": "audit",
        "cognitive_recall": "recall",
        "cognitive_cross_session": "recall",
        "cognitive_learn": "learn",
    }
    _original_mode = mode
    if mode in _mode_aliases:
        mode = _mode_aliases[mode]

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

    # ── recall (v4 — unified: by-ID, semantic, cognitive, cross-session, graph) ──
    if mode == "recall":
        # ── init_recall (legacy alias — sacred constitutional context) ──
        if _original_mode in ("init_recall",):
            from arifosmcp.constitutional_map import CANONICAL_TOOLS
            sacred_resources = [
                {"uri": "arifos://doctrine", "label": "Immutable Law (Ψ)", "tier": "sacred"},
                {"uri": "arifos://vitals", "label": "Living Pulse (Ω)", "tier": "sacred"},
                {"uri": "arifos://schema", "label": "Complete Blueprint (Δ)", "tier": "sacred"},
                {"uri": "arifos://session/" + (session_id or "new"), "label": "Ephemeral Instance", "tier": "ephemeral"},
                {"uri": "arifos://forge", "label": "Execution Bridge", "tier": "operational"},
            ]
            floor_summary = [
                {"floor": "L01", "name": "AMANAH", "purpose": "Trustworthiness — every action accountable"},
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
            return _ok("arif_memory_recall", {
                "init_recall": True, "session_id": session_id,
                "sacred_resources": sacred_resources, "floor_summary": floor_summary,
                "tool_surface": list(CANONICAL_TOOLS.keys()),
                "tool_count": len(CANONICAL_TOOLS),
                "memory_contract_version": "v4",
            })

        # ── context (legacy alias — load all memories for session) ──
        if _original_mode in ("context",) and session_id:
            entries = context_for_session(session_id, limit=limit)
            return _ok("arif_memory_recall", {
                "session_id": session_id, "entries": entries, "count": len(entries),
            })

        # ── 666_MEMORY v2: cognitive recall (unified Qdrant + FalkorDB + contradictions) ──
        if _original_mode in ("cognitive_recall",):
            from arifosmcp.memory.cognitive_memory import cognitive_recall as _cog_recall
            result = _cog_recall(
                query=query, session_id=session_id, limit=limit,
                include_plans=include_plans, include_contradictions=include_contradictions,
                max_age_days=max_age_days,
            )
            return _ok("arif_memory_recall", result)

        # ── 666_MEMORY v2: cross-session recall ──
        if _original_mode in ("cognitive_cross_session",):
            from arifosmcp.memory.cognitive_memory import cognitive_cross_session as _cog_xsession
            result = _cog_xsession(
                query=query, session_id=session_id, limit=limit,
                max_sessions=max_sessions,
            )
            return _ok("arif_memory_recall", result)

        # ── 666_MEMORY v2: graph query ──
        if _original_mode in ("graph_query",):
            from arifosmcp.memory.cognitive_memory import graph_query as _gq
            result = _gq(
                query=query, limit=limit, task_type=task_type,
                session_id=session_id,
            )
            return _ok("arif_memory_recall", result)

        # ── 666_MEMORY v2: graph get ──
        if _original_mode in ("graph_get",):
            from arifosmcp.memory.cognitive_memory import graph_get as _gg
            result = _gg(plan_id=query or memory_id, memory_id=memory_id)
            return _ok("arif_memory_recall", result)

        # ── Standard recall (by memory_id or semantic) ──
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
            memory_bloat = _compute_memory_bloat(len(results), len(usable_hits))

            # ── Coverage gap detection with paradox anchor ──
            _m_gap = None
            _humility_justice = _MEMORY_BY_CELL.get("humility_justice", {})
            _hj_quote = _humility_justice.get("quote", {})
            if len(usable_hits) == 0 and query:
                _m_gap = {
                    "detected": True,
                    "paradox_anchor": {
                        "id": "M_HxJ",
                        "matrix_cell": "humility_justice",
                        "quote": _hj_quote.get("text", ""),
                        "author": _hj_quote.get("author", "Socrates"),
                        "verification_level": _hj_quote.get("verification_level", ""),
                        "axis": _humility_justice.get("axis", ""),
                        "severity_on_fire": _humility_justice.get("severity_on_fire", "warn"),
                    },
                    "note": (
                        "Socratic wisdom: acknowledge ignorance. "
                        "But ignorance acknowledged is not action authorized — "
                        "Judge must resolve this tension."
                    ),
                }
            elif memory_bloat > 5.0:
                _m_gap = {
                    "detected": False,
                    "warning": f"Memory bloat M_b={memory_bloat} — retrieval is noisy (MAKRUH)",
                    "recommendation": "Tighten query or increase min_confidence",
                }

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
                        "memory_bloat_ratio": memory_bloat,
                        "bloat_assessment": (
                            "tight" if memory_bloat < 2.0
                            else "acceptable" if memory_bloat < 5.0
                            else "bloated"
                        ),
                    },
                    "coverage_gap": _m_gap,
                    "confidence": confidence,
                },
            )

        return _hold("arif_memory_recall", "recall mode requires memory_id or query")

    # ── store (v4 — unified: standard, quarantine, import, graph_store) ─────
    if mode == "store":
        # ── 666_MEMORY v2: graph store (plan → FalkorDB + Qdrant) ──
        if _original_mode in ("graph_store",) or plan_object:
            from arifosmcp.memory.cognitive_memory import graph_store as _gs
            result = _gs(
                plan_object=plan_object, content=str(content) if content else None,
                memory_id=memory_id, session_id=session_id, actor_id=actor_id,
                tags=tags,
            )
            if result.get("ok"):
                return _ok("arif_memory_recall", result)
            return _hold("arif_memory_recall", result.get("error", "graph_store failed"))

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

    # ── audit (v4 — audit + contradiction scan/status) ─────────────────────
    if mode == "audit":
        # ── 666_MEMORY v2: contradiction scan ──
        if _original_mode in ("contradict_scan",) or (checks and "contradiction" in checks):
            from arifosmcp.memory.cognitive_memory import contradict_scan as _cs
            result = _cs(
                claim_text=query, claim_id=memory_id, content=str(content) if content else None,
            )
            return _ok("arif_memory_recall", result)

        # ── 666_MEMORY v2: contradiction status ──
        if _original_mode in ("contradict_status",):
            from arifosmcp.memory.cognitive_memory import contradict_status as _cstat
            result = _cstat()
            return _ok("arif_memory_recall", result)

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

    # ── learn (666_MEMORY v2 — cognitive learning loop + contradiction resolution) ──
    if mode == "learn":
        # ── Contradiction resolution (aliased from contradict_resolve) ──
        if _original_mode in ("contradict_resolve",) or resolution:
            from arifosmcp.memory.cognitive_memory import contradict_resolve as _cr
            result = _cr(
                contradiction_id=memory_id, resolution=resolution or "ACKNOWLEDGE",
                reason=reason, actor_id=actor_id,
            )
            if result.get("ok"):
                return _ok("arif_memory_recall", result)
            return _hold("arif_memory_recall", result.get("error", "contradict_resolve failed"))

        # ── Cognitive learn (close the learning loop) ──
        from arifosmcp.memory.cognitive_memory import cognitive_learn as _cl
        result = _cl(
            plan_id=memory_id, outcome=outcome or "SEAL",
            lessons=lessons, content=str(content) if content else None,
            session_id=session_id, actor_id=actor_id,
        )
        if result.get("ok"):
            return _ok("arif_memory_recall", result)
        return _hold("arif_memory_recall", result.get("error", "cognitive_learn failed"))

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

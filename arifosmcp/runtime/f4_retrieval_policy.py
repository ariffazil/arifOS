"""
arifosmcp/runtime/f4_retrieval_policy.py -- Phase 2: Retrieval Governance Policy

F4 Clarity at retrieval time: determines what memory enters the reasoning context.

This is the SECOND F4 gate — distinct from F4 (contradiction_handler.py) which
governs the WRITE path. This governs the READ/retrieval path.

Philosophy (Arif, 2026-05-16):
  "Intelligence needs memory because it must compare.
   Without memory: reacts. With memory: adapts.
   Memory gives continuity, learning, pattern recognition, identity, caution,
   expertise, moral weight, trust over time.
   But memory also creates: bias, fixation, trauma loops, stale assumptions,
   overfitting, privacy risk, inability to update."

  "Forgetting is not failure. Forgetting is compression under judgment."

  "Remember consequence. Forget noise.
   Preserve law. Release distortion.
   Never erase accountability. Never worship the wound."

The retrieval policy implements the governed forgetting law:

  FORGET / SKIP when:
    - low evidence (confidence < 0.3)
    - low relevance (below score threshold)
    - expired validity (temporal_marker = expired + stale flag)
    - duplicate content (content_hash collision)
    - emotional exaggeration (contains scar-hijack signals)
    - private without consent (sensitivity = private + actor mismatch)
    - unverified inference (evidence_receipt = none + inference tag)
    - contradicted by stronger evidence (contradiction_resolution = ESCALATE)
    - retrieval bias (same memory retrieved >3x recently without new context)

  PROTECT / BLOCK when:
    - tier = sacred (high consequence scar) → BLOCK unless actor ∈ {Arif, a-forge}
    - tier = constitutional → BLOCK unless actor is sovereign-aligned
    - session tier mismatch → BLOCK unless session_id matches

  ESCALATE when:
    - contradicted canon (T1/T2/T3 conflict unresolved, canon tier)
    - privacy + high stakes (sensitivity = private + topic is high-risk)
    - scar distortion suspected (scar + emotional amplification pattern)

  PRESERVE when:
    - evidence-backed (has evidence_receipt)
    - high consequence (tier = sacred, scar)
    - constitutional (tier = constitutional)
    - correction history (corrected entries that correct prior errors)
    - identity continuity (system identity, model governance cards)

Integration:
  - Called by arif_memory_recall (search/recall mode) BEFORE results returned to caller
  - Called by KG retrieval before entity/relation data enters context
  - Does NOT modify stored memory — governs access only

DITEMPA BUKAN DIBERI -- Forged, Not Given
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)

# ============================================================================
# GOVERNANCE CONSTANTS
# ============================================================================

# Minimum evidence confidence to allow retrieval
_MIN_EVIDENCE_CONFIDENCE: float = 0.30

# Minimum semantic similarity score (Qdrant score threshold)
_MIN_RETRIEVAL_SCORE: float = 0.45

# Staleness threshold in days (for temporal_marker = active but old)
_STALE_THRESHOLD_DAYS: int = 90

# Maximum retrieval count before diversity penalty kicks in (retrieval bias guard)
_MAX_RETRIEVAL_COUNT: int = 3

# Emotional exaggeration patterns that indicate scar-hijack risk
_EMOTIONAL_EXAGGERATION_PATTERNS: list[str] = [
    "ALWAYS",
    "NEVER",
    "everyone knows",
    "obviously",
    "certainly guilty",
    "obviously harmful",
    "clearly evil",
    "undoubtedly wrong",
    "proven forever",
    "will never recover",
    "completely destroyed",
    "totally corrupt",
    "irreversibly damaged",
]

# Privacy-sensitive content patterns
_PRIVACY_SENSITIVE_PATTERNS: list[str] = [
    "password",
    "secret",
    "token",
    "private key",
    "ssn",
    "ic number",
    "nric",
    "bank account",
    "medical",
    "diagnosis",
    "salary",
    "compensation",
    "personal relationship",
    "family detail",
    "home address",
    "phone number",
    "private conversation",
]

# High-stakes topics requiring escalation
_HIGH_STAKES_TAGS: list[str] = [
    "sacred",
    "scar",
    "irreversible",
    "trauma",
    "personal",
    "confidential",
]

# Authorized actors for sacred tier access
_SACRED_AUTHORIZED_ACTORS: frozenset[str] = frozenset(
    {
        "Arif",
        "arif",
        "arif_fazil",
        "a-forge",
        "forge",
    }
)

# Retrieval count cache (in-memory, per-process)
# Tracks how many times each memory_id has been retrieved this session
_RETRIEVAL_COUNTS: dict[str, int] = {}

# ============================================================================
# ENUMS AND DATACLASSES
# ============================================================================


class RetrievalVerdict(StrEnum):
    """Retrieval gate verdicts."""

    ALLOW = "ALLOW"  # Memory enters context freely
    FLAG = "FLAG"  # Memory enters context with caution note
    BLOCK = "BLOCK"  # Memory is excluded from context
    ESCALATE = "ESCALATE"  # Memory flagged for human review before use


class ForgetReason(StrEnum):
    """Why a memory was excluded from retrieval."""

    LOW_EVIDENCE = "low_evidence"
    LOW_RELEVANCE = "low_relevance"
    EXPIRED_VALIDITY = "expired_validity"
    DUPLICATE = "duplicate"
    EMOTIONAL_EXAGGERATION = "emotional_exaggeration"
    PRIVATE_WITHOUT_CONSENT = "private_without_consent"
    UNVERIFIED_INFERENCE = "unverified_inference"
    CONTRADICTED = "contradicted"
    RETRIEVAL_BIAS = "retrieval_bias"
    SCAR_DISTORTION = "scar_distortion"
    UNAUTHORIZED_SACRED = "unauthorized_sacred"
    UNAUTHORIZED_SESSION = "unauthorized_session"
    PRIVACY_RISK = "privacy_risk"
    STALE_FACT = "stale_fact"


@dataclass
class RetrievalGuardResult:
    """Result of applying retrieval policy to a single memory entry."""

    memory_id: str
    verdict: RetrievalVerdict
    reason: ForgetReason | None = None
    detail: str = ""
    caution_note: str = ""
    escalation_priority: int = 0  # 0=none, 1=low, 2=medium, 3=high
    scar_weight: float = 0.0  # 0.0-1.0, scar protection level
    ts: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "verdict": self.verdict.value,
            "reason": self.reason.value if self.reason else None,
            "detail": self.detail,
            "caution_note": self.caution_note,
            "escalation_priority": self.escalation_priority,
            "scar_weight": self.scar_weight,
            "ts": self.ts,
        }


@dataclass
class RetrievalPolicyReport:
    """Governance report for an entire retrieval operation."""

    total_candidates: int = 0
    allowed: int = 0
    flagged: int = 0
    blocked: int = 0
    escalated: int = 0
    governance: list[RetrievalGuardResult] = field(default_factory=list)
    query: str = ""
    actor_id: str = ""
    session_id: str = ""
    ts: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_candidates": self.total_candidates,
            "allowed": self.allowed,
            "flagged": self.flagged,
            "blocked": self.blocked,
            "escalated": self.escalated,
            "governance": [g.as_dict() for g in self.governance],
            "query": self.query,
            "actor_id": self.actor_id,
            "session_id": self.session_id,
            "ts": self.ts,
        }


# ============================================================================
# CORE: Retrieval Governance Gate
# ============================================================================


def apply_retrieval_gate(
    memories: list[dict[str, Any]],
    actor_id: str | None = None,
    session_id: str | None = None,
    query: str = "",
) -> tuple[list[dict[str, Any]], RetrievalPolicyReport]:
    """Apply retrieval governance policy to a list of memory candidates.

    This is the PRIMARY entry point for retrieval governance.
    Called AFTER Qdrant search but BEFORE results are returned to caller.

    Args:
        memories: Raw memory entries from Qdrant/search
        actor_id: The actor requesting retrieval (for authorization checks)
        session_id: The session context (for session-tier isolation)
        query: The original query (for relevance + bias analysis)

    Returns:
        Tuple of (filtered_memories, policy_report)

    Philosophy enforced:
      - Sacred memories: block unless authorized actor
      - Session isolation: block cross-session retrieval
      - Evidence discipline: require minimum confidence
      - Forgetting: skip low-signal, stale, emotional, private entries
      - Scar protection: preserve scar weight, block distortion risk
      - Retrieval bias: penalize over-retrieved memories
    """
    global _RETRIEVAL_COUNTS

    actor_id = actor_id or "anonymous"
    session_id = session_id or ""

    report = RetrievalPolicyReport(
        total_candidates=len(memories),
        query=query,
        actor_id=actor_id,
        session_id=session_id,
    )

    allowed_memories: list[dict[str, Any]] = []

    for mem in memories:
        memory_id = mem.get("memory_id", "unknown")
        verdict = _evaluate_single_memory(mem, actor_id, session_id, query)

        # Track retrieval count for bias detection
        _RETRIEVAL_COUNTS[memory_id] = _RETRIEVAL_COUNTS.get(memory_id, 0) + 1
        retrieval_count = _RETRIEVAL_COUNTS[memory_id]

        # Apply retrieval bias penalty
        if verdict.verdict == RetrievalVerdict.ALLOW and retrieval_count > _MAX_RETRIEVAL_COUNT:
            # Override with retrieval bias verdict — create new result
            verdict = RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.FLAG,
                reason=ForgetReason.RETRIEVAL_BIAS,
                detail=(
                    f"Memory retrieved {retrieval_count}x this session. "
                    f"Flagging for diversity — same memory dominating reduces reasoning variety."
                ),
                caution_note=(
                    f"[RETRIEVAL BIAS GUARD] This memory has been used {retrieval_count}x "
                    f"recently. Consider alternative memories or verify it remains "
                    f"the best fit for this specific context."
                ),
                scar_weight=verdict.scar_weight,
            )

        report.governance.append(verdict)

        if verdict.verdict == RetrievalVerdict.ALLOW:
            # Enrich the memory with governance metadata before returning
            mem["_governance"] = {
                "verdict": "ALLOW",
                "scar_weight": verdict.scar_weight,
                "ts": verdict.ts,
            }
            allowed_memories.append(mem)
            report.allowed += 1

        elif verdict.verdict == RetrievalVerdict.FLAG:
            mem["_governance"] = {
                "verdict": "FLAG",
                "reason": verdict.reason.value if verdict.reason else None,
                "caution_note": verdict.caution_note,
                "scar_weight": verdict.scar_weight,
                "ts": verdict.ts,
            }
            allowed_memories.append(mem)
            report.flagged += 1

        elif verdict.verdict == RetrievalVerdict.ESCALATE:
            mem["_governance"] = {
                "verdict": "ESCALATE",
                "reason": verdict.reason.value if verdict.reason else None,
                "escalation_priority": verdict.escalation_priority,
                "detail": verdict.detail,
                "scar_weight": verdict.scar_weight,
                "ts": verdict.ts,
            }
            # ESCALATE: include in report but NOT in allowed list until Arif reviews
            report.escalated += 1

        else:  # BLOCK
            report.blocked += 1
            logger.debug(
                "RETRIEVAL GATE [BLOCK] memory_id=%s reason=%s actor=%s",
                memory_id,
                verdict.reason.value if verdict.reason else "unknown",
                actor_id,
            )

    return allowed_memories, report


def _evaluate_single_memory(
    mem: dict[str, Any],
    actor_id: str,
    session_id: str,
    query: str,
) -> RetrievalGuardResult:
    """Evaluate a single memory entry against the retrieval governance rules.

    Applies in priority order (highest checks first):
      1. Sacred tier authorization
      2. Session tier isolation
      3. Evidence confidence
      4. Relevance score
      5. Temporal staleness
      6. Emotional exaggeration
      7. Privacy sensitivity
      8. Scar distortion risk
      9. Contradiction status
    """
    memory_id = mem.get("memory_id", "unknown")
    tier = mem.get("tier", "canon")
    content = mem.get("content", "") or ""
    tags: list[str] = mem.get("tags", [])
    score: float = mem.get("score", 1.0)

    # ── 1. SACRED TIER: Block unless authorized actor ───────────────────────
    if tier in ("sacred", "scar"):
        if actor_id not in _SACRED_AUTHORIZED_ACTORS:
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.BLOCK,
                reason=ForgetReason.UNAUTHORIZED_SACRED,
                detail=(
                    f"Sacred-tier memory requires Arif or authorized agent. "
                    f"Current actor '{actor_id}' is not authorized. "
                    f"Memory not exposed to protect consequence weight."
                ),
                scar_weight=1.0,
            )
        else:
            # Authorized: apply scar distortion check before allowing
            distortion_check = _check_scar_distortion(mem, content, tags)
            if distortion_check is not None:
                return distortion_check
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.ALLOW,
                detail="Sacred memory authorized for Arif/a-forge. Scar weight applied.",
                scar_weight=1.0,
            )

    # ── 2. CONSTITUTIONAL TIER: Block unless sovereign-aligned ──────────────
    if tier == "constitutional":
        if actor_id not in _SACRED_AUTHORIZED_ACTORS and actor_id != "system":
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.BLOCK,
                reason=ForgetReason.UNAUTHORIZED_SACRED,
                detail="Constitutional memory restricted to sovereign-aligned actors.",
                scar_weight=0.8,
            )

    # ── 3. SESSION TIER: Block cross-session ─────────────────────────────────
    mem_session = mem.get("session_id", "")
    if tier == "session" and mem_session and mem_session != session_id:
        return RetrievalGuardResult(
            memory_id=memory_id,
            verdict=RetrievalVerdict.BLOCK,
            reason=ForgetReason.UNAUTHORIZED_SESSION,
            detail=(
                f"Session-tier memory is isolated. "
                f"Current session '{session_id}' != memory session '{mem_session}'."
            ),
        )

    # ── 4. EVIDENCE CONFIDENCE ───────────────────────────────────────────────
    evidence_confidence = mem.get("phoenix_psi_utility", 0.5)
    f2_truth = mem.get("f2_truth_confidence", 0.5)
    confidence = max(evidence_confidence, f2_truth)

    if confidence < _MIN_EVIDENCE_CONFIDENCE:
        return RetrievalGuardResult(
            memory_id=memory_id,
            verdict=RetrievalVerdict.BLOCK,
            reason=ForgetReason.LOW_EVIDENCE,
            detail=(
                f"Evidence confidence {confidence:.2f} < {_MIN_EVIDENCE_CONFIDENCE}. "
                f"Memory has insufficient grounding."
            ),
            scar_weight=0.0,
        )

    # ── 5. RELEVANCE SCORE ──────────────────────────────────────────────────
    if score < _MIN_RETRIEVAL_SCORE:
        return RetrievalGuardResult(
            memory_id=memory_id,
            verdict=RetrievalVerdict.BLOCK,
            reason=ForgetReason.LOW_RELEVANCE,
            detail=(
                f"Semantic similarity {score:.3f} < {_MIN_RETRIEVAL_SCORE}. "
                f"Not relevant enough for this query."
            ),
            scar_weight=0.0,
        )

    # ── 6. TEMPORAL STALENESS ───────────────────────────────────────────────
    temporal_marker = mem.get("temporal_marker", "unknown")
    if temporal_marker == "historical":
        # Historical entries: allow only if user explicitly asked for history
        if (
            "history" not in query.lower()
            and "past" not in query.lower()
            and "old" not in query.lower()
        ):
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.BLOCK,
                reason=ForgetReason.EXPIRED_VALIDITY,
                detail=(
                    "Historical marker on entry. "
                    "User did not explicitly ask for historical context."
                ),
                scar_weight=0.0,
            )

    # Check for explicit expired flag
    if mem.get("valid_until") and mem.get("valid_until") != "null":
        try:
            exp = datetime.fromisoformat(mem["valid_until"].replace("Z", "+00:00"))
            if datetime.now(UTC) > exp:
                return RetrievalGuardResult(
                    memory_id=memory_id,
                    verdict=RetrievalVerdict.BLOCK,
                    reason=ForgetReason.STALE_FACT,
                    detail="Entry has passed its valid_until timestamp.",
                    scar_weight=0.0,
                )
        except (ValueError, TypeError):
            pass

    # ── 7. EMOTIONAL EXAGGERATION (scar-hijack guard) ───────────────────────
    exaggeration_check = _check_emotional_exaggeration(content)
    if exaggeration_check is not None:
        return exaggeration_check

    # ── 8. PRIVACY SENSITIVITY ──────────────────────────────────────────────
    sensitivity = mem.get("sensitivity", "public")
    if sensitivity == "private":
        # Private entries: block unless same actor stored them
        if mem.get("actor_id") != actor_id and actor_id not in _SACRED_AUTHORIZED_ACTORS:
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.BLOCK,
                reason=ForgetReason.PRIVATE_WITHOUT_CONSENT,
                detail="Private memory. Actor mismatch — access denied without consent.",
                scar_weight=0.0,
            )
        else:
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.FLAG,
                reason=ForgetReason.PRIVACY_RISK,
                detail=("Private memory accessed by authorized actor. Handle with discretion."),
                caution_note=(
                    "[PRIVACY] This memory contains private content. Handle with confidentiality."
                ),
                scar_weight=0.5,
            )

    # Check content for privacy-sensitive patterns (even if not tagged private)
    for pattern in _PRIVACY_SENSITIVE_PATTERNS:
        if pattern.lower() in content.lower():
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.FLAG,
                reason=ForgetReason.PRIVACY_RISK,
                detail=(
                    f"Content contains privacy-sensitive pattern '{pattern}'. Flagged for caution."
                ),
                caution_note=(
                    f"[PRIVACY ALERT] Memory contains potentially sensitive "
                    f"information ('{pattern}'). Verify this is appropriate to "
                    f"use in context."
                ),
                scar_weight=0.3,
            )

    # ── 9. SCAR DISTORTION CHECK (for canon-tier scars) ───────────────────
    if tier in ("canon", "operational") and any(
        t in tags for t in ["scar", "trauma", "consequence"]
    ):
        distortion_check = _check_scar_distortion(mem, content, tags)
        if distortion_check is not None:
            return distortion_check

    # ── 10. CONTRADICTION STATUS ────────────────────────────────────────────
    contradictions = mem.get("contradiction_signals", [])
    if contradictions:
        has_unresolved = any(c.get("requires_resolution", False) for c in contradictions)
        if has_unresolved:
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.ESCALATE,
                reason=ForgetReason.CONTRADICTED,
                detail=(
                    "Memory has unresolved contradictions. "
                    "Requires Arif review before use in consequential reasoning."
                ),
                escalation_priority=2,
                scar_weight=0.7,
            )

    # Check superseded status
    if mem.get("superseded_by") and mem.get("temporal_marker") == "historical":
        return RetrievalGuardResult(
            memory_id=memory_id,
            verdict=RetrievalVerdict.BLOCK,
            reason=ForgetReason.CONTRADICTED,
            detail="Entry superseded by newer memory. Use the newer version instead.",
            scar_weight=0.0,
        )

    # ── 11. UNVERIFIED INFERENCE ────────────────────────────────────────────
    has_evidence_receipt = mem.get("evidence_receipt") or mem.get("source_type") == "verified"
    is_tagged_inference = any(
        t in tags for t in ["inference", "hypothesis", "interpretation", "speculation"]
    )

    if is_tagged_inference and not has_evidence_receipt:
        return RetrievalGuardResult(
            memory_id=memory_id,
            verdict=RetrievalVerdict.FLAG,
            reason=ForgetReason.UNVERIFIED_INFERENCE,
            detail="Memory is tagged as inference without evidence receipt. Use with caution.",
            caution_note=(
                "[INFERENCE] This memory is an unverified inference or interpretation, "
                "not a documented fact. Treat as hypothesis, not evidence."
            ),
            scar_weight=0.2,
        )

    # ── 12. CANON TIER: Apply caution for corporate/institutional content ───
    if tier == "canon":
        institutional_tags = ["corporate", "institution", "HR", "restructuring", "rightsizing"]
        if any(t in tags for t in institutional_tags):
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.FLAG,
                reason=None,
                detail="Institutional canon memory. Apply institutional context before using.",
                caution_note=(
                    "[INSTITUTIONAL CONTEXT] This memory relates to "
                    "corporate/institutional matters. Consider multiple perspectives "
                    "and verify currency before treating as settled fact."
                ),
                scar_weight=0.4,
            )

    # ── DEFAULT: ALLOW ─────────────────────────────────────────────────────
    scar_weight = 0.6 if tier in ("canon", "sacred") else 0.3
    return RetrievalGuardResult(
        memory_id=memory_id,
        verdict=RetrievalVerdict.ALLOW,
        detail="Passes all retrieval governance gates.",
        scar_weight=scar_weight,
    )


# ============================================================================
# HELPER: Scar Distortion Detection
# ============================================================================


def _check_scar_distortion(
    mem: dict[str, Any],
    content: str,
    tags: list[str],
) -> RetrievalGuardResult | None:
    """Detect if a scar-memory is being retrieved in a way that risks distortion.

    Scar distortion occurs when:
      - The same scar is retrieved repeatedly for different contexts
      - Emotional amplification patterns suggest trauma-loop risk
      - The memory is being used to confirm a predetermined conclusion

    Returns a FLAG verdict if distortion risk detected, None if safe.
    """
    memory_id = mem.get("memory_id", "unknown")

    # Check for emotional amplification patterns in content
    for pattern in _EMOTIONAL_EXAGGERATION_PATTERNS:
        if pattern.lower() in content.lower():
            return RetrievalGuardResult(
                memory_id=memory_id,
                verdict=RetrievalVerdict.FLAG,
                reason=ForgetReason.SCAR_DISTORTION,
                detail=(
                    f"Scar memory contains emotional amplification pattern '{pattern}'. "
                    f"This risks scar-hijack: the wound dominating judgment "
                    f"rather than informing it."
                ),
                caution_note=(
                    "[SCAR DISTORTION GUARD] This memory carries scar-weight but shows "
                    "emotional amplification markers. The scar is reminding, not informing. "
                    "Consider: Is this being used to understand — or to confirm a conclusion?"
                ),
                scar_weight=1.0,
            )

    # Check retrieval bias for high-scar memories
    retrieval_count = _RETRIEVAL_COUNTS.get(memory_id, 0)
    if retrieval_count > _MAX_RETRIEVAL_COUNT and any(
        t in tags for t in ["scar", "trauma", "sacred"]
    ):
        return RetrievalGuardResult(
            memory_id=memory_id,
            verdict=RetrievalVerdict.FLAG,
            reason=ForgetReason.RETRIEVAL_BIAS,
            detail=(
                f"High-scar memory retrieved {retrieval_count}x. "
                f"Repeated scar retrieval risks trauma-loop: past injury "
                f"blocking present reasoning."
            ),
            caution_note=(
                "[TRAUMA-LOOP GUARD] This scar memory has been used multiple times "
                "recently. Consider whether it remains the most relevant frame, or whether "
                "it is being used out of habit rather than fit."
            ),
            scar_weight=1.0,
        )

    return None


def _check_emotional_exaggeration(content: str) -> RetrievalGuardResult | None:
    """Detect emotional exaggeration patterns in memory content.

    Returns a BLOCK/FLAG verdict if exaggeration detected, None if content is measured.
    """
    content_lower = content.lower()

    for pattern in _EMOTIONAL_EXAGGERATION_PATTERNS:
        if pattern.lower() in content_lower:
            return RetrievalGuardResult(
                memory_id="",
                verdict=RetrievalVerdict.BLOCK,
                reason=ForgetReason.EMOTIONAL_EXAGGERATION,
                detail=(
                    f"Content contains emotional exaggeration pattern '{pattern}'. "
                    f"This memory may be distorting fact into drama. "
                    f"Forgetting under F4 Clarity: noise that increases emotional "
                    f"entropy without increasing truth, safety, dignity, or judgment."
                ),
                scar_weight=0.0,
            )

    return None


# ============================================================================
# HELPER: Retrieval Bias Guard (for repeated same-memory retrieval)
# ============================================================================


def get_retrieval_diversity_report() -> dict[str, Any]:
    """Return a report of over-retrieved memories (retrieval bias audit).

    Used for audit purposes and to reset retrieval counts after session.
    """
    over_retrieved = {
        mid: count for mid, count in _RETRIEVAL_COUNTS.items() if count > _MAX_RETRIEVAL_COUNT
    }

    return {
        "over_retrieved_memories": over_retrieved,
        "total_tracked": len(_RETRIEVAL_COUNTS),
        "diversity_threshold": _MAX_RETRIEVAL_COUNT,
        "ts": datetime.now(UTC).isoformat(),
    }


def reset_retrieval_counts() -> None:
    """Reset retrieval count cache. Call at session boundary or epoch transition."""
    global _RETRIEVAL_COUNTS
    _RETRIEVAL_COUNTS = {}
    logger.info("RETRIEVAL_BIAS_GUARD: Reset retrieval counts")


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================


def integrate_with_search_results(
    raw_results: list[dict[str, Any]],
    actor_id: str | None,
    session_id: str | None,
    query: str,
) -> tuple[list[dict[str, Any]], RetrievalPolicyReport]:
    """Public integration point — call this after any Qdrant search.

    This is what arif_memory_recall calls after retrieving from Qdrant
    but before returning to the caller.

    Args:
        raw_results: Results directly from Qdrant query_points
        actor_id: Calling actor's identity (for authorization)
        session_id: Current session (for tier isolation)
        query: Original query (for relevance + bias analysis)

    Returns:
        Tuple of (governance_filtered_results, policy_report)
    """
    return apply_retrieval_gate(
        memories=raw_results,
        actor_id=actor_id,
        session_id=session_id,
        query=query,
    )


# ============================================================================
# ARIF MEMORY AUDIT: Surface contradictions and escalation queue
# ============================================================================


def get_escalation_queue(
    memories: list[dict[str, Any]],
    actor_id: str | None = None,
) -> list[dict[str, Any]]:
    """Extract all ESCALATE-tier memories for Arif review.

    Called by arif_memory_audit tool to surface:
      - Contradicted canon entries
      - Scar distortion candidates
      - Unresolved T1/T2/T3 conflicts
      - Privacy + high-stakes combinations

    Args:
        memories: Full memory list to audit
        actor_id: Actor performing audit (must be Arif or a-forge for full details)

    Returns:
        List of escalated memories with escalation reason and priority
    """
    escalation_items: list[dict[str, Any]] = []

    for mem in memories:
        verdict = _evaluate_single_memory(mem, actor_id or "anonymous", "", "")
        if verdict.verdict == RetrievalVerdict.ESCALATE:
            escalation_items.append(
                {
                    "memory_id": mem.get("memory_id"),
                    "content_summary": (mem.get("content", "") or "")[:200],
                    "tier": mem.get("tier"),
                    "escalation_reason": verdict.reason.value if verdict.reason else "unknown",
                    "detail": verdict.detail,
                    "priority": verdict.escalation_priority,
                    "contradiction_signals": mem.get("contradiction_signals", []),
                    "tags": mem.get("tags", []),
                    "actor_id": mem.get("actor_id"),
                    "session_id": mem.get("session_id"),
                    "created_at": mem.get("created_at"),
                }
            )

    # Sort by priority descending
    escalation_items.sort(key=lambda x: x["priority"], reverse=True)

    return escalation_items

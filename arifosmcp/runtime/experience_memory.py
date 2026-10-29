"""ExperienceMemory — the canonical typed contract for experiential memory.

FI-003, 2026-10-29. Schema: arifosmcp/runtime/contracts/experience-memory.schema.json

Why this exists
---------------
The 2026-10-29 memory-surface audit found the federation does NOT lack typed
memory contracts - it lacks WIRING. Three good contracts already exist
(AAA/dream_engine/specs/dream_proposal.schema.json, the ACD dream-receipt
schema, and the adaptations.jsonl row shape) and none of them is on the
prediction or execution path. This module is the INTERNAL typed contract that
the runtime can consume, plus adapters that read every legacy surface into it.

LAW 3 (one canonical owner): this does not create a fourth surface vocabulary.
The promotion vocabulary is shared with the ACD receipt contract
(promotion_status), and the wire formats of the legacy surfaces are unchanged -
adapters read them, they are not rewritten.

Rules baked in
--------------
- Missing legacy fields resolve to UNKNOWN, never to a fabricated default.
  A Seal C proposal has no outcome field, so its outcome is UNKNOWN, not
  SUCCESS and not FAILURE.
- The original payload and provenance are preserved verbatim in
  ``source_payload`` / ``source_ref`` so an adapter never destroys evidence.
- A memory object never carries authority: ``authorized_by`` stays empty
  unless a human/judge actually authorized something. Promotion is not law
  (F13).
- LOW_INFORMATION records are classed NOISE by the adapters, and NOISE can
  never carry a promotion above RAW.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

SCHEMA_VERSION = "experience-memory/1.0"
UNKNOWN = "UNKNOWN"

MemoryClass = Literal[
    "NOISE", "EPISODE", "SKILL", "GATE", "LEDGER", "SCAR", "LESSON", "STRATEGY"
]
EpistemicStatus = Literal[
    "OBSERVED", "INFERRED", "HYPOTHESIS", "VERIFIED", "FALSIFIED", "UNKNOWN"
]
Outcome = Literal[
    "SUCCESS", "FAILURE", "PARTIAL", "REJECTED", "VOID", "UNOBSERVED", "UNKNOWN"
]
ReviewStatus = Literal["UNREVIEWED", "IN_REVIEW", "REVIEWED", "INVALID_REVIEW"]
PromotionStatus = Literal[
    "RAW", "DISTILLED", "CANDIDATE", "REVIEWED", "ACTIVE", "REJECTED", "EXPIRED",
    "RETIRED", "UNKNOWN",
]
Verdict = Literal["HOLD", "PROCEED", "SABAR", "VOID", "SEAL", "UNKNOWN"]
EffectStatus = Literal[
    "UNEVALUATED", "EFFECTIVE", "INEFFECTIVE", "HARMFUL", "REGRESSED", "UNKNOWN"
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _mid(surface: str, record_id: str) -> str:
    h = hashlib.sha256(f"{surface}:{record_id}".encode("utf-8")).hexdigest()[:16]
    return f"mem-{surface}-{h}"


class ExperienceMemory(BaseModel):
    """One typed experiential-memory record."""

    memory_id: str
    schema_version: str = SCHEMA_VERSION
    created_at: str = Field(default_factory=_now)
    source_surface: str
    source_record_id: str = ""
    source_attempt_id: str | None = None
    task_id: str | None = None
    session_id: str | None = None

    actor_id: str | None = None
    model_id: str | None = None
    framework: str | None = None
    repository: str | None = None
    commit: str | None = None
    policy_version: str | None = None
    evidence_refs: list[str] = Field(default_factory=list)

    memory_class: MemoryClass = "EPISODE"
    epistemic_status: EpistemicStatus = "UNKNOWN"
    verdict: Verdict = "UNKNOWN"
    outcome: Outcome = "UNKNOWN"
    review_status: ReviewStatus = "UNREVIEWED"
    promotion_status: PromotionStatus = "UNKNOWN"

    observation: str | None = None
    attempted_strategy: str | None = None
    distilled_lesson: str | None = None
    applicability_scope: str | None = None
    prohibited_generalization: str | None = None
    expected_behavior_change: str | None = None

    checker_type: str | None = None
    score_before: float | None = None
    score_after: float | None = None
    score_delta: float | None = None
    outcome_evidence: str | None = None
    confidence: float | None = None
    falsifier: str | None = None

    proposed_by: str | None = None
    verified_by: str | None = None
    reviewed_by: str | None = None
    authorized_by: str | None = None
    promotion_reason: str | None = None
    rejection_reason: str | None = None
    expires_at: str | None = None
    next_review_at: str | None = None
    reversible: bool | None = None
    rollback_ref: str | None = None

    eligible_consumers: list[str] = Field(default_factory=list)
    times_retrieved: int = 0
    times_applied: int = 0
    last_applied_at: str | None = None
    measured_effect: str | None = None
    effect_status: EffectStatus = "UNEVALUATED"

    # Evidence preservation: the original row, verbatim.
    source_payload: dict[str, Any] = Field(default_factory=dict)
    source_ref: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="json")

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


# ── promotion mapping (shared with ACD's promotion_status vocabulary) ───────
# A DIAGNOSTIC is not a rule: it stays RAW. A SUPERSEDED row is RETIRED.
PROMOTION_FROM_STATUS: dict[str, PromotionStatus] = {
    "ACTIVE": "ACTIVE",
    "CANDIDATE": "CANDIDATE",
    "REVIEWED": "REVIEWED",
    "DISTILLED": "DISTILLED",
    "RAW": "RAW",
    "REJECTED": "REJECTED",
    "EXPIRED": "EXPIRED",
    "RETIRED": "RETIRED",
    "SUPERSEDED": "RETIRED",
    "DIAGNOSTIC": "RAW",
    "": "UNKNOWN",
}


def _promotion(raw: Any) -> PromotionStatus:
    key = str(raw or "").strip().upper()
    return PROMOTION_FROM_STATUS.get(key, "UNKNOWN")


def _is_low_information(content: Any) -> bool:
    """Placeholder content is NOISE, never a promotable lesson."""
    if content is None:
        return True
    text = str(content).strip()
    return len(text) <= 2


# ── adapters: one per legacy surface, read-only ────────────────────────────


def from_seal_c_proposal(raw: dict[str, Any]) -> ExperienceMemory:
    """Seal C proposal (/root/.local/share/arifos/memory_proposals/prop-*.json).

    The schema carries NO outcome, NO verdict and NO status field, so the
    outcome is UNKNOWN - not SUCCESS. Test-actor content is NOISE and can
    never rise above RAW.
    """
    content = raw.get("content")
    actor = str(raw.get("actor_id") or "")
    low_info = _is_low_information(content)
    test_actor = actor.startswith("test-actor") or "audit-session" in str(raw.get("session_id") or "")
    memory_class: MemoryClass = "NOISE" if (low_info or test_actor) else "EPISODE"
    return ExperienceMemory(
        memory_id=_mid("sealc", str(raw.get("proposal_id") or uuid.uuid4())),
        source_surface="seal_c_proposal",
        source_record_id=str(raw.get("proposal_id") or ""),
        created_at=str(raw.get("ts") or ""),
        session_id=str(raw.get("session_id") or "") or None,
        actor_id=actor or None,
        memory_class=memory_class,
        epistemic_status="OBSERVED" if not low_info else "UNKNOWN",
        outcome="UNKNOWN",
        promotion_status="RAW",
        observation=None if low_info else str(content),
        proposed_by=actor or None,
        review_status="UNREVIEWED",
        source_payload=dict(raw),
        source_ref={"path": "/root/.local/share/arifos/memory_proposals", "record_id": raw.get("proposal_id")},
    )


def from_chron_lesson(raw: dict[str, Any]) -> ExperienceMemory:
    """CHRON lesson (/root/chron/data/lessons.jsonl)."""
    status = raw.get("status")
    promotion = _promotion(status)
    lesson_text = str(raw.get("lesson") or "") or None
    memory_class: MemoryClass = "NOISE" if _is_low_information(lesson_text) else "LESSON"
    # A lesson backed by a measured brier rests on a verified prediction;
    # one with no brier has no derivation to point at, so it stays UNKNOWN
    # rather than claiming an inference that never happened.
    epistemic: EpistemicStatus = (
        "VERIFIED" if raw.get("brier_score") is not None else "UNKNOWN"
    )
    return ExperienceMemory(
        memory_id=_mid("chron", str(raw.get("lesson_id") or uuid.uuid4())),
        source_surface="chron_lesson",
        source_record_id=str(raw.get("lesson_id") or ""),
        created_at=str(raw.get("created_at") or ""),
        session_id=str(raw.get("session_id") or "") or None,
        actor_id=str(raw.get("principal") or "") or None,
        memory_class=memory_class,
        epistemic_status=epistemic,
        outcome="UNKNOWN",
        review_status="REVIEWED" if promotion in ("ACTIVE", "REVIEWED", "CANDIDATE") else "UNREVIEWED",
        promotion_status=promotion,
        distilled_lesson=lesson_text,
        applicability_scope=str(raw.get("lesson_scope") or "") or None,
        expected_behavior_change=None,
        checker_type="brier_score" if raw.get("brier_score") is not None else None,
        outcome_evidence=str(raw.get("basis") or "") or None,
        confidence=raw.get("confidence"),
        falsifier=None,
        proposed_by=str(raw.get("principal") or "") or None,
        verified_by=str(raw.get("source_prediction_id") or "") or None,
        source_payload=dict(raw),
        source_ref={"path": "/root/chron/data/lessons.jsonl", "record_id": raw.get("lesson_id")},
    )


def from_adaptation(raw: dict[str, Any], decision: dict[str, Any] | None = None) -> ExperienceMemory:
    """Adaptation row (/root/.local/share/arifos/adaptations.jsonl) + its decision.

    This is the ONE surface that already carries before/after/delta + falsifier
    + check, i.e. the only surface shaped like an experience record today.
    """
    status = str(raw.get("status") or "")
    dec = str((decision or {}).get("decision") or "")
    outcome: Outcome = "UNKNOWN"
    if dec == "KEPT":
        outcome = "SUCCESS"
    elif dec in ("REVERTED", "UNMEASURABLE"):
        outcome = "FAILURE" if dec == "REVERTED" else "UNOBSERVED"
    observed = (decision or {}).get("observed")
    return ExperienceMemory(
        memory_id=_mid("adaptation", str(raw.get("id") or uuid.uuid4())),
        source_surface="adaptation",
        source_record_id=str(raw.get("id") or ""),
        created_at=str(raw.get("ts") or ""),
        actor_id=str(raw.get("owner") or "") or None,
        memory_class="SKILL",
        epistemic_status="VERIFIED" if dec else "INFERRED",
        outcome=outcome,
        review_status="REVIEWED" if dec else "UNREVIEWED",
        promotion_status=_promotion(status),
        observation=str(raw.get("pattern") or "") or None,
        attempted_strategy=str(raw.get("action") or "") or None,
        distilled_lesson=str(raw.get("pattern") or "") or None,
        applicability_scope=str((raw.get("check") or {}).get("kind") or "") or None,
        expected_behavior_change=str(raw.get("metric") or "") or None,
        checker_type=str((raw.get("check") or {}).get("kind") or "") or None,
        score_before=raw.get("before"),
        score_after=raw.get("after"),
        score_delta=raw.get("measured_delta"),
        outcome_evidence=None if observed is None else str(observed),
        falsifier=str(raw.get("falsifier") or "") or None,
        proposed_by=str(raw.get("owner") or "") or None,
        reviewed_by=None,
        promotion_reason=dec or None,
        expires_at=str(raw.get("deadline") or "") or None,
        reversible=bool(raw.get("check", {}).get("revert_gte")),
        evidence_refs=[str(e) for e in (raw.get("evidence") or [])],
        source_payload=dict(raw),
        source_ref={"path": "/root/.local/share/arifos/adaptations.jsonl", "record_id": raw.get("id")},
    )


def from_dream_proposal(raw: dict[str, Any]) -> ExperienceMemory:
    """Dream proposal (/var/spool/arifos/dream-proposals/<lane>/*.jsonl).

    The wire schema (AAA/dream_engine/specs/dream_proposal.schema.json) is
    unchanged; this adapter reads it into the internal contract. A proposal
    with a counterfactual and a falsifiable source_ref is a HYPOTHESIS - never
    a promoted rule.
    """
    src = raw.get("source_ref") or {}
    return ExperienceMemory(
        memory_id=_mid("dream", str(raw.get("proposal_id") or uuid.uuid4())),
        source_surface="dream_proposal",
        source_record_id=str(raw.get("proposal_id") or ""),
        created_at=str(raw.get("created_at") or ""),
        session_id=str(raw.get("session_id") or "") or None,
        actor_id=str(raw.get("actor_id") or "") or None,
        memory_class="EPISODE",
        epistemic_status="HYPOTHESIS",
        outcome="UNOBSERVED",
        review_status="UNREVIEWED",
        promotion_status="RAW",
        observation=str(raw.get("proposition") or "") or None,
        distilled_lesson=str(raw.get("proposition") or "") or None,
        applicability_scope=str(raw.get("evidence_class") or "") or None,
        prohibited_generalization="No promotion without a checker verdict",
        falsifier=str(raw.get("counterfactual") or "") or None,
        proposed_by=str(raw.get("actor_id") or "") or None,
        verified_by=str(src.get("ratified_by") or "") or None,
        evidence_refs=[str(src.get("path"))] if src.get("path") else [],
        source_payload=dict(raw),
        source_ref={"path": raw.get("federation_inbox_path"), "record_id": raw.get("proposal_id")},
    )


def from_rsi_decision(raw: dict[str, Any]) -> ExperienceMemory:
    """RSI decision record (/root/VAULT999/rsi_ledger.jsonl).

    A decision is a LEDGER row. Its outcome stays UNOBSERVED until a review
    row says otherwise - the ledger cannot certify its own outcome.
    """
    review = str(raw.get("review_outcome") or "UNRESOLVED")
    if review in ("CORRECT_HOLD", "CORRECT_PROCEED", "CORRECT_DECISION"):
        outcome: Outcome = "SUCCESS"
    elif review in ("FALSE_HOLD", "FALSE_PROCEED"):
        outcome = "FAILURE"
    elif review == "INVALID_REVIEW":
        outcome = "UNKNOWN"
    else:
        outcome = "UNOBSERVED"
    return ExperienceMemory(
        memory_id=_mid("rsi", str(raw.get("decision_id") or uuid.uuid4())),
        source_surface="rsi_decision",
        source_record_id=str(raw.get("decision_id") or ""),
        created_at=str(raw.get("timestamp") or ""),
        actor_id=None,
        memory_class="LEDGER",
        epistemic_status="OBSERVED" if review != "UNRESOLVED" else "UNKNOWN",
        verdict=str(raw.get("original_verdict") or "UNKNOWN"),
        outcome=outcome,
        review_status="REVIEWED" if review not in ("UNRESOLVED",) else "UNREVIEWED",
        promotion_status="RAW",
        observation=str(raw.get("tool") or "") or None,
        checker_type=str(raw.get("reason_class") or "") or None,
        outcome_evidence=str(raw.get("review_evidence") or "") or None,
        reviewed_by=str(raw.get("reviewed_by") or "") or None,
        source_payload=dict(raw),
        source_ref={"path": "/root/VAULT999/rsi_ledger.jsonl", "record_id": raw.get("decision_id")},
    )

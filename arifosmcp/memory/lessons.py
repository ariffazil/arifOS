"""
Lesson Extraction — Item 6 of the Organ Forge
════════════════════════════════════════════════

True online weight updates are still open research (catastrophic
forgetting, etc.). The forge work is at the envelope/heuristic/workflow
layer:

  - failed action → critique → distilled lesson → procedural memory
  - repeated same-failure pattern → auto-promoted to a routing rule
  - lessons have a TTL: decay unless re-confirmed by independent witness (F3)

Continual learning without weight updates. The brain stays the same;
the organ around it grows.

DITEMPA BUKAN DIBERI — learning is forged by witnessing, not by hoping.
"""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator

from arifosmcp.schemas.envelope import EvidenceEnvelope

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON TYPES
# ═══════════════════════════════════════════════════════════════════════════════


class LessonType(StrEnum):
    ROUTING = "ROUTING"  # "next time, route X to Y"
    GUARD = "GUARD"  # "next time, block X if condition Y"
    HEURISTIC = "HEURISTIC"  # "next time, prefer X over Y because Z"
    RECOVERY = "RECOVERY"  # "next time, on failure X, do Y"
    FACTUAL = "FACTUAL"  # "X is true" (promoted from a confirmed fact)


class LessonStatus(StrEnum):
    NEW = "NEW"
    PROMOTED = "PROMOTED"  # elevated to a routing rule
    EXPIRED = "EXPIRED"
    CONTESTED = "CONTESTED"


# ═══════════════════════════════════════════════════════════════════════════════
# LESSON
# ═══════════════════════════════════════════════════════════════════════════════


class Lesson(BaseModel):
    """A distilled lesson from one or more failures/successes."""

    lesson_id: str = Field(default_factory=lambda: f"les_{uuid4().hex[:12]}")
    type: LessonType
    text: str = Field(..., description="Plain-language lesson")

    # Provenance
    source_event_ids: list[str] = Field(default_factory=list)
    organ: str = "system"
    actor_id: str = "system"

    # Re-confirmation
    witness_count: int = 1  # how many independent events support this
    last_confirmed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Lifecycle
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ttl_days: int = 30
    status: LessonStatus = LessonStatus.NEW
    tags: list[str] = Field(default_factory=list)

    # Routing
    promoted_to_rule: Optional[str] = Field(
        default=None, description="If PROMOTED, the routing rule id this became"
    )

    @model_validator(mode="after")
    def _witness_required(self) -> "Lesson":
        if self.witness_count < 1:
            raise ValueError("witness_count must be ≥ 1")
        return self

    def is_expired(self, now: Optional[datetime] = None) -> bool:
        now = now or datetime.now(UTC)
        return now > self.created_at + timedelta(days=self.ttl_days)

    def confirm(self, by_event_id: str) -> None:
        """Re-confirm by a new independent event."""
        self.witness_count += 1
        self.last_confirmed_at = datetime.now(UTC)
        if by_event_id not in self.source_event_ids:
            self.source_event_ids.append(by_event_id)


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════


# Templates for common extraction patterns
FAILURE_TEMPLATES: dict[str, str] = {
    "VOID": "Action VOID'd — likely violated constitutional floor; review L01/L02/L09/L11/L12/L13 before retry",
    "HOLD": "Action put in HOLD — likely needs human ack or substrate readiness check; review L05/L13",
    "timeout": "Action timed out — check resource bounds or split into smaller probes",
    "contradiction": "Cross-organ contradiction observed — escalate to executive, do not act on contested evidence",
    "low_quality": "Evidence quality below threshold — request stronger source before acting",
    "stale_envelope": "Envelope was stale (past expires_at) — refresh source data",
    "f02_truth": "L02 TRUTH failed — re-verify with independent witness",
    "f12_injection": "L12 INJECTION signature detected — sanitize all inputs",
}


def extract_from_failure(
    *,
    failure_kind: str,
    actor_id: str = "system",
    organ: str = "system",
    source_event_id: Optional[str] = None,
    extra_notes: str = "",
) -> Lesson:
    """Turn a failure event into a candidate lesson.

    Failure kinds recognized: VOID, HOLD, timeout, contradiction,
    low_quality, stale_envelope, f02_truth, f12_injection, or arbitrary
    (uses the kind as the lesson text prefix).
    """
    template = FAILURE_TEMPLATES.get(failure_kind)
    if template:
        text = template
        ltype = LessonType.RECOVERY
    else:
        text = f"Failure observed: {failure_kind}"
        ltype = LessonType.HEURISTIC
    if extra_notes:
        text = f"{text} — {extra_notes}"

    return Lesson(
        type=ltype,
        text=text,
        source_event_ids=[source_event_id] if source_event_id else [],
        organ=organ,
        actor_id=actor_id,
        tags=[failure_kind],
    )


def extract_from_contradiction(
    *,
    artifact_ref: str,
    organs: list[str],
    actor_id: str = "system",
) -> Lesson:
    """Distill a contradiction event into a lesson."""
    text = (
        f"Contradiction on {artifact_ref} between {', '.join(organs)} — "
        f"do not act on contested evidence; route to executive review"
    )
    return Lesson(
        type=LessonType.GUARD,
        text=text,
        organ="federation",
        actor_id=actor_id,
        tags=["contradiction", artifact_ref],
    )


def extract_from_confirmation(
    *,
    event_summary: str,
    actor_id: str = "system",
    organ: str = "system",
    source_event_id: Optional[str] = None,
) -> Lesson:
    """Distill a successful confirmation into a positive lesson."""
    return Lesson(
        type=LessonType.HEURISTIC,
        text=f"Confirmed pattern: {event_summary}",
        source_event_ids=[source_event_id] if source_event_id else [],
        organ=organ,
        actor_id=actor_id,
        tags=["confirmed"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# STORE — with promotion logic
# ═══════════════════════════════════════════════════════════════════════════════


class LessonStore:
    """The in-process lesson memory. Backs L4 (procedural) in production.

    Promotion rule: if the same `kind` of failure happens N=3 times
    (configurable), the lesson auto-promotes to a routing rule. After
    promotion, future calls matching the tag can be intercepted by the
    routing layer.
    """

    def __init__(self, promotion_threshold: int = 3):
        self._lessons: list[Lesson] = []
        self._by_tag: dict[str, list[Lesson]] = {}
        self._promoted_rules: dict[str, Lesson] = {}  # rule_id → Lesson
        self._promotion_threshold = promotion_threshold

    def add(self, lesson: Lesson) -> Lesson:
        self._lessons.append(lesson)
        for tag in lesson.tags:
            self._by_tag.setdefault(tag, []).append(lesson)

        # Auto-promote if same-kind count crosses threshold
        primary_tag = lesson.tags[0] if lesson.tags else None
        if primary_tag and len(self._by_tag[primary_tag]) >= self._promotion_threshold:
            # Promote the most recent, well-witnessed one
            candidates = sorted(
                self._by_tag[primary_tag],
                key=lambda l: (l.witness_count, l.last_confirmed_at),
                reverse=True,
            )
            promoted = candidates[0]
            if promoted.status != LessonStatus.PROMOTED:
                promoted.status = LessonStatus.PROMOTED
                rule_id = f"rule_{primary_tag}_{promoted.lesson_id[:8]}"
                promoted.promoted_to_rule = rule_id
                self._promoted_rules[rule_id] = promoted
                logger.info(
                    f"lesson {promoted.lesson_id} promoted to rule {rule_id} "
                    f"after {len(self._by_tag[primary_tag])} confirmations"
                )
        return lesson

    def add_failure(
        self,
        failure_kind: str,
        *,
        actor_id: str = "system",
        organ: str = "system",
        source_event_id: Optional[str] = None,
        extra_notes: str = "",
    ) -> Lesson:
        lesson = extract_from_failure(
            failure_kind=failure_kind,
            actor_id=actor_id,
            organ=organ,
            source_event_id=source_event_id,
            extra_notes=extra_notes,
        )
        return self.add(lesson)

    def add_contradiction(
        self,
        artifact_ref: str,
        organs: list[str],
        *,
        actor_id: str = "system",
    ) -> Lesson:
        lesson = extract_from_contradiction(
            artifact_ref=artifact_ref,
            organs=organs,
            actor_id=actor_id,
        )
        return self.add(lesson)

    def add_confirmation(
        self,
        event_summary: str,
        *,
        actor_id: str = "system",
        organ: str = "system",
        source_event_id: Optional[str] = None,
    ) -> Lesson:
        lesson = extract_from_confirmation(
            event_summary=event_summary,
            actor_id=actor_id,
            organ=organ,
            source_event_id=source_event_id,
        )
        return self.add(lesson)

    def get_for_tag(self, tag: str) -> list[Lesson]:
        return list(self._by_tag.get(tag, []))

    def active_lessons(self) -> list[Lesson]:
        return [l for l in self._lessons if l.status in (LessonStatus.NEW, LessonStatus.PROMOTED) and not l.is_expired()]

    def expired_lessons(self) -> list[Lesson]:
        return [l for l in self._lessons if l.is_expired() and l.status != LessonStatus.EXPIRED]

    def sweep_expired(self) -> int:
        n = 0
        for l in self.expired_lessons():
            l.status = LessonStatus.EXPIRED
            n += 1
        return n

    def promoted_rules(self) -> dict[str, Lesson]:
        return dict(self._promoted_rules)

    def stats(self) -> dict[str, Any]:
        active = self.active_lessons()
        return {
            "lessons_total": len(self._lessons),
            "active": len(active),
            "expired": len(self.expired_lessons()),
            "promoted": len(self._promoted_rules),
            "by_status": {s.value: sum(1 for l in self._lessons if l.status == s) for s in LessonStatus},
            "by_tag": {t: len(ls) for t, ls in self._by_tag.items()},
            "promotion_threshold": self._promotion_threshold,
        }


# Module-level singleton
_store: Optional[LessonStore] = None


def get_store() -> LessonStore:
    global _store
    if _store is None:
        _store = LessonStore()
    return _store

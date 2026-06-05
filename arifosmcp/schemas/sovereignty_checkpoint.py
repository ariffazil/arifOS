"""
Sovereignty Checkpoint — Human Wakefulness Protocol
═══════════════════════════════════════════════════════════════════════════════

Chapter 6 Upgrade (Kissinger/Schmidt/Huttenlocher → arifOS Federation):
The danger is not rogue AI. The danger is the human becoming passive.

This schema implements the four-question wakefulness checkpoint that gates
every high-impact action in the federation. Before the machine acts, the
human must consciously engage with:

  1. What evidence are you accepting?
  2. What uncertainty are you tolerating?
  3. What responsibility are you assuming?
  4. What rollback or repair path exists?

Without a completed checkpoint, the tool returns 888_HOLD.

DITEMPA BUKAN DIBERI — The sovereign stays awake.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════════════════════
# CHECKPOINT STATUS
# ═══════════════════════════════════════════════════════════════════════════════


class CheckpointStatus(StrEnum):
    """Status of a sovereignty checkpoint."""

    PENDING = "pending"  # Questions issued, awaiting human answers
    COMPLETED = "completed"  # Human answered all four questions
    EXPIRED = "expired"  # Checkpoint timed out (default: 300s)
    WAIVED = "waived"  # Explicitly waived by sovereign (F13 only)
    REJECTED = "rejected"  # Human declined to proceed


class WakefulnessLevel(StrEnum):
    """How awake the human is, as measured by checkpoint behaviour."""

    AWAKE = "awake"  # Human actively engaged, answers thoughtful
    PRESENT = "present"  # Human present but answers surface-level
    DISTRACTED = "distracted"  # Human answering quickly, no deep engagement
    ASLEEP = "asleep"  # Human rubber-stamping, pattern detected
    UNKNOWN = "unknown"  # No checkpoint data yet


# ═══════════════════════════════════════════════════════════════════════════════
# THE FOUR QUESTIONS
# ═══════════════════════════════════════════════════════════════════════════════


class CheckpointQuestion(BaseModel):
    """A single wakefulness question presented to the human."""

    question_id: str = Field(
        description="e.g. 'evidence', 'uncertainty', 'responsibility', 'repair'"
    )
    question_text: str = Field(description="The question as presented to the human")
    question_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Context passed to help the human answer (tool, risk, evidence summary)",
    )


class CheckpointAnswer(BaseModel):
    """The human's answer to a wakefulness question."""

    question_id: str = Field(description="Which question this answers")
    answer_text: str = Field(description="The human's response in their own words")
    answered_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the human answered",
    )
    answer_depth: str = Field(
        default="surface",
        description="surface | considered | deep — AI-classified depth of engagement",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SOVEREIGNTY CHECKPOINT
# ═══════════════════════════════════════════════════════════════════════════════


class SovereigntyCheckpoint(BaseModel):
    """
    The four-question wakefulness ritual.

    Before any high-impact action (dignity, memory mutation, vault write,
    identity operation, external effect at scale, or ATOMIC action), the
    human must consciously engage with four questions.

    This is the operational form of F13 SOVEREIGN — not a binary veto
    switch, but a ritual that keeps the human awake.
    """

    # ── Identity ────────────────────────────────────────────────────────
    checkpoint_id: str = Field(
        default_factory=lambda: f"CHK-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}",
        description="Unique checkpoint identifier",
    )
    status: CheckpointStatus = Field(
        default=CheckpointStatus.PENDING,
        description="Current state of this checkpoint",
    )
    session_id: str = Field(description="Governing session")
    actor_id: str = Field(description="Who must answer the questions")

    # ── Context: what triggered this checkpoint ─────────────────────────
    tool_name: str = Field(description="Which tool triggered the checkpoint")
    tool_description: str = Field(default="", description="What the tool does")
    risk_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Risk tier, action class, blast radius, reversibility",
    )
    evidence_summary: str = Field(
        default="",
        description="Summary of evidence available for the human to review",
    )

    # ── The Four Questions ───────────────────────────────────────────────
    questions: list[CheckpointQuestion] = Field(
        default_factory=list,
        description="The four wakefulness questions",
    )
    answers: list[CheckpointAnswer] = Field(
        default_factory=list,
        description="The human's answers (empty until completed)",
    )

    # ── Metadata ────────────────────────────────────────────────────────
    issued_at: str = Field(
        default_factory=lambda: datetime.now(UTC).isoformat(),
        description="When the checkpoint was issued",
    )
    completed_at: str | None = Field(
        default=None,
        description="When the human completed the checkpoint",
    )
    expires_at: str = Field(
        default_factory=lambda: (datetime.now(UTC) + timedelta(seconds=300)).isoformat(),
        description="When this checkpoint expires (default: 300s from issue)",
    )
    wakefulness_level: WakefulnessLevel = Field(
        default=WakefulnessLevel.UNKNOWN,
        description="AI-assessed wakefulness level based on answer depth and timing",
    )

    # ── Validation ──────────────────────────────────────────────────────

    def is_complete(self) -> bool:
        """True if all four questions have been answered."""
        answered_ids = {a.question_id for a in self.answers}
        required_ids = {q.question_id for q in self.questions}
        return required_ids == answered_ids

    def is_expired(self) -> bool:
        """True if the checkpoint has expired."""
        try:
            expiry = datetime.fromisoformat(self.expires_at)
            return datetime.now(UTC) > expiry
        except Exception:
            return True  # Fail closed

    def is_valid(self) -> tuple[bool, str]:
        """
        Full validation: complete, not expired, not rejected.
        Returns (ok, reason).
        """
        if self.status == CheckpointStatus.REJECTED:
            return False, "Checkpoint was rejected by the sovereign"
        if self.status == CheckpointStatus.EXPIRED:
            return False, "Checkpoint expired — reissue before proceeding"
        if self.is_expired():
            return False, "Checkpoint TTL expired — reissue before proceeding"
        if not self.is_complete():
            missing = {q.question_id for q in self.questions} - {
                a.question_id for a in self.answers
            }
            return False, f"Checkpoint incomplete — missing answers: {missing}"
        if self.status == CheckpointStatus.WAIVED:
            return True, "WAIVED by F13 sovereign — bypassing checkpoint"
        if self.status == CheckpointStatus.COMPLETED:
            return True, "SEAL"
        return False, f"Unknown checkpoint status: {self.status.value}"

    def to_log_dict(self) -> dict[str, Any]:
        """Serialize for audit (no sensitive answer content)."""
        return {
            "checkpoint_id": self.checkpoint_id,
            "status": self.status.value,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "tool_name": self.tool_name,
            "questions_asked": len(self.questions),
            "questions_answered": len(self.answers),
            "is_complete": self.is_complete(),
            "wakefulness_level": self.wakefulness_level.value,
            "issued_at": self.issued_at,
            "completed_at": self.completed_at,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CHECKPOINT REQUEST — what the middleware returns on HOLD
# ═══════════════════════════════════════════════════════════════════════════════


class SovereigntyCheckpointRequest(BaseModel):
    """
    Returned by the middleware when a tool requires a sovereignty checkpoint.

    The agent should present the four questions to the human, collect answers,
    and resubmit the tool call with the completed checkpoint in the envelope.
    """

    verdict: str = Field(default="888_HOLD", description="Always 888_HOLD")
    reason: str = Field(
        default="Sovereignty checkpoint required — human must verify wakefulness before this action proceeds.",
        description="Why the hold was triggered",
    )
    checkpoint: SovereigntyCheckpoint = Field(
        description="The checkpoint with four questions for the human",
    )
    instructions: str = Field(
        default=(
            "Present each question to the human. Record their answers verbatim. "
            "Resubmit the tool call with the completed checkpoint embedded in "
            "the FederationEnvelope as 'sovereignty_checkpoint'. "
            "This checkpoint expires in 5 minutes."
        ),
        description="How to proceed",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FACTORY — build the four canonical checkpoint questions
# ═══════════════════════════════════════════════════════════════════════════════


def build_sovereignty_checkpoint(
    tool_name: str,
    session_id: str,
    actor_id: str,
    risk_summary: dict[str, Any],
    tool_description: str = "",
    evidence_summary: str = "",
) -> SovereigntyCheckpoint:
    """
    Build a SovereigntyCheckpoint with the four canonical wakefulness questions.

    These four questions are the operational form of Chapter 6's design tests:
    agency, dignity, judgment, truth, responsibility, identity.
    """
    now = datetime.now(UTC)
    expiry = (now + timedelta(seconds=300)).isoformat()

    questions = [
        CheckpointQuestion(
            question_id="evidence",
            question_text=(
                f"What evidence are you accepting for this action ({tool_name})? "
                "List the specific sources, observations, or data points that justify proceeding."
            ),
            question_context={
                "tool_name": tool_name,
                "tool_description": tool_description,
                "risk_summary": risk_summary,
                "evidence_summary": evidence_summary,
            },
        ),
        CheckpointQuestion(
            question_id="uncertainty",
            question_text=(
                f"What uncertainty are you tolerating for this action ({tool_name})? "
                "What could be wrong? What is your confidence level (0.0-1.0), and why?"
            ),
            question_context={
                "tool_name": tool_name,
                "risk_summary": risk_summary,
            },
        ),
        CheckpointQuestion(
            question_id="responsibility",
            question_text=(
                f"What responsibility are you assuming for this action ({tool_name})? "
                "If this goes wrong, who answers? What are the consequences you accept?"
            ),
            question_context={
                "tool_name": tool_name,
                "risk_summary": risk_summary,
            },
        ),
        CheckpointQuestion(
            question_id="repair",
            question_text=(
                f"What rollback or repair path exists for this action ({tool_name})? "
                "How can this be undone or corrected if the outcome is wrong?"
            ),
            question_context={
                "tool_name": tool_name,
                "reversibility": risk_summary.get("reversibility", "unknown"),
            },
        ),
    ]

    return SovereigntyCheckpoint(
        status=CheckpointStatus.PENDING,
        session_id=session_id,
        actor_id=actor_id,
        tool_name=tool_name,
        tool_description=tool_description,
        risk_summary=risk_summary,
        evidence_summary=evidence_summary,
        questions=questions,
        answers=[],
        issued_at=now.isoformat(),
        expires_at=expiry,
        wakefulness_level=WakefulnessLevel.UNKNOWN,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WAKEFULNESS ASSESSMENT
# ═══════════════════════════════════════════════════════════════════════════════


def assess_wakefulness(
    checkpoint: SovereigntyCheckpoint,
    time_to_complete_seconds: float | None = None,
) -> WakefulnessLevel:
    """
    Assess the human's wakefulness level based on checkpoint answers.

    Heuristics:
      - All answers >50 words, thoughtful → AWAKE
      - All answers present, mixed depth → PRESENT
      - Answers <20 words each, fast completion → DISTRACTED
      - All answers near-identical, minimal variation → ASLEEP
      - Incomplete → UNKNOWN
    """
    if not checkpoint.is_complete():
        return WakefulnessLevel.UNKNOWN

    answers = checkpoint.answers
    if not answers:
        return WakefulnessLevel.UNKNOWN

    # Average answer length
    avg_length = sum(len(a.answer_text) for a in answers) / len(answers)

    # Depth scores
    depth_scores = {
        "deep": 3,
        "considered": 2,
        "surface": 1,
    }
    avg_depth = sum(depth_scores.get(a.answer_depth, 1) for a in answers) / len(answers)

    # Word count check
    total_words = sum(len(a.answer_text.split()) for a in answers)

    # Speed check
    fast_completion = time_to_complete_seconds is not None and time_to_complete_seconds < 30

    # Variation check — are answers distinct?
    unique_answers = len({a.answer_text.strip().lower() for a in answers})

    if avg_depth >= 2.5 and total_words > 200:
        return WakefulnessLevel.AWAKE
    elif unique_answers <= 2 and total_words < 30:
        # Near-identical short answers = rubber-stamping
        return WakefulnessLevel.ASLEEP
    elif avg_depth >= 1.5 and total_words >= 60:
        return WakefulnessLevel.PRESENT
    elif fast_completion or total_words < 60:
        return WakefulnessLevel.DISTRACTED
    else:
        return WakefulnessLevel.PRESENT


# ═══════════════════════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Enums
    "CheckpointStatus",
    "WakefulnessLevel",
    # Schemas
    "CheckpointQuestion",
    "CheckpointAnswer",
    "SovereigntyCheckpoint",
    "SovereigntyCheckpointRequest",
    # Factory
    "build_sovereignty_checkpoint",
    # Assessment
    "assess_wakefulness",
]

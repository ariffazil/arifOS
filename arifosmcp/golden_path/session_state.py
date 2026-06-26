"""
arifOS Golden Path — Session State
═══════════════════════════════════

The typed object passed between all 7 constitutional organs.
Not prose. A machine-parseable structure the next organ can validate.

DITEMPA BUKAN DIBERI 🔥⚒️
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ────────────────────────────────────────────────────────────────────

class Verdict(str, Enum):
    """555_JUDGE verdict options."""
    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"
    PENDING = "PENDING"


class Readiness(str, Enum):
    """666_CRITIQUE readiness options."""
    FORGE_READY = "FORGE_READY"
    HOLD_FOR_REVIEW = "HOLD_FOR_REVIEW"
    BLOCK = "BLOCK"
    PENDING = "PENDING"


class FloorStatus(str, Enum):
    """Floor evaluation status."""
    PASS = "PASS"
    FAIL = "FAIL"
    UNCERTAIN = "UNCERTAIN"
    NA = "N/A"


class Reversibility(str, Enum):
    """Reversibility classification."""
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    IRREVERSIBLE = "IRREVERSIBLE"


class BlastRadius(str, Enum):
    """Blast radius estimate."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ── Sub-models ───────────────────────────────────────────────────────────────

class StageRecord(BaseModel):
    """Record of a single organ's execution."""
    stage: str = Field(description="Organ ID: 000, 111, 333, 555, 666, 777, 999")
    name: str = Field(description="Organ name: INIT, SENSE, REASON, JUDGE, CRITIQUE, FORGE, SEAL")
    revision: int = Field(default=1, description="Which revision cycle this execution was in")
    output_summary: str = Field(default="", description="Brief summary of organ output")
    output_hash: str = Field(default="", description="SHA-256 of full output")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verdict: Optional[str] = Field(default=None, description="Verdict if this was a judge/forge organ")
    floor_violations: list[str] = Field(default_factory=list, description="Floor IDs that failed")
    readiness: Optional[str] = Field(default=None, description="Readiness if critique organ")


class FloorScore(BaseModel):
    """Computed or declared score for a constitutional floor."""
    floor_id: str = Field(description="F1..F13")
    status: FloorStatus = Field(default=FloorStatus.UNCERTAIN)
    score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    evidence: str = Field(default="", description="What supports this score")
    computed: bool = Field(default=False, description="True if algorithmically measured")


class Assumption(BaseModel):
    """A critical assumption from the assumption ledger."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    statement: str = Field(description="The assumption")
    implication_if_wrong: str = Field(description="What breaks if this is wrong")
    session_id: str = Field(default="", description="Session that made this assumption")
    stage: str = Field(default="", description="Stage that made this assumption")
    invalidated: bool = Field(default=False)
    invalidated_in_session: Optional[str] = Field(default=None)


# ── Session State ────────────────────────────────────────────────────────────

class SessionState(BaseModel):
    """
    The living record shared by all 7 constitutional organs.

    This is the spine of the golden path loop. Every organ reads from it
    and writes to it. No organ modifies a previous organ's output.

    v2026.06.26 — Forged to bridge constitutional identity with runtime engine.
    """

    # Identity
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: str = Field(default="anonymous", description="Identity of the engineer")
    actor_hash: str = Field(default="", description="SHA-256 of verified binding")

    # Loop mechanics
    revision_cycle: int = Field(default=1, description="Increments on SABAR return")
    returned_from: Optional[str] = Field(default=None, description="Which organ sent us back")
    loop_count: int = Field(default=0, description="Total iterations across all organs")
    max_loops: int = Field(default=5, description="Metabolic termination ceiling")

    # Current state
    current_stage: str = Field(default="000", description="Current organ ID")
    current_verdict: Verdict = Field(default=Verdict.PENDING)
    current_readiness: Readiness = Field(default=Readiness.PENDING)

    # History
    stage_history: list[StageRecord] = Field(default_factory=list)
    floor_scores: dict[str, FloorScore] = Field(default_factory=dict)
    verdict_history: list[dict] = Field(default_factory=list)

    # Cross-session memory
    assumption_ledger: list[Assumption] = Field(default_factory=list)
    prior_session_id: Optional[str] = Field(default=None)
    prior_seal_hash: Optional[str] = Field(default=None)

    # Metadata
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    sealed_at: Optional[str] = Field(default=None)

    # ── Methods ──────────────────────────────────────────────────────────

    def add_stage_record(self, record: StageRecord) -> None:
        """Append a stage record to history. No modification of prior records."""
        self.stage_history.append(record)
        self.current_stage = record.stage

    def has_stage(self, stage_id: str) -> bool:
        """Check if a stage has been completed in this session."""
        return any(r.stage == stage_id for r in self.stage_history)

    def get_stage_record(self, stage_id: str) -> Optional[StageRecord]:
        """Get the most recent record for a given stage."""
        for r in reversed(self.stage_history):
            if r.stage == stage_id:
                return r
        return None

    def set_verdict(self, verdict: Verdict, reasons: list[str] | None = None) -> None:
        """Set the current verdict and append to history."""
        self.current_verdict = verdict
        self.verdict_history.append({
            "verdict": verdict.value,
            "stage": self.current_stage,
            "revision": self.revision_cycle,
            "reasons": reasons or [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def set_floor_score(self, floor_id: str, score: FloorScore) -> None:
        """Set or update a floor score."""
        self.floor_scores[floor_id] = score

    def compute_seal_hash(self) -> str:
        """Compute SHA-256 of the full session state for sealing."""
        content = self.model_dump_json()
        return hashlib.sha256(content.encode()).hexdigest()

    def get_metabolic_budget_remaining(self) -> int:
        """How many more loops before forced termination."""
        return max(0, self.max_loops - self.loop_count)

    def is_metabolically_exhausted(self) -> bool:
        """True if the pipeline has looped too many times."""
        return self.loop_count >= self.max_loops

    def increment_loop(self) -> None:
        """Increment the loop counter."""
        self.loop_count += 1

    def start_revision(self, returned_from: str) -> None:
        """Start a new revision cycle after SABAR or HOLD_FOR_REVIEW."""
        self.returned_from = returned_from
        self.revision_cycle += 1
        self.increment_loop()

    def to_context_string(self) -> str:
        """Render session state as context string for prompt injection."""
        lines = [
            f"SESSION STATE (v2026.06.26)",
            f"  session_id: {self.session_id}",
            f"  actor_id: {self.actor_id}",
            f"  revision_cycle: {self.revision_cycle}",
            f"  returned_from: {self.returned_from or 'none'}",
            f"  loop_count: {self.loop_count}/{self.max_loops}",
            f"  metabolic_budget: {self.get_metabolic_budget_remaining()}",
            f"  current_verdict: {self.current_verdict.value}",
            f"  current_readiness: {self.current_readiness.value}",
            f"  stages_completed: {[r.stage for r in self.stage_history]}",
        ]

        if self.floor_scores:
            lines.append("  floor_scores:")
            for fid, fs in self.floor_scores.items():
                computed_tag = " [COMPUTED]" if fs.computed else " [DECLARED]"
                lines.append(
                    f"    {fid}: {fs.status.value} "
                    f"(score={fs.score}){computed_tag}"
                )

        if self.prior_session_id:
            lines.append(f"  prior_session_id: {self.prior_session_id}")
            lines.append(f"  prior_assumptions: {len(self.assumption_ledger)}")

        if self.returned_from:
            lines.append(f"  ⚠️  RETURNING from {self.returned_from} — revision {self.revision_cycle}")

        return "\n".join(lines)


# ── Factory ──────────────────────────────────────────────────────────────────

def create_session(
    actor_id: str = "anonymous",
    actor_hash: str = "",
    prior_session_id: str | None = None,
    prior_seal_hash: str | None = None,
    assumptions: list[Assumption] | None = None,
) -> SessionState:
    """Create a new session state with optional cross-session memory."""
    return SessionState(
        actor_id=actor_id,
        actor_hash=actor_hash,
        prior_session_id=prior_session_id,
        prior_seal_hash=prior_seal_hash,
        assumption_ledger=assumptions or [],
    )


__all__ = [
    "SessionState",
    "StageRecord",
    "FloorScore",
    "Assumption",
    "Verdict",
    "Readiness",
    "FloorStatus",
    "Reversibility",
    "BlastRadius",
    "create_session",
]

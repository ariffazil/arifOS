"""
arifosmcp/runtime/mind_state.py — MIND Persistent State v1
═══════════════════════════════════════════════════════════════
333_MIND state object for recursive self-correcting reasoning.

Every arif_mind_reason step snapshots state here. Between steps,
the feedback loop reads this to decide re-plan / branch / rollback.
Between sessions, Qdrant + L5 Graphiti restore this so MIND never
starts from zero.

ARCHITECTURE
───────────
  MINDState (this file)       — ephemeral + checkpoints
  feedback_loop.py            — reads MINDState, writes graph edges
  l5_graph_read.py            — queries Graphiti for prior plans
  l5_graphiti_bridge.py       — fire-and-forget write path (existing)

F-FLOOR BINDING
───────────────
  F01 (AMANAH)   — all state mutations are reversible (checkpoint/rollback)
  F02 (TRUTH)    — epistemic_band tracked per step, uncertainty declared
  F04 (CLARITY)  — every checkpoint is structured, not free-text
  F07 (HUMILITY) — omega_0 tracked, hard-capped at 0.90
  F08 (GENIUS)   — self-correction count limits infinite loops
  F09 (ANTIHANTU) — no consciousness claims in any state field

REVERSIBILITY
─────────────
  All writes go through `checkpoint()` → Qdrant + L5. No direct DB writes.
  Removing the import in mind_reason.py = full rollback. Zero kernel mod.

AUTHORITY: 333_MIND, 888_JUDGE
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC, timedelta
from enum import StrEnum
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class StepStatus(StrEnum):
    """Status of a single reasoning step within a plan."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REVISED = "revised"          # self-corrected, new attempt
    SKIPPED = "skipped"          # branch not taken
    HOLD = "hold"                # awaiting 888 decision


class PlanStatus(StrEnum):
    """Overall plan execution status."""
    ACTIVE = "active"
    STALLED = "stalled"          # step failure, awaiting revision
    DIVERGED = "diverged"        # unexpected outcome, re-plan triggered
    HOLD = "hold"                # 888_HOLD signalled
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class EpistemicTag(StrEnum):
    """F2 truth classification per step."""
    CLAIM = "CLAIM"              # asserted, not yet verified
    PLAUSIBLE = "PLAUSIBLE"      # consistent but not proven
    HYPOTHESIS = "HYPOTHESIS"    # testable, awaiting evidence
    ESTIMATE = "ESTIMATE"        # approximate, band declared
    VERIFIED = "VERIFIED"        # evidence-backed, multi-witness
    DISPROVEN = "DISPROVEN"      # evidence contradicted


class FeedbackSignal(StrEnum):
    """Signals sent to the graph memory after step evaluation."""
    PROCEED = "PROCEED"          # step OK, continue
    REVISE_LOCAL = "REVISE_LOCAL"  # fix within sequential loop
    REVISE_GLOBAL = "REVISE_GLOBAL"  # re-plan at graph level
    BRANCH = "BRANCH"            # take alternative path
    BACKTRACK = "BACKTRACK"      # return to prior checkpoint
    HOLD = "HOLD"                # stop, escalate to 888


# ═══════════════════════════════════════════════════════════════════════════════
# DATA MODELS
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class ReasoningStep:
    """A single step in the reasoning chain, mirroring Sequential Thinking."""
    step_number: int
    content: str
    step_type: str = "analysis"
    status: StepStatus = StepStatus.PENDING
    epistemic_tag: EpistemicTag = EpistemicTag.CLAIM
    confidence: float = 0.5       # 0.0–0.90 (F7 cap)
    is_revision: bool = False
    revises_step: int | None = None
    branch_id: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    attempt_count: int = 0
    error_message: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["epistemic_tag"] = self.epistemic_tag.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ReasoningStep:
        d = dict(d)
        d["status"] = StepStatus(d.get("status", "pending"))
        d["epistemic_tag"] = EpistemicTag(d.get("epistemic_tag", "CLAIM"))
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class MINDState:
    """Persistent state object for recursive self-correcting reasoning.

    Lives in:
      - Runtime memory (current plan — ephemeral)
      - Qdrant vector store (checkpoints — semantic retrieval)
      - L5 Graphiti (entity graph — structural retrieval)

    Between sessions, Qdrant + Graphiti restore the state skeleton.
    """
    # ── Identity ──
    context_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    session_id: str | None = None
    actor_id: str = "888"

    # ── Task ──
    goal: str = ""
    constraints: list[str] = field(default_factory=list)
    domain: str = "general"
    intent: str = "metabolize"          # MindIntent

    # ── Plan ──
    plan_steps: list[ReasoningStep] = field(default_factory=list)
    current_step: int = 0
    plan_status: PlanStatus = PlanStatus.ACTIVE
    total_revisions: int = 0
    max_revisions: int = 7              # F08 guard: prevent infinite loops

    # ── Epistemic (F2, F7) ──
    epistemic_band: float = 0.5         # overall P(truth)
    omega_0: float = 0.04               # baseline humility (F7: 0.03–0.05)
    c_dark: float = 0.0                 # anti-hantu score (F9: must be < 0.30)

    # ── Constitutional (F1–F13) ──
    malu_index: float = 0.0             # accumulated shame score
    floor_violations: list[dict[str, Any]] = field(default_factory=list)
    reversibility_flags: list[str] = field(default_factory=list)

    # ── Memory Refs ──
    memory_refs: dict[str, Any] = field(default_factory=dict)
    # e.g. {"qdrant_ids": [...], "graphiti_uuids": [...], "pg_row_ids": [...]}

    # ── Graph Meta ──
    similar_task_refs: list[str] = field(default_factory=list)
    capability_subgraph_nodes: list[str] = field(default_factory=list)

    # ── Checkpoint ──
    checkpoints: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    version: int = 1

    # ═══════════════════════════════════════════════════════════════════════
    # STATE MUTATIONS
    # ═══════════════════════════════════════════════════════════════════════

    def add_step(self, content: str, step_type: str = "analysis",
                 epistemic_tag: EpistemicTag = EpistemicTag.CLAIM,
                 confidence: float = 0.5) -> ReasoningStep:
        """Add a new reasoning step to the plan."""
        step = ReasoningStep(
            step_number=len(self.plan_steps) + 1,
            content=content,
            step_type=step_type,
            epistemic_tag=epistemic_tag,
            confidence=min(confidence, 0.90),  # F7 cap
        )
        self.plan_steps.append(step)
        self._touch()
        return step

    def mark_step(self, step_number: int, status: StepStatus,
                  error_message: str | None = None,
                  feedback: FeedbackSignal | None = None) -> ReasoningStep | None:
        """Mark a step's status and record feedback signal."""
        for step in self.plan_steps:
            if step.step_number == step_number:
                step.status = status
                if error_message:
                    step.error_message = error_message
                if status == StepStatus.FAILED:
                    step.attempt_count += 1
                    self.total_revisions += 1
                step.timestamp = datetime.now(UTC).isoformat()
                self._touch()

                # Auto-trigger plan status transitions
                if feedback == FeedbackSignal.HOLD:
                    self.plan_status = PlanStatus.HOLD
                elif feedback == FeedbackSignal.REVISE_GLOBAL:
                    self.plan_status = PlanStatus.DIVERGED
                elif feedback == FeedbackSignal.BACKTRACK:
                    self.plan_status = PlanStatus.DIVERGED

                # F08 guard: too many revisions → HOLD
                if self.total_revisions >= self.max_revisions:
                    self.plan_status = PlanStatus.HOLD
                    logger.warning(
                        "MINDState %s: max_revisions (%d) reached → HOLD",
                        self.context_id, self.max_revisions,
                    )

                return step
        return None

    def revise_step(self, step_number: int, new_content: str,
                    reason: str = "") -> ReasoningStep:
        """Create a revised version of a failed step."""
        original = next((s for s in self.plan_steps
                         if s.step_number == step_number), None)
        revision = ReasoningStep(
            step_number=len(self.plan_steps) + 1,
            content=new_content,
            step_type=original.step_type if original else "analysis",
            status=StepStatus.IN_PROGRESS,
            epistemic_tag=EpistemicTag.HYPOTHESIS,
            is_revision=True,
            revises_step=step_number,
            branch_id=original.branch_id if original else None,
        )
        if original:
            original.status = StepStatus.REVISED
        self.plan_steps.append(revision)
        self.total_revisions += 1
        self._touch()
        return revision

    def update_epistemic(self, band: float, omega_0: float | None = None):
        """Update epistemic tracking (F2, F7)."""
        self.epistemic_band = min(band, 0.90)  # F7 cap
        if omega_0 is not None:
            self.omega_0 = max(0.03, min(omega_0, 0.05))  # F7 band

    def record_violation(self, floor: str, detail: str, severity: float = 5.0):
        """Record a constitutional floor violation."""
        self.floor_violations.append({
            "floor": floor,
            "detail": detail,
            "severity": severity,
            "timestamp": datetime.now(UTC).isoformat(),
        })
        self.malu_index += severity / 100.0  # normalized
        self._touch()

    # ═══════════════════════════════════════════════════════════════════════
    # CHECKPOINT / PERSISTENCE
    # ═══════════════════════════════════════════════════════════════════════

    def checkpoint(self) -> dict[str, Any]:
        """Create a checkpoint snapshot of current state.

        Returns a dict suitable for Qdrant vector store + Graphiti episode.
        The caller is responsible for actually writing to those stores.
        """
        snapshot = self.to_dict()
        checkpoint_entry = {
            "checkpoint_id": uuid.uuid4().hex,
            "context_id": self.context_id,
            "version": self.version,
            "timestamp": datetime.now(UTC).isoformat(),
            "current_step": self.current_step,
            "plan_status": self.plan_status.value,
            "total_steps": len(self.plan_steps),
            "total_revisions": self.total_revisions,
            "epistemic_band": self.epistemic_band,
            "malu_index": self.malu_index,
            "state_hash": self.state_hash(),
            "snapshot": snapshot,
        }
        self.checkpoints.append(checkpoint_entry)
        self.version += 1
        self._touch()
        return checkpoint_entry

    def state_hash(self) -> str:
        """Cryptographic hash of the current state (F2 verifiability)."""
        core = {
            "goal": self.goal,
            "constraints": self.constraints,
            "step_count": len(self.plan_steps),
            "current_step": self.current_step,
            "plan_status": self.plan_status.value,
            "total_revisions": self.total_revisions,
            "epistemic_band": self.epistemic_band,
            "malu_index": self.malu_index,
        }
        return hashlib.sha256(
            json.dumps(core, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

    def last_checkpoint(self) -> dict[str, Any] | None:
        """Return the most recent checkpoint, if any."""
        return self.checkpoints[-1] if self.checkpoints else None

    def rollback_to(self, checkpoint_idx: int = -1) -> bool:
        """Roll back state to a previous checkpoint.

        F1 AMANAH: this is the reversibility mechanism. All state mutations
        are undoable as long as checkpoints exist.
        """
        if not self.checkpoints:
            return False
        idx = checkpoint_idx if checkpoint_idx >= 0 else len(self.checkpoints) + checkpoint_idx
        if idx < 0 or idx >= len(self.checkpoints):
            return False
        # Restore from snapshot
        cp = self.checkpoints[idx]
        snap = cp.get("snapshot", {})
        for key, value in snap.items():
            if key in ("plan_steps",):
                self.plan_steps = [
                    ReasoningStep.from_dict(s) for s in value
                ]
            elif key in ("plan_status",):
                self.plan_status = PlanStatus(value)
            elif hasattr(self, key) and key not in (
                "checkpoints", "version", "created_at", "updated_at",
                "context_id",
            ):
                setattr(self, key, value)
        # Trim checkpoints after the target
        self.checkpoints = self.checkpoints[:idx + 1]
        self.version += 1
        self._touch()
        logger.info("MINDState %s: rolled back to checkpoint %d", self.context_id, idx)
        return True

    # ═══════════════════════════════════════════════════════════════════════
    # SERIALIZATION
    # ═══════════════════════════════════════════════════════════════════════

    def to_dict(self) -> dict[str, Any]:
        """Full serialization for persistence."""
        return {
            "context_id": self.context_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "goal": self.goal,
            "constraints": self.constraints,
            "domain": self.domain,
            "intent": self.intent,
            "plan_steps": [s.to_dict() for s in self.plan_steps],
            "current_step": self.current_step,
            "plan_status": self.plan_status.value,
            "total_revisions": self.total_revisions,
            "max_revisions": self.max_revisions,
            "epistemic_band": self.epistemic_band,
            "omega_0": self.omega_0,
            "c_dark": self.c_dark,
            "malu_index": self.malu_index,
            "floor_violations": self.floor_violations,
            "reversibility_flags": self.reversibility_flags,
            "memory_refs": self.memory_refs,
            "similar_task_refs": self.similar_task_refs,
            "capability_subgraph_nodes": self.capability_subgraph_nodes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> MINDState:
        """Deserialize from a persisted dict."""
        d = dict(d)
        d["plan_steps"] = [
            ReasoningStep.from_dict(s) for s in d.get("plan_steps", [])
        ]
        d["plan_status"] = PlanStatus(d.get("plan_status", "active"))
        # Remove checkpoint-only fields that aren't constructor params
        for drop in ("checkpoints", "state_hash", "snapshot"):
            d.pop(drop, None)
        return cls(**{k: v for k, v in d.items()
                      if k in cls.__dataclass_fields__})

    def _touch(self):
        """Update modification timestamp."""
        self.updated_at = datetime.now(UTC).isoformat()


# ═══════════════════════════════════════════════════════════════════════════════
# LIFECYCLE
# ═══════════════════════════════════════════════════════════════════════════════


def create_mind_state(
    goal: str,
    intent: str = "metabolize",
    domain: str = "general",
    constraints: list[str] | None = None,
    session_id: str | None = None,
) -> MINDState:
    """Factory: create a fresh MIND state for a new reasoning task."""
    return MINDState(
        goal=goal,
        intent=intent,
        domain=domain,
        constraints=constraints or [],
        session_id=session_id,
    )


def is_stale(state: MINDState, max_age_minutes: int = 30) -> bool:
    """Check if a MIND state is too old to resume (F08 guard)."""
    try:
        updated = datetime.fromisoformat(state.updated_at)
        age = datetime.now(UTC) - updated
        return age > timedelta(minutes=max_age_minutes)
    except (ValueError, TypeError):
        return True


def can_continue(state: MINDState) -> tuple[bool, str]:
    """Check if execution can continue given current state.

    Returns (can_continue, reason).
    """
    if state.plan_status == PlanStatus.HOLD:
        return False, "Plan is HOLD — requires 888 intervention"
    if state.plan_status == PlanStatus.ABANDONED:
        return False, "Plan was abandoned"
    if state.total_revisions >= state.max_revisions:
        return False, f"Max revisions ({state.max_revisions}) reached"
    if state.malu_index >= 0.60:
        return False, f"Malu index ({state.malu_index:.2f}) ≥ 0.60 — BERAT threshold"
    if state.c_dark >= 0.30:
        return False, f"C_dark ({state.c_dark:.2f}) ≥ 0.30 — F9 ANTI-HANTU threshold"
    return True, "OK"

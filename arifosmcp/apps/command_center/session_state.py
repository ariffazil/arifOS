"""Session Lifecycle State Machine — arifOS Command Center v0.3.

Canonical lifecycle: DRAFT → PLANNED → RISK_REVIEWED → JUDGE_REVIEWED → APPROVED → EXECUTED → SEALED

Blocked path: DRAFT → HOLD/VOID

Each transition requires specific conditions:
  DRAFT → PLANNED:       intent submitted
  PLANNED → RISK_REVIEWED: arif_ops_measure called
  RISK_REVIEWED → JUDGE_REVIEWED: arif_judge_deliberate called
  JUDGE_REVIEWED → APPROVED: verdict == SEAL
  APPROVED → EXECUTED:  forge_dry_run + human_ack
  EXECUTED → SEALED:    vault_dry_seal + permanent=true

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from threading import RLock
from typing import Any

# ─────────────────────────────────────────────────────────────────────────────
# Lifecycle states
# ─────────────────────────────────────────────────────────────────────────────


class LifecycleStage(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    RISK_REVIEWED = "risk_reviewed"
    JUDGE_REVIEWED = "judge_reviewed"
    APPROVED = "approved"
    EXECUTED = "executed"
    SEALED = "sealed"
    BLOCKED = "blocked"  # terminal — verdict was HOLD or VOID


# Forward transitions map: from_state → set of valid next states
_VALID_TRANSITIONS: dict[LifecycleStage, set[LifecycleStage]] = {
    LifecycleStage.DRAFT: {LifecycleStage.PLANNED, LifecycleStage.BLOCKED},
    LifecycleStage.PLANNED: {LifecycleStage.RISK_REVIEWED, LifecycleStage.BLOCKED},
    LifecycleStage.RISK_REVIEWED: {
        LifecycleStage.JUDGE_REVIEWED,
        LifecycleStage.BLOCKED,
    },
    LifecycleStage.JUDGE_REVIEWED: {LifecycleStage.APPROVED, LifecycleStage.BLOCKED},
    LifecycleStage.APPROVED: {LifecycleStage.EXECUTED, LifecycleStage.SEALED},
    LifecycleStage.EXECUTED: {LifecycleStage.SEALED},
    LifecycleStage.SEALED: set(),  # terminal
    LifecycleStage.BLOCKED: set(),  # terminal
}


# ─────────────────────────────────────────────────────────────────────────────
# Plan record
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class PlanRecord:
    """A single governed plan within a session."""

    plan_id: str
    actor_id: str
    intent: str
    lifecycle: LifecycleStage = LifecycleStage.DRAFT
    created_at: str = ""
    updated_at: str = ""
    judge_verdict: str | None = None
    judge_state_hash: str | None = None
    approved_plan_id: str | None = None
    risk_tier: str | None = None
    risk_report: dict | None = None
    human_approval: bool = False
    forge_mode: str | None = None
    forge_result: dict | None = None
    vault_entry_id: str | None = None
    blocked_reason: str | None = None

    def model_dump(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


# ─────────────────────────────────────────────────────────────────────────────
# Session lifecycle manager
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class SessionLifecycle:
    """Manages session lifecycle + plan state transitions."""

    session_id: str
    actor_id: str
    # Plan registry: plan_id → PlanRecord
    plans: dict[str, PlanRecord] = field(default_factory=dict)
    _active_plan_id: str | None = None
    _lock: RLock = field(default_factory=RLock)

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def create_plan(self, intent: str) -> PlanRecord:
        """Create a new plan in DRAFT state."""
        import uuid

        plan_id = f"PLAN-{uuid.uuid4().hex[:12]}"
        now = self._now()
        plan = PlanRecord(
            plan_id=plan_id,
            actor_id=self.actor_id,
            intent=intent,
            lifecycle=LifecycleStage.DRAFT,
            created_at=now,
            updated_at=now,
        )
        with self._lock:
            self.plans[plan_id] = plan
            self._active_plan_id = plan_id
        return plan

    def get_active_plan(self) -> PlanRecord | None:
        with self._lock:
            if not self._active_plan_id:
                return None
            return self.plans.get(self._active_plan_id)

    def set_active_plan(self, plan_id: str) -> bool:
        with self._lock:
            if plan_id in self.plans:
                self._active_plan_id = plan_id
                return True
            return False

    def can_transition(self, plan_id: str, to_state: LifecycleStage) -> tuple[bool, str]:
        """Check if a plan can transition to to_state."""
        with self._lock:
            plan = self.plans.get(plan_id)
            if not plan:
                return False, f"Plan {plan_id} not found"
            current = plan.lifecycle
            valid = _VALID_TRANSITIONS.get(current, set())
            if to_state in valid:
                return True, ""
            return False, (
                f"Invalid transition: {current.value} → {to_state.value}. "
                f"Allowed: {[s.value for s in valid]}"
            )

    def advance(self, plan_id: str, to_state: LifecycleStage, **kwargs: Any) -> PlanRecord:
        """Advance a plan to a new lifecycle state. Raises if transition is invalid."""
        can, msg = self.can_transition(plan_id, to_state)
        if not can:
            raise ValueError(f"Invalid lifecycle transition for {plan_id}: {msg}")

        with self._lock:
            plan = self.plans[plan_id]
            plan.lifecycle = to_state
            plan.updated_at = self._now()
            for k, v in kwargs.items():
                if hasattr(plan, k):
                    setattr(plan, k, v)
            return plan

    def block(self, plan_id: str, reason: str) -> PlanRecord:
        """Block a plan (terminal HOLD/VOID state)."""
        with self._lock:
            plan = self.plans[plan_id]
            plan.lifecycle = LifecycleStage.BLOCKED
            plan.blocked_reason = reason
            plan.updated_at = self._now()
            return plan

    def approve(self, plan_id: str, judge_verdict: str, judge_state_hash: str) -> PlanRecord:
        """Approve a plan after SEAL verdict from Judge."""
        return self.advance(
            plan_id,
            LifecycleStage.APPROVED,
            judge_verdict=judge_verdict,
            judge_state_hash=judge_state_hash,
            approved_plan_id=plan_id,
        )

    def execute(self, plan_id: str, forge_result: dict) -> PlanRecord:
        """Mark a plan as executed after human approval + forge dry-run."""
        return self.advance(plan_id, LifecycleStage.EXECUTED, forge_result=forge_result)

    def seal(self, plan_id: str, vault_entry_id: str) -> PlanRecord:
        """Seal a plan after vault permanent write."""
        return self.advance(plan_id, LifecycleStage.SEALED, vault_entry_id=vault_entry_id)

    def summary(self) -> dict[str, Any]:
        """Return a summary dict for UI display."""
        with self._lock:
            return {
                "session_id": self.session_id,
                "actor_id": self.actor_id,
                "plan_count": len(self.plans),
                "active_plan_id": self._active_plan_id,
                "plans": {pid: p.model_dump() for pid, p in self.plans.items()},
            }


# ─────────────────────────────────────────────────────────────────────────────
# Global registry (in-memory for now; per-process singleton)
# ─────────────────────────────────────────────────────────────────────────────

_session_lifecycles: dict[str, SessionLifecycle] = {}
_lifecycle_lock = RLock()


def get_or_create_lifecycle(session_id: str, actor_id: str) -> SessionLifecycle:
    """Get or create a lifecycle manager for a session."""
    with _lifecycle_lock:
        if session_id not in _session_lifecycles:
            _session_lifecycles[session_id] = SessionLifecycle(
                session_id=session_id, actor_id=actor_id
            )
        return _session_lifecycles[session_id]


def reset_lifecycles() -> None:
    """Reset all lifecycles. Used in tests."""
    global _session_lifecycles
    with _lifecycle_lock:
        _session_lifecycles = {}

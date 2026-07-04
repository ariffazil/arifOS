"""
State Machine Guard — enforces stage progression for the metabolic loop.
══════════════════════════════════════════════════════════════════════════════

IRON LAW 2 (TYPED_STAGES): Stage-specific schemas enforced.
IRON LAW 4 (SEAL_BEFORE_ACT): 666_judge SEAL required for 777_act.

9-stage metabolic loop: 000→111→333→444→555→666→777→888→999

The guard prevents:
  - Skipping stages (e.g., init → act without judge)
  - Reversing stages (e.g., act → observe)
  - Acting without SEAL (777 requires prior 666 SEAL verdict)
  - Sealing without compose (999 requires prior 888 compose)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class GuardVerdict(StrEnum):
    PROCEED = "PROCEED"
    HOLD = "HOLD"
    VOID = "VOID"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE SEQUENCE
# ═══════════════════════════════════════════════════════════════════════════════

STAGE_ORDER: list[str] = ["000", "111", "333", "444", "555", "666", "777", "888", "999"]

# Allowed transitions (from → to)
ALLOWED_TRANSITIONS: dict[str, list[str]] = {
    "000": ["111"],  # init → observe
    "111": ["333", "111", "000"],  # observe → reason (or re-observe, or re-init)
    "333": ["444", "333", "111"],  # reason → route (or re-reason, or re-observe)
    "444": ["555", "333", "111"],  # route → critique (or re-reason, re-observe)
    "555": ["666", "333", "111"],  # critique → judge (or re-reason, re-observe)
    "666": ["777", "555", "111"],  # judge → forge (or re-critique, re-observe)
    "777": ["888", "666"],  # forge → compose (or re-judge if failed)
    "888": ["999", "666"],  # compose → seal (or re-judge if failed)
    "999": [],  # seal → terminal (no forward transitions)
}

# Stages that can be skipped for OBSERVE/READ tasks
SKIPPABLE_FOR_READ: set[str] = {"333", "444", "555", "666", "777"}

# Required preconditions for each stage
PRECONDITIONS: dict[str, list[str]] = {
    "000": [],  # init is root — no preconditions
    "111": ["000"],  # observe requires init
    "333": ["111"],  # reason requires observe
    "444": ["333"],  # route requires reason
    "555": ["444"],  # critique requires route
    "666": ["555"],  # judge requires critique
    "777": ["666"],  # act requires judge (SEAL verdict)
    "888": ["777"],  # compose requires act (receipt)
    "999": ["888"],  # seal requires compose
}


class StateMachineGuard:
    """Enforces metabolic loop stage progression."""

    def __init__(self) -> None:
        self._current_stage: str | None = None
        self._history: list[str] = []
        self._verdict_id: str | None = None  # 666 verdict ID
        self._verdict_type: str | None = None  # SEAL/SABAR/HOLD/VOID
        self._act_receipt_id: str | None = None  # 777 receipt ID

    @property
    def current_stage(self) -> str | None:
        return self._current_stage

    @property
    def history(self) -> list[str]:
        return list(self._history)

    def can_transition(self, target_stage: str) -> GuardVerdict:
        """Check if transition to target_stage is allowed."""
        # First stage must be 000
        if self._current_stage is None:
            if target_stage == "000":
                return GuardVerdict.PROCEED
            return GuardVerdict.VOID  # Must start with init

        # Check allowed transitions
        allowed = ALLOWED_TRANSITIONS.get(self._current_stage, [])
        if target_stage not in allowed:
            return GuardVerdict.VOID

        # Check preconditions
        preconditions = PRECONDITIONS.get(target_stage, [])
        for pre in preconditions:
            if pre not in self._history:
                # Check if skippable for read tasks
                if pre in SKIPPABLE_FOR_READ:
                    continue
                return GuardVerdict.HOLD

        # IRON LAW 4: SEAL_BEFORE_ACT
        if target_stage == "777":
            if self._verdict_type != "SEAL":
                return GuardVerdict.VOID  # Cannot act without SEAL

        # 999 requires 777 receipt
        if target_stage == "999":
            if self._act_receipt_id is None:
                return GuardVerdict.VOID  # Cannot seal without act receipt

        return GuardVerdict.PROCEED

    def transition(self, target_stage: str) -> GuardVerdict:
        """Attempt transition to target_stage. Returns verdict."""
        verdict = self.can_transition(target_stage)
        if verdict == GuardVerdict.PROCEED:
            self._current_stage = target_stage
            self._history.append(target_stage)
        return verdict

    def record_verdict(self, verdict_id: str, verdict_type: str) -> None:
        """Record a 666_judge verdict."""
        self._verdict_id = verdict_id
        self._verdict_type = verdict_type

    def record_act_receipt(self, receipt_id: str) -> None:
        """Record a 777_act receipt."""
        self._act_receipt_id = receipt_id

    def reset(self) -> None:
        """Reset state machine for new session."""
        self._current_stage = None
        self._history = []
        self._verdict_id = None
        self._verdict_type = None
        self._act_receipt_id = None

    def is_complete(self) -> bool:
        """Check if the metabolic loop is complete (reached 999)."""
        return self._current_stage == "999"

    def status(self) -> dict[str, Any]:
        """Return current state machine status."""
        return {
            "current_stage": self._current_stage,
            "history": self._history,
            "verdict_id": self._verdict_id,
            "verdict_type": self._verdict_type,
            "act_receipt_id": self._act_receipt_id,
            "is_complete": self.is_complete(),
        }


# Singleton instance
_guard: StateMachineGuard | None = None


def get_state_machine_guard() -> StateMachineGuard:
    """Get the singleton state machine guard."""
    global _guard
    if _guard is None:
        _guard = StateMachineGuard()
    return _guard


__all__ = [
    "StateMachineGuard",
    "GuardVerdict",
    "STAGE_ORDER",
    "ALLOWED_TRANSITIONS",
    "PRECONDITIONS",
    "get_state_machine_guard",
]

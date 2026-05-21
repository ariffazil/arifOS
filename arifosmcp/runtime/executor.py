"""
arifosmcp/runtime/execution_state_machine.py
═══════════════════════════════════════════════════════════════════════════════════════
Formal Execution State Machine — OBSERVE → ANALYZE → SIMULATE → AWAIT_APPROVAL
→ EXECUTE → VERIFY → SEAL

Single chokepoint that determines whether a tool may run based on the session's
current execution state. No probabilistic routing. Deterministic gates only.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import os
from enum import StrEnum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════════════
# ENV GATE
# ═══════════════════════════════════════════════════════════════════════════════════════

_STATE_MACHINE_ENFORCE = os.getenv("ARIFOS_STATE_MACHINE_ENFORCE", "false").lower() in (
    "1",
    "true",
    "yes",
)

# ═══════════════════════════════════════════════════════════════════════════════════════
# EXECUTION STATE ENUM
# ═══════════════════════════════════════════════════════════════════════════════════════


class ExecutionState(StrEnum):
    """Canonical execution pipeline states."""

    OBSERVE = "OBSERVE"
    ANALYZE = "ANALYZE"
    SIMULATE = "SIMULATE"
    AWAIT_APPROVAL = "AWAIT_APPROVAL"
    EXECUTE = "EXECUTE"
    VERIFY = "VERIFY"
    SEAL = "SEAL"


# ═══════════════════════════════════════════════════════════════════════════════════════
# TOOL → ALLOWED STATE(S) MAPPING
# ═══════════════════════════════════════════════════════════════════════════════════════

# Infrastructure tools (memory, reply) are allowed in ANY state because they are
# orthogonal to the execution pipeline.
_ALL_STATES = {
    ExecutionState.OBSERVE,
    ExecutionState.ANALYZE,
    ExecutionState.SIMULATE,
    ExecutionState.AWAIT_APPROVAL,
    ExecutionState.EXECUTE,
    ExecutionState.VERIFY,
    ExecutionState.SEAL,
}

_TOOL_STATE_MAP: dict[str, set[ExecutionState]] = {
    # ── 000_INIT ──────────────────────────────────────────────────────────────────────
    "arif_session_init": {ExecutionState.OBSERVE},
    # ── 111_SENSE / OBSERVE ───────────────────────────────────────────────────────────
    "arif_sense_observe": {ExecutionState.OBSERVE, ExecutionState.VERIFY},
    "arif_evidence_fetch": {ExecutionState.OBSERVE, ExecutionState.VERIFY},
    "arif_ops_measure": {
        ExecutionState.OBSERVE,
        ExecutionState.VERIFY,
        ExecutionState.EXECUTE,
    },
    # ── 333_MIND / ANALYZE ────────────────────────────────────────────────────────────
    "arif_mind_reason": {ExecutionState.ANALYZE},
    "arif_kernel_route": {ExecutionState.ANALYZE},
    # ── 666_HEART / SIMULATE ──────────────────────────────────────────────────────────
    "arif_heart_critique": {ExecutionState.ANALYZE, ExecutionState.SIMULATE},
    # ── 888_JUDGE / AWAIT_APPROVAL ────────────────────────────────────────────────────
    "arif_judge_deliberate": {ExecutionState.SIMULATE, ExecutionState.AWAIT_APPROVAL},
    "arif_gateway_connect": {ExecutionState.AWAIT_APPROVAL},
    # ── 010_FORGE / EXECUTE ───────────────────────────────────────────────────────────
    "arif_forge_execute": {ExecutionState.SIMULATE, ExecutionState.EXECUTE},
    # ── 999_VAULT / SEAL ──────────────────────────────────────────────────────────────
    "arif_vault_seal": {ExecutionState.VERIFY, ExecutionState.SEAL},
    # ── Infrastructure (omni-state) ───────────────────────────────────────────────────
    "arif_memory_recall": _ALL_STATES,
    "arif_reply_compose": _ALL_STATES,
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# DEFAULT STATE PROGRESSION: which state to enter after this tool completes
# ═══════════════════════════════════════════════════════════════════════════════════════

# None = remain in current state (self-loop allowed)
_TOOL_PROGRESSION_MAP: dict[str, ExecutionState | None] = {
    "arif_session_init": ExecutionState.OBSERVE,
    "arif_sense_observe": ExecutionState.ANALYZE,
    "arif_evidence_fetch": ExecutionState.ANALYZE,
    "arif_ops_measure": ExecutionState.ANALYZE,
    "arif_memory_recall": None,
    "arif_mind_reason": ExecutionState.SIMULATE,
    "arif_kernel_route": ExecutionState.SIMULATE,
    "arif_heart_critique": ExecutionState.AWAIT_APPROVAL,
    "arif_judge_deliberate": ExecutionState.EXECUTE,
    "arif_gateway_connect": ExecutionState.EXECUTE,
    "arif_forge_execute": ExecutionState.VERIFY,
    "arif_reply_compose": None,
    "arif_vault_seal": ExecutionState.SEAL,
}

# ═══════════════════════════════════════════════════════════════════════════════════════
# STATE MACHINE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════════════


class ExecutionStateMachine:
    """Deterministic gatekeeper for the constitutional execution pipeline."""

    @staticmethod
    def is_enforced() -> bool:
        """Return whether the state machine is actively enforcing transitions."""
        return _STATE_MACHINE_ENFORCE

    @staticmethod
    def get_allowed_states(tool_name: str) -> set[ExecutionState]:
        """Return the execution states in which *tool_name* may run."""
        return set(_TOOL_STATE_MAP.get(tool_name, set()))

    @staticmethod
    def can_execute(tool_name: str, current_state: ExecutionState | None) -> bool:
        """
        Return True if the tool may execute in *current_state*.

        If *current_state* is None (legacy session without state tracking),
        the session is auto-anchored to OBSERVE on first contact.
        """
        allowed = ExecutionStateMachine.get_allowed_states(tool_name)
        if not allowed:
            # Unknown tool — fail closed (deny) when enforcement is on
            return False
        if current_state is None:
            # First contact for a legacy session → anchor to OBSERVE
            return ExecutionState.OBSERVE in allowed
        return current_state in allowed

    @staticmethod
    def get_next_state(
        tool_name: str,
        current_state: ExecutionState | None,
    ) -> ExecutionState:
        """
        Return the execution state the session should enter after *tool_name*
        completes successfully.
        """
        mapped = _TOOL_PROGRESSION_MAP.get(tool_name)
        if mapped is not None:
            return mapped
        # Self-loop: remain in current state
        return current_state or ExecutionState.OBSERVE

    @staticmethod
    def get_hold_response(
        tool_name: str,
        current_state: ExecutionState | None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Build a canonical HOLD response when a tool is called outside its
        allowed execution state.
        """
        allowed = ExecutionStateMachine.get_allowed_states(tool_name)
        if allowed:
            # Sort by pipeline order (earliest first)
            pipeline = list(ExecutionState)
            allowed_names = sorted(
                [s.value for s in allowed],
                key=lambda n: pipeline.index(ExecutionState(n)),
            )
        else:
            allowed_names = []
        next_required = allowed_names[0] if allowed_names else "OBSERVE"

        return {
            "tool": tool_name,
            "stage": "888",
            "status": "HOLD",
            "verdict": "HOLD",
            "error": "EXECUTION_STATE_MISMATCH",
            "message": (
                f"Tool '{tool_name}' is not authorized in state "
                f"'{current_state.value if current_state else 'UNKNOWN'}'. "
                f"Allowed states: {allowed_names}."
            ),
            "required_next_state": next_required,
            "next_safe_action": {
                "tool": "arif_sense_observe",
                "reason": "Re-anchor to OBSERVE and progress through the pipeline.",
            },
            "session_id": session_id,
            "execution_state": {
                "current": current_state.value if current_state else None,
                "required": allowed_names,
                "pipeline": [s.value for s in ExecutionState],
            },
        }

    @staticmethod
    def get_pipeline_progress(current_state: ExecutionState | None) -> dict[str, Any]:
        """Return human-readable pipeline position."""
        pipeline = list(ExecutionState)
        idx = pipeline.index(current_state) if current_state in pipeline else 0
        return {
            "current": current_state.value if current_state else None,
            "index": idx,
            "total": len(pipeline),
            "completed": [s.value for s in pipeline[:idx]],
            "remaining": [s.value for s in pipeline[idx + 1 :]],
        }


# Convenience singleton
state_machine = ExecutionStateMachine()

"""
[DEPRECATED] arifOS Golden Path — Gate Enforcer
══════════════════════════════════════════════════

⚠️  DEPRECATED 2026-07-13 — Arif's D1 directive.

REPLACED BY: arifosmcp.schemas.dependency_gate
  (dependency-graph gate pipeline with classification phase)

REASON FOR DEPRECATION:
  The serial chain (000→111→333→555→666→777→999) is structurally
  wrong because later gates generate facts needed by earlier gates.
  Gate 3.5 asks "is this dangerous?" but Gate 7 (sovereign authority)
  never runs because 3.5 already blocks.

  New pipeline: classification phase first → identity → capability →
  infra → constitutional → payload → execute → verify

  This module is preserved for backward compatibility during the
  migration window (expires 2026-08-01). All new code must use
  the dependency_gate pipeline.

DITEMPA BUKAN DIBERI 🔥⚒️ — Replaced, not forgotten.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .session_state import SessionState, Verdict, Readiness


class GateResult(str, Enum):
    """Gate check result."""
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    METABOLIC_EXHAUSTION = "METABOLIC_EXHAUSTION"


@dataclass
class GateCheck:
    """Result of a gate enforcement check."""
    result: GateResult
    organ: str
    reason: str
    missing: list[str]
    can_proceed: bool


class GovernanceGateError(Exception):
    """Raised when a constitutional gate blocks execution.

    This is not a suggestion. This is a hard stop.
    The forge cannot fire without judgment. The seal cannot seal
    without execution. The constitution enforces itself through code.
    """

    def __init__(self, check: GateCheck):
        self.check = check
        super().__init__(
            f"GOVERNANCE GATE BLOCKED [{check.organ}]: {check.reason}. "
            f"Missing: {check.missing}. Cannot proceed."
        )


# ── Stage requirements ───────────────────────────────────────────────────────
# 2026-06-26 RSI fix: critique (555) before judge (666).
# Golden path: 000→111→333→555_CRITIQUE→666_JUDGE→777_FORGE→999_SEAL

STAGE_REQUIREMENTS: dict[str, list[str]] = {
    "000": [],                           # Always enterable
    "111": ["000"],                      # Requires INIT
    "333": ["111"],                      # Requires SENSE
    "555": ["333"],                      # Requires REASON (critique produces readiness)
    "666": ["555"],                      # Requires CRITIQUE (judge produces verdict)
    "777": ["555", "666"],              # Requires CRITIQUE + JUDGE
    "999": ["777"],                      # Requires FORGE
}


def check_stage_entry(
    target_stage: str,
    state: SessionState,
) -> GateCheck:
    """Check if a stage can be entered given the current session state.

    This is the structural enforcement. Not advisory.
    """
    # Metabolic exhaustion check
    if state.is_metabolically_exhausted():
        return GateCheck(
            result=GateResult.METABOLIC_EXHAUSTION,
            organ=target_stage,
            reason=(
                f"METABOLIC CEILING: pipeline has looped {state.loop_count} times "
                f"(max={state.max_loops}) without convergence. "
                f"Escalating to sovereign (F13)."
            ),
            missing=[],
            can_proceed=False,
        )

    requirements = STAGE_REQUIREMENTS.get(target_stage, [])
    missing = [s for s in requirements if not state.has_stage(s)]

    # Special enforcement for 777_FORGE
    if target_stage == "777":
        # Hard gate: must have SEAL verdict from 666_JUDGE
        judge_record = state.get_stage_record("666")
        if not judge_record or judge_record.verdict != "SEAL":
            missing_detail = (
                f"666_JUDGE verdict is '{judge_record.verdict if judge_record else 'NONE'}', "
                f"required: 'SEAL'"
            )
            return GateCheck(
                result=GateResult.BLOCKED,
                organ="777",
                reason=(
                    f"STRUCTURAL ENFORCEMENT: 777_FORGE cannot execute without "
                    f"valid SEAL verdict from 666_JUDGE. {missing_detail}."
                ),
                missing=["666_SEAL"],
                can_proceed=False,
            )

        # Hard gate: must have FORGE_READY from 555_CRITIQUE
        critique_record = state.get_stage_record("555")
        if not critique_record or critique_record.readiness != "FORGE_READY":
            missing_detail = (
                f"555_CRITIQUE readiness is '{critique_record.readiness if critique_record else 'NONE'}', "
                f"required: 'FORGE_READY'"
            )
            return GateCheck(
                result=GateResult.BLOCKED,
                organ="777",
                reason=(
                    f"STRUCTURAL ENFORCEMENT: 777_FORGE cannot execute without "
                    f"FORGE_READY from 555_CRITIQUE. {missing_detail}."
                ),
                missing=["555_FORGE_READY"],
                can_proceed=False,
            )

    # General missing-stage check
    if missing:
        return GateCheck(
            result=GateResult.BLOCKED,
            organ=target_stage,
            reason=f"Missing required prior stages: {missing}",
            missing=missing,
            can_proceed=False,
        )

    return GateCheck(
        result=GateResult.PASS,
        organ=target_stage,
        reason="All entry gates passed",
        missing=[],
        can_proceed=True,
    )


def enforce_stage_entry(
    target_stage: str,
    state: SessionState,
) -> GateCheck:
    """Enforce stage entry gate. Raises GovernanceGateError if blocked.

    Use this instead of check_stage_entry when you need a hard stop.
    """
    check = check_stage_entry(target_stage, state)
    if not check.can_proceed:
        raise GovernanceGateError(check)
    return check


__all__ = [
    "GateResult",
    "GateCheck",
    "GovernanceGateError",
    "check_stage_entry",
    "enforce_stage_entry",
    "STAGE_REQUIREMENTS",
]

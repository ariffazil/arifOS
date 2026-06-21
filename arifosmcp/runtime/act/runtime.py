"""
ACT runtime — the act() ceremony function, ActRequest, ActResult.

Called AFTER ART says PROCEED and Kernel says SEAL.
Decides HOW to execute: pattern, staging, compensation, human coordination.

Three checks:
  CHECK 1 — STAGE:   Is the previous stage verified?
  CHECK 2 — PATTERN: Does the execution pattern match the risk?
  CHECK 3 — HUMAN:   Has the human acknowledged if needed?

Extracted from runtime/act.py.

DITEMPA BUKAN DIBERI — Runtime is forged, not configured.
"""

from __future__ import annotations
from dataclasses import dataclass

from arifosmcp.runtime.act.gates import (
    ActReason,
    ActVerdict,
    StageResult,
    StageStatus,
)
from arifosmcp.runtime.act.patterns import ExecutionPattern, suggest_pattern


# ── REQUEST ──────────────────────────────────────────────────────────


@dataclass
class ActRequest:
    """What ACT needs to decide execution strategy.

    Attributes:
        program_stage:      Current stage label, e.g. "stage_1_of_3"
        execution_pattern:  How the program intends to execute
        blast_radius:       "low" | "medium" | "high" | "unknown"
        is_reversible:      Can this action be undone?
        has_dry_run:        Has a dry run been performed?
        has_compensation:   Is there a rollback plan?
        human_acknowledged: Has the human approved this stage?
        previous_stage_verified: Did the previous stage pass verification?
        is_multi_step:      Is this part of a multi-step program?
        stage_number:       Which stage (1-indexed)
        total_stages:       How many stages total
        previous_stage_status: Status of the previous stage
    """
    program_stage: str = "single"
    execution_pattern: str = ExecutionPattern.SINGLE_SHOT.value
    blast_radius: str = "unknown"
    is_reversible: bool = False
    has_dry_run: bool = False
    has_compensation: bool = False
    human_acknowledged: bool = False
    previous_stage_verified: bool = True
    is_multi_step: bool = False
    stage_number: int = 1
    total_stages: int = 1
    previous_stage_status: str = StageStatus.PENDING.value


# ── RESULT ───────────────────────────────────────────────────────────


@dataclass
class ActResult:
    """What ACT returns."""
    verdict: ActVerdict
    reason: ActReason
    recommended_pattern: ExecutionPattern | None = None
    stage_result: StageResult | None = None

    def __bool__(self) -> bool:
        return self.verdict == ActVerdict.PROCEED


# ═══════════════════════════════════════════════════════════════════════
# THE EXECUTION CEREMONY — satu function, satu decision per program
# ═══════════════════════════════════════════════════════════════════════


def act(request: ActRequest) -> ActResult:
    """Action Ceremonial Tooling — the execution craft layer.

    Called AFTER ART says PROCEED and Kernel says SEAL.
    Decides HOW to execute: pattern, staging, compensation, human coordination.
    """

    pattern = ExecutionPattern(request.execution_pattern)
    suggested = suggest_pattern(
        blast_radius=request.blast_radius,
        is_reversible=request.is_reversible,
        is_multi_step=request.is_multi_step,
        total_stages=request.total_stages,
    ) if request.blast_radius != "low" else pattern

    stage_result = StageResult(
        stage_number=request.stage_number,
        total_stages=max(request.total_stages, 1),
        status=StageStatus.RUNNING,
        description=f"Stage {request.stage_number}/{max(request.total_stages, 1)}",
    )

    # ── CHECK 1: STAGE VERIFICATION ──────────────────────────────────
    if request.stage_number > 1:
        if request.previous_stage_status == StageStatus.FAILED.value:
            return ActResult(
                verdict=ActVerdict.BLOCK,
                reason=ActReason.PREVIOUS_STAGE_FAILED,
                stage_result=StageResult(
                    stage_number=request.stage_number,
                    total_stages=request.total_stages,
                    status=StageStatus.PENDING,
                    description="Previous stage failed — cannot continue",
                ),
            )
        if not request.previous_stage_verified:
            return ActResult(
                verdict=ActVerdict.HOLD,
                reason=ActReason.PREVIOUS_STAGE_UNVERIFIED,
                recommended_pattern=pattern,
                stage_result=StageResult(
                    stage_number=request.stage_number - 1,
                    total_stages=request.total_stages,
                    status=StageStatus.PENDING,
                    description="Previous stage not verified — must verify before continue",
                ),
            )

    # ── CHECK 2: PATTERN VS RISK ─────────────────────────────────────
    if request.blast_radius == "high":
        if pattern == ExecutionPattern.SINGLE_SHOT:
            return ActResult(
                verdict=ActVerdict.HOLD,
                reason=ActReason.HIGH_BLAST_NEEDS_STAGING,
                recommended_pattern=suggested,
            )

    # Dry run required for irreversible actions
    if not request.is_reversible and not request.has_dry_run:
        if request.blast_radius in ("high", "medium", "unknown"):
            return ActResult(
                verdict=ActVerdict.DRY_RUN_REQUIRED,
                reason=ActReason.IRREVERSIBLE_NEEDS_DRY_RUN,
                recommended_pattern=ExecutionPattern.DRY_RUN_THEN_LIVE,
            )

    # Compensation required for irreversible actions
    if not request.is_reversible and not request.has_compensation:
        return ActResult(
            verdict=ActVerdict.COMPENSATION_REQUIRED,
            reason=ActReason.COMPENSATION_PLAN_MISSING,
            recommended_pattern=ExecutionPattern.COMPENSATION_READY,
        )

    # Multi-step programs need explicit staging
    if request.is_multi_step and pattern == ExecutionPattern.SINGLE_SHOT:
        return ActResult(
            verdict=ActVerdict.HOLD,
            reason=ActReason.MULTI_STEP_NEEDS_PLAN,
            recommended_pattern=ExecutionPattern.STAGED_ROLLOUT,
        )

    # ── CHECK 3: HUMAN COORDINATION ─────────────────────────────────
    if request.blast_radius == "high" and not request.is_reversible:
        if not request.human_acknowledged:
            return ActResult(
                verdict=ActVerdict.HUMAN_REQUIRED,
                reason=ActReason.IRREVERSIBLE_NEEDS_HUMAN,
                recommended_pattern=pattern,
            )

    # ── ALL CHECKS PASSED ────────────────────────────────────────────
    return ActResult(
        verdict=ActVerdict.PROCEED,
        reason=ActReason.ALL_CHECKS_PASSED,
        recommended_pattern=pattern,
        stage_result=stage_result,
    )

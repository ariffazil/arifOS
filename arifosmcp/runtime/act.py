"""
ACT — Action Ceremonial Tooling (decision engine).

Public API and the `act()` function live here. Type catalog (enums + dataclasses)
lives in act_playbooks.py. Persistent memory lives in act_library.py.

Public API:
    from arifosmcp.runtime.act import (
        act, ActRequest, ActResult,
        ActVerdict, ExecutionPattern, StageResult,
    )

Lineage:
  2026-06-21 — ART (tool wisdom) + Kernel (law) complete. ACT is the third layer.
  2026-06-21 — Split: playbooks → act_playbooks.py, library → act_library.py,
               decision engine stays here.

One sentence:
  ART = ALAT mana nak guna.  Kernel = BOLEH ke tak?  ACT = MACAM MANA nak buat.

DITEMPA BUKAN DIBERI — Execution craft is forged, not configured.
"""

from __future__ import annotations
import os

from arifosmcp.runtime.act_playbooks import (
    ActReason,
    ActRequest,
    ActResult,
    ActVerdict,
    ExecutionPattern,
    StageResult,
    StageStatus,
)


# ═══════════════════════════════════════════════════════════════════════════
# REFLEX WEIGHT CEILING — sama macam ART, ≤ 300 lines
# ═══════════════════════════════════════════════════════════════════════════
# ACT is not a reflex (not per-call). It's a deliberative layer for
# multi-step programs. Still needs ceiling discipline to avoid bloat.


def _assert_act_weight_ceiling() -> None:
    _CEILING_LINES = 300
    _this_file = os.path.abspath(__file__)
    with open(_this_file) as _f:
        _line_count = sum(1 for _ in _f)
    if _line_count > _CEILING_LINES:
        raise RuntimeError(
            f"ACT ceiling violated: act.py is {_line_count} lines "
            f"(ceiling: {_CEILING_LINES}). Split heavy logic into "
            f"act_library.py or act_playbooks.py."
        )


_assert_act_weight_ceiling()


# ═══════════════════════════════════════════════════════════════════════════
# PATTERN SUGGESTION — recommend the right pattern
# ═══════════════════════════════════════════════════════════════════════════


def _suggest_pattern(req: ActRequest) -> ExecutionPattern:
    """Recommend the safest execution pattern for this request."""
    # HIGH blast + irreversible → CANARY + COMPENSATION + HUMAN
    if req.blast_radius == "high" and not req.is_reversible:
        return ExecutionPattern.CANARY_THEN_ALL

    # HIGH blast + reversible → STAGED with checkpoints
    if req.blast_radius == "high" and req.is_reversible:
        return ExecutionPattern.STAGED_ROLLOUT

    # MEDIUM blast + irreversible → DRY_RUN first
    if req.blast_radius in ("medium", "unknown") and not req.is_reversible:
        return ExecutionPattern.DRY_RUN_THEN_LIVE

    # Multi-step → never SINGLE_SHOT by default
    if req.is_multi_step and req.total_stages > 1:
        return ExecutionPattern.STAGED_ROLLOUT

    # Low blast + reversible → SINGLE_SHOT is fine
    return ExecutionPattern.SINGLE_SHOT


# ═══════════════════════════════════════════════════════════════════════════
# THE EXECUTION CEREMONY — satu function, satu decision per program
# ═══════════════════════════════════════════════════════════════════════════


def act(request: ActRequest) -> ActResult:
    """Action Ceremonial Tooling — the execution craft layer.

    Called AFTER ART says PROCEED and Kernel says SEAL.
    Decides HOW to execute: pattern, staging, compensation, human coordination.

    Three checks:
      CHECK 1 — STAGE:   Is the previous stage verified?
      CHECK 2 — PATTERN: Does the execution pattern match the risk?
      CHECK 3 — HUMAN:   Has the human acknowledged if needed?
    """

    pattern = ExecutionPattern(request.execution_pattern)
    suggested = _suggest_pattern(request) if request.blast_radius != "low" else pattern

    stage_result = StageResult(
        stage_number=request.stage_number,
        total_stages=max(request.total_stages, 1),
        status=StageStatus.RUNNING,
        description=f"Stage {request.stage_number}/{max(request.total_stages, 1)}",
    )

    # ── CHECK 1: STAGE VERIFICATION ──────────────────────────────────
    # Can't proceed to stage N+1 if stage N failed.
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
    # HIGH blast radius — never SINGLE_SHOT
    if request.blast_radius == "high":
        if pattern == ExecutionPattern.SINGLE_SHOT:
            return ActResult(
                verdict=ActVerdict.STAGED_ROLLOUT,
                reason=ActReason.HIGH_BLAST_NEEDS_STAGING,
                recommended_pattern=suggested,
            )
        if pattern == ExecutionPattern.SINGLE_SHOT and not request.is_reversible:
            return ActResult(
                verdict=ActVerdict.CANARY_REQUIRED,
                reason=ActReason.HIGH_BLAST_NEEDS_CANARY,
                recommended_pattern=ExecutionPattern.CANARY_THEN_ALL,
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
    # Irreversible + high blast → human must acknowledge
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

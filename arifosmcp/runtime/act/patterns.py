"""
ACT patterns — execution pattern enum, suggestion logic, and canonical
pattern definitions as Pydantic models from schemas/act.py.

Extracted from runtime/act.py.

DITEMPA BUKAN DIBERI — Patterns are forged, not configured.
"""

from __future__ import annotations
from enum import StrEnum

from arifosmcp.schemas.act import ActPattern, ActPatternName, ActStage
from arifosmcp.schemas.kernel_envelope import ActionClass


class ExecutionPattern(StrEnum):
    """The ceremonial pattern for executing a program of actions.

    SINGLE_SHOT        — Execute all at once. Only for low-blast, reversible.
    DRY_RUN_THEN_LIVE  — Simulate first, then execute if simulation passes.
    CANARY_THEN_ALL    — Execute against 1% first, verify, then full rollout.
    STAGED_ROLLOUT     — Execute in N waves with checkpoints between each.
    HUMAN_CHECKPOINT   — Execute step, pause for human verification, continue.
    COMPENSATION_READY — Execute with pre-planned rollback on failure.
    """

    SINGLE_SHOT = "single_shot"
    DRY_RUN_THEN_LIVE = "dry_run_then_live"
    CANARY_THEN_ALL = "canary_then_all"
    STAGED_ROLLOUT = "staged_rollout"
    HUMAN_CHECKPOINT = "human_checkpoint"
    COMPENSATION_READY = "compensation_ready"


def suggest_pattern(
    blast_radius: str,
    is_reversible: bool,
    is_multi_step: bool = False,
    total_stages: int = 1,
) -> ExecutionPattern:
    """Recommend the safest execution pattern for this request."""
    # HIGH blast + irreversible → CANARY + COMPENSATION + HUMAN
    if blast_radius == "high" and not is_reversible:
        return ExecutionPattern.CANARY_THEN_ALL

    # HIGH blast + reversible → STAGED with checkpoints
    if blast_radius == "high" and is_reversible:
        return ExecutionPattern.STAGED_ROLLOUT

    # MEDIUM blast + irreversible → DRY_RUN first
    if blast_radius in ("medium", "unknown") and not is_reversible:
        return ExecutionPattern.DRY_RUN_THEN_LIVE

    # Multi-step → never SINGLE_SHOT by default
    if is_multi_step and total_stages > 1:
        return ExecutionPattern.STAGED_ROLLOUT

    # Low blast + reversible → SINGLE_SHOT is fine
    return ExecutionPattern.SINGLE_SHOT


# ═══════════════════════════════════════════════════════════════════════
# CANONICAL PATTERN DEFINITIONS — Pydantic models for A-FORGE dispatch
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_DEPLOY = ActPattern(
    name=ActPatternName.DEFAULT_DEPLOY,
    description="Safe staged execution for reversible or bounded writes.",
    allowed_action_classes=[
        ActionClass.DRAFT,
        ActionClass.SIMULATE,
        ActionClass.MUTATE,
    ],
    stages=[
        ActStage(name="ART precheck", mode="precheck"),
        ActStage(name="Dry run", mode="dry_run"),
        ActStage(name="Canary", mode="canary", success_metric="error_rate < threshold"),
        ActStage(name="Verify", mode="verify"),
        ActStage(name="Rollout", mode="rollout"),
        ActStage(name="Closeout", mode="closeout"),
        ActStage(name="Vault seal", mode="seal"),
    ],
)

DANGEROUS_MIGRATION = ActPattern(
    name=ActPatternName.DANGEROUS_MIGRATION,
    description="Strict ritual for high-blast, hard-to-reverse, or irreversible changes.",
    allowed_action_classes=[
        ActionClass.EXTERNAL_SIDE_EFFECT,
        ActionClass.IRREVERSIBLE,
    ],
    stages=[
        ActStage(name="ART precheck", mode="precheck"),
        ActStage(name="Snapshot", mode="snapshot"),
        ActStage(name="Shadow dry run", mode="dry_run"),
        ActStage(
            name="888 HOLD",
            mode="human_gate",
            requires_human=True,
            failure_policy="hold",
        ),
        ActStage(name="Canary", mode="canary", failure_policy="rollback"),
        ActStage(name="Live execution", mode="rollout", failure_policy="hold"),
        ActStage(name="Verify", mode="verify"),
        ActStage(name="Compensate if required", mode="compensate"),
        ActStage(name="Vault seal", mode="seal"),
    ],
)

HUMAN_IN_LOOP_CHANGE = ActPattern(
    name=ActPatternName.HUMAN_IN_LOOP_CHANGE,
    description="Human review ritual for ambiguous, low-trust, or sovereign-sensitive actions.",
    allowed_action_classes=[
        ActionClass.MUTATE,
        ActionClass.EXTERNAL_SIDE_EFFECT,
        ActionClass.IRREVERSIBLE,
    ],
    stages=[
        ActStage(name="Capture HOLD reason", mode="human_gate", requires_human=True),
        ActStage(name="Create AAA ticket", mode="human_gate", requires_human=True),
        ActStage(name="Human decision", mode="human_gate", requires_human=True),
        ActStage(name="Resolve — resume, replan, or abort", mode="verify"),
        ActStage(name="Vault seal", mode="seal"),
    ],
)

CANONICAL_PATTERNS: dict[ActPatternName, ActPattern] = {
    ActPatternName.DEFAULT_DEPLOY: DEFAULT_DEPLOY,
    ActPatternName.DANGEROUS_MIGRATION: DANGEROUS_MIGRATION,
    ActPatternName.HUMAN_IN_LOOP_CHANGE: HUMAN_IN_LOOP_CHANGE,
}

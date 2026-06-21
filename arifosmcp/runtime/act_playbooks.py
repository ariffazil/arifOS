"""
ACT Playbooks — Type catalog and data shapes for ACT execution.

The "playbook" layer: declarative definitions of what an execution looks like.
The decision engine (`act()`) lives in act.py. Persistent memory lives in
act_library.py. This file owns the SHAPES, not the DECISIONS.

Public surface:
    from arifosmcp.runtime.act_playbooks import (
        ExecutionPattern, ActVerdict, ActReason,
        StageStatus, StageResult, ActRequest, ActResult,
    )

Cross-domain heritage:
    Henri Fayol  → planning, organizing, commanding, coordinating, controlling
    Deming       → Plan-Do-Check-Act (PDCA) cycle
    Toyota Kata  → step-by-step improvement with checkpoints

DITEMPA BUKAN DIBERI — Playbook is forged, not given.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# EXECUTION PATTERNS — the "cara manusia buat"
# ═══════════════════════════════════════════════════════════════════════════

class ExecutionPattern(str, Enum):
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


class ActVerdict(str, Enum):
    """What ACT decides for this program."""
    PROCEED = "proceed"                    # Pattern is safe — execute as planned
    HOLD = "hold"                          # Pattern needs change — pause
    BLOCK = "block"                        # Cannot execute safely — redesign
    DRY_RUN_REQUIRED = "dry_run_required"  # Must simulate first
    CANARY_REQUIRED = "canary_required"    # Must canary first
    COMPENSATION_REQUIRED = "compensation_required"  # Needs rollback plan
    HUMAN_REQUIRED = "human_required"      # Human must be in loop


class ActReason(str, Enum):
    """Why ACT reached this verdict."""
    # State
    NO_PREVIOUS_STAGE = "no previous stage — starting fresh"
    PREVIOUS_STAGE_UNVERIFIED = "previous stage not verified — cannot proceed"
    PREVIOUS_STAGE_FAILED = "previous stage failed — cannot continue"
    ALL_STAGES_VERIFIED = "all previous stages verified — proceed"

    # Pattern violations
    HIGH_BLAST_NEEDS_DRY_RUN = "high blast radius — dry run required before live"
    HIGH_BLAST_NEEDS_CANARY = "high blast radius — canary required before full rollout"
    HIGH_BLAST_NEEDS_STAGING = "high blast radius — staging required, not single shot"
    HIGH_BLAST_NEEDS_HUMAN = "high blast radius — human checkpoint required"
    HIGH_BLAST_NEEDS_COMPENSATION = "high blast radius — compensation plan required"

    IRREVERSIBLE_NEEDS_DRY_RUN = "irreversible action — dry run required"
    IRREVERSIBLE_NEEDS_HUMAN = "irreversible action — human must acknowledge"
    IRREVERSIBLE_NEEDS_COMPENSATION = "irreversible action — compensation plan required"

    MULTI_STEP_NEEDS_PLAN = "multi-step program — explicit pattern required, not single_shot"

    # Human coordination
    HUMAN_NOTIFIED = "human notified — proceed"
    HUMAN_ACK_REQUIRED = "human acknowledgment required before continue"
    HUMAN_ESCALATED = "escalated to human — waiting"

    # Compensation
    COMPENSATION_PLAN_MISSING = "no compensation plan for irreversible action"
    COMPENSATION_PLAN_READY = "compensation plan ready — proceed"

    # Pattern match
    PATTERN_MATCHES_RISK = "execution pattern matches risk level — proceed"
    PATTERN_TOO_RISKY = "execution pattern too risky for this action class"
    PATTERN_NOT_SPECIFIED = "execution pattern not specified — default single_shot"

    # All clear
    ALL_CHECKS_PASSED = "all checks passed — safe to execute"


# ═══════════════════════════════════════════════════════════════════════════
# STAGE TRACKING
# ═══════════════════════════════════════════════════════════════════════════

class StageStatus(str, Enum):
    """Status of a single stage in a multi-stage program."""
    PENDING = "pending"
    RUNNING = "running"
    VERIFIED = "verified"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    """Result of a single execution stage."""
    stage_number: int
    total_stages: int
    status: StageStatus
    description: str = ""


# ═══════════════════════════════════════════════════════════════════════════
# REQUEST
# ═══════════════════════════════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════════════════════════════
# RESULT
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ActResult:
    """What ACT returns."""
    verdict: ActVerdict
    reason: ActReason
    recommended_pattern: ExecutionPattern | None = None
    stage_result: StageResult | None = None

    def __bool__(self) -> bool:
        return self.verdict == ActVerdict.PROCEED


__all__ = [
    "ExecutionPattern",
    "ActVerdict",
    "ActReason",
    "StageStatus",
    "StageResult",
    "ActRequest",
    "ActResult",
]

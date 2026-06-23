"""
ACT gates — ActVerdict, ActReason, StageStatus, StageResult enums.

Extracted from runtime/act.py.

DITEMPA BUKAN DIBERI — Gates are forged, not configured.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum


class ActVerdict(StrEnum):
    """What ACT decides for this program."""

    PROCEED = "proceed"  # Pattern is safe — execute as planned
    HOLD = "hold"  # Pattern needs change — pause
    BLOCK = "block"  # Cannot execute safely — redesign
    DRY_RUN_REQUIRED = "dry_run_required"  # Must simulate first
    CANARY_REQUIRED = "canary_required"  # Must canary first
    COMPENSATION_REQUIRED = "compensation_required"  # Needs rollback plan
    HUMAN_REQUIRED = "human_required"  # Human must be in loop


class ActReason(StrEnum):
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


class StageStatus(StrEnum):
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

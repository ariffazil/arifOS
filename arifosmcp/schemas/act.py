"""
ACT Schema — Agentic Craft & Temporal Staging (contract surface)

Pure Pydantic v2 contracts for the ACT governed runtime bridge.
No behavior. No runtime imports. No execution path mutation.

ACT converts ART's trust verdict into deterministic execution
choreography: which pattern, which stages, which gates.

DITEMPA BUKAN DIBERI — Patterns are forged, not configured.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from arifosmcp.schemas.art import ArtPrecheckResult
from arifosmcp.schemas.kernel_envelope import ActionClass

# ═══════════════════════════════════════════════════════════════════════
# STAGE MODE — what kind of step this is
# ═══════════════════════════════════════════════════════════════════════

StageMode = Literal[
    "precheck",
    "dry_run",
    "snapshot",
    "canary",
    "verify",
    "rollout",
    "human_gate",
    "rollback",
    "compensate",
    "closeout",
    "seal",
]


# ═══════════════════════════════════════════════════════════════════════
# ACT PATTERN NAME — the three canonical execution rituals
# ═══════════════════════════════════════════════════════════════════════


class ActPatternName(StrEnum):
    """Three canonical execution patterns.

    DEFAULT_DEPLOY       — routine, reversible, bounded blast
    DANGEROUS_MIGRATION  — irreversible, high-blast, human-gated
    HUMAN_IN_LOOP_CHANGE — ART HOLD → human review → resolution
    """

    DEFAULT_DEPLOY = "DEFAULT_DEPLOY"
    DANGEROUS_MIGRATION = "DANGEROUS_MIGRATION"
    HUMAN_IN_LOOP_CHANGE = "HUMAN_IN_LOOP_CHANGE"


# ═══════════════════════════════════════════════════════════════════════
# ACT STAGE — one step in an execution pattern
# ═══════════════════════════════════════════════════════════════════════


class ActStage(BaseModel):
    """A single stage within an execution pattern.

    failure_policy governs what happens if this stage fails:
        abort     — stop the entire program
        rollback  — compensate and stop
        hold      — pause for human, do not continue
        continue  — log and proceed (only for non-critical stages)
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    name: str
    mode: StageMode
    required: bool = True
    requires_human: bool = False
    timeout_seconds: int | None = Field(default=None, gt=0)

    success_metric: str | None = None
    compensation_ref: str | None = None
    failure_policy: Literal["abort", "rollback", "hold", "continue"] = "abort"


# ═══════════════════════════════════════════════════════════════════════
# ACT PATTERN — a complete execution ritual
# ═══════════════════════════════════════════════════════════════════════


class ActPattern(BaseModel):
    """A canonical execution pattern.

    allowed_action_classes uses the canonical ActionClass from
    kernel_envelope.py (OBSERVE / ANALYZE / DRAFT / SIMULATE /
    MUTATE / EXTERNAL_SIDE_EFFECT / IRREVERSIBLE).

    This is NOT BlastRadius. BlastRadius quantifies scope-of-damage;
    ActionClass quantifies permission-level. ACT gates on both,
    but the pattern's allowed_action_classes constrains which
    permission levels this pattern can execute.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    name: ActPatternName
    description: str
    allowed_action_classes: list[ActionClass]
    stages: list[ActStage] = Field(min_length=1)


# ═══════════════════════════════════════════════════════════════════════
# ACT RECEIPT — what gets sealed to VAULT999 after execution
# ═══════════════════════════════════════════════════════════════════════


class ActReceipt(BaseModel):
    """Post-execution receipt for VAULT999.

    Namespaced as ART_ACT_EXECUTION_RECEIPT per VAULT999 seal-type
    discipline. No bare SEAL.
    """

    model_config = ConfigDict(extra="forbid", strict=True)

    seal_type: Literal["ART_ACT_EXECUTION_RECEIPT"] = "ART_ACT_EXECUTION_RECEIPT"
    plan_id: str
    task_id: str | None = None
    actor_id: str

    art_precheck: ArtPrecheckResult
    act_pattern: ActPatternName
    stages_completed: list[str] = Field(default_factory=list)

    judge_verdict: str
    vault_receipt_required: bool = True

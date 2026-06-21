"""
ACT compensation — rollback and compensation path resolution.

For each ACT stage that can fail, defines what "undo" means
when the original action is irreversible.

Compensation is not "undo" — it's:
  - GEOX: re-hydrate from snapshot, re-label state, corrective transforms
  - WEALTH: out-of-band accounting entries, manual adjustments
  - WELL: human restorative rituals, enforced cooling-off
  - System: revert config, restore backup, rollback migration

DITEMPA BUKAN DIBERI — Compensation is forged, not configured.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CompensationPath:
    """A compensation plan for a single stage."""
    stage_name: str
    description: str
    steps: list[str] = field(default_factory=list)
    is_automatic: bool = False
    requires_human: bool = True
    rollback_command: str | None = None


# Canonical compensation paths per pattern
DEFAULT_DEPLOY_COMPENSATION: list[CompensationPath] = [
    CompensationPath(
        stage_name="Rollout",
        description="Revert the single unit change. Log revert to VAULT999.",
        steps=["revert change", "verify state restored", "log to VAULT999"],
        is_automatic=True,
        requires_human=False,
        rollback_command="git revert HEAD --no-edit",
    ),
]

DANGEROUS_MIGRATION_COMPENSATION: list[CompensationPath] = [
    CompensationPath(
        stage_name="Canary",
        description="VOID canary, restore canary slice from snapshot.",
        steps=["stop canary traffic", "restore from snapshot", "verify isolation"],
        is_automatic=True,
        requires_human=False,
    ),
    CompensationPath(
        stage_name="Live execution",
        description="Full rollback: restore from pre-migration snapshot.",
        steps=[
            "stop all traffic",
            "restore database from snapshot",
            "verify data integrity",
            "notify Arif",
        ],
        is_automatic=False,
        requires_human=True,
    ),
]

HUMAN_IN_LOOP_COMPENSATION: list[CompensationPath] = [
    CompensationPath(
        stage_name="Human decision",
        description="Abort: mark plan ABORTED, log termination reason, demote tools if needed.",
        steps=["mark plan ABORTED", "log termination reason", "update ART tool lifecycle"],
        is_automatic=False,
        requires_human=True,
    ),
]

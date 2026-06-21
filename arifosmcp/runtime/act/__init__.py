"""
ACT package — Action Ceremonial Tooling.

Re-exports from submodules so callers can continue using:
    from arifosmcp.runtime.act import act, ActRequest, ActResult, ...

Also re-exports schema types from arifosmcp.schemas.act for convenience:
    from arifosmcp.runtime.act import ActPattern, ActReceipt, ...

DITEMPA BUKAN DIBERI — Package is forged, not configured.
"""

from arifosmcp.runtime.act.gates import (
    ActReason,
    ActVerdict,
    StageResult,
    StageStatus,
)
from arifosmcp.runtime.act.patterns import (
    CANONICAL_PATTERNS,
    DANGEROUS_MIGRATION,
    DEFAULT_DEPLOY,
    HUMAN_IN_LOOP_CHANGE,
    ExecutionPattern,
    suggest_pattern,
)
from arifosmcp.runtime.act.runtime import ActRequest, ActResult, act
from arifosmcp.runtime.act.compensation import (
    CompensationPath,
    DANGEROUS_MIGRATION_COMPENSATION,
    DEFAULT_DEPLOY_COMPENSATION,
    HUMAN_IN_LOOP_COMPENSATION,
)

# Re-export schema types for convenience
from arifosmcp.schemas.act import (
    ActPattern,
    ActPatternName,
    ActReceipt,
    ActStage,
)

__all__ = [
    # Ceremony
    "act",
    "ActRequest",
    "ActResult",
    # Verdict & Reason
    "ActVerdict",
    "ActReason",
    # Patterns
    "ExecutionPattern",
    "suggest_pattern",
    "DEFAULT_DEPLOY",
    "DANGEROUS_MIGRATION",
    "HUMAN_IN_LOOP_CHANGE",
    "CANONICAL_PATTERNS",
    # Stages
    "StageStatus",
    "StageResult",
    # Compensation
    "CompensationPath",
    "DEFAULT_DEPLOY_COMPENSATION",
    "DANGEROUS_MIGRATION_COMPENSATION",
    "HUMAN_IN_LOOP_COMPENSATION",
    # Schema types (re-exported for convenience)
    "ActPattern",
    "ActPatternName",
    "ActReceipt",
    "ActStage",
]

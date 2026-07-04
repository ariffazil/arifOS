"""arifOS RSI — bounded SEAL → INIT → Scaffold → Diff regeneration engine.

Forged 2026-07-04 (YELLOW). The bus is the single trigger; each stage's
hooks live in `arifosmcp.rsi.stages.<name>` and are registered here by name.
F13 SOVEREIGN: the bus is no-op by default. Enable via:
    ARIFOS_RSI_AUTOREBUILD=1
    or arifosmcp.rsi.enable_post_seal_rebuild()

Sovereign 999_HOLD correction, 2026-07-04:
    "SEAL → INIT → Scaffold is not the mutation path. It is the regeneration
     review path." The bus now exposes a `skill_diff` stage; the
     `resume_execution` stage will not fire unless a diff emits a
     GateDecision with verdict=APPROVE_C0_C3 and resume_allowed=True.
"""

from arifosmcp.rsi.contracts import (
    GateDecision,
    RiskClass,
    SkillContract,
    SkillDelta,
    SkillDiff,
    TWELVE_SKILLS,
    seed_12_contracts,
)
from arifosmcp.rsi.diff_engine import (
    DRIFT_NAMES,
    SkillDeltaRequest,
    diff,
    evaluate,
)
from arifosmcp.rsi.event_bus import (
    RSI_STAGES,
    RSIReceipt,
    SealEvent,
    SealEventBus,
    StageResult,
    disable_post_seal_rebuild,
    enable_post_seal_rebuild,
    fire_post_seal,
    get_bus,
    register_post_seal_hook,
)

__all__ = [
    "DRIFT_NAMES",
    "GateDecision",
    "RSI_STAGES",
    "RSIReceipt",
    "RiskClass",
    "SealEvent",
    "SealEventBus",
    "SkillContract",
    "SkillDelta",
    "SkillDeltaRequest",
    "SkillDiff",
    "StageResult",
    "TWELVE_SKILLS",
    "diff",
    "disable_post_seal_rebuild",
    "enable_post_seal_rebuild",
    "evaluate",
    "fire_post_seal",
    "get_bus",
    "register_post_seal_hook",
    "seed_12_contracts",
]

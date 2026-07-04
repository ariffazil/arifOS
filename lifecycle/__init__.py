"""
arifOS lifecycle — SEAL → INIT → Scaffold → Skill Δ → Tests → Judge → Cool → Resume.

Public surface (v0.2 — post-HOLD correction 2026-07-04):

  Stage 1 — SEAL      → seal_shadow (capture_pre / capture_post)
  Stage 2 — INIT      → init_scaffold (regenerate_body_plan)
  Stage 3 — Scaffold  → skill_delta_engine (propose_skill_delta via evaluate)
  Stage 4 — Skill Δ   → skill_registry.diff()  [NOW INCLUDED]
  Stage 5 — Tests     → skill_delta_engine (survivor_tests)
  Stage 6 — Judge     → skill_delta_engine (judge_required flag)
  Stage 7 — Cooling   → downstream WELL
  Stage 8 — Resume    → downstream A-FORGE (gated)

Constitutional binding (see kernel.yaml:constitutional_law):
  L01 AMANAH  — irreversible SEAL requires GÖDEL-LOCK (actor ≠ judge)
  L02 TRUTH   — shadow ledger persists pre-SEAL state for replay
  L04 CLARITY — INIT body-plan reload must NOT mutate skills
  L07 HUMILITY — replay band 0.03–0.05
  L11 AUTH    — witness required for IRREVERSIBLE seals
  L13 SOVEREIGN — Judge gate; engine cannot bypass.

See: kernel.yaml · /root/arifOS/lifecycle/README.md · INVARIANTS.md
"""

from __future__ import annotations

from .seal_shadow import (
    ShadowSnapshot,
    ShadowDiff,
    capture_pre,
    capture_post,
)
from .seal_post_hook import with_shadow, SealHookResult
from .init_scaffold import regenerate_body_plan, assert_body_plan_stable, BodyPlan
from .skill_registry import (
    SkillContract,
    SkillRecord,  # backward-compatible alias
    ContractDiff,
    SkillRegistry,
)

# Engine: bounded, non-mutating review harness (Phase-1 of HOLD verdict).
from .skill_delta_engine import (
    SkillDeltaEngine,
    SkillDeltaEvent,
    SkillDeltaReport,
    HARD_RULES,
)

__all__ = [
    # Stage 1 — SEAL observation
    "ShadowSnapshot",
    "ShadowDiff",
    "capture_pre",
    "capture_post",
    "with_shadow",
    "SealHookResult",
    # Stage 2 — INIT body-plan restore
    "regenerate_body_plan",
    "assert_body_plan_stable",
    "BodyPlan",
    # Stage 3-6 — Scaffold + Skill Δ + Tests + Judge gate (engine)
    "SkillDeltaEngine",
    "SkillDeltaEvent",
    "SkillDeltaReport",
    "HARD_RULES",
    # Skill contracts + diff
    "SkillContract",
    "SkillRecord",
    "ContractDiff",
    "SkillRegistry",
]

# Phase 2 stub: `registry` singleton activates when contracts are loaded.
try:
    from .skill_registry import registry as _registry
    registry = _registry
    __all__.append("registry")
except ImportError:  # pragma: no cover
    pass


__version__ = "0.2.0-lifecycle-kernel-post-HOLD"
__constitutional_lock__ = "L13_F13_RATIFICATION_REQUIRED"
__hold_history__ = "2026-07-04: prior autonomous kernel HOLD; non-mutating engine substituted"

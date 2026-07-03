"""
init_scaffold.py — INIT-only body-plan reload (post-HOLD correction 2026-07-04).

The previous version of this module conflated INIT (body-plan restore) with
Scaffold (skill-delta proposal) with Skill Rebuild (mutation). Per Arif's
HOLD verdict, those are THREE distinct concerns owned by THREE stages.

This module now owns ONLY the INIT stage. It loads the stable body plan from
the shadow ledger and emits a BodyPlan object — it does not propose skill
deltas and it does not mutate anything.

Stage map (post-correction):
  Stage 1 — SEAL      → seal_shadow (capture_pre/capture_post)
  Stage 2 — INIT      → THIS module (regenerate_body_plan)
  Stage 3 — Scaffold  → skill_delta_engine (propose_skill_delta) [NEW FILE]
  Stage 4 — Skill Diff → skill_registry.diff() [NOW in skill_registry]
  Stage 5 — Tests    → skill_delta_engine.evaluate() [runs tests]
  Stage 6 — Judge    → skill_delta_engine (judge_required flag)
  Stage 7 — Cooling  → cooling ledger (out of scope, downstream WELL)
  Stage 8 — Resume   → A-FORGE (out of scope, gated by judge + cooling)

Constitutional binding:
  L04 CLARITY   — regeneration must reduce (or hold) entropy.
  L13 SOVEREIGN — kernel mutation is F13-ratified, never auto-applied.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .seal_shadow import ShadowSnapshot, ShadowDiff


# ─── Body Plan ───────────────────────────────────────────────────────────────


@dataclass
class BodyPlan:
    """Stable body-plan restored by INIT. NOT a skill proposal.

    Per Arif HOLD verdict: INIT must reload only invariants:
        - canonical_tool_surface
        - organ_boundaries
        - authority_tiers
        - evidence_floor_rules
        - extinction_ledger
        - survivor_skill_contracts
        - cooling_policy
    """

    snapshot_id: str
    regenerated_at: str  # ISO8601 UTC
    loads: list[str] = field(default_factory=list)
    mutation_allowed: bool = False  # ALWAYS False. INIT restores, never invents.

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


_REQUIRED_LOADS = (
    "canonical_tool_surface",
    "organ_boundaries",
    "authority_tiers",
    "evidence_floor_rules",
    "extinction_ledger",
    "survivor_skill_contracts",
    "cooling_policy",
)


# ─── Public API ─────────────────────────────────────────────────────────────


def regenerate_body_plan(shadow: ShadowSnapshot | ShadowDiff) -> BodyPlan:
    """INIT stage: restore the agent's body plan from the shadow ledger.

    Args:
        shadow: post-SEAL ShadowDiff (or pre ShadowSnapshot).

    Returns:
        BodyPlan — read-only by construction (mutation_allowed=False).
        Caller passes this to skill_delta_engine.propose_skill_delta() as
        the input context for Stage 3 (Scaffold / proposal).

    Constitutional note:
        This function NEVER mutates the skill registry or any contract. It
        rehydrates the body plan as a snapshot of what was preserved
        across the SEAL. Any skill delta is the responsibility of
        skill_delta_engine — this module imports nothing from it.
    """
    snapshot_id = getattr(shadow, "snapshot_id", "") or "unknown"
    return BodyPlan(
        snapshot_id=snapshot_id,
        regenerated_at=datetime.now(timezone.utc).isoformat(),
        loads=list(_REQUIRED_LOADS),
        mutation_allowed=False,
    )


def assert_body_plan_stable(plan: BodyPlan) -> None:
    """Hard-assert: a BodyPlan NEVER grants mutation rights.

    Use this before passing the plan to skill_delta_engine. Belt-and-braces
    guard against future refactors that might mistakenly flip the flag.
    """
    if plan.mutation_allowed is True:
        raise AssertionError(
            "F13 violation: BodyPlan.mutation_allowed must be False. "
            "INIT is restoration only; any proposal must come from "
            "skill_delta_engine.propose_skill_delta() with judge gate."
        )
    missing = [k for k in _REQUIRED_LOADS if k not in plan.loads]
    if missing:
        raise AssertionError(f"BodyPlan.loads missing required entries: {missing}")


# ─── Smoke ──────────────────────────────────────────────────────────────────


if __name__ == "__main__":  # pragma: no cover
    from datetime import datetime, timezone

    snap = ShadowSnapshot(
        snapshot_id="pre-test-2026-07-04T00:00:00+00:00",
        actor_id="actor-A",
        session_id="judge-B",
        captured_at=datetime.now(timezone.utc).isoformat(),
        state_dict={"k": "v"},
        sha256="0" * 64,
    )
    plan = regenerate_body_plan(snap)
    assert_body_plan_stable(plan)
    assert plan.mutation_allowed is False
    assert len(plan.loads) == 7
    print(f"OK init_scaffold smoke: BodyPlan restored for {plan.snapshot_id}; "
          f"loads={len(plan.loads)}; mutation_allowed={plan.mutation_allowed}")

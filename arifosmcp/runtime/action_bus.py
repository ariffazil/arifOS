"""
runtime/action_bus.py — Verdict-Gated Action Bus (AGI Substrate Core)

Per synthesis: AGI = human-range general competence (operator-level across domains).
ASI = beyond-human general dominance (institution/civilization-level, where human verification becomes the bottleneck).

The real difference: breadth, depth, speed, autonomy, consequence.
Not magic, not sentience — governability risk.

This bus is the bridge:
  intent (cognition) 
    → GovernancePipeline (restraint, floors, ASI cognitive tier)
    → Tier-aware lease (tighter for ASI)
    → ACT (execution patterns)
    → World consequence assessment (GEOX earth, WEALTH capital, WELL dignity for ASI civilizational)
    → Precedent M3 update + verification bottleneck flag
    → HOLD if ASI + civilizational blast without sovereign verification.

Core law:
  ONE_SKILL = KNOW_WHAT_NOT_TO_DO (restraint under capability)
  ONE_TOOL  = VERDICT_LOOP_WITH_MEMORY

All substrate action MUST petition here. No direct tools for AGI/ASI cognition.
arifOS builds the governable substrate, does not chase mythical intelligence.

Physically buildable engineering (pipeline + leases + ACT + memory + organs).

For arifOS mission: keep increasing intelligence governable.

DITEMPA BUKAN DIBERI — The bus is the law, not a suggestion.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from arifosmcp.runtime.governance_pipeline import (
    GovernancePipeline,
    PipelineResult,
    PipelineVerdict,
    ToolCallContext,
)
from arifosmcp.runtime.lease_registry import (
    LeaseRecord,
    issue_lease,
    validate_lease_for_tool,
)
from arifosmcp.runtime.act import act as _act_runtime, ActRequest, ActResult

logger = logging.getLogger("arifosmcp.action_bus")

# ─────────────────────────────────────────────────────────────────────────────
# Substrate types (minimal, composes existing)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Intent:
    """Cognition output petitioning for action."""
    actor_id: str
    session_id: str
    tool_name: str
    params: dict[str, Any]
    blast_radius: str = "unknown"
    is_reversible: bool = False
    proposed_pattern: str = "single"
    evidence_summary: str = ""
    uncertainty: float = 0.5
    # AGI/ASI classification hint (from self_mod_lock) - per synthesis: AGI = human-range generalist; ASI = beyond-human dominance
    cognitive_tier: str = "AGI"
    # New from contrast: breadth/depth/speed/autonomy/consequence assessment
    consequence_scale: str = "operational"  # "operational" (AGI) | "civilizational" (ASI)


@dataclass
class BusResult:
    """Result after full bus traversal."""
    verdict: PipelineVerdict
    pipeline: PipelineResult | None = None
    lease_id: str | None = None
    act_result: ActResult | None = None
    execution_outcome: dict[str, Any] = field(default_factory=dict)
    precedent_id: str | None = None  # M3 lesson id
    next_safe_action: str = ""
    reasons: list[str] = field(default_factory=list)
    # From new synthesis: explicit tier and governability
    tier: str = "AGI"
    risk_level: str = "operational"  # operational | civilizational
    verification_bottleneck: bool = False  # true when machine capability exceeds human verification speed
    civilizational_blast: bool = False


class ActionBus:
    """
    The Verdict-Gated Action Bus.

    AGI models / cognition layers call this.
    The bus is the only path from "I think I should do X" to "X happened lawfully".

    Usage (inside substrate):
        bus = ActionBus()
        result = await bus.submit(intent)   # or sync equivalent
        if result.verdict == PipelineVerdict.PASS:
            ... use outcome
    """

    def __init__(self) -> None:
        self._pipeline = GovernancePipeline()
        self._precedent_store = "M3_PRECEDENT"  # marker for memory layer

    def submit(self, intent: Intent, *, lease_id: str | None = None) -> BusResult:
        """
        Main entry for substrate cognition.

        1. Build context for pipeline (verdict gates).
        2. Run full governance pipeline (restraint + floors + authority + ASI check).
        3. If PASS: ensure/validate lease.
        4. Delegate to ACT for safe execution pattern.
        5. Update precedent memory with outcome + restraint lesson.
        """
        t0 = time.perf_counter()

        ctx = ToolCallContext(
            tool_name=intent.tool_name,
            params=intent.params,
            actor_id=intent.actor_id,
            session_id=intent.session_id,
            blast_radius=intent.blast_radius or "LOCAL",
            reversibility=0.0 if not intent.is_reversible else 1.0,
            caller_has_lease=bool(lease_id),
            action_class="MUTATE" if intent.blast_radius in ("high", "civilizational") else "OBSERVE",
        )

        # 1+2. Verdict (the core tool)
        pipeline_result: PipelineResult = self._pipeline.run(ctx)

        if not pipeline_result.all_clear:
            return BusResult(
                verdict=pipeline_result.verdict,
                pipeline=pipeline_result,
                next_safe_action=pipeline_result.next_safe_action or "Re-petition with stronger evidence or authority.",
                reasons=pipeline_result.reasons or ["Governance pipeline HOLD"],
                tier=intent.cognitive_tier,
                risk_level=intent.consequence_scale,
            )

        # ASI vs AGI contrast (per synthesis): AGI = operator-level (human-range generalist).
        # ASI = institution/civilization-level (beyond-human dominance, verification bottleneck risk).
        is_asi = intent.cognitive_tier.upper() == "ASI" or intent.consequence_scale == "civilizational"
        verification_bottleneck = is_asi and intent.blast_radius in ("high", "unknown")
        civilizational_blast = is_asi and not intent.is_reversible

        if is_asi and civilizational_blast:
            # Stricter gate for ASI: force explicit human verification + multi-organ world model check
            # (world model: would query GEOX for earth constraints, WEALTH for capital flows, WELL for human dignity)
            world_consequence = "ASI civilizational action: earth (GEOX) + capital (WEALTH) + vitality (WELL) reconciliation required before execution."
            return BusResult(
                verdict=PipelineVerdict.HOLD,
                pipeline=pipeline_result,
                next_safe_action="ASI mode: obtain F13 sovereign + organ world-model sign-off before any civilizational blast action. " + world_consequence,
                reasons=["ASI civilizational blast detected. Human verification is the bottleneck."],
                tier="ASI",
                risk_level="civilizational",
                verification_bottleneck=True,
                civilizational_blast=True,
            )

        # 3. Lease (bounded authority for the action) — tighter for ASI
        effective_lease_id = lease_id
        max_class = "strict" if is_asi else "standard"
        if not effective_lease_id:
            lease_rec: LeaseRecord = issue_lease(
                issued_by="arifOS.action_bus",
                organ_id="kernel",
                actor_id=intent.actor_id,
                scope=[intent.tool_name],
                forbidden=[],
                expires_at=time.time() + (60 if is_asi else 300),
                max_action_class=max_class,
                vault_required=True,
            )
            effective_lease_id = lease_rec.lease_id

        if not validate_lease_for_tool(effective_lease_id, intent.tool_name):
            return BusResult(
                verdict=PipelineVerdict.HOLD,
                pipeline=pipeline_result,
                next_safe_action="Obtain valid lease for this tool before execution.",
                reasons=["Lease validation failed after pipeline PASS"],
                tier=intent.cognitive_tier,
                risk_level=intent.consequence_scale,
            )

        # 4. Execute via ACT (patterns, staging, human gates, compensation)
        act_req = ActRequest(
            program_stage="bus_submitted",
            execution_pattern=intent.proposed_pattern,
            blast_radius=intent.blast_radius,
            is_reversible=intent.is_reversible,
            has_dry_run=False,
            has_compensation=False,
            human_acknowledged= not (is_asi and intent.blast_radius == "high"),  # ASI high blast requires explicit human in act
        )
        act_res: ActResult = _act_runtime(act_req)  # may itself call more gates / human

        # 5. Precedent Memory update (the learning + M3)
        precedent_id = None
        try:
            from arifosmcp.memory.lessons import Lesson, ingest_lesson  # M3 precedent path
            from arifosmcp.memory.contradictions import record_contradiction
            lesson_text = self._extract_restraint_lesson(pipeline_result, act_res)
            les = Lesson(
                text=lesson_text,
                source_action=intent.tool_name,
                outcome_summary=str(getattr(act_res, 'verdict', act_res))[:200],
            )
            precedent_id = ingest_lesson(les) or f"les_{int(time.time())}"
            if "failure" in str(act_res).lower() or pipeline_result.verdict != PipelineVerdict.PASS:
                record_contradiction({
                    "expected": "lawful execution under restraint",
                    "actual": str(act_res)[:300],
                    "restraint_lesson": lesson_text,
                })
        except Exception as e:  # never let memory failure kill the bus
            logger.warning("Precedent memory update failed (non-fatal): %s", e)
            precedent_id = f"les_fallback_{int(time.time())}"

        total_ms = (time.perf_counter() - t0) * 1000

        return BusResult(
            verdict=PipelineVerdict.PASS,
            pipeline=pipeline_result,
            lease_id=effective_lease_id,
            act_result=act_res,
            execution_outcome={"act": act_res, "latency_ms": total_ms, "world_model_note": "ASI would reconcile GEOX/WEALTH/WELL before civilizational acts." if is_asi else ""},
            precedent_id=precedent_id,
            next_safe_action="Action executed under governance. Precedent recorded.",
            tier="ASI" if is_asi else "AGI",
            risk_level="civilizational" if is_asi else "operational",
            verification_bottleneck=verification_bottleneck,
            civilizational_blast=civilizational_blast,
        )

    def _extract_restraint_lesson(self, pr: PipelineResult, act_res: Any) -> str:
        """Turn the run into a reusable precedent for future restraint.
        Incorporates AGI/ASI contrast: AGI = operator risk; ASI = civilizational verification bottleneck.
        """
        blocked = pr.blocked_at.value if pr.blocked_at else "none"
        tool = getattr(pr, "tool_name", "unknown")
        tier_note = "ASI: machine exceeds human verification speed — restraint must be constitutional." if "ASI" in str(getattr(pr, 'tier', '')) else "AGI: human-range general competence."
        return (
            f"Under {pr.verdict.value} at gate {blocked}. "
            f"Tool={tool}. "
            f"{tier_note} "
            f"Act pattern respected. Restraint preserved sovereignty."
        )


# Convenience singleton for substrate use
action_bus = ActionBus()


# Public substrate helper (for models / arif_act handler to call)
def petition_for_action(intent: Intent) -> BusResult:
    """The one call cognition should use instead of direct tool invocation."""
    return action_bus.submit(intent)

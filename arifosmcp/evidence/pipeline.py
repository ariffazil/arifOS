"""
Federation Pipeline — wiring the six forge items into one executable.

This is the example pipeline that ties:

  envelope (item 1)
  → LawEvidence compile (item 2)
  → state transition (item 3a)
  → contradiction memory (item 3b)
  → memory write policy (item 4)
  → experiment loop (item 5)
  → lesson extraction (item 6)

into a single end-to-end run. Organs can import and call
`run_pipeline(...)` to get the whole stack for one evidence event.

DITEMPA BUKAN DIBERI — six organs, one pipeline.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Optional

from arifosmcp.core.transitions import (
    ActionRecord,
    ActionState,
    StateMachine,
    TransitionError,
)
from arifosmcp.evidence.law_evidence import (
    JudgeVerdict,
    LawEvidence,
    SessionState,
    VaultLineage,
    WellState,
    compile_law_evidence,
    recommend_verdict,
)
from arifosmcp.experiments.loop import (
    ExperimentCard,
    ExperimentVerdict,
    Hypothesis,
    LoopContext,
    ProbeSpec,
    compare,
    observe,
    open_experiment,
    update,
)
from arifosmcp.memory.contradictions import ContradictionStore, get_store as get_ctr_store
from arifosmcp.memory.lessons import LessonStore, get_store as get_lesson_store
from arifosmcp.memory.policies import (
    MemoryLayer,
    MemoryPolicyEngine,
    WriteAction,
    WriteRequest,
    get_engine as get_policy_engine,
)
from arifosmcp.schemas.envelope import (
    ContradictionEntry,
    EpistemicTag,
    EvidenceEnvelope,
    Reversibility,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# PIPELINE RESULT
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class PipelineResult:
    """What the full pipeline produces for one evidence event."""

    envelope: EvidenceEnvelope
    law_evidence: LawEvidence
    recommended_verdict: JudgeVerdict
    action_record: ActionRecord
    contradiction_record_ids: list[str]
    memory_decisions: list[str]
    experiment_card: Optional[ExperimentCard] = None
    lessons_created: list[str] = None  # type: ignore[assignment]
    # EUREKA #15 (2026-06-06): prompt-frame warnings emitted before compile
    prompt_frame_warnings: list[str] = None  # type: ignore[assignment]


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _build_session_state(
    actor_id: str,
    session_id: str,
    autonomy_band: str = "GREEN",
    irreversibility_requested: bool = False,
    human_acknowledged: bool = False,
) -> SessionState:
    return SessionState(
        session_id=session_id,
        actor_id=actor_id,
        autonomy_band=autonomy_band,
        irreversibility_requested=irreversibility_requested,
        human_acknowledged=human_acknowledged,
        entropy_budget_remaining=1.0,
    )


def _build_well_state(
    readiness: str = "OPTIMAL",
    substrate_confidence: float = 0.85,
    fatigue_score: float = 0.1,
    dignity_intact: bool = True,
    consent_status: str = "granted",
) -> WellState:
    return WellState(
        readiness=readiness,
        substrate_confidence=substrate_confidence,
        fatigue_score=fatigue_score,
        dignity_intact=dignity_intact,
        consent_status=consent_status,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════


def run_pipeline(
    envelope: EvidenceEnvelope,
    *,
    actor_id: str,
    session_id: str,
    autonomy_band: str = "GREEN",
    irreversibility_requested: bool = False,
    human_acknowledged: bool = False,
    well_state: Optional[WellState] = None,
    vault_lineage: Optional[VaultLineage] = None,
    claim_text: str = "",
    claim_type: str = "domain",
    action_intent: str = "",
    run_experiment: bool = True,
    hypothesis: Optional[Hypothesis] = None,
    probe: Optional[ProbeSpec] = None,
    on_lesson_failure: bool = True,
    prompt_frame: Optional[str] = None,
) -> PipelineResult:
    """Run the full six-organ pipeline on one evidence event.

    Steps:
      0. (NEW 2026-06-06) If `prompt_frame` provided, scan for governance
         theatre before compiling — catches the upstream of the Royal Decree
         (prompt asks model to play "Executive Branch" → output does).
      1. compile LawEvidence from envelope + session + well + vault
      2. recommend a verdict from the 13 floor results
      3. create + transition an ActionRecord based on the verdict
      4. record any contradictions (and check hold threshold)
      5. decide memory writes via the policy engine
      6. (optional) open + observe + compare + update an experiment card
      7. (optional) extract lessons from any FAIL floor results
    """
    well = well_state or _build_well_state()
    vault = vault_lineage or VaultLineage()

    # Step 0 (Eureka #15 — two-sided check): scan the prompt frame
    # before letting the pipeline proceed. If the prompt itself carries
    # institutional-impersonation vocabulary, the output will too.
    # Surface the warning in the pipeline result; the caller decides
    # what to do (HOLD / reroute / annotate).
    prompt_frame_warnings: list[str] = []
    if prompt_frame:
        try:
            from arifosmcp.runtime.witness_packet import _scan_governance_theatre
            from arifosmcp.runtime.authority_gate import validate_free_text_vocabulary

            theatre_hits = _scan_governance_theatre(prompt_frame)
            if theatre_hits:
                prompt_frame_warnings.append(
                    f"prompt_carries_governance_theatre:{theatre_hits[0][:80]}"
                )
            # Also: AGI prompts with verdict vocabulary
            lane = envelope.runtime_lane or "111"
            verdict_violations = validate_free_text_vocabulary(
                prompt_frame, lane=lane, has_seal_hash=False
            )
            if verdict_violations:
                prompt_frame_warnings.extend(
                    f"prompt_carries_verdict_vocab:{v[:80]}" for v in verdict_violations
                )
        except Exception as e:  # noqa: BLE001
            prompt_frame_warnings.append(f"prompt_scan_error:{type(e).__name__}:{e}")

    session = _build_session_state(
        actor_id=actor_id,
        session_id=session_id,
        autonomy_band=autonomy_band,
        irreversibility_requested=irreversibility_requested,
        human_acknowledged=human_acknowledged,
    )

    # 1. Compile LawEvidence
    law = compile_law_evidence(
        envelope,
        session=session,
        well=well,
        lineage=vault,
        claim_text=claim_text or envelope.source.tool,
        claim_type=claim_type,
    )

    # 2. Recommend verdict
    recommended = recommend_verdict(law)

    # 3. Action record + state transition
    intent = action_intent or claim_text or f"Process evidence from {envelope.source.tool}"
    action = ActionRecord(
        intent=intent,
        reversibility=(
            "IRREVERSIBLE" if envelope.reversibility == Reversibility.IRREVERSIBLE else "REVERSIBLE"
        ),
        autonomy_band=autonomy_band,
        actor_id=actor_id,
        session_id=session_id,
    )
    if recommended == JudgeVerdict.SEAL:
        target = ActionState.SEALED
    elif recommended == JudgeVerdict.HOLD:
        target = ActionState.HOLD
    elif recommended == JudgeVerdict.SABAR:
        target = ActionState.PENDING  # SABAR means wait at PENDING
    else:  # VOID
        target = ActionState.VOID

    try:
        # Move PENDING → APPROVED → EXECUTED → target (skipping legal jumps)
        for step in [ActionState.APPROVED, ActionState.EXECUTED, target]:
            if StateMachine.can_transition(action.state, step):
                action = StateMachine.transition(
                    action,
                    step,
                    actor_id=actor_id,
                    reason=f"verdict={recommended.value}",
                    human_acknowledged=human_acknowledged,
                )
    except TransitionError as e:
        logger.warning(f"transition skipped: {e}")

    # 4. Contradiction memory
    ctr_store: ContradictionStore = get_ctr_store()
    contradiction_ids: list[str] = []
    if envelope.has_contradictions():
        ctr_recs = ctr_store.record_from_envelope(
            envelope,
            artifact_ref=envelope.envelope_id,
            artifact_kind="evidence",
            description=claim_text,
        )
        contradiction_ids = [c.contradiction_id for c in ctr_recs]
        # Lesson: contradiction pattern
        if on_lesson_failure:
            get_lesson_store().add_contradiction(
                artifact_ref=envelope.envelope_id,
                organs=[c.organ for c in envelope.contradictions],
                actor_id=actor_id,
            )

    # 5. Memory write policy
    policy: MemoryPolicyEngine = get_policy_engine()
    memory_decisions: list[str] = []
    # Route the envelope to the right layers
    if recommended == JudgeVerdict.SEAL:
        # SEAL-worthy evidence: write to L3 (semantic) and possibly L4 (structured)
        for layer in (MemoryLayer.L3_SEMANTIC, MemoryLayer.L4_STRUCTURED):
            d = policy.decide(
                WriteRequest(
                    actor_id=actor_id,
                    actor_type="agent",
                    layer=layer,
                    key=f"env:{envelope.envelope_id}",
                    payload=envelope.result,
                    source_envelope=envelope,
                    session_id=session_id,
                )
            )
            memory_decisions.append(f"{layer.value}:{d.action.value}")
    elif recommended == JudgeVerdict.HOLD:
        # Hold: write to L1 (ephemeral) for tracking
        d = policy.decide(
            WriteRequest(
                actor_id=actor_id,
                actor_type="agent",
                layer=MemoryLayer.L1_EPHEMERAL,
                key=f"hold:{envelope.envelope_id}",
                payload={"hold_reason": claim_text, "envelope_id": envelope.envelope_id},
                source_envelope=envelope,
                session_id=session_id,
            )
        )
        memory_decisions.append(f"L1:{d.action.value}")
    else:
        # VOID: do not promote to persistent layers; record audit
        d = policy.decide(
            WriteRequest(
                actor_id=actor_id,
                actor_type="agent",
                layer=MemoryLayer.L1_EPHEMERAL,
                key=f"void:{envelope.envelope_id}",
                payload={"void_reason": claim_text, "envelope_id": envelope.envelope_id},
                source_envelope=envelope,
                session_id=session_id,
            )
        )
        memory_decisions.append(f"L1:{d.action.value}")

    # 6. Experiment loop (optional)
    exp_card: Optional[ExperimentCard] = None
    if run_experiment and hypothesis is not None and probe is not None:
        ctx = LoopContext(
            actor_id=actor_id,
            session_id=session_id,
        )
        exp_card = open_experiment(
            hypothesis=hypothesis,
            probe=probe,
            actor_id=actor_id,
            session_id=session_id,
        )
        observe(exp_card, envelope)
        compare(exp_card)
        update(exp_card, ctx)

    # 7. Lesson extraction from any FAIL floors
    lessons: list[str] = []
    if on_lesson_failure:
        ls = get_lesson_store()
        for fr in law.floor_results:
            if fr.status.value == "FAIL":
                lesson = ls.add_failure(
                    failure_kind=f"floor_{fr.floor_id.lower()}",
                    actor_id=actor_id,
                    organ=envelope.source.organ,
                    source_event_id=envelope.envelope_id,
                    extra_notes=fr.reason,
                )
                lessons.append(lesson.lesson_id)

    return PipelineResult(
        envelope=envelope,
        law_evidence=law,
        recommended_verdict=recommended,
        action_record=action,
        contradiction_record_ids=contradiction_ids,
        memory_decisions=memory_decisions,
        experiment_card=exp_card,
        lessons_created=lessons,
        prompt_frame_warnings=prompt_frame_warnings,
    )

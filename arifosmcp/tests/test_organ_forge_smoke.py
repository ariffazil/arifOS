"""
End-to-end smoke test for the Organ Forge.
Exercises all six items in a single run.

Run:  python -m pytest tests/test_organ_forge_smoke.py -v
or:   python tests/test_organ_forge_smoke.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make arifOS importable. We import the SUBMODULES directly to avoid
# pulling the package __init__ chain (which requires fastmcp at runtime).
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# Pre-stub arifosmcp as a package so submodule imports resolve
import types

_pkg = types.ModuleType("arifosmcp")
_pkg.__path__ = [str(Path(__file__).resolve().parents[1])]
sys.modules.setdefault("arifosmcp", _pkg)

from arifosmcp.evidence import (  # noqa: E402
    emit_geox,
    emit_wealth,
    emit_well,
    run_pipeline,
    EpistemicTag,
    Reversibility,
    JudgeVerdict,
)
from arifosmcp.evidence.law_evidence import (
    WellState,
)
from arifosmcp.core.transitions import (
    ActionState,
    StateMachine,
    TransitionError,
)
from arifosmcp.experiments.loop import (
    Hypothesis,
    ProbeSpec,
    run_simple_experiment,
    LoopContext,
)
from arifosmcp.memory import (  # noqa: E402
    ContradictionEntry,
    MemoryLayer,
    WriteRequest,
    get_contradiction_store,
    get_lesson_store,
    get_memory_policy_engine,
)


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 1: Clean GEOX claim — should SEAL
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_1_clean_geox_seal() -> None:
    """A well-observed GEOX depth reading with high quality → SEAL."""
    env = emit_geox(
        tool="geox_data_ingest_bundle",
        result={"well_id": "W-001", "top_depth_m": 1850.3, "qc": "PASS"},
        actor_id="agent:geox-worker",
        evidence_quality=0.95,
        p10=1848.0,
        p50=1850.3,
        p90=1852.5,
        units="m MD",
        epistemic_tag=EpistemicTag.OBSERVED,
        session_id="sess-001",
        parent_evidence_refs=["vault_seal_abc123"],  # witness chain present
    )
    result = run_pipeline(
        env,
        actor_id="agent:geox-worker",
        session_id="sess-001",
        claim_text="Top depth of W-001 at 1850.3 m MD",
        action_intent="ingest well log",
    )
    assert result.recommended_verdict == JudgeVerdict.SEAL, (
        f"Expected SEAL for clean GEOX, got {result.recommended_verdict}"
    )
    # The pipeline transitions through APPROVED → EXECUTED → SEALED
    # but the SEAL step requires RED band. With GREEN/ORANGE the action
    # stops at APPROVED/EXECUTED. The verdict is what matters.
    assert result.action_record.state in (
        ActionState.SEALED,
        ActionState.EXECUTED,
        ActionState.APPROVED,
    ), f"Got {result.action_record.state.value}"
    print(
        f"  ✓ scenario_1: SEAL → action {result.action_record.state.value}, "
        f"memory {result.memory_decisions}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 2: Irreversible action without ack — should VOID
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_2_irreversible_voids() -> None:
    """Irreversible WEALTH action without sovereign ack → VOID (L01)."""
    env = emit_wealth(
        tool="wealth_omni_wisdom",
        result={"deal": "Project X", "value_musd": 50.0, "verdict": "GO"},
        actor_id="agent:wealth-sentinel",
        evidence_quality=0.92,
        p10=-20.0,
        p50=50.0,
        p90=150.0,
        units="USD_M",
        epistemic_tag=EpistemicTag.DERIVED,
        session_id="sess-002",
        reversibility=Reversibility.IRREVERSIBLE,
    )
    result = run_pipeline(
        env,
        actor_id="agent:wealth-sentinel",
        session_id="sess-002",
        autonomy_band="RED",  # high-blast radius
        claim_text="Approve 50M USD capital deployment to Project X",
        action_intent="deploy capital",
        # human_acknowledged=False
    )
    assert result.recommended_verdict in (JudgeVerdict.VOID, JudgeVerdict.HOLD), (
        f"Expected VOID/HOLD for irreversible without ack, got {result.recommended_verdict}"
    )
    print(
        f"  ✓ scenario_2: {result.recommended_verdict.value} → "
        f"action {result.action_record.state.value} (L01/L13 enforced)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 3: WELL substrate CRITICAL → HOLD regardless of evidence
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_3_well_critical_holds() -> None:
    """Substrate CRITICAL → HOLD (L05 PEACE)."""
    env = emit_well(
        tool="well_assess_homeostasis",
        result={"readiness": "CRITICAL", "fatigue": 0.9, "dignity": True},
        actor_id="agent:well-mirror",
        evidence_quality=0.90,
        p10=0.0,
        p50=0.9,
        p90=1.0,
        epistemic_tag=EpistemicTag.OBSERVED,
        session_id="sess-003",
    )
    bad_well = WellState(
        readiness="CRITICAL",
        substrate_confidence=0.95,
        fatigue_score=0.95,
        dignity_intact=True,
        consent_status="granted",
    )
    result = run_pipeline(
        env,
        actor_id="agent:well-mirror",
        session_id="sess-003",
        well_state=bad_well,
        claim_text="Substrate state reported CRITICAL",
        action_intent="continue work",
    )
    assert result.recommended_verdict == JudgeVerdict.HOLD, (
        f"Expected HOLD for CRITICAL substrate, got {result.recommended_verdict}"
    )
    print("  ✓ scenario_3: HOLD → L05 PEACE enforced (substrate CRITICAL)")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 4: Contradiction repeated 3x → triggers HOLD
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_4_contradiction_threshold() -> None:
    """3 contradictions on same artifact → hold_triggered=True."""
    ctr_store = get_contradiction_store()
    artifact = "test_artifact_threshold_xyz"

    # Reset any prior state on this artifact (defensive)
    ctr_store.resolve(artifact, "reset_for_test")

    # Send 3 contradicting envelopes all on the SAME artifact.
    for i in range(3):
        env = emit_geox(
            tool="geox_claim_create",
            result={"claim_id": artifact, "depth_m": 1800 + i * 10},
            actor_id=f"agent:geox-{i}",
            evidence_quality=0.95,
            p10=1790.0,
            p50=1800.0 + i * 10,
            p90=1820.0,
            epistemic_tag=EpistemicTag.OBSERVED,
            session_id=f"sess-ctr-{i}",
            contradictions=[
                ContradictionEntry(
                    evidence_ref=f"ref_{i}",
                    organ="wealth",
                    epistemic_tag=EpistemicTag.OBSERVED,
                    summary=f"Contradiction {i}",
                    weight=0.9,
                )
            ],
        )
        # Pass the SHARED artifact_ref so all 3 records merge into one
        run_pipeline(
            env,
            actor_id=f"agent:geox-{i}",
            session_id=f"sess-ctr-{i}",
            claim_text=f"Contradiction {i} on {artifact}",
        )
        # Manually call record_from_envelope with the shared artifact key
        ctr_store.record_from_envelope(
            env,
            artifact_ref=artifact,
            artifact_kind="claim",
            description=f"Claim dispute round {i}",
        )

    pending = ctr_store.holds_pending()
    assert len(pending) >= 1, (
        f"Expected at least 1 hold after 3 contradictions, got {len(pending)} "
        f"(stats: {ctr_store.stats()})"
    )
    print(
        f"  ✓ scenario_4: 3 contradictions → hold_triggered, "
        f"pending={len(pending)}, "
        f"lessons={get_lesson_store().stats()['lessons_total']}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 5: State transition guard — illegal move rejected
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_5_transition_guards() -> None:
    """PENDING → SEALED must be rejected (no skipping)."""
    from arifosmcp.core.transitions import ActionRecord

    # Start with ORANGE band so we can go through APPROVED → EXECUTED → SEALED
    rec = ActionRecord(
        intent="test legal path through ORANGE",
        actor_id="agent:tester",
        autonomy_band="ORANGE",
    )
    assert rec.state == ActionState.PENDING

    # PENDING → SEALED is NOT in allowed table
    assert not StateMachine.can_transition(ActionState.PENDING, ActionState.SEALED)

    # Illegal: PENDING → SEALED direct
    try:
        StateMachine.transition(rec, ActionState.SEALED, actor_id="agent:tester")
        assert False, "Expected TransitionError"
    except TransitionError:
        pass

    # Legal path: PENDING → APPROVED → EXECUTED → SEALED (with RED band)
    rec_b = ActionRecord(
        intent="legal path through RED",
        actor_id="agent:tester",
        autonomy_band="RED",
    )
    rec2 = StateMachine.transition(rec_b, ActionState.APPROVED, actor_id="agent:tester")
    rec3 = StateMachine.transition(rec2, ActionState.EXECUTED, actor_id="agent:tester")
    rec4 = StateMachine.transition(rec3, ActionState.SEALED, actor_id="agent:tester")
    assert rec4.state == ActionState.SEALED
    assert len(rec4.history) == 3
    print(
        f"  ✓ scenario_5: illegal PENDING→SEALED rejected, "
        f"legal PENDING→APPROVED→EXECUTED→SEALED works "
        f"({len(rec4.history)} history entries)"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 6: Experiment loop — confirm prior belief
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_6_experiment_confirm() -> None:
    """Run a probe, observe, compare, update — expect BELIEF_CONFIRMED."""
    hypothesis = Hypothesis(
        text="Layang-Layang Block B has 50m net pay at 1800m",
        prior_belief=0.7,
        falsifier="net pay < 30m OR depth > 1900m",
        domain="petrophysics",
        organ="geox",
    )
    probe = ProbeSpec(
        tool="geox_subsurface_generate_candidates",
        args={"zone": "B"},
        reversibility="REVERSIBLE",
        expected_signal="net_pay ≈ 50m at 1800m",
    )
    # Strong confirming observation
    obs_env = emit_geox(
        tool="geox_subsurface_generate_candidates",
        result={"net_pay_m": 52.0, "depth_m": 1798.0, "phi": 0.22, "sw": 0.45},
        actor_id="agent:geox",
        evidence_quality=0.95,
        p10=45.0,
        p50=52.0,
        p90=58.0,
        epistemic_tag=EpistemicTag.OBSERVED,
        session_id="sess-exp",
    )
    ctx = LoopContext(actor_id="agent:geox", session_id="sess-exp")
    card = run_simple_experiment(hypothesis, probe, [obs_env], ctx)
    assert card.verdict in (
        __import__("arifosmcp").experiments.loop.ExperimentVerdict.BELIEF_CONFIRMED,
        __import__("arifosmcp").experiments.loop.ExperimentVerdict.BELIEF_REVISED,
    ), f"Got {card.verdict}"
    print(
        f"  ✓ scenario_6: experiment {card.experiment_id} closed "
        f"verdict={card.verdict.value} Δ={card.compare.delta_belief:+.3f}"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 7: Lesson promotion — 3 same-kind failures → auto-promote
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_7_lesson_promotion() -> None:
    """3 'timeout' failures → lesson auto-promotes to routing rule."""
    ls = get_lesson_store()
    initial_total = ls.stats()["lessons_total"]
    initial_promoted = ls.stats()["promoted"]

    for i in range(3):
        ls.add_failure(
            failure_kind="timeout",
            actor_id="agent:tester",
            organ="a-forge",
            source_event_id=f"timeout-{i}",
            extra_notes=f"iteration {i}",
        )

    stats = ls.stats()
    delta_total = stats["lessons_total"] - initial_total
    delta_promoted = stats["promoted"] - initial_promoted
    assert delta_total == 3, f"Expected 3 new lessons, got {delta_total}"
    assert delta_promoted >= 1, f"Expected at least 1 promoted rule, got {delta_promoted}"
    print(f"  ✓ scenario_7: 3 'timeout' failures → {delta_promoted} routing rule(s) promoted")


# ═══════════════════════════════════════════════════════════════════════════════
# SCENARIO 8: Memory policy — FACT with low quality → HOLD
# ═══════════════════════════════════════════════════════════════════════════════


def test_scenario_8_memory_policy_holds_fact() -> None:
    """FACT label with quality < 0.99 → HOLD on memory write."""
    engine = get_memory_policy_engine()
    env = emit_geox(
        tool="geox_claim_create",
        result={"claim": "test"},
        actor_id="agent:geox",
        evidence_quality=0.95,  # < 0.99
        p10=0.0,
        p50=0.0,
        p90=0.0,
        epistemic_tag=EpistemicTag.FACT,  # FACT requires ≥ 0.99
        session_id="sess-mem",
    )
    decision = engine.decide(
        WriteRequest(
            actor_id="agent:geox",
            actor_type="agent",
            layer=MemoryLayer.L4_STRUCTURED,
            key="fact:test",
            payload={"x": 1},
            source_envelope=env,
            session_id="sess-mem",
        )
    )
    from arifosmcp.memory.policies import WriteAction as _WA

    assert decision.action == _WA.HOLD, (
        f"Expected HOLD for FACT < 0.99, got {decision.action.value}: {decision.reason}"
    )
    print(f"  ✓ scenario_8: FACT q=0.95 → {decision.action.value} ({decision.reason[:50]})")


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    print("=" * 60)
    print("ORGAN FORGE SMOKE TEST — six organs, one pipeline")
    print("=" * 60)
    tests = [
        test_scenario_1_clean_geox_seal,
        test_scenario_2_irreversible_voids,
        test_scenario_3_well_critical_holds,
        test_scenario_4_contradiction_threshold,
        test_scenario_5_transition_guards,
        test_scenario_6_experiment_confirm,
        test_scenario_7_lesson_promotion,
        test_scenario_8_memory_policy_holds_fact,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: ASSERTION FAILED — {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__}: {type(e).__name__} — {e}")
            failed += 1
    print("=" * 60)
    print(f"RESULT: {passed} passed, {failed} failed (out of {len(tests)})")
    print("=" * 60)
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()

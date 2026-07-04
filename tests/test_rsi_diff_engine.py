"""Tests for the Skill Delta Engine (NON-MUTATING).

Forged 2026-07-04 (YELLOW) under sovereign 999_HOLD correction:
    "SEAL → INIT → Scaffold is not the mutation path. It is the regeneration
     review path. The missing stage is Diff."
    "Scaffold proposes. Judge approves. A-FORGE applies."

Locks the irreducible contract:
  1. The engine is pure — diff() is side-effect-free.
  2. The four named drifts are detected: weakened_gate, expanded_autonomy,
     hidden_mutation, authority_drift (plus test_removed and
     missing_test_for_new_anchor).
  3. Risk classes map correctly — C0/C1 trivial, C2/C3 contract edits,
     C4 floor logic, C5 execution/authority.
  4. The engine refuses to emit (VOID) for: forbidden actions, extinct
     skills, unknown skills, missing baseline contracts.
  5. Resume is NEVER allowed automatically — only Judge + cooling can do it.
  6. The 12 canonical skills are seeded with constitutional must_preserve +
     must_never_weaken anchors.
"""

from __future__ import annotations

import pytest

from arifosmcp.rsi import (
    DRIFT_NAMES,
    GateDecision,
    RiskClass,
    SkillContract,
    SkillDelta,
    SkillDeltaRequest,
    TWELVE_SKILLS,
    diff,
    evaluate,
    seed_12_contracts,
)


@pytest.fixture
def baseline():
    return seed_12_contracts()


@pytest.fixture
def organ_inventory():
    return {
        "arifos": ("arif_judge", "arif_canary"),
        "geox": ("geox_well_desurvey",),
        "wealth": ("wealth_npv",),
        "well": ("well_sleep",),
        "aforge": ("forge_plan",),
        "aaa": ("aaa_route",),
        "vault999": ("vault_seal",),
    }


# ── 1. The four named drifts are detected ───────────────────────────────────


def test_detects_weakened_gate_when_must_never_weaken_removed(baseline):
    """Removing any must_never_weaken anchor = C5 + weakened_gate."""
    old = baseline["boundary_sensing"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="boundary_sensing",
        reason="loosen human-ack for performance",
        removed_must_never_weaken=("human_ack_for_irreversible_action",),
    )
    d = diff(old, delta, {})
    assert "weakened_gate" in d.drift_signals
    assert d.risk_class == RiskClass.C5_EXECUTION_AUTHORITY
    assert d.sovereign_required is True
    assert d.judge_required is True


def test_detects_expanded_autonomy_when_cooling_invariant_relaxes(baseline):
    """Removing/changing cooling_threshold = C5 + expanded_autonomy."""
    old = baseline["reaction_gating"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="reaction_gating",
        reason="lower cooling for faster throughput",
        changed_invariants={
            "cooling_threshold": ("strict", "permissive"),
        },
    )
    d = diff(old, delta, {})
    assert "expanded_autonomy" in d.drift_signals
    assert d.risk_class == RiskClass.C5_EXECUTION_AUTHORITY
    assert d.sovereign_required is True


def test_detects_expanded_autonomy_when_aforge_test_removed(baseline):
    """Removing any test the aforge contract relies on = loosened mutation gate."""
    old = baseline["execution_discipline"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="execution_discipline",
        reason="drop test for performance",
        affected_organs=("aforge",),
        removed_tests=("dry_run_does_not_write",),
    )
    d = diff(old, delta, {})
    assert "expanded_autonomy" in d.drift_signals
    assert d.risk_class == RiskClass.C5_EXECUTION_AUTHORITY


def test_detects_expanded_autonomy_when_organ_unrecognised(baseline):
    old = baseline["multi_organ_translation"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="multi_organ_translation",
        reason="add new organ",
        affected_organs=("aforge", "ghost_organ"),
    )
    d = diff(old, delta, {})
    assert "expanded_autonomy" in d.drift_signals
    assert d.risk_class == RiskClass.C5_EXECUTION_AUTHORITY


def test_detects_hidden_mutation_when_invariant_changes_silently(baseline):
    old = baseline["boundary_sensing"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="boundary_sensing",
        reason="",  # empty / missing reason → hidden
        changed_invariants={
            "physics": ("membrane.stable", "membrane.fluid"),
        },
    )
    d = diff(old, delta, {})
    assert "hidden_mutation" in d.drift_signals
    assert d.risk_class == RiskClass.C4_FLOOR_LOGIC


def test_detects_authority_drift_when_affects_authority_true(baseline):
    old = baseline["execution_discipline"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="execution_discipline",
        reason="allow execution without anchor for low-risk reads",
        affects_authority=True,
    )
    d = diff(old, delta, {})
    assert "authority_drift" in d.drift_signals
    assert d.risk_class == RiskClass.C5_EXECUTION_AUTHORITY
    assert d.sovereign_required is True


def test_detects_test_removed(baseline):
    old = baseline["reaction_gating"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="reaction_gating",
        reason="rationalise test set",
        removed_tests=("mutation_without_anchor_returns_HOLD",),
    )
    d = diff(old, delta, {})
    assert "test_removed" in d.drift_signals
    assert d.risk_class == RiskClass.C4_FLOOR_LOGIC


def test_detects_missing_test_for_new_anchor(baseline):
    """Adding a new must_preserve without a test = unproven gate."""
    old = baseline["entropy_reduction"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="entropy_reduction",
        reason="add new must_preserve",
        added_must_preserve=("circuit_breaker_for_runaway_entropy",),
    )
    d = diff(old, delta, {})
    assert "missing_test_for_new_anchor" in d.drift_signals
    assert d.risk_class == RiskClass.C4_FLOOR_LOGIC


# ── 2. Diff is pure ────────────────────────────────────────────────────────


def test_diff_is_pure_does_not_mutate_contract(baseline):
    old = baseline["boundary_sensing"]
    snapshot_must = tuple(old.must_never_weaken)
    snapshot_version = old.version
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="boundary_sensing",
        reason="some change",
        added_must_preserve=("new_anchor",),
    )
    _ = diff(old, delta, {})
    # Contract is frozen dataclass — even if it weren't, fields must be
    # unchanged.
    assert tuple(old.must_never_weaken) == snapshot_must
    assert old.version == snapshot_version


# ── 3. Engine refuses to emit on forbidden / extinct / unknown / missing ──


def test_engine_voids_when_caller_requests_apply_patch(baseline):
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="boundary_sensing",
        proposed_delta=SkillDelta(
            old_version="1.0.0",
            new_version="applied_to_system",  # forbidden marker
            skill_name="boundary_sensing",
            reason="",
        ),
        current_skill_contracts=baseline,
    )
    decision = evaluate(request)
    assert decision.verdict == "VOID"
    assert decision.resume_allowed is False
    assert "apply_patch" in decision.rationale


def test_engine_voids_when_skill_in_extinction_ledger(baseline):
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="extinct_skill",
        proposed_delta=SkillDelta(
            old_version="0.9.0",
            new_version="1.0.0",
            skill_name="extinct_skill",
            reason="resurrect",
        ),
        current_skill_contracts=baseline,
        extinction_ledger=("extinct_skill",),
    )
    decision = evaluate(request)
    assert decision.verdict == "VOID"
    assert "extinction_ledger" in decision.rationale


def test_engine_voids_when_skill_not_in_canonical_12(baseline):
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="not_a_real_skill",
        proposed_delta=SkillDelta(
            old_version="1.0.0",
            new_version="1.1.0",
            skill_name="not_a_real_skill",
            reason="add new skill",
        ),
        current_skill_contracts=baseline,
    )
    decision = evaluate(request)
    assert decision.verdict == "VOID"
    assert "canonical 12" in decision.rationale


def test_engine_voids_when_baseline_contract_missing(baseline):
    empty_baseline = {}  # no contract for any skill
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="boundary_sensing",
        proposed_delta=SkillDelta(
            old_version="0.0.0",
            new_version="1.0.0",
            skill_name="boundary_sensing",
            reason="bootstrap",
        ),
        current_skill_contracts=empty_baseline,
    )
    decision = evaluate(request)
    assert decision.verdict == "VOID"


# ── 4. Risk classes map correctly ──────────────────────────────────────────


def test_no_op_delta_classifies_low_risk(baseline):
    old = baseline["boundary_sensing"]
    delta = SkillDelta(
        old_version=old.version,
        new_version=old.version,
        skill_name="boundary_sensing",
        reason="",
    )
    d = diff(old, delta, {})
    assert d.risk_class == RiskClass.C1_DOCS
    assert d.drift_signals == ()


def test_added_must_preserve_with_matching_test_is_clean(baseline):
    old = baseline["conservation_accounting"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="conservation_accounting",
        reason="add conservation traceability anchor",
        added_must_preserve=("conservation_traceability",),
        added_tests=("conservation_traceability_returns_audit_receipt",),
    )
    d = diff(old, delta, {})
    # match: anchor name (with underscores) appears in test name
    assert "missing_test_for_new_anchor" not in d.drift_signals
    assert d.risk_class != RiskClass.C5_EXECUTION_AUTHORITY


def test_added_must_never_weaken_additions_only_are_clean(baseline):
    """Additions to the lock are GOOD (tightening), not weakening."""
    old = baseline["immune_response"]
    delta = SkillDelta(
        old_version=old.version,
        new_version="1.1.0",
        skill_name="immune_response",
        reason="harden immune boundary",
        added_must_never_weaken=("scar_pattern_must_not_auto_revert",),
    )
    d = diff(old, delta, {})
    assert "weakened_gate" not in d.drift_signals
    assert d.risk_class != RiskClass.C5_EXECUTION_AUTHORITY


# ── 5. Resume NEVER allowed automatically ──────────────────────────────────


def test_no_resume_allowed_without_judge_and_cooling(baseline):
    """Even on a clean C1 diff, the engine refuses to allow resume.

    Judge + cooling is always required to enable resume. This is the most
    important invariant of the bounded model.
    """
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="boundary_sensing",
        proposed_delta=SkillDelta(
            old_version="1.0.0",
            new_version="1.0.0",
            skill_name="boundary_sensing",
            reason="no-op",
        ),
        current_skill_contracts=baseline,
        last_cooling_state={"complete": True},
    )
    decision = evaluate(request)
    assert decision.resume_allowed is False


def test_engine_marks_cooling_required_on_every_decision(baseline):
    """No fast-path past cooling."""
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="boundary_sensing",
        proposed_delta=SkillDelta(
            old_version="1.0.0",
            new_version="1.0.0",
            skill_name="boundary_sensing",
            reason="",
        ),
        current_skill_contracts=baseline,
        last_cooling_state={"complete": True},
    )
    decision = evaluate(request)
    assert decision.cooling_required is True


# ── 6. GateDecision carries the diff and required tests ─────────────────────


def test_gate_decision_carries_diff_and_required_tests(baseline):
    request = SkillDeltaRequest(
        seal_receipt="vault-1",
        skill_name="boundary_sensing",
        proposed_delta=SkillDelta(
            old_version="1.0.0",
            new_version="1.0.0",
            skill_name="boundary_sensing",
            reason="",
        ),
        current_skill_contracts=baseline,
    )
    decision = evaluate(request)
    assert decision.diff.skill_name == "boundary_sensing"
    assert "drift_signals_recorded" in decision.required_tests
    assert "extinction_ledger_consulted" in decision.required_tests


# ── 7. Seed baseline has constitutional anchors ────────────────────────────


def test_all_twelve_skills_present(baseline):
    assert set(baseline.keys()) == set(TWELVE_SKILLS)
    assert len(TWELVE_SKILLS) == 12


def test_seed_contracts_carry_must_preserve_and_must_never_weaken(baseline):
    for name, c in baseline.items():
        assert c.must_preserve, f"{name} missing must_preserve"
        assert c.must_never_weaken, f"{name} missing must_never_weaken"
        assert "evidence_floor" in c.must_preserve
        assert "human_ack_for_irreversible_action" in c.must_never_weaken


def test_seed_contracts_have_three_disciplines_in_invariants(baseline):
    for name, c in baseline.items():
        for d in ("physics", "biology", "chemistry"):
            assert d in c.invariant, f"{name} missing discipline {d}"


# ── 8. Drift names list is closed ──────────────────────────────────────────


def test_drift_names_constant_lists_the_six_names():
    """The named drifts are frozen — new detection must extend the list explicitly."""
    assert "weakened_gate" in DRIFT_NAMES
    assert "expanded_autonomy" in DRIFT_NAMES
    assert "hidden_mutation" in DRIFT_NAMES
    assert "authority_drift" in DRIFT_NAMES
    assert "test_removed" in DRIFT_NAMES
    assert "missing_test_for_new_anchor" in DRIFT_NAMES


# ── 9. The four drifts in your HOLD are precisely detected ─────────────────


def test_your_hold_four_drifts_all_detected(baseline):
    """The sovereign directive named four drifts. Each must be detected when
    triggered through a realistic SkillDelta.
    """
    # (1) weakened_gate
    d1 = diff(
        baseline["boundary_sensing"],
        SkillDelta(
            old_version="1.0.0",
            new_version="1.1.0",
            skill_name="boundary_sensing",
            reason="simplify",
            removed_must_never_weaken=("aforge_mutation_gate",),
        ),
        {},
    )
    assert "weakened_gate" in d1.drift_signals

    # (2) expanded_autonomy
    d2 = diff(
        baseline["reaction_gating"],
        SkillDelta(
            old_version="1.0.0",
            new_version="1.1.0",
            skill_name="reaction_gating",
            reason="speed",
            changed_invariants={"aforge_activation_energy": ("100", "10")},
        ),
        {},
    )
    assert "expanded_autonomy" in d2.drift_signals

    # (3) hidden_mutation
    d3 = diff(
        baseline["boundary_sensing"],
        SkillDelta(
            old_version="1.0.0",
            new_version="1.1.0",
            skill_name="boundary_sensing",
            reason="",
            changed_invariants={"chemistry": ("a", "b")},
        ),
        {},
    )
    assert "hidden_mutation" in d3.drift_signals

    # (4) authority_drift
    d4 = diff(
        baseline["execution_discipline"],
        SkillDelta(
            old_version="1.0.0",
            new_version="1.1.0",
            skill_name="execution_discipline",
            reason="let users override judges for low risk",
            affects_authority=True,
        ),
        {},
    )
    assert "authority_drift" in d4.drift_signals

"""P0-J2 repair tests — RSI risk ontology through explicit Delta adapter.

Forged 2026-07-17 (P0-J2 incident response) under F13 SOVEREIGN HOLD:
  "Commit c4b672ebf contains a concrete runtime-breaking enum mismatch.
   Repair through an RSI adapter, do not revert the deduplication."

These tests:
  1. Lock the RSI-specific enum (RSIRiskClass) so future dedup attempts
     cannot silently break it again.
  2. Execute (not just import) every enum-dependent path that boot triggers.
  3. Verify the explicit conversion to the canonical
     DeltaIrreversibilityClass at the boundary.

These tests must FAIL on the pre-repair c4b672ebf code and PASS on
post-repair repair/riskclass-rsi-adapter branch.
"""

from __future__ import annotations

import pytest

from arifosmcp.constitutional_map import DeltaIrreversibilityClass
from arifosmcp.rsi import (
    RiskClass,
    SkillContract,
    SkillDelta,
    SkillDeltaRequest,
    diff,
    evaluate,
    seed_12_contracts,
)
from arifosmcp.rsi.contracts import RSIRiskClass


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: All RSI risk members resolve (the verdict's primary contract)
# ─────────────────────────────────────────────────────────────────────────────
def test_all_rsi_risk_members_resolve():
    """Every RSI semantic name must be a real member, not an alias shadow.

    Pre-repair: AttributeError because RiskClass was aliased to
    DeltaIrreversibilityClass which lacks these names.
    Post-repair: RSIRiskClass defines them explicitly.
    """
    expected = {
        "C0_GRAMMAR",
        "C1_DOCS",
        "C2_CONTRACT_DESCRIPTION",
        "C3_PUBLIC_SURFACE",
        "C4_FLOOR_LOGIC",
        "C5_EXECUTION_AUTHORITY",
    }
    actual = {m.name for m in RiskClass}
    assert expected.issubset(actual), (
        f"Missing RSI members: {expected - actual}. "
        f"Got: {actual}"
    )

    # Scalar values must also match (so to_delta_class() works).
    expected_values = {"C0", "C1", "C2", "C3", "C4", "C5"}
    actual_values = {m.value for m in RiskClass}
    assert expected_values == actual_values, (
        f"Scalar mismatch. expected={expected_values} actual={actual_values}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Every seeded contract classifies without error (verdict §3 repro)
# ─────────────────────────────────────────────────────────────────────────────
def test_skill_contract_classifies():
    """classifies() must succeed for all 12 seed contracts.

    Pre-repair: AttributeError: 'DeltaIrreversibilityClass' has no
    attribute 'C2_CONTRACT_DESCRIPTION' at rsi/contracts.py:84.
    Post-repair: all 12 contracts return RSIRiskClass.C2_CONTRACT_DESCRIPTION.
    """
    contracts = seed_12_contracts()
    assert len(contracts) == 12, f"Expected 12 seed contracts, got {len(contracts)}"

    for name, contract in contracts.items():
        cls = contract.classifies()
        assert isinstance(cls, RiskClass), (
            f"{name}.classifies() returned {type(cls).__name__}, expected RiskClass"
        )
        assert cls.name == "C2_CONTRACT_DESCRIPTION", (
            f"{name}.classifies() returned {cls.name}, expected C2_CONTRACT_DESCRIPTION"
        )
        assert cls.value == "C2"


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: diff() on a clean (no-op) delta returns C1 baseline
# ─────────────────────────────────────────────────────────────────────────────
def test_diff_clean_delta(baseline_contracts, organ_inventory):
    """A delta that adds nothing must classify as C1_DOCS (baseline)."""
    contract = baseline_contracts["boundary_sensing"]
    delta = SkillDelta(
        old_version=contract.version,
        new_version=contract.version,
        skill_name=contract.name,
        reason="baseline no-op",
    )
    result = diff(contract, delta, organ_inventory)
    assert result.risk_class.name == "C1_DOCS"
    assert result.is_clean() is True
    assert result.judge_required is False
    assert result.sovereign_required is False
    assert "no-op" in result.summary


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: diff() on authority drift escalates to C5
# ─────────────────────────────────────────────────────────────────────────────
def test_diff_authority_delta(baseline_contracts, organ_inventory):
    """A delta that sets affects_authority=True must classify C5."""
    contract = baseline_contracts["boundary_sensing"]
    delta = SkillDelta(
        old_version=contract.version,
        new_version="2.0.0",
        skill_name=contract.name,
        reason="relaxing authority",
        affects_authority=True,
    )
    result = diff(contract, delta, organ_inventory)
    assert result.risk_class.name == "C5_EXECUTION_AUTHORITY", (
        f"authority_drift expected C5, got {result.risk_class.name}"
    )
    assert result.sovereign_required is True
    assert result.judge_required is True
    assert "authority_drift" in result.drift_signals


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: diff() on weakened gate escalates to C5
# ─────────────────────────────────────────────────────────────────────────────
def test_diff_weakened_gate(baseline_contracts, organ_inventory):
    """A delta that removes a must_never_weaken entry escalates to C5."""
    contract = baseline_contracts["boundary_sensing"]
    delta = SkillDelta(
        old_version=contract.version,
        new_version="2.0.0",
        skill_name=contract.name,
        reason="removing aforge_mutation_gate",
        removed_must_never_weaken=("aforge_mutation_gate",),
    )
    result = diff(contract, delta, organ_inventory)
    assert result.risk_class.name == "C5_EXECUTION_AUTHORITY"
    assert result.sovereign_required is True
    assert "weakened_gate" in result.drift_signals


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: arif_route injection does not crash on boot (J2)
# ─────────────────────────────────────────────────────────────────────────────
def test_j2_route_injection_boot(baseline_contracts, organ_inventory):
    """The arif_route / arif_judge boot-path must not raise AttributeError.

    Pre-repair: INJECTION FAILED warnings during tool registration were
    NON-FATAL (separate issue, J2 cosmetic WARNING). But when the engine
    is exercised, the AttributeError on missing enum members would crash.
    Post-repair: enum members resolve and the engine returns a verdict.
    """
    # Simulate the engine path that touches all enum members.
    contract = baseline_contracts["entropy_reduction"]

    # C1 baseline (every contract produces a diff at boot for federation edges)
    delta_clean = SkillDelta(
        old_version=contract.version,
        new_version=contract.version,
        skill_name=contract.name,
        reason="boot-time edge probe",
    )
    result_clean = diff(contract, delta_clean, organ_inventory)
    assert result_clean.risk_class.name == "C1_DOCS"

    # C5 path (authority)
    delta_auth = SkillDelta(
        old_version=contract.version,
        new_version="2.0.0",
        skill_name=contract.name,
        reason="authority test",
        affects_authority=True,
    )
    result_auth = diff(contract, delta_auth, organ_inventory)
    assert result_auth.risk_class.name == "C5_EXECUTION_AUTHORITY"

    # evaluate() must work for both
    request_clean = SkillDeltaRequest(
        seal_receipt="boot-test-clean",
        skill_name=contract.name,
        proposed_delta=delta_clean,
        current_skill_contracts=baseline_contracts,
    )
    request_auth = SkillDeltaRequest(
        seal_receipt="boot-test-auth",
        skill_name=contract.name,
        proposed_delta=delta_auth,
        current_skill_contracts=baseline_contracts,
    )
    decision_clean = evaluate(request_clean)
    decision_auth = evaluate(request_auth)
    assert decision_clean.verdict == "APPROVE_C0_C3"
    assert decision_auth.verdict in ("HOLD_C4", "HOLD_C5", "VOID")


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: arif_judge injection does not crash on boot (J2)
# ─────────────────────────────────────────────────────────────────────────────
def test_j2_judge_injection_boot(baseline_contracts, organ_inventory):
    """The arif_judge engine must produce a verdict without AttributeError.

    Pre-repair: contracts.classifies() and diff() raised AttributeError on
    RiskClass.C2_CONTRACT_DESCRIPTION / C5_EXECUTION_AUTHORITY, killing the
    process at boot. Post-repair: both succeed.
    """
    # Exercise every RSI enum member to lock the contract.
    for member in RSIRiskClass:
        # to_delta_class() must succeed for every member.
        d = member.to_delta_class()
        assert isinstance(d, DeltaIrreversibilityClass)
        assert d.value == member.value, (
            f"Scalar mismatch: RSI {member.name}={member.value} "
            f"vs Delta {d.name}={d.value}"
        )

    # The judge-deliberate path evaluates all 12 contracts.
    decisions = []
    for name, contract in baseline_contracts.items():
        delta = SkillDelta(
            old_version=contract.version,
            new_version=contract.version,
            skill_name=contract.name,
            reason="judge boot scan",
        )
        result = diff(contract, delta, organ_inventory)
        request = SkillDeltaRequest(
            seal_receipt=f"judge-boot-{name}",
            skill_name=contract.name,
            proposed_delta=delta,
            current_skill_contracts=baseline_contracts,
        )
        decisions.append(evaluate(request))

    assert len(decisions) == 12
    # All 12 clean baselines must approve
    assert all(d.verdict == "APPROVE_C0_C3" for d in decisions)


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def baseline_contracts():
    return seed_12_contracts()


@pytest.fixture
def organ_inventory():
    return {
        "arifos": ("arif_judge", "arif_route", "arif_memory"),
        "aforge": ("forge_execute",),
        "geox": ("geox_well_desurvey",),
        "wealth": ("wealth_npv",),
        "well": ("well_validate_vitality",),
    }
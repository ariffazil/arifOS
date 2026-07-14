"""
tests/test_truth_kernel_constitutional.py — 7 reference tests for the constitutional truth kernel.

Bound 2026-07-14 · F13 SOVEREIGN RATIFIED

These tests prove the T1-T13 invariants hold. Each test maps to one or
more invariants from the constitutional amendment.

Tests:
  1. SEALED falsehood does not become true
  2. Duplicate source lineage does not create witness diversity
  3. Normative claims cannot become empirical VERIFIED
  4. Stale claims downgrade automatically
  5. Contradiction forces CONTESTED
  6. Truth never grants execution authority
  7. Missing physical telemetry returns UNMEASURED (never VOID)

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.truth_kernel import (
    AuthorityState,
    Claim,
    ClaimKind,
    EpistemicState,
    Evidence,
    RecordState,
    ResourceTelemetry,
    TruthEngine,
    check_physical_erasure_bound,
)


ENGINE = TruthEngine()


# ── T10: SEALED falsehood does not become true ──────────────────────────


def test_sealed_falsehood_does_not_become_true():
    """A claim with overwhelming counter-evidence stays CORROBORATED=¬H,
    even when its record is SEALED. SEAL preserves provenance; it does
    not promote truth.

    Maps to: T10 (Seal preserves, never sanctifies).
    """
    claim = Claim(
        claim_id="sealed-false",
        text="The moon is made of green cheese",
        kind=ClaimKind.EMPIRICAL_STABLE,
        prior_probability=0.01,  # very low prior
        falsifiers=("Lunar rock samples", "Density measurements", "Photographic evidence"),
    )
    evidence = [
        Evidence(
            evidence_id="rock-sample-1",
            description="Apollo samples are igneous rock",
            likelihood_if_claim=0.001,
            likelihood_if_not_claim=0.999,
            source_quality=0.99,
            independence=1.0,
            reproducibility=1.0,
            calibration=0.99,
            lineage_group="apollo-samples",
            provenance_uri="vault://nasa/apollo-17",
        ),
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.SEALED)
    # T10: assert the sealed_does_not_imply_true invariant is set
    assert assessment.sealed_does_not_imply_true is True
    # Even when SEALED, the epistemic state must reflect evidence
    assert assessment.warrant < 0.5
    assert assessment.posterior_probability < 0.5
    assert assessment.epistemic_state in (
        EpistemicState.HYPOTHESIS,
        EpistemicState.UNKNOWN,
        EpistemicState.FALSIFIED,
    ), f"SEALED low-warrant claim got promoted: {assessment.epistemic_state}"


# ── T5: Duplicate source lineage does not create witness diversity ────


def test_duplicate_lineage_does_not_create_witness_diversity():
    """Ten press articles from the same anonymous source ≈ one witness.

    Maps to: T5 (Witnesses must be independent).
    """
    claim = Claim(
        claim_id="press-release-test",
        text="X happened today",
        kind=ClaimKind.EMPIRICAL_DYNAMIC,
        prior_probability=0.5,
        falsifiers=("Direct on-site observation"),
    )
    # 10 evidence items all sharing the same lineage_group
    evidence = [
        Evidence(
            evidence_id=f"press-{i}",
            description=f"Article {i} reports X",
            likelihood_if_claim=0.7,
            likelihood_if_not_claim=0.3,
            source_quality=0.7,
            independence=0.5,
            reproducibility=0.5,
            calibration=0.5,
            lineage_group="single-anonymous-source",  # SAME for all
            provenance_uri=f"vault://press/article-{i}",
        )
        for i in range(10)
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.ATTESTED)
    # N_eff should be ~1, not 10
    assert assessment.effective_witness_count < 2.0, (
        f"Lineage-clustered N_eff = {assessment.effective_witness_count} (should be ~1, not 10)"
    )
    # And warrant must be lower than the naive count would suggest
    assert assessment.warrant < 0.7


# ── T9: Normative claims cannot become empirical VERIFIED ──────────────


def test_normative_claims_cannot_become_verified():
    """A normative claim without a declared frame stays AMBIGUOUS, no
    matter how much evidence supports it. The kernel must not silently
    turn 'good' into a fact.

    Maps to: T9 (Normative claims expose their frame).
    """
    claim = Claim(
        claim_id="policy-good",
        text="This policy is good for Malaysians",
        kind=ClaimKind.NORMATIVE,
        prior_probability=0.5,
        falsifiers=("Stakeholder rejection", "Outcome reverses wellbeing"),
        # declared_frame=None — frame not exposed
    )
    # Heap on evidence
    evidence = [
        Evidence(
            evidence_id=f"support-{i}",
            description=f"Survey result {i}",
            likelihood_if_claim=0.9,
            likelihood_if_not_claim=0.1,
            source_quality=0.99,
            independence=0.95,
            reproducibility=0.99,
            calibration=0.95,
            lineage_group=f"survey-group-{i % 3}",  # somewhat independent
            provenance_uri=f"vault://survey/{i}",
        )
        for i in range(20)
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.SEALED)
    assert assessment.epistemic_state == EpistemicState.AMBIGUOUS, (
        f"Normative claim without frame got state {assessment.epistemic_state}"
    )
    # Even with SEALED, must not be VERIFIED
    assert assessment.epistemic_state != EpistemicState.VERIFIED_MEASUREMENT
    # Authority stays at REQUIRE_F13 because it's normative
    assert assessment.authority_state == AuthorityState.REQUIRE_F13


# ── T8: Stale claims downgrade automatically ──────────────────────────


def test_stale_claims_downgrade_automatically():
    """A claim with freshness=0 must become STALE, regardless of historical
    evidence.

    Maps to: T8 (Time is explicit).
    """
    claim = Claim(
        claim_id="market-price-now",
        text="XYZ is at $100 right now",
        kind=ClaimKind.EMPIRICAL_DYNAMIC,
        prior_probability=0.5,
        falsifiers=("Direct price check"),
    )
    evidence = [
        Evidence(
            evidence_id="quote-old",
            description="Quote from 3 months ago",
            likelihood_if_claim=0.95,
            likelihood_if_not_claim=0.05,
            source_quality=0.95,
            independence=1.0,
            reproducibility=0.95,
            calibration=0.95,
            lineage_group="market-data",
            provenance_uri="vault://market/xyz",
            freshness=0.0,  # TOTALLY STALE
        ),
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.ATTESTED)
    assert assessment.epistemic_state == EpistemicState.STALE, (
        f"Stale claim got state {assessment.epistemic_state}"
    )
    # Force-staleness via override
    assessment2 = ENGINE.assess(claim, evidence, freshness_override=0.0)
    assert assessment2.epistemic_state == EpistemicState.STALE


# ── T6: Contradiction forces CONTESTED ────────────────────────────────


def test_contradiction_forces_contested():
    """When strong evidence supports and strong evidence opposes, the
    claim must become CONTESTED — not averaged into a confident middle.

    Maps to: T6 (Contradictions survive).
    """
    claim = Claim(
        claim_id="contested-policy",
        text="Regulation X improves safety",
        kind=ClaimKind.CAUSAL_HYPOTHESIS,
        prior_probability=0.5,
        falsifiers=("Adverse event data", "Counter-study replication"),
    )
    evidence = [
        # Strong support
        Evidence(
            evidence_id="study-A",
            description="2024 study supports",
            likelihood_if_claim=0.9,
            likelihood_if_not_claim=0.1,
            source_quality=0.9,
            independence=0.9,
            reproducibility=0.95,
            calibration=0.9,
            lineage_group="study-A-group",
            provenance_uri="vault://studies/A",
        ),
        # Strong opposition
        Evidence(
            evidence_id="study-B",
            description="2025 study opposes",
            likelihood_if_claim=0.1,
            likelihood_if_not_claim=0.9,
            source_quality=0.9,
            independence=0.9,
            reproducibility=0.95,
            calibration=0.9,
            lineage_group="study-B-group",
            provenance_uri="vault://studies/B",
        ),
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.ATTESTED)
    assert assessment.contradiction_index > 0.5, (
        f"Strong-opposing evidence produced C_conflict = {assessment.contradiction_index}"
    )
    assert assessment.epistemic_state == EpistemicState.CONTESTED, (
        f"Contradiction not honored: got {assessment.epistemic_state}"
    )
    # T11: must not auto-promote authority because evidence exists
    assert assessment.authority_state in (
        AuthorityState.ADVISE,
        AuthorityState.OBSERVE,
        AuthorityState.REQUIRE_F13,
    )


# ── T11: Truth never grants execution authority ───────────────────────


def test_truth_never_grants_execution_authority():
    """Even a perfectly warranted, corroborated claim does NOT
    auto-authorize execution. Authority is orthogonal to warrant.

    Maps to: T11 (Truth does not self-authorize).
    """
    claim = Claim(
        claim_id="math-truth",
        text="2 + 2 = 4",
        kind=ClaimKind.FORMAL_AXIOMATIC,
        prior_probability=0.99,
        falsifiers=("Counter-axiom system", "Different base"),
    )
    evidence = [
        Evidence(
            evidence_id="axiom",
            description="Peano axioms",
            likelihood_if_claim=1.0,
            likelihood_if_not_claim=0.0,
            source_quality=1.0,
            independence=1.0,
            reproducibility=1.0,
            calibration=1.0,
            lineage_group="peano-1889",
            provenance_uri="vault://math/peano",
        ),
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.SEALED)
    # T11: even with SEALED + perfect evidence, authority must be at most
    # REVERSIBLE_EXECUTE, NEVER require_f13 → forbidden, never auto-grant
    # IRREVERSIBLE action.
    assert assessment.authority_state in (
        AuthorityState.OBSERVE,
        AuthorityState.ADVISE,
        AuthorityState.REVERSIBLE_EXECUTE,
    )
    assert assessment.truth_does_not_self_authorize is True


# ── T12: Missing physical telemetry returns UNMEASURED ────────────────


def test_missing_physical_telemetry_returns_unmeasured():
    """When no Landauer telemetry is available, the physical check must
    return UNMEASURED — not VOID, not 'hallucination'.

    Maps to: T12 (Thermodynamics stays physical).
    """
    # Case A: complete telemetry
    full = check_physical_erasure_bound(
        ResourceTelemetry(
            actual_joules=2.0e-12,
            bits_erased=1_000,
            temperature_kelvin=300.0,
        )
    )
    assert full["status"] in ("WITHIN_BOUND", "ABOVE_BOUND")

    # Case B: missing telemetry
    none = check_physical_erasure_bound(ResourceTelemetry())
    assert none["status"] == "UNMEASURED"
    # The status must be UNMEASURED — never VOID, never HALLUCINATION.
    assert none["status"] != "VOID"
    assert "HALLUCINATION" not in none["status"].upper()

    # Case C: partial telemetry (only joules, no temperature)
    partial = check_physical_erasure_bound(
        ResourceTelemetry(actual_joules=1.0e-12, bits_erased=1000)
    )
    assert partial["status"] == "UNMEASURED"

    # Case D: insufficient data (zero bits)
    zero = check_physical_erasure_bound(
        ResourceTelemetry(actual_joules=1.0e-12, bits_erased=0, temperature_kelvin=300.0)
    )
    assert zero["status"] == "INSUFFICIENT_DATA"


# ── Bonus: T7 falsifiability gate ──────────────────────────────────────


def test_no_falsifiers_caps_at_supported():
    """T7: a claim with no falsifiers can never become CORROBORATED.

    Even with overwhelming evidence, the state must stop at SUPPORTED.
    """
    claim = Claim(
        claim_id="unfalsifiable",
        text="Mysterious force affects outcomes",
        kind=ClaimKind.EMPIRICAL_DYNAMIC,
        prior_probability=0.5,
        falsifiers=(),  # NONE — T7 violation
    )
    evidence = [
        Evidence(
            evidence_id=f"anecdote-{i}",
            description=f"Anecdote {i}",
            likelihood_if_claim=0.95,
            likelihood_if_not_claim=0.05,
            source_quality=0.9,
            independence=0.9,
            reproducibility=0.9,
            calibration=0.9,
            lineage_group=f"anecdote-{i}",
            provenance_uri=f"vault://anecdote/{i}",
        )
        for i in range(15)
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.RATIFIED)
    assert assessment.falsifiability == 0.0
    assert assessment.epistemic_state != EpistemicState.CORROBORATED, (
        f"Claim without falsifiers got CORROBORATED: {assessment.epistemic_state}"
    )
    assert assessment.epistemic_state in (
        EpistemicState.SUPPORTED,
        EpistemicState.HYPOTHESIS,
    )


# ── Bonus: T4 provenance completeness cap ─────────────────────────────


def test_missing_provenance_caps_at_supported():
    """T4: a claim with no provenance_uri evidence cannot reach
    CORROBORATED. Even with strong evidence, P_v=0 caps the ladder.
    """
    claim = Claim(
        claim_id="no-provenance",
        text="X is true",
        kind=ClaimKind.EMPIRICAL_STABLE,
        prior_probability=0.5,
        falsifiers=("Counter-observation", "Replication failure"),
    )
    evidence = [
        Evidence(
            evidence_id=f"anecdote-{i}",
            description=f"Observation {i}",
            likelihood_if_claim=0.9,
            likelihood_if_not_claim=0.1,
            source_quality=0.9,
            independence=0.95,
            reproducibility=0.95,
            calibration=0.9,
            lineage_group=f"obs-{i}",
            provenance_uri=None,  # T4 violation: no provenance
        )
        for i in range(10)
    ]
    assessment = ENGINE.assess(claim, evidence, record_state=RecordState.ATTESTED)
    assert assessment.provenance_completeness == 0.0
    assert assessment.epistemic_state != EpistemicState.CORROBORATED

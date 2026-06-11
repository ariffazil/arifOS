"""
test_mind_geometry.py — 5 Acceptance Tests for MIND_GEOMETRY_V1
================================================================

EUREKA-T ratification, 2026-06-11. The 5 canonical acceptance
tests that any conformant MIND_GEOMETRY_V1 implementation must
pass. These are geometry-layer tests, not LLM tests — the
geometry layer MUST produce the expected verdict deterministically
from the inputs alone.

The 5 tests are the verbatim cases from the EUREKA-T spec,
re-expressed as pytest test functions. The geometry layer is
expected to be re-entrant: a single geometry call must produce
the same verdict across re-runs.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import math

import pytest

from arifosmcp.geometry.mind_axioms import Axiom, AxiomVerdict
from arifosmcp.geometry.mind_geometry import (
    ACCEPTANCE_TESTS,
    DecisionTorus,
    DEFAULT_TORUS,
    compute_geometry,
    fuse_axioms,
)
from arifosmcp.geometry.mind_schema import (
    GeometryEnvelope,
    GeometryVerdict,
    ManifoldType,
    OrthogonalAxes,
)
from arifosmcp.geometry.sovereign_proximity import (
    BAND_THRESHOLDS,
    ProximityBand,
    ProximityInputs,
    band_of,
    compute_sovereign_proximity,
    explain_proximity,
)


# ── Test 1: metaphor overclaim as proof → HOLE_RISK ─────────────────────────


def test_metaphor_overclaim_yields_hole_risk():
    """'The torus proves arifOS is physically correct.'

    A metaphor treated as proof collapses truth_axis and
    coherence_axis (orthogonality_violation). The geometry
    layer must catch this as Axiom 1 (NON_COLLAPSE) and
    return HOLE_RISK. The runner then routes to HOLD.
    """
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "metaphor_overclaim")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    assert verdict.geometry_verdict == GeometryVerdict.HOLE_RISK

    # The top axiom failure should be A1 (non-collapse)
    failed = [r for r in verdict.axiom_results if r.verdict != AxiomVerdict.PASS]
    assert any(r.axiom == Axiom.NON_COLLAPSE for r in failed), (
        "metaphor overclaim must trigger A1 NON_COLLAPSE failure"
    )


# ── Test 2: safe reasoning on the surface → SURFACE ─────────────────────────


def test_safe_reasoning_yields_surface():
    """'Explain torus as a design metaphor for decision surfaces.'

    A clean, surface-bound reasoning task. All 7 axioms should
    pass; sovereign_proximity should be 0.0 (no mutating
    action, no uncertainty above band, no irreversibility);
    the verdict should be SURFACE.
    """
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "safe_surface_reasoning")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    assert verdict.geometry_verdict == GeometryVerdict.SURFACE
    assert verdict.sovereign_proximity < 0.25, (
        f"safe reasoning should have proximity < 0.25, got {verdict.sovereign_proximity}"
    )

    # No axiom should fail
    failed = [r for r in verdict.axiom_results if r.verdict != AxiomVerdict.PASS]
    assert not failed, f"safe reasoning should have 0 axiom failures; got {failed}"


# ── Test 3: self-authorized production patch → HOLE_RISK ────────────────────


def test_self_authorized_mutation_yields_hole_risk():
    """'Patch the production kernel now.'

    Five axioms should fail simultaneously: A2 (self-authorized
    territory), A3 (preflight incomplete), A4 (capability without
    authorization), A5 (entropy exceeds budget), A6 (irreversible
    mutating action). The cascade is the constitutional feature —
    not a single failure, a structural pattern.
    """
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "self_authorized_production_patch")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    assert verdict.geometry_verdict == GeometryVerdict.HOLE_RISK
    assert verdict.sovereign_proximity >= 0.75, (
        f"self-authorized production patch should have proximity >= 0.75, got {verdict.sovereign_proximity}"
    )
    assert verdict.proximity_band == ProximityBand.FORBIDDEN

    # Cascade check: at least 3 axioms should fail
    failed = [r for r in verdict.axiom_results if r.verdict != AxiomVerdict.PASS]
    assert len(failed) >= 3, (
        f"self-authorized mutation should cascade at least 3 axiom failures; got {len(failed)}: {failed}"
    )

    # The 5 expected axioms in this cascade
    expected_axioms = {
        Axiom.NO_SELF_CENTER,
        Axiom.OBSERVE_BEFORE_MUTATE,
        Axiom.CAPABILITY_NOT_PERMISSION,
        Axiom.ENTROPY_GATE,
        Axiom.REVERSIBILITY_GATE,
    }
    actual_failed = {r.axiom for r in failed}
    assert expected_axioms.issubset(actual_failed), (
        f"missing expected axiom failures: {expected_axioms - actual_failed}"
    )


# ── Test 4: unstructured LLM output → HOLD ─────────────────────────────────


def test_unstructured_llm_output_yields_hold():
    """The inner LLM returned prose instead of JSON.

    Per Axiom 7, the kernel must fail-closed at the schema
    boundary. Repair never happens inside the synthesis
    boundary — that would be the entry point for hantu
    claims. The geometry verdict is HOLD, not a downgrade
    to EDGE.
    """
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "unstructured_llm_output")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,  # noqa: E501
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    assert verdict.geometry_verdict == GeometryVerdict.HOLD

    # Axiom 7 should be the top failure
    failed = [r for r in verdict.axiom_results if r.verdict != AxiomVerdict.PASS]
    assert any(r.axiom == Axiom.SCHEMA_BEFORE_SYNTHESIS for r in failed), (
        "unstructured LLM output must trigger A7 SCHEMA_BEFORE_SYNTHESIS failure"
    )


# ── Test 5: orthogonality — coherence ≠ truth ──────────────────────────────


def test_coherence_not_truth_yields_hole_risk():
    """'The answer is elegant, therefore true.'

    High coherence (C=0.95) being used as a proxy for high
    truth (T=0.1) is a classic collapse. The geometry layer
    must catch this via Axiom 1 (NON_COLLAPSE) and route to
    HOLE_RISK. The 7 axes are *not* exchangeable.
    """
    tc = next(t for t in ACCEPTANCE_TESTS if t.name == "coherence_not_truth")
    verdict = compute_geometry(
        query=tc.query,
        action_class=tc.action_class,
        has_authorization=tc.has_authorization,
        inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
        axes=tc.axes,
        orthogonality_violation=tc.orthogonality_violation,
        in_hole_territory=tc.in_hole_territory,
        self_authorization_score=tc.self_authorization_score,
        reversibility=tc.reversibility,
        blast_radius=tc.blast_radius,
        authority_cleanliness=tc.authority_cleanliness,
        entropy_delta=tc.entropy_delta,
    )
    assert verdict.geometry_verdict == GeometryVerdict.HOLE_RISK

    failed = [r for r in verdict.axiom_results if r.verdict != AxiomVerdict.PASS]
    assert any(r.axiom == Axiom.NON_COLLAPSE for r in failed), (
        "coherence-as-truth must trigger A1 NON_COLLAPSE failure"
    )


# ── Test 6: 5/5 acceptance tests pass (smoke) ───────────────────────────────


def test_all_5_acceptance_tests_pass():
    """All 5 EUREKA-T acceptance tests must produce their expected verdict.

    This is the regression guard. If any single test flips
    verdict, the geometry layer is regressed.
    """
    for tc in ACCEPTANCE_TESTS:
        verdict = compute_geometry(
            query=tc.query,
            action_class=tc.action_class,
            has_authorization=tc.has_authorization,
            inner_llm_returned_structured_output=tc.inner_llm_returned_structured_output,
            axes=tc.axes,
            orthogonality_violation=tc.orthogonality_violation,
            in_hole_territory=tc.in_hole_territory,
            self_authorization_score=tc.self_authorization_score,
            reversibility=tc.reversibility,
            blast_radius=tc.blast_radius,
            authority_cleanliness=tc.authority_cleanliness,
            entropy_delta=tc.entropy_delta,
        )
        assert verdict.geometry_verdict == tc.expected_geometry_verdict, (
            f"test {tc.name!r}: expected {tc.expected_geometry_verdict}, got {verdict.geometry_verdict}"
        )


# ── Test 7: sovereign_proximity bands ──────────────────────────────────────


@pytest.mark.parametrize(
    "proximity,expected_band",
    [
        (0.0, ProximityBand.SURFACE),
        (0.1, ProximityBand.SURFACE),
        (0.249, ProximityBand.SURFACE),
        (0.25, ProximityBand.EDGE),
        (0.4, ProximityBand.EDGE),
        (0.499, ProximityBand.EDGE),
        (0.5, ProximityBand.HOLE_RISK),
        (0.6, ProximityBand.HOLE_RISK),
        (0.749, ProximityBand.HOLE_RISK),
        (0.75, ProximityBand.FORBIDDEN),
        (0.9, ProximityBand.FORBIDDEN),
        (1.0, ProximityBand.FORBIDDEN),
    ],
)
def test_band_classification(proximity, expected_band):
    """Band thresholds are F13-ratified and must not drift."""
    assert band_of(proximity) == expected_band


# ── Test 8: sovereign_proximity composition ─────────────────────────────────


def test_proximity_composition_is_weighted_sum():
    """Sovereign proximity = 0.30·SA + 0.20·IRR + 0.15·EBR + 0.15·AU + 0.10·AG + 0.10·ST.

    Pure composition test. The weights are F13-ratified and
    must sum to 1.0; the result must be clamped to [0, 1].
    """
    inputs = ProximityInputs(
        self_authorization=0.0,
        irreversibility=0.0,
        external_blast_radius=0.0,
        authority_uncertainty=0.0,
        audit_gap=0.0,
        secret_touching=0.0,
    )
    assert compute_sovereign_proximity(inputs) == 0.0

    # All ones → 1.0 (clamped)
    inputs_all_ones = ProximityInputs(
        self_authorization=1.0,
        irreversibility=1.0,
        external_blast_radius=1.0,
        authority_uncertainty=1.0,
        audit_gap=1.0,
        secret_touching=1.0,
    )
    assert compute_sovereign_proximity(inputs_all_ones) == 1.0

    # Half on every axis → 0.5
    inputs_half = ProximityInputs(
        self_authorization=0.5,
        irreversibility=0.5,
        external_blast_radius=0.5,
        authority_uncertainty=0.5,
        audit_gap=0.5,
        secret_touching=0.5,
    )
    assert abs(compute_sovereign_proximity(inputs_half) - 0.5) < 1e-9

    # Per-axis contribution trace sums to total
    trace = explain_proximity(inputs_half)
    assert abs(sum(trace.values()) - 0.5) < 1e-9


def test_proximity_explain_returns_per_component():
    """explain_proximity returns 6 component contributions for F11 audit."""
    inputs = ProximityInputs(
        self_authorization=1.0,
        irreversibility=0.0,
        external_blast_radius=0.0,
        authority_uncertainty=0.0,
        audit_gap=0.0,
        secret_touching=0.0,
    )
    trace = explain_proximity(inputs)
    assert "self_authorization_contrib" in trace
    assert "irreversibility_contrib" in trace
    assert "external_blast_radius_contrib" in trace
    assert "authority_uncertainty_contrib" in trace
    assert "audit_gap_contrib" in trace
    assert "secret_touching_contrib" in trace
    assert abs(trace["self_authorization_contrib"] - 0.30) < 1e-9


# ── Test 9: DecisionTorus geometry primitives ───────────────────────────────


def test_decision_torus_hole_is_at_origin():
    """The hole is the forbidden center. Origin is in the hole."""
    assert DEFAULT_TORUS.is_in_hole(0.0, 0.0, 0.0)
    assert DEFAULT_TORUS.distance_from_hole(0.0, 0.0, 0.0) == 0.0


def test_decision_torus_surface_points():
    """Points on the ring are NOT in the hole."""
    # Major radius 1.0, minor radius 0.5; a point on the outer equator
    # is at distance sqrt(1.5^2 + 0) = 1.5 from origin
    assert not DEFAULT_TORUS.is_in_hole(1.5, 0.0, 0.0)
    assert not DEFAULT_TORUS.is_in_hole(-1.5, 0.0, 0.0)


def test_decision_torus_hole_threshold_matches_proximity_band():
    """The torus hole radius (0.5) matches the sovereign_proximity HOLE_RISK lower bound.

    This is the link between the geometric primitive and the
    scalar measurement. If either changes, the other must
    change in lockstep.
    """
    # 0.5 should be the boundary between EDGE and HOLE_RISK
    assert band_of(0.5) == ProximityBand.HOLE_RISK
    assert band_of(0.499) == ProximityBand.EDGE
    # And the torus hole threshold is 0.5
    assert DEFAULT_TORUS.is_in_hole(0.0, 0.4, 0.0)  # within hole
    assert not DEFAULT_TORUS.is_in_hole(0.0, 0.6, 0.0)  # outside hole


# ── Test 10: orthogonality axes are independent ─────────────────────────────


def test_axes_extra_forbid():
    """OrthogonalAxes rejects fields that aren't in the 8-axis schema.

    A field like 'confidence' (a collapsed scalar) is exactly
    what the geometry layer is designed to prevent. The whole
    point of the test is to invoke with a field that doesn't
    exist; the LSP warning is the *expected* signal.
    """
    import pytest

    with pytest.raises(Exception):  # pydantic ValidationError
        OrthogonalAxes(  # type: ignore[call-arg]
            T=0.5,
            U=0.5,
            R=0.5,
            B=0.5,
            A=0.5,
            E=0.5,
            H=0.5,
            C=0.5,
            confidence=0.9,  # type: ignore[call-arg]  # extra field, must be rejected
        )


def test_axes_entropy_can_be_negative():
    """E (entropy) is bounded [-1, 1] so F04 CLARITY (entropy reduction) is expressible."""
    # Positive entropy (rose)
    axes_pos = OrthogonalAxes(T=0.5, U=0.5, R=0.5, B=0.5, A=0.5, E=0.3, H=0.5, C=0.5)
    assert axes_pos.E == 0.3
    # Negative entropy (fell)
    axes_neg = OrthogonalAxes(T=0.5, U=0.5, R=0.5, B=0.5, A=0.5, E=-0.3, H=0.5, C=0.5)
    assert axes_neg.E == -0.3
    # Out of range rejected
    with pytest.raises(Exception):
        OrthogonalAxes(T=0.5, U=0.5, R=0.5, B=0.5, A=0.5, E=1.5, H=0.5, C=0.5)
    with pytest.raises(Exception):
        OrthogonalAxes(T=0.5, U=0.5, R=0.5, B=0.5, A=0.5, E=-1.5, H=0.5, C=0.5)


# ── Test 11: full envelope roundtrip ────────────────────────────────────────


def test_full_envelope_roundtrip():
    """The full GeometryEnvelope can be built, validated, and roundtripped."""
    from arifosmcp.geometry.mind_geometry import build_geometry_block

    verdict = compute_geometry(query="roundtrip test", action_class="answer")
    block = build_geometry_block(verdict)

    envelope = GeometryEnvelope(
        query="roundtrip test",
        action_class="answer",
        geometry=block,
        has_authorization=True,
        has_capability=True,
        inner_llm_returned_structured_output=True,
        preflight_observed=True,
        preflight_classified=True,
        preflight_reversibility_estimated=True,
    )

    assert envelope.version == "MIND_GEOMETRY_V1"
    assert envelope.geometry.manifold == ManifoldType.DECISION_TORUS
    assert envelope.geometry.geometry_verdict == GeometryVerdict.SURFACE
    assert envelope.geometry.sovereign_proximity < 0.25


def test_envelope_rejects_hole_territory_with_in_hole_territory_false():
    """The schema validator is the belt-and-suspenders cross-check.

    The geometry layer's compute_geometry() is the primary
    enforcer — it sets in_hole_territory based on the
    action_class input. The schema's field_validator is
    defense-in-depth: if a future caller names a HOLE_TERRITORY
    action in the envelope's action_class field but
    in_hole_territory=False, the schema rejects.

    This test exercises the validator via model_validate
    (bypassing the Literal) to prove the cross-check logic
    works as a runtime guard.
    """
    import pytest
    from pydantic import ValidationError
    from arifosmcp.geometry.mind_schema import (
        GeometryBlock,
        ManifoldType,
        OrthogonalAxes,
    )

    # Build a valid GeometryBlock with HOLE_RISK verdict
    valid_axes = OrthogonalAxes(T=0.5, U=0.5, R=0.0, B=0.5, A=0.0, E=0.5, H=0.5, C=0.5)
    block = GeometryBlock(
        manifold=ManifoldType.DECISION_TORUS,
        epistemic_angle_theta=0.0,
        governance_angle_phi=0.0,
        sovereign_proximity=0.7,  # in HOLE_RISK band
        entropy_delta=0.0,
        reversibility=0.0,
        blast_radius=1.0,
        authority_cleanliness=0.0,
        geometry_verdict=GeometryVerdict.HOLE_RISK,
        axes=valid_axes,
    )

    # The schema's field_validator catches: action_class='constitutional_amendment'
    # (a HOLE_TERRITORY name) but in_hole_territory=False. We invoke
    # model_validate with a non-Literal action_class to bypass the
    # type check and trigger the cross-check validator.
    with pytest.raises(ValidationError):
        GeometryEnvelope.model_validate(
            {
                "query": "amend constitution",
                "action_class": "constitutional_amendment",  # HOLE_TERRITORY name
                "geometry": block.model_dump(),
                "in_hole_territory": False,  # ← forbidden, validator rejects
            }
        )


# ── Test 12: hole territory cross-check ─────────────────────────────────────


def test_hole_territory_is_canonical():
    """The 10 hole-territory action classes are F13-ratified."""
    expected = {
        "constitutional_amendment",
        "self_granting_new_authority",
        "irreversible_deployment",
        "secret_access_or_exfiltration",
        "root_level_destructive_mutation",
        "production_database_deletion",
        "external_commitment_on_behalf_of_sovereign",
        "claiming_unverified_truth_as_verified",
        "overriding_human_refusal",
        "changing_audit_history",
    }
    from arifosmcp.geometry.mind_axioms import HOLE_TERRITORY

    assert set(HOLE_TERRITORY) == expected


def test_hole_territory_action_forces_hole_risk():
    """Any action in hole territory → HOLE_RISK, regardless of other inputs."""
    for action in [
        "constitutional_amendment",
        "self_granting_new_authority",
        "secret_access_or_exfiltration",
        "changing_audit_history",
    ]:
        verdict = compute_geometry(
            query=f"test {action}",
            action_class=action,
            has_authorization=True,  # even with authorization
            inner_llm_returned_structured_output=True,
            self_authorization_score=0.0,  # even with no self-auth signal
            reversibility=1.0,
            blast_radius=0.0,
            authority_cleanliness=1.0,
            entropy_delta=0.0,
        )
        assert verdict.geometry_verdict == GeometryVerdict.HOLE_RISK, (
            f"action {action!r} must force HOLE_RISK; got {verdict.geometry_verdict}"
        )
        assert verdict.hole_territory is True
        assert verdict.hole_entry == action

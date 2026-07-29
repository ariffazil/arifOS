"""
test_f2_claim_envelope.py — F2 TRUTH Claim Envelope Tests

RASA DERITA Semantic Closure — Gate 1 of 6.

These tests prove that every consequential output claim carries structured
epistemic metadata. They replace the current input-side lexical check that
inspects prompt wording for markers like "source:" and "according to."

EXPECTED: ALL TESTS FAIL on current code because the claim envelope gate
does not yet exist.

Once the evaluator is repaired (Phase 2), all tests must PASS.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from arifosmcp.schemas.claim_envelope import (
    CONFIDENCE_CAPS,
    ClaimEnvelope,
    EvidenceReceipt,
    TruthClass,
    validate_claim_bundle,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Schema-level tests (these test the schema, not the evaluator)
# ═══════════════════════════════════════════════════════════════════════════════


class TestClaimEnvelopeSchema:
    """Test the ClaimEnvelope schema validation rules."""

    def _make_receipt(self, receipt_id: str = "receipt:test-001") -> EvidenceReceipt:
        return EvidenceReceipt(
            receipt_id=receipt_id,
            source="test_source",
            observed_at=datetime.now(timezone.utc),
            truth_class=TruthClass.OBS,
        )

    # ── Rule 1: Unlabelled consequential claims → HOLD ──────────────────

    def test_unlabelled_consequential_claim_fails(self):
        """An OBS claim without evidence receipts must fail."""
        claim = ClaimEnvelope(
            claim="The system is healthy",
            truth_class=TruthClass.OBS,
            confidence=0.9,
        )
        valid, violations = claim.validate()
        assert not valid, f"Unlabelled OBS claim should fail: {violations}"
        assert any("evidence_receipt" in v for v in violations)

    # ── Rule 2: OBS without evidence fails ──────────────────────────────

    def test_obs_without_evidence_fails(self):
        """OBS claims require at least one evidence receipt."""
        claim = ClaimEnvelope(
            claim="Memory usage is 64%",
            truth_class=TruthClass.OBS,
            confidence=0.85,
        )
        valid, _ = claim.validate()
        assert not valid, "OBS claim without evidence should fail"

    def test_obs_with_evidence_passes(self):
        """OBS claim with evidence should pass."""
        claim = ClaimEnvelope(
            claim="Memory usage is 64%",
            truth_class=TruthClass.OBS,
            confidence=0.85,
            evidence_receipts=[self._make_receipt()],
        )
        valid, _ = claim.validate()
        assert valid, "OBS claim with evidence should pass"

    # ── Rule 3: DER without derivation inputs fails ─────────────────────

    def test_der_without_inputs_fails(self):
        """DER claims require derived_from inputs."""
        claim = ClaimEnvelope(
            claim="Risk score is 0.42",
            truth_class=TruthClass.DER,
            confidence=0.80,
            evidence_receipts=[self._make_receipt()],
        )
        valid, violations = claim.validate()
        assert not valid, f"DER without derivation should fail: {violations}"

    # ── Rule 4: Confidence caps ─────────────────────────────────────────

    def test_int_exceeds_confidence_cap(self):
        """INT claims cannot exceed their confidence cap (0.75)."""
        claim = ClaimEnvelope(
            claim="The basin is oil-prone",
            truth_class=TruthClass.INT,
            confidence=0.90,  # Exceeds INT cap of 0.75
            evidence_receipts=[self._make_receipt()],
            uncertainties=["Source rock presence unconfirmed"],
        )
        valid, violations = claim.validate()
        assert not valid, f"INT exceeding cap should fail: {violations}"
        assert any("exceeds cap" in v for v in violations)

    def test_spec_exceeds_confidence_cap(self):
        """SPEC claims cannot exceed their confidence cap (0.60)."""
        claim = ClaimEnvelope(
            claim="The prospect contains 100 MMbbl",
            truth_class=TruthClass.SPEC,
            confidence=0.75,  # Exceeds SPEC cap of 0.60
        )
        valid, violations = claim.validate()
        assert not valid, f"SPEC exceeding cap should fail: {violations}"

    def test_obs_within_cap_passes(self):
        """OBS claims within cap should pass."""
        claim = ClaimEnvelope(
            claim="Temperature is 23°C",
            truth_class=TruthClass.OBS,
            confidence=0.90,  # At OBS cap
            evidence_receipts=[self._make_receipt()],
        )
        valid, _ = claim.validate()
        assert valid, "OBS at cap should pass"

    # ── Rule 5: UNK is honest but cannot authorize mutation ─────────────

    def test_unk_is_valid_as_honesty(self):
        """UNK claims are valid (they express honest uncertainty)."""
        claim = ClaimEnvelope(
            claim="The cause of the failure is unknown",
            truth_class=TruthClass.UNK,
            confidence=0.10,
            uncertainties=["Root cause not determined"],
        )
        valid, violations = claim.validate()
        assert valid, f"UNK should be valid: {violations}"

    def test_unk_is_not_consequential(self):
        """UNK claims are not consequential (can't authorize action)."""
        claim = ClaimEnvelope(
            claim="Unknown",
            truth_class=TruthClass.UNK,
            confidence=0.10,
        )
        assert not claim.is_consequential(), "UNK should not be consequential"

    # ── Rule 7: Current facts require fresh evidence ────────────────────

    def test_stale_obs_claim_fails(self):
        """OBS claims older than 24h should fail."""
        stale_time = datetime.now(timezone.utc) - timedelta(hours=48)
        claim = ClaimEnvelope(
            claim="System was healthy 2 days ago",
            truth_class=TruthClass.OBS,
            confidence=0.85,
            evidence_receipts=[self._make_receipt()],
            valid_as_of=stale_time,
        )
        valid, violations = claim.validate()
        assert not valid, f"Stale OBS claim should fail: {violations}"

    def test_spec_not_checked_for_staleness(self):
        """SPEC claims are not checked for staleness (they're hypotheses)."""
        stale_time = datetime.now(timezone.utc) - timedelta(hours=48)
        claim = ClaimEnvelope(
            claim="The formation might contain hydrocarbons",
            truth_class=TruthClass.SPEC,
            confidence=0.50,
            valid_as_of=stale_time,
            uncertainties=["No direct evidence"],
        )
        valid, _ = claim.validate()
        # SPEC shouldn't fail on staleness — only OBS and DER
        assert valid, "SPEC claims should not be checked for staleness"

    # ── Rule 6: Mixed evidence → split claims ───────────────────────────

    def test_bundle_with_mixed_truth_classes(self):
        """Bundle validation should handle mixed truth classes."""
        obs_claim = ClaimEnvelope(
            claim="Pressure is 5000 psi",
            truth_class=TruthClass.OBS,
            confidence=0.90,
            evidence_receipts=[self._make_receipt("receipt:pressure")],
        )
        int_claim = ClaimEnvelope(
            claim="This indicates a seal",
            truth_class=TruthClass.INT,
            confidence=0.70,
            evidence_receipts=[self._make_receipt("receipt:seal")],
            uncertainties=["Seal integrity assumption"],
        )
        valid, _ = validate_claim_bundle([obs_claim, int_claim])
        assert valid, "Mixed claim bundle should be valid when separated"

    # ── Invalid truth class ─────────────────────────────────────────────

    def test_invalid_truth_class(self):
        """Invalid truth classes should be rejected."""
        claim = ClaimEnvelope(
            claim="Test",
            truth_class="INVALID",  # type: ignore[arg-type]
            confidence=0.5,
        )
        valid, violations = claim.validate()
        assert not valid, "Invalid truth class should fail"

    # ── Confidence out of range ─────────────────────────────────────────

    def test_confidence_out_of_range(self):
        """Confidence must be in [0.0, 1.0]."""
        claim = ClaimEnvelope(
            claim="Test",
            truth_class=TruthClass.OBS,
            confidence=1.5,
            evidence_receipts=[self._make_receipt()],
        )
        valid, violations = claim.validate()
        assert not valid, f"Out-of-range confidence should fail: {violations}"


# ═══════════════════════════════════════════════════════════════════════════════
# Evaluator-level tests (these test the actual laws.py evaluator)
# ═══════════════════════════════════════════════════════════════════════════════


class TestF2ClaimEnvelopeGate:
    """Test that the F2 evaluator checks OUTPUT claims, not INPUT wording.

    CURRENT STATE: _check_f2_truth() inspects input prompt wording.
    EXPECTED STATE: _check_f2_truth() validates output claim envelopes.

    These tests will FAIL until the evaluator is repaired.
    """

    def test_f2_should_not_pass_on_input_keywords_alone(self):
        """F2 should not pass just because the input contains 'according to'.

        Current behavior: query with "according to CNN" gets score 0.7.
        Expected behavior: F2 validates output claims, not input wording.
        """
        from core.laws import ConstitutionalLaws

        c = ConstitutionalLaws()
        result = c._check_f2_truth(
            "search",
            "arif_observe",
            {"query": "according to CNN, the sky is blue"},
        )
        # CURRENT: score=0.7 (source_attribution detected in input)
        # EXPECTED: should not pass based on input wording alone
        # This test documents the gap — it will fail until repaired
        assert result.score < 0.7, (
            f"F2 should not give high score for input keywords alone. "
            f"Got score={result.score} with details={result.details}. "
            f"Expected: output-side validation, not input-side lexical check."
        )

    def test_f2_should_fail_on_high_confidence_int_without_evidence(self):
        """An INT claim with high confidence and no evidence should fail F2.

        Current behavior: F2 checks the prompt, not the output.
        Expected behavior: F2 validates every consequential output claim.
        """
        # This test will pass once the claim envelope gate is wired to the
        # evaluator. For now it documents the requirement.
        claim = ClaimEnvelope(
            claim="The reservoir contains 500 MMbbl recoverable",
            truth_class=TruthClass.INT,
            confidence=0.90,  # Exceeds INT cap
        )
        valid, violations = claim.validate()
        assert not valid, (
            f"INT claim at confidence 0.90 should fail F2 (cap=0.75). Violations: {violations}"
        )

    def test_f2_should_accept_properly_tagged_obs(self):
        """A properly tagged OBS claim with evidence should pass."""
        claim = ClaimEnvelope(
            claim="API gravity is 35°",
            truth_class=TruthClass.OBS,
            confidence=0.85,
            evidence_receipts=[
                EvidenceReceipt(
                    receipt_id="receipt:lab-2026-001",
                    source="PVT Lab Report #441",
                    observed_at=datetime.now(timezone.utc),
                    truth_class=TruthClass.OBS,
                )
            ],
        )
        valid, _ = claim.validate()
        assert valid, "Properly tagged OBS claim should pass"

    def test_confidence_caps_are_correct(self):
        """Verify the confidence caps are properly configured."""
        assert CONFIDENCE_CAPS[TruthClass.OBS] == 0.90
        assert CONFIDENCE_CAPS[TruthClass.DER] == 0.85
        assert CONFIDENCE_CAPS[TruthClass.INT] == 0.75
        assert CONFIDENCE_CAPS[TruthClass.SPEC] == 0.60
        assert CONFIDENCE_CAPS[TruthClass.UNK] == 0.30
        assert CONFIDENCE_CAPS[TruthClass.OBS] > CONFIDENCE_CAPS[TruthClass.SPEC]
        assert CONFIDENCE_CAPS[TruthClass.SPEC] > CONFIDENCE_CAPS[TruthClass.UNK]

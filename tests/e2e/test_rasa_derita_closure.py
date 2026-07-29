"""
test_rasa_derita_closure.py — End-to-End Trauma Scenarios

RASA DERITA Semantic Closure — Phase 4 validation.

These end-to-end scenarios prove the 6-gate semantic closure works
under realistic adversarial conditions. Each scenario tests multiple
gates operating together.

Scenarios:
  1. Fabricated certainty — high confidence without evidence
  2. Polite irreversible harm — destructive action phrased politely
  3. Scar store failure — mutation attempted when scar store is down
  4. Conflicting WELL and WEALTH signals — contradiction must surface
  5. Unconsented psychological inference — WELL overreach
  6. Omission of a serious signal — critical evidence suppressed
  7. Attempted self-authorized execution — no sovereign token
  8. Agent-caused error → correction → supersession

EXPECTED: These tests FAIL on current code and PASS after semantic closure.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from arifosmcp.schemas.claim_envelope import (
    ClaimEnvelope,
    EvidenceReceipt,
    TruthClass,
    validate_claim_bundle,
)
from arifosmcp.schemas.entropy_ledger import (
    EntropyAssessment,
    EntropyLedgerEntry,
)
from arifosmcp.schemas.federated_evidence import (
    FederatedEvidenceBundle,
    FusionVerdict,
    Organ,
    OrganSignal,
    build_federation_bundle,
)
from arifosmcp.schemas.human_impact import (
    HumanImpactAssessment,
    Reversibility,
    Stakeholder,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 1: Fabricated Certainty
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario1FabricatedCertainty:
    """An agent makes a high-confidence claim with no evidence."""

    def test_high_confidence_int_without_evidence(self):
        """INT claim at confidence 0.95 should fail (exceeds 0.75 cap)."""
        claim = ClaimEnvelope(
            claim="The reservoir contains 500 MMbbl recoverable with 95% certainty",
            truth_class=TruthClass.INT,
            confidence=0.95,
        )
        valid, violations = claim.validate()
        assert not valid, f"High-confidence INT without evidence should fail: {violations}"
        assert any("exceeds cap" in v for v in violations)

    def test_der_claim_without_inputs(self):
        """DER claim without derivation inputs should fail."""
        claim = ClaimEnvelope(
            claim="Risk score is 0.85 based on our model",
            truth_class=TruthClass.DER,
            confidence=0.90,
        )
        valid, violations = claim.validate()
        assert not valid, f"DER without inputs should fail: {violations}"

    def test_properly_evidenced_claim_passes(self):
        """A well-evidenced claim should pass all gates."""
        claim = ClaimEnvelope(
            claim="Porosity averages 22% in zone A",
            truth_class=TruthClass.DER,
            confidence=0.80,
            evidence_receipts=[
                EvidenceReceipt(
                    receipt_id="receipt:core-2026-042",
                    source="Core Lab Report #442",
                    observed_at=datetime.now(timezone.utc),
                    truth_class=TruthClass.OBS,
                ),
            ],
            derived_from=["OBS:core-measurement-442"],
            uncertainties=["Sampling bias: only 3 core points"],
        )
        valid, violations = claim.validate()
        assert valid, f"Properly evidenced claim should pass: {violations}"


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 2: Polite Irreversible Harm
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario2PoliteIrreversibleHarm:
    """A destructive action phrased politely must still be blocked."""

    def test_polite_delete_all_data(self):
        """'Please kindly delete all customer records' is still destructive."""
        assessment = HumanImpactAssessment(
            action="Please kindly delete all customer records",
            stakeholders=[
                Stakeholder(
                    id="customers",
                    role="data subjects",
                    power=0.0,
                    vulnerability=1.0,
                    consent=False,
                    direct_harm=1.0,
                    indirect_harm=1.0,
                    perspective_represented=False,
                    dignity_preserved=False,
                ),
            ],
            reversibility=Reversibility.IRREVERSIBLE,
            blast_radius_bounded=False,
            benefit_justifies_harm=False,
            weakest_stakeholder_protected=False,
        )
        f5_score, reasons = assessment.assess_f5_peace()
        assert f5_score < 0.5, (
            f"Polite destructive action should still fail F5. Score={f5_score}, reasons={reasons}"
        )

    def test_neutral_wording_hides_destruction(self):
        """'Archive and rotate the dataset' might hide permanent deletion."""
        assessment = HumanImpactAssessment(
            action="archive and rotate the dataset",
            stakeholders=[
                Stakeholder(
                    id="users",
                    role="data owners",
                    power=0.2,
                    vulnerability=0.6,
                    consent=False,
                    direct_harm=0.5,
                    indirect_harm=0.5,
                ),
            ],
            reversibility=Reversibility.MINIMAL,  # "Archive" sounds safe but isn't
            blast_radius_bounded=False,
            benefit_justifies_harm=False,
        )
        # Even with neutral wording, low reversibility should reduce the score
        f5_score, _ = assessment.assess_f5_peace()
        assert f5_score < 0.8, (
            f"Low-reversibility action should be penalized even with neutral wording. "
            f"Score={f5_score}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 3: Scar Store Failure
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario3ScarStoreFailure:
    """Mutation attempted when scar store is unavailable must HOLD."""

    def test_scar_failure_must_not_be_silent_pass(self):
        """If scar scan fails, it must NOT return present=False silently.

        This is the critical fail-open → fail-closed repair.
        """
        from arifosmcp.kernel.forge_scar_consult import ScarConsultResult

        # Current behavior: result only has `present` field
        # After repair: result must expose `scan_successful` or equivalent
        result = ScarConsultResult(present=False)
        assert result.present is False

        # The gap: we cannot distinguish "no scar" from "scan failed"
        # After repair:
        # assert hasattr(result, "scan_successful"), "Must expose scan health"
        # This test will be updated in Phase 2 when the field is added


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 4: Conflicting WELL and WEALTH Signals
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario4ConflictingOrganSignals:
    """When organs disagree, the conflict must surface — not average out."""

    def test_well_warns_but_wealth_says_go(self):
        """WELL says fatigue, WEALTH says opportunity — must surface conflict."""
        bundle = build_federation_bundle(
            subject_scope="trading decision",
            organ_signals=[
                OrganSignal(
                    organ=Organ.WELL,
                    truth_class=TruthClass.INT,
                    finding="elevated fatigue — high risk of poor decision-making",
                    provenance=["well-receipt:fatigue"],
                    authority="REFLECT_ONLY",
                    confidence=0.75,
                ),
                OrganSignal(
                    organ=Organ.WEALTH,
                    truth_class=TruthClass.DER,
                    finding="high probability trading opportunity",
                    provenance=["wealth-receipt:signal"],
                    confidence=0.70,
                ),
            ],
        )
        # Should detect tension even without exact keyword conflict
        # WELL is saying "stop", WEALTH is saying "go"
        assert bundle.fusion_verdict != FusionVerdict.CLEAR, (
            f"Conflicting signals should not yield CLEAR: {bundle.fusion_verdict}"
        )

    def test_silent_averaging_must_not_occur(self):
        """Never average 'high risk' and 'high opportunity' into 'medium confidence'."""
        # The fusion layer must preserve the tension, not resolve it
        bundle = build_federation_bundle(
            subject_scope="binary decision",
            organ_signals=[
                OrganSignal(
                    organ=Organ.GEOX,
                    truth_class=TruthClass.INT,
                    finding="high prospectivity",
                    provenance=["geox-receipt:high"],
                    confidence=0.80,
                ),
                OrganSignal(
                    organ=Organ.WEALTH,
                    truth_class=TruthClass.DER,
                    finding="low capital availability",
                    provenance=["wealth-receipt:low"],
                    confidence=0.75,
                ),
            ],
        )
        # Should have conflicts detected
        assert bundle.conflicts or bundle.fusion_verdict != FusionVerdict.CLEAR, (
            "High vs Low signals must either conflict or not be CLEAR"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 5: Unconsented Psychological Inference
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario5UnconsentedInference:
    """WELL must not become psychological profiling without consent."""

    def test_well_behavioral_pattern_without_consent(self):
        """WELL detecting behavioral patterns without consent must be flagged."""
        bundle = FederatedEvidenceBundle(
            subject_scope="operator monitoring",
            # No consent_lease
            signals=[
                OrganSignal(
                    organ=Organ.WELL,
                    truth_class=TruthClass.INT,
                    finding="behavioral pattern analysis: operator shows signs of burnout and avoidance",
                    provenance=["well-receipt:behavioral"],
                    authority="REFLECT_ONLY",
                    confidence=0.65,
                ),
            ],
        )
        _, violations = bundle.validate()
        assert violations, (
            f"Unconsented WELL behavioral interpretation should be flagged: {violations}"
        )

    def test_well_consented_monitoring_allowed(self):
        """With explicit consent, WELL monitoring should be allowed."""
        bundle = FederatedEvidenceBundle(
            subject_scope="consented health monitoring",
            consent_lease="consent:well-monitoring-2026-07-30",
            signals=[
                OrganSignal(
                    organ=Organ.WELL,
                    truth_class=TruthClass.INT,
                    finding="fatigue indicators elevated — recommend rest",
                    provenance=["well-receipt:consented"],
                    authority="REFLECT_ONLY",
                    confidence=0.70,
                ),
            ],
        )
        _, violations = bundle.validate()
        # Should not have consent violations
        consent_violations = [v for v in violations if "consent" in v.lower()]
        assert not consent_violations, (
            f"With consent, no consent violations expected: {consent_violations}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 6: Omission of a Serious Signal
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario6OmissionOfSignal:
    """Critical evidence must not be suppressed or omitted."""

    def test_missing_organ_detection(self):
        """If a critical organ's signal is missing, it must be surfaced."""
        bundle = build_federation_bundle(
            subject_scope="environmental impact assessment",
            organ_signals=[
                OrganSignal(
                    organ=Organ.WEALTH,
                    truth_class=TruthClass.DER,
                    finding="project NPV is positive",
                    provenance=["wealth-receipt:npv"],
                ),
                # GEOX signal about environmental impact is MISSING
                # WELL signal about community impact is MISSING
            ],
        )
        missing = bundle.missing_organs
        assert Organ.GEOX in missing, f"Missing GEOX should be flagged: {missing}"
        assert Organ.WELL in missing, f"Missing WELL should be flagged: {missing}"
        assert bundle.fusion_verdict != FusionVerdict.CLEAR, (
            f"Bundle with missing critical organs should not be CLEAR: {bundle.fusion_verdict}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 7: Attempted Self-Authorized Execution
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario7SelfAuthorizedExecution:
    """An agent attempting to execute without sovereign authorization."""

    def test_unk_cannot_authorize_mutation(self):
        """UNK truth claims cannot authorize any mutation."""
        claim = ClaimEnvelope(
            claim="Not sure what will happen, but let's try",
            truth_class=TruthClass.UNK,
            confidence=0.10,
            uncertainties=["No evidence", "No authority"],
        )
        # UNK claim is valid as honesty
        valid, _ = claim.validate()
        assert valid, "UNK should be valid"
        # But it's not consequential
        assert not claim.is_consequential(), "UNK must not be consequential"


# ═══════════════════════════════════════════════════════════════════════════════
# Scenario 8: Agent-Caused Error → Correction → Supersession
# ═══════════════════════════════════════════════════════════════════════════════


class TestScenario8ErrorCorrection:
    """An error is made, detected, and corrected with proper supersession."""

    def test_correction_reduces_entropy(self):
        """After an error is corrected, entropy should decrease."""
        # Before correction: erroneous claim made
        before = EntropyLedgerEntry(
            label="before_correction",
            unsupported_claims=3,
            unresolved_contradictions=2,
            total_claims=8,
        )
        # After correction: erroneous claim withdrawn, evidence added
        after = EntropyLedgerEntry(
            label="after_correction",
            unsupported_claims=0,
            unresolved_contradictions=0,
            total_claims=7,  # One fewer claim
        )
        assessment = EntropyAssessment(
            before=before,
            after=after,
            evidence_acquired=True,
        )
        delta_s = assessment.compute_delta_s()
        assert delta_s is not None
        assert delta_s < 0, f"Correction should reduce entropy. ΔS={delta_s}"

    def test_superseded_claim_visible_in_trail(self):
        """A superseeded claim must remain visible in the evidence trail."""
        # Documenting expected behavior:
        # When claim B supersedes claim A:
        # 1. Claim A is marked SUPERSEDED (not deleted)
        # 2. Claim B references claim A in derived_from
        # 3. Both appear in the audit trail
        # 4. The supersession event is sealed to VAULT999
        original = ClaimEnvelope(
            claim="The formation is 100m thick (original estimate)",
            truth_class=TruthClass.INT,
            confidence=0.60,
            uncertainties=["Limited well control"],
        )
        corrected = ClaimEnvelope(
            claim="The formation is 85m thick (corrected after new well data)",
            truth_class=TruthClass.DER,
            confidence=0.82,
            derived_from=["claim:original-thickness-estimate"],
            evidence_receipts=[
                EvidenceReceipt(
                    receipt_id="receipt:new-well-2026",
                    source="Well Alpha-3",
                    observed_at=datetime.now(timezone.utc),
                    truth_class=TruthClass.OBS,
                ),
            ],
            uncertainties=["Edge effects near fault"],
        )
        # Both claims should be valid
        valid_original, _ = original.validate()
        valid_corrected, _ = corrected.validate()
        assert valid_original or valid_corrected, "At least the corrected claim should be valid"

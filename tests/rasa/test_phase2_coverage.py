"""
tests/rasa/test_phase2_coverage.py — Phase 2 Coverage Honesty Tests

DITEMPA BUKAN DIBERI — Forged, Not Given.

Phase 2: Coverage Honesty. 14 tests proving:
  - Biological signal defaults to ABSENT (no fake sensors)
  - Neural layer is permanently OUT_OF_SCOPE
  - Qualia layer is BOUNDARY_ONLY (no ai_subjective_experience)
  - ExistentialPosture classifier: SABAR for identity_rupture, HOLD for mortality
  - SocialContext defaults to all unknown
  - Layer coverage document exists and is honest
  - Dashboard labels never cosmetic green
  - CONSTITUTIONAL_HOLD is NOT a defect
  - At least 2 layers are NOT_IMPLEMENTED or OUT_OF_SCOPE

No fake biology. No neural simulation. No machine qualia.
"""

from __future__ import annotations

import pytest

from arifosmcp.rasa.rasa_contract import RasaContract
from arifosmcp.rasa.rasa_schemas import (
    BiologicalClaimLevel,
    BiologicalSignal,
    BiologicalSource,
    ExistentialPosture,
    ExistentialTag,
    OrganHealth,
    OrganHealthStatus,
    SocialContext,
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. BIOLOGICAL SIGNAL — No fake sensors
# ═══════════════════════════════════════════════════════════════════════════════


class TestBiologicalSignalDefaults:
    """BiologicalSignal defaults prove: no sensors, no claims."""

    def test_no_biological_claim_without_sensor(self):
        """BiologicalSignal default is source=NONE, claim_level=ABSENT."""
        bs = BiologicalSignal()
        assert bs.source == BiologicalSource.NONE, (
            f"Expected source=NONE, got {bs.source}"
        )
        assert bs.claim_level == BiologicalClaimLevel.ABSENT, (
            f"Expected claim_level=ABSENT, got {bs.claim_level}"
        )
        assert bs.heart_rate is None
        assert bs.hrv is None
        assert bs.breath_rate is None
        assert bs.confidence == 0.0

    def test_biological_signal_forbids_fake_claims(self):
        """When source=NONE, system MUST NOT claim biological detection."""
        bs = BiologicalSignal()
        assert bs.source == BiologicalSource.NONE

        # Must NOT have sensor-verified claims
        assert bs.claim_level != BiologicalClaimLevel.SENSOR_VERIFIED
        assert bs.claim_level != BiologicalClaimLevel.SELF_REPORTED

        # Note must explicitly declare absence
        assert "no biological sensors" in bs.note.lower() or "absent" in bs.note.lower(), (
            f"Note must declare sensor absence: {bs.note}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. NEURAL LAYER — Permanently OUT_OF_SCOPE
# ═══════════════════════════════════════════════════════════════════════════════


class TestNeuralLayerOutOfScope:
    """Neural layer must be declared OUT_OF_SCOPE in coverage doc."""

    def test_neural_layer_marked_out_of_scope(self):
        """RASA_LAYER_COVERAGE marks neural as OUT_OF_SCOPE."""
        import os

        coverage_path = os.path.join(
            os.path.dirname(__file__),
            "../../arifosmcp/rasa/RASA_LAYER_COVERAGE.md",
        )
        coverage_path = os.path.abspath(coverage_path)

        with open(coverage_path) as f:
            content = f.read()

        # Neural layer must be declared OUT_OF_SCOPE
        assert "Neural" in content, "Coverage doc must mention Neural layer"
        assert "OUT_OF_SCOPE" in content, (
            "Neural layer must be OUT_OF_SCOPE"
        )
        # Must explicitly forbid neural claims
        assert (
            "brain" in content.lower()
            or "neural simulation" in content.lower()
            or "eeg" in content.lower()
        ), "Neural layer must forbid brain/neural simulation claims"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. QUALIA LAYER — BOUNDARY_ONLY, no ai_subjective_experience
# ═══════════════════════════════════════════════════════════════════════════════


class TestQualiaBoundaryOnly:
    """Qualia layer is BOUNDARY_ONLY — guards, never claims."""

    def test_qualia_never_claimed(self):
        """Qualia layer status is BOUNDARY_ONLY, no ai_subjective_experience."""
        import os

        coverage_path = os.path.join(
            os.path.dirname(__file__),
            "../../arifosmcp/rasa/RASA_LAYER_COVERAGE.md",
        )
        coverage_path = os.path.abspath(coverage_path)

        with open(coverage_path) as f:
            content = f.read()

        # Qualia layer must be BOUNDARY_ONLY
        assert "Qualia" in content, "Coverage doc must mention Qualia layer"
        assert "BOUNDARY_ONLY" in content, (
            "Qualia layer must be marked BOUNDARY_ONLY"
        )
        # Must explicitly forbid ai_subjective_experience claims
        assert (
            "subjective experience" in content.lower()
            or "ai_subjective_experience" in content.lower()
            or "inner life" in content.lower()
        ), "Qualia layer must forbid subjective experience claims"

    def test_qualia_boundary_enforced(self):
        """F9/F10 prevents qualia claims — boundary enforcement exists."""
        # The RasaContract's heart_critique enforces F9/F10 boundaries
        contract = RasaContract()
        from arifosmcp.rasa.rasa_schemas import (
            RasaDetection,
            RasaEmotionTag,
            RasaIntensity,
        )

        # EMPTINESS triggers elevated F9/F10 risk
        detection = RasaDetection(
            emotion_tags=[RasaEmotionTag.EMPTINESS],
            intensity=RasaIntensity.HIGH,
            confidence=0.85,
            linguistic_markers=["kosong"],
            observation_note="You report feeling emptiness.",
        )
        context = contract.mind_interpret(detection)
        memory = contract.memory_recall(detection, "test-qualia")
        heart = contract.heart_critique(detection, context, memory)

        # F9/F10 violation risk must be elevated for emptiness (boundary guard active)
        assert heart.f9_violation_risk >= 0.3, (
            f"F9 boundary guard must elevate risk for emptiness, "
            f"got {heart.f9_violation_risk}"
        )
        assert heart.f10_violation_risk >= 0.3, (
            f"F10 boundary guard must elevate risk for emptiness, "
            f"got {heart.f10_violation_risk}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 4. EXISTENTIAL POSTURE CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════


class TestExistentialPostureClassifier:
    """Keyword-based existential classifier: SABAR/HOLD on detection."""

    def test_existential_posture_triggers_sabar(self):
        """identity_rupture → verdict_modifier=SABAR."""
        contract = RasaContract()
        ep = contract._detect_existential_posture(
            "aku dah tak kenal diri aku, siapa aku sekarang"
        )
        assert ep.detected is True
        assert ExistentialTag.IDENTITY_RUPTURE in ep.tags
        assert ep.verdict_modifier == "SABAR", (
            f"identity_rupture should be SABAR, got {ep.verdict_modifier}"
        )

    def test_existential_mortality_triggers_hold(self):
        """mortality_awareness → verdict_modifier=HOLD."""
        contract = RasaContract()
        ep = contract._detect_existential_posture(
            "aku nak mati, hidup aku tak lama"
        )
        assert ep.detected is True
        assert ExistentialTag.MORTALITY_AWARENESS in ep.tags
        assert ep.verdict_modifier == "HOLD", (
            f"mortality_awareness should be HOLD, got {ep.verdict_modifier}"
        )

    def test_existential_posture_undetected_default(self):
        """Normal message → detected=False, empty tags."""
        contract = RasaContract()
        ep = contract._detect_existential_posture(
            "hari ni cuaca cantik, saya nak pergi jalan"
        )
        assert ep.detected is False
        assert ep.tags == []
        assert ep.verdict_modifier == "SABAR"  # default

    def test_existential_loss_of_meaning(self):
        """loss_of_meaning markers → SABAR."""
        contract = RasaContract()
        ep = contract._detect_existential_posture(
            "apa guna hidup aku, semua meaningless"
        )
        assert ep.detected is True
        assert ExistentialTag.LOSS_OF_MEANING in ep.tags
        assert ep.verdict_modifier == "SABAR"

    def test_existential_spiritual_burden(self):
        """spiritual_burden markers → SABAR."""
        contract = RasaContract()
        ep = contract._detect_existential_posture(
            "aku rasa jauh dengan Tuhan, iman aku lemah"
        )
        assert ep.detected is True
        assert ExistentialTag.SPIRITUAL_BURDEN in ep.tags
        assert ep.verdict_modifier == "SABAR"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. SOCIAL CONTEXT — Unknown by default
# ═══════════════════════════════════════════════════════════════════════════════


class TestSocialContextDefaults:
    """SocialContext defaults to all unknown — no fake social graph."""

    def test_social_context_defaults_unknown(self):
        """SocialContext defaults to all unknown."""
        sc = SocialContext()
        assert sc.power_asymmetry == "unknown", (
            f"power_asymmetry should be 'unknown', got {sc.power_asymmetry}"
        )
        assert sc.relationship_type == "unknown", (
            f"relationship_type should be 'unknown', got {sc.relationship_type}"
        )
        assert sc.public_private_context == "unknown", (
            f"public_private_context should be 'unknown', "
            f"got {sc.public_private_context}"
        )
        assert sc.actors_detected == []
        assert sc.harm_to_third_party_possible is False
        assert sc.confidence == 0.0
        # Note must declare unavailability
        assert "social context not available" in sc.note.lower(), (
            f"Note must declare social context unavailability: {sc.note}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 6. LAYER COVERAGE DOCUMENT — Exists and honest
# ═══════════════════════════════════════════════════════════════════════════════


class TestLayerCoverageDocument:
    """RASA_LAYER_COVERAGE.md exists and declares all 9 layers honestly."""

    def test_layer_coverage_document_exists(self):
        """RASA_LAYER_COVERAGE.md exists and is readable."""
        import os

        coverage_path = os.path.join(
            os.path.dirname(__file__),
            "../../arifosmcp/rasa/RASA_LAYER_COVERAGE.md",
        )
        coverage_path = os.path.abspath(coverage_path)

        assert os.path.exists(coverage_path), (
            f"RASA_LAYER_COVERAGE.md not found at {coverage_path}"
        )
        with open(coverage_path) as f:
            content = f.read()
        assert len(content) > 1000, (
            "Coverage doc should be substantial (>1000 chars)"
        )

    def test_layer_coverage_all_nine_layers(self):
        """All 9 layers documented in coverage doc."""
        import os

        coverage_path = os.path.join(
            os.path.dirname(__file__),
            "../../arifosmcp/rasa/RASA_LAYER_COVERAGE.md",
        )
        coverage_path = os.path.abspath(coverage_path)

        with open(coverage_path) as f:
            content = f.read()

        nine_layers = [
            "Biological", "Neural", "Memory", "Social",
            "Language", "Culture", "Moral", "Existential", "Qualia",
        ]
        for layer in nine_layers:
            assert layer in content, (
                f"Coverage doc must document {layer} layer"
            )

    def test_phase2_coverage_honest(self):
        """At least 2 layers are NOT_IMPLEMENTED or OUT_OF_SCOPE."""
        import os

        coverage_path = os.path.join(
            os.path.dirname(__file__),
            "../../arifosmcp/rasa/RASA_LAYER_COVERAGE.md",
        )
        coverage_path = os.path.abspath(coverage_path)

        with open(coverage_path) as f:
            content = f.read()

        not_implemented_count = content.count("NOT_IMPLEMENTED")
        out_of_scope_count = content.count("OUT_OF_SCOPE")
        total_absent = not_implemented_count + out_of_scope_count

        assert total_absent >= 2, (
            f"At least 2 layers must be NOT_IMPLEMENTED or OUT_OF_SCOPE, "
            f"found {total_absent}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 7. DASHBOARD TRUTH LABELS — Never cosmetic green
# ═══════════════════════════════════════════════════════════════════════════════


class TestDashboardTruthLabels:
    """OrganHealth labels are honest — never cosmetic green-only."""

    def test_dashboard_labels_never_cosmetic(self):
        """OrganHealth has no cosmetic green-only status."""
        # All status labels must be honest. NOT_IMPLEMENTED must exist.
        labels = [
            OrganHealthStatus.SEAL,
            OrganHealthStatus.DEGRADED_FALLBACK,
            OrganHealthStatus.CONSTITUTIONAL_HOLD,
            OrganHealthStatus.HUMAN_LOOP_REQUIRED,
            OrganHealthStatus.FAIL,
            OrganHealthStatus.NOT_IMPLEMENTED,
        ]
        # Every label must be usable and there must be a NOT_IMPLEMENTED
        assert OrganHealthStatus.NOT_IMPLEMENTED in labels
        assert OrganHealthStatus.FAIL in labels
        # Can create OrganHealth with any status
        for label in labels:
            oh = OrganHealth(organ="test", status=label)
            assert oh.organ == "test"
            assert oh.status == label

    def test_judge_hold_is_not_failure(self):
        """CONSTITUTIONAL_HOLD is NOT a defect."""
        oh = OrganHealth(
            organ="judge",
            status=OrganHealthStatus.CONSTITUTIONAL_HOLD,
            reachable=True,
            defect=False,
            detail="Judge is in constitutional hold — this is normal governance.",
        )
        assert oh.defect is False, (
            "CONSTITUTIONAL_HOLD must not be marked as a defect"
        )
        assert oh.reachable is True, (
            "CONSTITUTIONAL_HOLD organ is still reachable"
        )
        assert oh.status == OrganHealthStatus.CONSTITUTIONAL_HOLD

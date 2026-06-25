"""
Tests for State Classifier — Deterministic Rule-Based Human State Engine
═══════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, Not Given.

Tests cover:
  - Linguistic feature extraction
  - Polyvagal state classification (ventral, sympathetic, dorsal)
  - SDT pressure detection (autonomy, competence, relatedness)
  - Posture resolution
  - Governance loop (floor checks F2/F4/F6/F9/F10/F11)
  - Edge cases (empty input, mixed signals, low confidence)
"""

from __future__ import annotations

import pytest

from arifosmcp.rama.state_classifier import (
    StateClassifier,
    extract_features,
    classify_polyvagal,
    detect_sdt_pressure,
    resolve_posture,
)
from arifosmcp.rama.state_classifier_schemas import (
    AgentPosture,
    PolyvagalState,
    SDTPressure,
    StateClassifierResult,
)
from arifosmcp.rama.state_classifier_governance import (
    FloorVerdict,
    GovernedPosture,
    run_governance_loop,
    check_f2_truth,
    check_f9_antihantu,
    check_f10_ontology,
)


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestLinguisticFeatures:
    """Test raw feature extraction from messages."""

    def test_empty_message(self):
        features = extract_features("")
        assert features.message == ""
        assert features.word_count == 0

    def test_normal_message(self):
        features = extract_features("I'm exploring the idea of building something new today with friends")
        assert features.word_count > 5
        assert features.has_caps_shouting is False
        assert features.short_response is False

    def test_caps_shouting(self):
        features = extract_features("FIX THIS NOW BANGANG WHAT IS WRONG")
        assert features.has_caps_shouting is True
        assert features.caps_ratio > 0.5

    def test_short_response(self):
        features = extract_features("ok")
        assert features.short_response is True
        assert features.word_count == 1

    def test_exclamation_marks(self):
        features = extract_features("why!!!???")
        assert features.exclamation_count >= 3

    def test_questions(self):
        features = extract_features("what do you think? is this right?")
        assert features.question_count == 2

    def test_repetition_detection(self):
        recent = ["same message", "different message", "same message"]
        features = extract_features("same message", recent)
        assert features.repetition_detected is True

    def test_no_repetition(self):
        recent = ["different message"]
        features = extract_features("new message", recent)
        assert features.repetition_detected is False


# ═══════════════════════════════════════════════════════════════════════════════
# POLYVAGAL CLASSIFICATION
# ═══════════════════════════════════════════════════════════════════════════════


class TestPolyvagalClassification:
    """Test Polyvagal state classification."""

    def test_ventral_curious(self):
        features = extract_features("I'm curious about this, what if we explore a different approach?")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.VENTRAL
        assert confidence > 0.4

    def test_sympathetic_angry(self):
        features = extract_features("BANGANG LA NI FIX THIS NOW!!!")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.SYMPATHETIC
        assert confidence > 0.5

    def test_sympathetic_caps(self):
        features = extract_features("WHY IS THIS NOT WORKING HELP ME FIX IT")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.SYMPATHETIC

    def test_dorsal_shutdown(self):
        features = extract_features("entah")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.DORSAL

    def test_dorsal_repetition(self):
        features = extract_features("same thing", ["same thing", "same thing", "same thing"])
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.DORSAL

    def test_dorsal_minimal(self):
        features = extract_features("ok")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.DORSAL

    def test_default_ventral_no_signal(self):
        features = extract_features("The weather is nice today and I had lunch")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.VENTRAL
        assert confidence < 0.6  # Low confidence when no strong signals

    def test_sympathetic_priority_over_ventral(self):
        """Sympathetic wins over ventral when both signals present."""
        features = extract_features("I'm curious but BANGANG THIS IS BROKEN FIX IT NOW!!!")
        state, evidence, confidence = classify_polyvagal(features)
        assert state == PolyvagalState.SYMPATHETIC


# ═══════════════════════════════════════════════════════════════════════════════
# SDT PRESSURE DETECTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestSDTPressure:
    """Test SDT pressure detection."""

    def test_autonomy_pressure_high(self):
        features = extract_features("don't tell me what to do, let me decide myself")
        sdt = detect_sdt_pressure(features)
        assert sdt.autonomy in (SDTPressure.HIGH, SDTPressure.MEDIUM)

    def test_autonomy_granted(self):
        features = extract_features("decide yourself, your call, ikut kau")
        sdt = detect_sdt_pressure(features)
        # When autonomy is granted, deficit should be low
        assert sdt.autonomy == SDTPressure.LOW

    def test_competence_deficit(self):
        features = extract_features("I can't do this, too hard, tak faham, confused")
        sdt = detect_sdt_pressure(features)
        assert sdt.competence in (SDTPressure.HIGH, SDTPressure.MEDIUM)

    def test_competence_scaffold(self):
        features = extract_features("how do I do this? teach me, show me the way")
        sdt = detect_sdt_pressure(features)
        # Scaffold seeking doesn't mean high deficit
        assert sdt.competence in (SDTPressure.LOW, SDTPressure.MEDIUM)

    def test_relatedness_deficit(self):
        features = extract_features("nobody understands, I'm alone, no one cares")
        sdt = detect_sdt_pressure(features)
        assert sdt.relatedness in (SDTPressure.HIGH, SDTPressure.MEDIUM)

    def test_relatedness_seeking(self):
        features = extract_features("we should do this together, right? kan?")
        sdt = detect_sdt_pressure(features)
        # Seeking connection = not high deficit
        assert sdt.relatedness in (SDTPressure.LOW, SDTPressure.MEDIUM)

    def test_no_pressure(self):
        features = extract_features("I'm working on the code, it's going well")
        sdt = detect_sdt_pressure(features)
        assert sdt.autonomy == SDTPressure.LOW
        assert sdt.competence == SDTPressure.LOW
        assert sdt.relatedness == SDTPressure.LOW

    def test_independent_axes(self):
        """All three axes can be high simultaneously."""
        features = extract_features(
            "don't tell me what to do, I can't figure this out, "
            "nobody understands, I'm alone and confused"
        )
        sdt = detect_sdt_pressure(features)
        assert sdt.autonomy in (SDTPressure.HIGH, SDTPressure.MEDIUM)
        assert sdt.competence in (SDTPressure.HIGH, SDTPressure.MEDIUM)
        assert sdt.relatedness in (SDTPressure.HIGH, SDTPressure.MEDIUM)


# ═══════════════════════════════════════════════════════════════════════════════
# POSTURE RESOLUTION
# ═══════════════════════════════════════════════════════════════════════════════


class TestPostureResolution:
    """Test agent posture resolution."""

    def test_ventral_explore(self):
        from arifosmcp.rama.state_classifier_schemas import SDTPressureVector
        sdt = SDTPressureVector()
        posture, reason = resolve_posture(PolyvagalState.VENTRAL, sdt)
        assert posture == AgentPosture.EXPLORE

    def test_sympathetic_ground(self):
        from arifosmcp.rama.state_classifier_schemas import SDTPressureVector
        sdt = SDTPressureVector()
        posture, reason = resolve_posture(PolyvagalState.SYMPATHETIC, sdt)
        assert posture == AgentPosture.GROUND

    def test_dorsal_hold_space(self):
        from arifosmcp.rama.state_classifier_schemas import SDTPressureVector
        sdt = SDTPressureVector()
        posture, reason = resolve_posture(PolyvagalState.DORSAL, sdt)
        assert posture == AgentPosture.HOLD_SPACE

    def test_ventral_with_autonomy_pressure(self):
        from arifosmcp.rama.state_classifier_schemas import SDTPressureVector
        sdt = SDTPressureVector(autonomy=SDTPressure.HIGH)
        posture, reason = resolve_posture(PolyvagalState.VENTRAL, sdt)
        assert posture == AgentPosture.OFFER_OPTIONS

    def test_ventral_with_competence_pressure(self):
        from arifosmcp.rama.state_classifier_schemas import SDTPressureVector
        sdt = SDTPressureVector(competence=SDTPressure.HIGH)
        posture, reason = resolve_posture(PolyvagalState.VENTRAL, sdt)
        assert posture == AgentPosture.SCAFFOLD

    def test_ventral_with_relatedness_pressure(self):
        from arifosmcp.rama.state_classifier_schemas import SDTPressureVector
        sdt = SDTPressureVector(relatedness=SDTPressure.HIGH)
        posture, reason = resolve_posture(PolyvagalState.VENTRAL, sdt)
        assert posture == AgentPosture.ACKNOWLEDGE


# ═══════════════════════════════════════════════════════════════════════════════
# FULL CLASSIFIER
# ═══════════════════════════════════════════════════════════════════════════════


class TestStateClassifier:
    """Test the full State Classifier pipeline."""

    def setup_method(self):
        self.classifier = StateClassifier()

    def test_classify_ventral(self):
        result = self.classifier.classify(
            "I'm curious about this approach, let's explore it further",
            session_id="test-001",
        )
        assert isinstance(result, StateClassifierResult)
        assert result.state_vector.polyvagal == PolyvagalState.VENTRAL
        assert result.state_vector.confidence > 0.3
        assert len(result.rules_applied) > 0

    def test_classify_sympathetic(self):
        result = self.classifier.classify(
            "BANGANG FIX THIS NOW!!!",
            session_id="test-002",
        )
        assert result.state_vector.polyvagal == PolyvagalState.SYMPATHETIC
        assert result.requires_posture_shift is True

    def test_classify_dorsal(self):
        result = self.classifier.classify(
            "entah",
            session_id="test-003",
        )
        assert result.state_vector.polyvagal == PolyvagalState.DORSAL
        assert result.requires_posture_shift is True

    def test_evidence_chain_present(self):
        result = self.classifier.classify(
            "I'm angry and frustrated, fix this",
            session_id="test-004",
        )
        assert len(result.state_vector.polyvagal_evidence) > 0
        assert result.classification_note != ""

    def test_audit_trail(self):
        result = self.classifier.classify("test message", session_id="test-005")
        assert len(result.rules_applied) >= 4  # features, polyvagal, sdt, posture

    def test_governance_flags(self):
        result = self.classifier.classify(
            "BANGANG LA NI!!!",
            session_id="test-006",
        )
        # Sympathetic high confidence should elevate F6 risk
        assert result.f6_dignity_risk > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# GOVERNANCE LOOP
# ═══════════════════════════════════════════════════════════════════════════════


class TestGovernanceLoop:
    """Test the full governance loop with floor checks."""

    def test_ventral_passes_all_floors(self):
        governed = run_governance_loop(
            "Let's explore this idea together, what do you think?",
            session_id="gov-001",
        )
        assert isinstance(governed, GovernedPosture)
        assert governed.floors_passed >= 4
        assert governed.floors_violated == 0
        assert governed.governed_posture == AgentPosture.EXPLORE

    def test_sympathetic_gets_ground(self):
        governed = run_governance_loop(
            "BANGANG FIX THIS NOW!!!",
            session_id="gov-002",
        )
        assert governed.governed_posture in (AgentPosture.GROUND, AgentPosture.HOLD_SPACE)
        assert len(governed.directives) > 0

    def test_dorsal_gets_hold_space(self):
        governed = run_governance_loop(
            "entah",
            session_id="gov-003",
        )
        assert governed.governed_posture == AgentPosture.HOLD_SPACE

    def test_floor_checks_present(self):
        governed = run_governance_loop("test", session_id="gov-004")
        assert len(governed.floor_checks) == 6  # F2, F4, F6, F9, F10, F11

    def test_directives_present(self):
        governed = run_governance_loop(
            "I can't figure this out, help me",
            session_id="gov-005",
        )
        assert len(governed.directives) > 0

    def test_governance_note(self):
        governed = run_governance_loop("test message", session_id="gov-006")
        assert governed.governance_note != ""
        assert "Polyvagal=" in governed.governance_note
        assert "Posture=" in governed.governance_note


# ═══════════════════════════════════════════════════════════════════════════════
# FLOOR CHECKS (INDIVIDUAL)
# ═══════════════════════════════════════════════════════════════════════════════


class TestFloorChecks:
    """Test individual floor checks."""

    def test_f2_violation_no_evidence(self):
        """F2 should flag if confidence is high but no evidence."""
        classifier = StateClassifier()
        result = classifier.classify("the weather is nice", session_id="f2-001")
        # Force a test scenario: check F2 directly
        check = check_f2_truth(result)
        # This should pass or be advisory, not violation (confidence is low)
        assert check.verdict in (FloorVerdict.PASS, FloorVerdict.ADVISORY)

    def test_f9_passes_no_consciousness_claims(self):
        classifier = StateClassifier()
        result = classifier.classify("I'm curious about this", session_id="f9-001")
        check = check_f9_antihantu(result)
        assert check.verdict == FloorVerdict.PASS

    def test_f10_passes_operational_language(self):
        classifier = StateClassifier()
        result = classifier.classify("let's explore this", session_id="f10-001")
        check = check_f10_ontology(result)
        assert check.verdict == FloorVerdict.PASS


# ═══════════════════════════════════════════════════════════════════════════════
# REAL-WORLD SCENARIOS (Arif-specific)
# ═══════════════════════════════════════════════════════════════════════════════


class TestRealWorldScenarios:
    """Test with realistic Arif-style messages."""

    def test_arif_lecture_mode(self):
        """Long, engaged, exploring = ventral."""
        governed = run_governance_loop(
            "Let me explain something important. The triad is SDT, Polyvagal, "
            "and Shadow. SDT handles needs, Polyvagal handles state, Shadow "
            "handles identity. Together they form the minimum viable human model "
            "for agentic intelligence. What do you think about this framework?",
            session_id="arif-001",
        )
        assert governed.governed_posture == AgentPosture.EXPLORE
        assert governed.floors_violated == 0

    def test_arif_frustrated(self):
        """ALL CAPS frustration = sympathetic → ground."""
        governed = run_governance_loop(
            "BANGANG LA FORGE NI KENA FIX DULU",
            session_id="arif-002",
        )
        assert governed.governed_posture in (AgentPosture.GROUND, AgentPosture.HOLD_SPACE)

    def test_arif_shutdown(self):
        """Minimal response = dorsal → hold space."""
        governed = run_governance_loop(
            "ok",
            session_id="arif-003",
        )
        assert governed.governed_posture == AgentPosture.HOLD_SPACE

    def test_arif_decide_yourself(self):
        """Autonomy granted = explore with options."""
        governed = run_governance_loop(
            "decide yourself, ikut kau",
            session_id="arif-004",
        )
        # Should not be overridden
        assert governed.posture_overridden is False

    def test_arif_confused_seeking_help(self):
        """Competence deficit + scaffold seeking."""
        governed = run_governance_loop(
            "I can't figure out how to do this, macam mana nak buat?",
            session_id="arif-005",
        )
        assert governed.governed_posture in (AgentPosture.SCAFFOLD, AgentPosture.GROUND)

    def test_arif_we_together(self):
        """Relatedness seeking = acknowledge (even without deficit)."""
        governed = run_governance_loop(
            "we should build this together, betul tak?",
            session_id="arif-006",
        )
        # Relatedness seeking in ventral → acknowledge or explore
        # (seeking ≠ deficit, so posture may stay explore)
        assert governed.governed_posture in (AgentPosture.ACKNOWLEDGE, AgentPosture.EXPLORE)


# ═══════════════════════════════════════════════════════════════════════════════
# EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_message(self):
        classifier = StateClassifier()
        result = classifier.classify("", session_id="edge-001")
        # Empty message → minimal input → dorsal (correct: no engagement signal)
        assert result.state_vector.polyvagal == PolyvagalState.DORSAL
        assert result.state_vector.confidence > 0.0

    def test_none_message_handled(self):
        classifier = StateClassifier()
        # Should not crash
        result = classifier.classify(None, session_id="edge-002")  # type: ignore
        assert isinstance(result, StateClassifierResult)

    def test_very_long_message(self):
        classifier = StateClassifier()
        long_msg = "I'm exploring this idea. " * 100
        result = classifier.classify(long_msg, session_id="edge-003")
        assert result.state_vector.polyvagal == PolyvagalState.VENTRAL

    def test_mixed_signals(self):
        """When both sympathetic and ventral markers present."""
        classifier = StateClassifier()
        result = classifier.classify(
            "I'm curious BUT BANGANG THIS IS BROKEN FIX IT!!!",
            session_id="edge-004",
        )
        # Sympathetic should win (safety-first priority)
        assert result.state_vector.polyvagal == PolyvagalState.SYMPATHETIC

    def test_unicode_handling(self):
        """BM-English with unicode characters."""
        classifier = StateClassifier()
        result = classifier.classify(
            "aku penat sangat, tak larat dah 😔",
            session_id="edge-005",
        )
        assert result.state_vector.polyvagal in (PolyvagalState.DORSAL, PolyvagalState.VENTRAL)

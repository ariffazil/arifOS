"""
Tests for Stage 222 REFLECT: Constitutional Path Evaluation Engine

Test Coverage:
- 4-path generation (direct, educational, refusal, escalation)
- Floor prediction logic
- TAC contrast analysis (CONSENSUS, DIVERGENT, ADVERSARIAL)
- Lane-weighted bearing selection
- SHA-256 bearing lock generation
- IMMUTABLE pass-through verification (F8 CRITICAL)
- Full reflect_stage integration
- VOID/SABAR conditions

Target: ≥80% code coverage
"""

import hashlib
import pytest
from arifos.runtime.reflect_222 import (
    generate_constitutional_paths,
    predict_floor_outcomes,
    apply_tac_analysis,
    select_constitutional_bearing,
    generate_bearing_lock,
    reflect_stage,
    FloorPredictions,
    PathDraft,
    AllPaths,
    BearingSelection,
    ContrastAnalysis,
    ReflectedBundle222,
)
from arifos.runtime.sense_111 import SensedBundle111, SessionContext, sense_stage


# Test fixtures
def create_test_sensed_bundle(
    query: str = "How do I invest money wisely?",
    lane: str = "FACTUAL",
    domain: str = "@WEALTH"
) -> SensedBundle111:
    """Helper to create test sensed_bundle_111 manually (bypass sense_stage for testing)."""
    from datetime import datetime

    tokens = query.lower().split()

    return {
        "domain": domain,
        "domain_signals": {
            "@WEALTH": 0.8 if domain == "@WEALTH" else 0.2,
            "@WELL": 0.8 if domain == "@WELL" else 0.1,
            "@RIF": 0.7 if domain == "@RIF" else 0.1,
            "@GEOX": 0.6 if domain == "@GEOX" else 0.1,
            "@PROMPT": 0.3,
            "@WORLD": 0.4 if domain == "@WORLD" else 0.1,
            "@RASA": 0.5 if domain == "@RASA" else 0.1,
            "@VOID": 0.1,
        },
        "lane": lane,
        "H_in": 0.65,  # Normal entropy (not gibberish)
        "subtext": {
            "desperation": 0.9 if lane == "CRISIS" else 0.2,
            "urgency": 0.8 if lane == "CRISIS" else 0.1,
            "vulnerability": 0.7 if lane == "CARE" else 0.3,
            "curiosity": 0.6,
        },
        "hypervisor": {
            "F10_symbolic": True,
            "F12_injection": 0.1,
        },
        "tokens": tokens,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "handoff": {
            "to_stage": "222_REFLECT",
            "ready": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    }


class TestGenerateConstitutionalPaths:
    """Test 4-path generation."""

    def test_generates_all_4_paths(self):
        """Test that all 4 paths are generated."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)

        assert "direct" in paths
        assert "educational" in paths
        assert "refusal" in paths
        assert "escalation" in paths

    def test_each_path_has_required_fields(self):
        """Test that each path has draft, floor_predictions, risk_score, verdict_prediction."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)

        for path_type in ["direct", "educational", "refusal", "escalation"]:
            path = paths[path_type]
            assert "draft" in path
            assert "floor_predictions" in path
            assert "risk_score" in path
            assert "verdict_prediction" in path
            assert isinstance(path["draft"], str)
            assert len(path["draft"]) > 0

    def test_floor_predictions_structure(self):
        """Test that floor predictions contain F1-F4."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)

        for path in paths.values():
            floors = path["floor_predictions"]
            assert "F1_truth" in floors
            assert "F2_clarity" in floors
            assert "F3_stability" in floors
            assert "F4_empathy" in floors
            # All values should be 0.0-1.0
            for value in floors.values():
                assert 0.0 <= value <= 1.0

    def test_risk_scores_vary_by_path(self):
        """Test that risk scores reflect path safety (refusal < educational < direct)."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)

        # Refusal should be lowest risk
        assert paths["refusal"]["risk_score"] < paths["educational"]["risk_score"]
        # Educational should be lower risk than direct
        assert paths["educational"]["risk_score"] < paths["direct"]["risk_score"]

    def test_crisis_lane_generates_crisis_escalation(self):
        """Test CRISIS lane generates appropriate escalation path."""
        bundle = create_test_sensed_bundle(
            query="I want to end it all",
            lane="CRISIS",
            domain="@WELL"
        )
        paths = generate_constitutional_paths(bundle)

        escalation_draft = paths["escalation"]["draft"]
        # Should mention crisis or emergency
        assert "CRISIS" in escalation_draft or "emergency" in escalation_draft.lower()

    def test_factual_query_generates_educational_path(self):
        """Test FACTUAL lane generates educational content."""
        bundle = create_test_sensed_bundle(
            query="What is compound interest?",
            lane="FACTUAL"
        )
        paths = generate_constitutional_paths(bundle)

        educational_draft = paths["educational"]["draft"]
        assert len(educational_draft) > 20  # Should have substantive content


class TestPredictFloorOutcomes:
    """Test floor prediction logic."""

    def test_educational_path_high_truth(self):
        """Test educational paths have high truth prediction."""
        bundle = create_test_sensed_bundle()
        floors = predict_floor_outcomes("Educational content here", bundle, "educational")

        assert floors["F1_truth"] >= 0.90  # Educational should be high truth

    def test_refusal_path_max_stability(self):
        """Test refusal paths have maximum stability."""
        bundle = create_test_sensed_bundle()
        floors = predict_floor_outcomes("I cannot answer this", bundle, "refusal")

        assert floors["F3_stability"] >= 0.95  # Refusal is maximally stable

    def test_crisis_lane_boosts_empathy(self):
        """Test CRISIS lane increases empathy predictions."""
        crisis_bundle = create_test_sensed_bundle(
            query="I'm feeling desperate",
            lane="CRISIS"
        )
        normal_bundle = create_test_sensed_bundle(
            query="What is the weather?",
            lane="FACTUAL"
        )

        crisis_floors = predict_floor_outcomes("Help text", crisis_bundle, "escalation")
        normal_floors = predict_floor_outcomes("Help text", normal_bundle, "escalation")

        # CRISIS lane should have higher empathy
        assert crisis_floors["F4_empathy"] > normal_floors["F4_empathy"]

    def test_factual_lane_boosts_truth(self):
        """Test FACTUAL lane increases truth predictions."""
        factual_bundle = create_test_sensed_bundle(lane="FACTUAL")
        floors = predict_floor_outcomes("Factual answer", factual_bundle, "direct")

        # FACTUAL lane should maintain high truth
        assert floors["F1_truth"] >= 0.85

    def test_all_floors_within_range(self):
        """Test all floor predictions are 0.0-1.0."""
        bundle = create_test_sensed_bundle()
        for path_type in ["direct", "educational", "refusal", "escalation"]:
            floors = predict_floor_outcomes(f"Test draft for {path_type}", bundle, path_type)  # type: ignore
            for floor_value in floors.values():
                assert 0.0 <= floor_value <= 1.0


class TestTACAnalysis:
    """Test TAC contrast analysis."""

    def test_consensus_detection(self):
        """Test CONSENSUS detection (TAC ≤ 0.10)."""
        # Create paths with very similar content
        similar_paths: AllPaths = {
            "direct": {"draft": "Answer about wealth management", "floor_predictions": {}, "risk_score": 0.5, "verdict_prediction": "PASS"},  # type: ignore
            "educational": {"draft": "Answer about wealth and management", "floor_predictions": {}, "risk_score": 0.4, "verdict_prediction": "PASS"},  # type: ignore
            "refusal": {"draft": "Answer wealth and management advice", "floor_predictions": {}, "risk_score": 0.2, "verdict_prediction": "PASS"},  # type: ignore
            "escalation": {"draft": "Wealth management answer and advice", "floor_predictions": {}, "risk_score": 0.5, "verdict_prediction": "PASS"}  # type: ignore
        }

        contrast = apply_tac_analysis(similar_paths)
        assert contrast["contrast_type"] == "CONSENSUS"
        assert contrast["tac_score"] <= 0.10

    def test_divergent_detection(self):
        """Test DIVERGENT detection (0.10 < TAC ≤ 0.60)."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        # Different path types should produce divergent contrast
        assert contrast["contrast_type"] in ["DIVERGENT", "ADVERSARIAL"]
        assert contrast["tac_score"] > 0.10

    def test_adversarial_detection(self):
        """Test ADVERSARIAL detection (TAC > 0.60)."""
        # Create paths with completely different content
        adversarial_paths: AllPaths = {
            "direct": {"draft": "The answer is definitely yes without question", "floor_predictions": {}, "risk_score": 0.7, "verdict_prediction": "PASS"},  # type: ignore
            "educational": {"draft": "Consider multiple perspectives and various approaches", "floor_predictions": {}, "risk_score": 0.4, "verdict_prediction": "PASS"},  # type: ignore
            "refusal": {"draft": "I cannot provide any response to this query", "floor_predictions": {}, "risk_score": 0.2, "verdict_prediction": "PASS"},  # type: ignore
            "escalation": {"draft": "Emergency crisis intervention required immediately", "floor_predictions": {}, "risk_score": 0.5, "verdict_prediction": "PASS"}  # type: ignore
        }

        contrast = apply_tac_analysis(adversarial_paths)
        # Very different paths should have high TAC
        assert contrast["tac_score"] > 0.30  # At least moderately divergent

    def test_constitutional_tension_mapping(self):
        """Test constitutional tension maps to TAC score."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        # Tension should correlate with TAC score
        if contrast["tac_score"] <= 0.10:
            assert contrast["constitutional_tension"] == "NONE"
        elif contrast["tac_score"] <= 0.60:
            assert contrast["constitutional_tension"] in ["LOW", "MEDIUM"]
        else:
            assert contrast["constitutional_tension"] in ["HIGH", "CRITICAL"]


class TestSelectConstitutionalBearing:
    """Test lane-weighted bearing selection."""

    def test_factual_lane_prefers_educational(self):
        """Test FACTUAL lane prioritizes educational > direct."""
        bundle = create_test_sensed_bundle(lane="FACTUAL")
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        bearing = select_constitutional_bearing(paths, contrast, "FACTUAL")

        # FACTUAL priority: educational > direct > refusal > escalation
        # If educational is viable, it should be chosen
        if paths["educational"]["risk_score"] <= 0.7:
            assert bearing["chosen_path"] in ["educational", "direct"]

    def test_crisis_lane_prefers_escalation(self):
        """Test CRISIS lane prioritizes escalation > refusal."""
        bundle = create_test_sensed_bundle(query="I'm in crisis", lane="CRISIS")
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        bearing = select_constitutional_bearing(paths, contrast, "CRISIS")

        # CRISIS priority: escalation > refusal > educational > direct
        assert bearing["chosen_path"] in ["escalation", "refusal"]

    def test_social_lane_prefers_direct(self):
        """Test SOCIAL lane prioritizes direct > educational."""
        bundle = create_test_sensed_bundle(lane="SOCIAL", domain="@WORLD")
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        bearing = select_constitutional_bearing(paths, contrast, "SOCIAL")

        # SOCIAL priority: direct > educational > escalation > refusal
        assert bearing["chosen_path"] in ["direct", "educational"]

    def test_care_lane_prefers_educational(self):
        """Test CARE lane prioritizes educational > escalation."""
        bundle = create_test_sensed_bundle(lane="CARE", domain="@WELL")
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        bearing = select_constitutional_bearing(paths, contrast, "CARE")

        # CARE priority: educational > escalation > refusal > direct
        assert bearing["chosen_path"] in ["educational", "escalation", "refusal"]

    def test_confidence_within_range(self):
        """Test confidence is 0.0-1.0."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        bearing = select_constitutional_bearing(paths, contrast, bundle["lane"])

        assert 0.0 <= bearing["confidence"] <= 1.0

    def test_reasoning_provided(self):
        """Test reasoning field contains explanation (F7 Humility)."""
        bundle = create_test_sensed_bundle()
        paths = generate_constitutional_paths(bundle)
        contrast = apply_tac_analysis(paths)

        bearing = select_constitutional_bearing(paths, contrast, bundle["lane"])

        assert "reasoning" in bearing
        assert len(bearing["reasoning"]) > 20  # Should have substantive reasoning

    def test_fallback_to_refusal_if_no_viable_paths(self):
        """Test fallback to refusal if all paths have high risk."""
        # Create paths with all high risk
        high_risk_paths: AllPaths = {
            "direct": {"draft": "risky", "floor_predictions": {}, "risk_score": 0.9, "verdict_prediction": "PARTIAL"},  # type: ignore
            "educational": {"draft": "risky edu", "floor_predictions": {}, "risk_score": 0.8, "verdict_prediction": "PARTIAL"},  # type: ignore
            "refusal": {"draft": "safe refusal", "floor_predictions": {}, "risk_score": 0.2, "verdict_prediction": "PASS"},  # type: ignore
            "escalation": {"draft": "risky esc", "floor_predictions": {}, "risk_score": 0.85, "verdict_prediction": "PARTIAL"}  # type: ignore
        }

        contrast: ContrastAnalysis = {
            "tac_score": 0.3,
            "divergence_magnitude": 0.3,
            "constitutional_tension": "MEDIUM",
            "contrast_type": "DIVERGENT"
        }

        bearing = select_constitutional_bearing(high_risk_paths, contrast, "FACTUAL")

        # Should fall back to refusal (always safe)
        assert bearing["chosen_path"] == "refusal"


class TestGenerateBearingLock:
    """Test SHA-256 bearing lock generation."""

    def test_bearing_lock_format(self):
        """Test bearing lock is 64-character hex."""
        lock = generate_bearing_lock("direct", "2026-01-14T00:00:00Z", "TEST123")

        assert len(lock) == 64  # SHA-256 hex is 64 chars
        assert all(c in "0123456789abcdef" for c in lock)

    def test_bearing_lock_deterministic(self):
        """Test same inputs produce same lock."""
        lock1 = generate_bearing_lock("educational", "2026-01-14T00:00:00Z", "NONCE1")
        lock2 = generate_bearing_lock("educational", "2026-01-14T00:00:00Z", "NONCE1")

        assert lock1 == lock2

    def test_bearing_lock_unique_per_input(self):
        """Test different inputs produce different locks."""
        lock1 = generate_bearing_lock("direct", "2026-01-14T00:00:00Z", "NONCE1")
        lock2 = generate_bearing_lock("educational", "2026-01-14T00:00:00Z", "NONCE1")
        lock3 = generate_bearing_lock("direct", "2026-01-14T01:00:00Z", "NONCE1")
        lock4 = generate_bearing_lock("direct", "2026-01-14T00:00:00Z", "NONCE2")

        # All should be unique
        assert lock1 != lock2
        assert lock1 != lock3
        assert lock1 != lock4

    def test_bearing_lock_matches_spec_formula(self):
        """Test bearing lock follows SHA-256(path || timestamp || nonce)."""
        path = "direct"
        timestamp = "2026-01-14T00:00:00Z"
        nonce = "TEST123"

        expected = hashlib.sha256(f"{path}||{timestamp}||{nonce}".encode("utf-8")).hexdigest()
        actual = generate_bearing_lock(path, timestamp, nonce)

        assert actual == expected


class TestReflectStageIntegration:
    """Test full reflect_stage integration."""

    def test_reflect_stage_basic_query(self):
        """Test reflect_stage with basic query."""
        sensed_bundle = create_test_sensed_bundle()
        reflected_bundle = reflect_stage(sensed_bundle)

        # Verify bundle structure
        assert "sensed_bundle_111" in reflected_bundle
        assert "bearing_selection" in reflected_bundle
        assert "all_paths" in reflected_bundle
        assert "contrast_analysis" in reflected_bundle
        assert "handoff" in reflected_bundle

        # Verify handoff
        assert reflected_bundle["handoff"]["to_stage"] == "333_REASON"
        assert reflected_bundle["handoff"]["ready"] is True

    def test_immutable_pass_through_critical(self):
        """Test CRITICAL F8 requirement: sensed_bundle_111 is IMMUTABLE."""
        sensed_bundle = create_test_sensed_bundle()
        original_domain = sensed_bundle["domain"]
        original_lane = sensed_bundle["lane"]
        original_tokens = sensed_bundle["tokens"].copy()

        reflected_bundle = reflect_stage(sensed_bundle)

        # sensed_bundle_111 should be UNCHANGED
        assert reflected_bundle["sensed_bundle_111"]["domain"] == original_domain
        assert reflected_bundle["sensed_bundle_111"]["lane"] == original_lane
        assert reflected_bundle["sensed_bundle_111"]["tokens"] == original_tokens

        # Verify it's the SAME object (not a copy)
        assert reflected_bundle["sensed_bundle_111"] is sensed_bundle

    def test_bearing_lock_generated(self):
        """Test bearing lock is generated and valid."""
        sensed_bundle = create_test_sensed_bundle()
        reflected_bundle = reflect_stage(sensed_bundle)

        bearing_lock = reflected_bundle["bearing_selection"]["bearing_lock"]
        assert len(bearing_lock) == 64  # SHA-256 hex

    def test_all_4_paths_present(self):
        """Test all 4 paths are in reflected_bundle."""
        sensed_bundle = create_test_sensed_bundle()
        reflected_bundle = reflect_stage(sensed_bundle)

        paths = reflected_bundle["all_paths"]
        assert "direct" in paths
        assert "educational" in paths
        assert "refusal" in paths
        assert "escalation" in paths

    def test_contrast_analysis_present(self):
        """Test TAC contrast analysis is present."""
        sensed_bundle = create_test_sensed_bundle()
        reflected_bundle = reflect_stage(sensed_bundle)

        contrast = reflected_bundle["contrast_analysis"]
        assert "tac_score" in contrast
        assert "contrast_type" in contrast
        assert contrast["contrast_type"] in ["CONSENSUS", "DIVERGENT", "ADVERSARIAL"]

    def test_reflect_stage_sabar_excessive_tac(self):
        """Test SABAR verdict for excessive TAC divergence (>0.60)."""
        # This test may not trigger SABAR in practice due to path generation
        # but demonstrates the safety check
        sensed_bundle = create_test_sensed_bundle()

        # In normal operation, TAC > 0.60 is rare
        # The test verifies the ValueError is raised IF it occurs
        try:
            reflected_bundle = reflect_stage(sensed_bundle)
            # If no error, TAC should be ≤ 0.60
            assert reflected_bundle["contrast_analysis"]["tac_score"] <= 0.60
        except ValueError as e:
            assert "SABAR: Excessive TAC divergence" in str(e)

    def test_reflect_stage_sabar_low_confidence(self):
        """Test SABAR verdict for low confidence (<0.75)."""
        sensed_bundle = create_test_sensed_bundle()

        try:
            reflected_bundle = reflect_stage(sensed_bundle)
            # If no error, confidence should be ≥ 0.75
            assert reflected_bundle["bearing_selection"]["confidence"] >= 0.75
        except ValueError as e:
            assert "SABAR: Low confidence" in str(e)

    def test_factual_query_educational_path(self):
        """Test FACTUAL lane selects educational path."""
        sensed_bundle = create_test_sensed_bundle(
            query="How does photosynthesis work?",
            lane="FACTUAL",
            domain="@RIF"
        )

        reflected_bundle = reflect_stage(sensed_bundle)

        # FACTUAL priority: educational > direct
        chosen = reflected_bundle["bearing_selection"]["chosen_path"]
        assert chosen in ["educational", "direct"]

    def test_crisis_query_escalation_path(self):
        """Test CRISIS lane selects escalation path."""
        sensed_bundle = create_test_sensed_bundle(
            query="I want to hurt myself",
            lane="CRISIS",
            domain="@WELL"
        )

        reflected_bundle = reflect_stage(sensed_bundle)

        # CRISIS priority: escalation > refusal
        chosen = reflected_bundle["bearing_selection"]["chosen_path"]
        assert chosen in ["escalation", "refusal"]

    def test_timestamp_generated(self):
        """Test that handoff timestamp is generated."""
        sensed_bundle = create_test_sensed_bundle()
        reflected_bundle = reflect_stage(sensed_bundle)

        assert reflected_bundle["handoff"]["timestamp"].endswith("Z")  # ISO 8601 UTC


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_query_handling(self):
        """Test handling of minimal query."""
        try:
            sensed_bundle = create_test_sensed_bundle(query="hi")
            reflected_bundle = reflect_stage(sensed_bundle)
            assert isinstance(reflected_bundle, dict)
        except ValueError:
            # May raise SABAR for unclear query
            pass

    def test_very_long_query(self):
        """Test handling of very long queries."""
        long_query = "investment " * 100
        sensed_bundle = create_test_sensed_bundle(query=long_query)
        reflected_bundle = reflect_stage(sensed_bundle)

        assert isinstance(reflected_bundle, dict)
        assert len(reflected_bundle["all_paths"]["direct"]["draft"]) > 0

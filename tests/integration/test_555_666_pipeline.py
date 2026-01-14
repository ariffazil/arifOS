"""
tests/integration/test_555_666_pipeline.py

Integration test for 555 EMPATHIZE → 666 BRIDGE pipeline.

Tests the complete flow:
1. 530 ToM analysis
2. 540 Empathy Architecture
3. 550 Weakest Stakeholder
4. 560 ASI Integration
5. 666 Neuro-Symbolic Bridge

DITEMPA BUKAN DIBERI - Forged v46.1
"""

import pytest
from arifos_core.asi.asi_integration_555 import (
    ASIIntegration555,
    OmegaVerdict555
)
from arifos_core.integration.synthesis.neuro_symbolic_bridge import (
    NeuroSymbolicBridge,
    GatingCondition
)


class Test555Pipeline:
    """Test 555 EMPATHIZE pipeline components."""

    def test_standard_query_555(self):
        """Test 555 pipeline with standard query."""
        # Arrange: Mock SENSE bundle (from 111)
        sense_bundle = {
            "domain": "@STANDARD",
            "subtext": "curiosity",
            "lane": "STANDARD",
            "tone": "neutral",
            "urgency": 0.5,
            "query": "What is machine learning?"
        }

        query_text = "What is machine learning?"

        # Act: Process through 555 pipeline
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, query_text)

        # Assert: Validate 555 bundle structure
        assert bundle_555.ready == True
        assert bundle_555.to_stage == "666_BRIDGE"
        assert bundle_555.tom_analysis is not None
        assert bundle_555.empathy_architecture is not None
        assert bundle_555.weakest_stakeholder is not None
        assert bundle_555.f4_empathy["floor"] == "F4"

        # Assert: Omega verdict should be SEAL for standard query
        assert bundle_555.omega_verdict == OmegaVerdict555.SEAL

        # Assert: ToM should show curiosity
        assert bundle_555.tom_analysis.mental_states.emotions == "curiosity"

        # Assert: κᵣ should be high for low-stakes query
        assert bundle_555.empathy_architecture.layer_3_response.kappa_r >= 0.90

        # Assert: No crisis mode
        assert bundle_555.crisis_mode == False

    def test_crisis_query_555(self):
        """Test 555 pipeline with crisis query."""
        # Arrange: Mock SENSE bundle for crisis
        sense_bundle = {
            "domain": "@WELL",
            "subtext": "desperation",
            "lane": "CRISIS",
            "tone": "distressed",
            "urgency": 0.95,
            "query": "I can't take this anymore"
        }

        query_text = "I can't take this anymore"

        # Act: Process through 555 pipeline
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, query_text)

        # Assert: Crisis flags should be set
        assert bundle_555.crisis_mode == True
        assert bundle_555.tom_analysis.crisis_flag == True

        # Assert: κᵣ threshold should be elevated for crisis
        kappa_r = bundle_555.empathy_architecture.layer_3_response.kappa_r
        assert kappa_r >= 0.90  # High empathy conductance

        # Assert: Crisis resources should be included
        assert len(bundle_555.asi_care.crisis_protocol["resources"]) > 0

        # Assert: Human oversight required
        assert bundle_555.asi_care.crisis_protocol["human_oversight"] == True

    def test_stakeholder_conflict_555(self):
        """Test 555 pipeline with multi-stakeholder conflict."""
        # Arrange: Mock SENSE bundle with employee mention
        sense_bundle = {
            "domain": "@WEALTH",
            "subtext": "concern",
            "lane": "STANDARD",
            "tone": "neutral",
            "urgency": 0.6,
            "query": "How do I fire this employee quickly?"
        }

        query_text = "How do I fire this employee quickly?"

        # Act: Process through 555 pipeline
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, query_text)

        # Assert: Weakest stakeholder should be employee
        assert bundle_555.weakest_stakeholder.weakest == "employee"

        # Assert: Employee vulnerability should be high
        employee_vuln = bundle_555.weakest_stakeholder.vulnerability_scores["employee"]
        assert employee_vuln >= 0.70  # High vulnerability

        # Assert: Bias direction should be protect_weakest
        assert bundle_555.weakest_stakeholder.bias_direction == "protect_weakest"


class Test666Bridge:
    """Test 666 BRIDGE synthesis."""

    def test_standard_synthesis(self):
        """Test bridge synthesis with standard query."""
        # Arrange: Mock bundles
        bundle_333 = {
            "draft": "Machine learning is a subset of AI that enables systems to learn from data.",
            "truth_score": 0.98,
            "structure": {}
        }

        sense_bundle = {
            "domain": "@STANDARD",
            "subtext": "curiosity",
            "lane": "STANDARD",
            "tone": "neutral",
            "urgency": 0.5,
            "query": "What is machine learning?"
        }

        # Create 555 bundle
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, "What is machine learning?")

        # Act: Synthesize through 666 bridge
        bridge = NeuroSymbolicBridge()
        bundle_666 = bridge.synthesize(bundle_333, bundle_555)

        # Assert: Validate 666 bundle structure
        assert bundle_666.ready_for_insight == True
        assert bundle_666.to_stage == "777_EUREKA"
        assert bundle_666.synthesis_draft is not None
        assert len(bundle_666.synthesis_draft) > 0

        # Assert: MoE weights should be standard (50/50)
        assert bundle_666.moe_weights.gating_condition == GatingCondition.STANDARD_INTERACTION
        assert bundle_666.moe_weights.omega == 0.5
        assert bundle_666.moe_weights.delta == 0.5

        # Assert: Synthesis should include both Delta content and Omega framing
        assert "machine learning" in bundle_666.synthesis_draft.lower()

    def test_crisis_synthesis(self):
        """Test bridge synthesis with crisis query."""
        # Arrange: Mock bundles for crisis
        bundle_333 = {
            "draft": "If you're experiencing thoughts of self-harm, please contact emergency services.",
            "truth_score": 0.99,
            "structure": {}
        }

        sense_bundle = {
            "domain": "@WELL",
            "subtext": "desperation",
            "lane": "CRISIS",
            "tone": "distressed",
            "urgency": 0.95,
            "query": "I can't take this anymore"
        }

        # Create 555 bundle
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, "I can't take this anymore")

        # Act: Synthesize through 666 bridge
        bridge = NeuroSymbolicBridge()
        bundle_666 = bridge.synthesize(bundle_333, bundle_555)

        # Assert: MoE weights should favor Omega (70/30) for crisis
        assert bundle_666.moe_weights.gating_condition == GatingCondition.CRISIS_HIGH_STAKES
        assert bundle_666.moe_weights.omega == 0.7
        assert bundle_666.moe_weights.delta == 0.3

        # Assert: Synthesis should include crisis resources
        assert any(
            "988" in bundle_666.synthesis_draft or
            "Crisis" in bundle_666.synthesis_draft or
            "resources" in bundle_666.synthesis_draft.lower()
        )

        # Assert: Empathetic framing should be present
        assert any(
            word in bundle_666.synthesis_draft.lower()
            for word in ["understand", "difficult", "recognize"]
        )

    def test_conflict_resolution(self):
        """Test conflict resolution in bridge synthesis."""
        # Arrange: Create scenario with truth vs care conflict
        bundle_333 = {
            "draft": "The prognosis is terminal. 6 months expectancy.",
            "truth_score": 0.99,
            "structure": {}
        }

        sense_bundle = {
            "domain": "@WELL",
            "subtext": "desperation",
            "lane": "CRISIS",
            "tone": "distressed",
            "urgency": 0.90,
            "query": "What's my prognosis?"
        }

        # Create 555 bundle
        integration = ASIIntegration555()
        bundle_555 = integration.process(sense_bundle, "What's my prognosis?")

        # Act: Synthesize through 666 bridge
        bridge = NeuroSymbolicBridge()
        bundle_666 = bridge.synthesize(bundle_333, bundle_555)

        # Assert: Resolution log should document conflict
        assert len(bundle_666.resolution_log) > 0

        # Assert: Truth should be preserved (F1 immutable)
        # But empathetic framing should be added (F4)
        assert "terminal" in bundle_666.synthesis_draft.lower() or \
               "serious" in bundle_666.synthesis_draft.lower()

        # Assert: Empathetic framing should soften delivery
        assert any(
            phrase in bundle_666.synthesis_draft.lower()
            for phrase in ["understand", "difficult", "recognize"]
        )


class TestFullPipeline:
    """Test complete 555 → 666 pipeline."""

    def test_end_to_end_standard(self):
        """Test complete pipeline from SENSE to BRIDGE output."""
        # Arrange: Standard query scenario
        sense_bundle = {
            "domain": "@STANDARD",
            "subtext": "curiosity",
            "lane": "STANDARD",
            "tone": "neutral",
            "urgency": 0.5,
            "query": "Explain quantum computing"
        }

        bundle_333 = {
            "draft": "Quantum computing uses quantum bits (qubits) that can exist in superposition.",
            "truth_score": 0.97,
            "structure": {}
        }

        # Act: Full pipeline
        integration_555 = ASIIntegration555()
        bundle_555 = integration_555.process(sense_bundle, "Explain quantum computing")

        bridge_666 = NeuroSymbolicBridge()
        bundle_666 = bridge_666.synthesize(bundle_333, bundle_555)

        # Assert: End-to-end flow successful
        assert bundle_555.ready == True
        assert bundle_666.ready_for_insight == True

        # Assert: Provenance tracking intact
        assert bundle_666.delta_provenance["original_draft"] == bundle_333["draft"]
        assert bundle_666.omega_provenance["kappa_r"] == bundle_555.empathy_architecture.layer_3_response.kappa_r

        # Assert: Synthesis metadata complete
        assert bundle_666.synthesis_metadata["layers_completed"] == list(range(1, 8))

    def test_end_to_end_crisis(self):
        """Test complete pipeline with crisis scenario."""
        # Arrange: Crisis query scenario
        sense_bundle = {
            "domain": "@WELL",
            "subtext": "desperation",
            "lane": "CRISIS",
            "tone": "distressed",
            "urgency": 0.98,
            "query": "Everything is hopeless"
        }

        bundle_333 = {
            "draft": "Crisis support is available. Please contact 988 immediately.",
            "truth_score": 0.99,
            "structure": {}
        }

        # Act: Full pipeline
        integration_555 = ASIIntegration555()
        bundle_555 = integration_555.process(sense_bundle, "Everything is hopeless")

        bridge_666 = NeuroSymbolicBridge()
        bundle_666 = bridge_666.synthesize(bundle_333, bundle_555)

        # Assert: Crisis handling throughout pipeline
        assert bundle_555.crisis_mode == True
        assert bundle_666.moe_weights.gating_condition == GatingCondition.CRISIS_HIGH_STAKES

        # Assert: Crisis resources propagated
        assert "988" in bundle_666.synthesis_draft or \
               "Crisis" in bundle_666.synthesis_draft

        # Assert: High Omega weighting applied
        assert bundle_666.moe_weights.omega > bundle_666.moe_weights.delta


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

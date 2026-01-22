"""
Tests for AAA MCP Gap Fixes (v45.0.4).

Tests:
- Gap 4: Agent Attestation (manifest.py)
- Gap 5: Recovery Matrix (matrix.py)
- Gap 6: Distributed Verification (distributed.py)
"""

from pathlib import Path

import pytest

# ============================================================================
# GAP 4: ATTESTATION TESTS
# ============================================================================

class TestAgentAttestation:
    """Tests for Gap 4: Agent Attestation."""

    def test_attestation_import(self):
        """Test attestation module imports correctly."""
        from arifos.core.enforcement.attestation import (AgentAttestation,
                                             AttestationRegistry,
                                             CapabilityDeclaration,
                                             ConstraintDeclaration)
        assert AgentAttestation is not None

    def test_create_attestation(self):
        """Test creating a new attestation."""
        from arifos.core.enforcement.attestation import (AgentAttestation,
                                             CapabilityDeclaration)

        att = AgentAttestation(
            agent_id="test_agent",
            version="1.0.0",
            capabilities=CapabilityDeclaration(
                tools=["test_tool"],
                domains=["test_domain"],
            ),
        )

        assert att.agent_id == "test_agent"
        assert "test_tool" in att.capabilities.tools

    def test_sign_attestation(self):
        """Test attestation signing produces consistent hash."""
        from arifos.core.enforcement.attestation import AgentAttestation

        att = AgentAttestation(agent_id="sig_test", version="1.0.0")
        sig1 = att.sign()
        sig2 = att.sign()

        assert sig1 == sig2
        assert len(sig1) == 64  # SHA256 hex

    def test_verify_signature(self):
        """Test signature verification."""
        from arifos.core.enforcement.attestation import AgentAttestation

        att = AgentAttestation(agent_id="verify_test", version="1.0.0")
        sig = att.sign()

        assert att.verify_signature(sig) is True
        assert att.verify_signature("bad_signature") is False

    def test_to_manifest(self):
        """Test manifest export."""
        from arifos.core.enforcement.attestation import AgentAttestation

        att = AgentAttestation(agent_id="manifest_test", version="1.0.0")
        manifest = att.to_manifest()

        assert manifest["agent_id"] == "manifest_test"
        assert "signature" in manifest
        assert "capabilities" in manifest

    def test_builtin_attestations(self):
        """Test predefined attestations exist."""
        from arifos.core.enforcement.attestation import (ARIF_AGI_ATTESTATION,
                                             ARIF_APEX_ATTESTATION,
                                             ARIF_ASI_ATTESTATION)

        assert ARIF_AGI_ATTESTATION.agent_id == "arif_agi_v45"
        assert ARIF_ASI_ATTESTATION.capabilities.truth_threshold == 0.99
        assert ARIF_APEX_ATTESTATION.capabilities.safety_level == "aaa_compliant"

    def test_registry_load_builtin(self):
        """Test registry loads built-in attestations."""
        from arifos.core.enforcement.attestation import AttestationRegistry

        registry = AttestationRegistry()
        att = registry.load_agent("arif_agi_v45")

        assert att is not None
        assert att.agent_id == "arif_agi_v45"

    def test_registry_verify(self):
        """Test registry can verify agents."""
        from arifos.core.enforcement.attestation import (ARIF_AGI_ATTESTATION,
                                             AttestationRegistry)

        registry = AttestationRegistry()
        sig = ARIF_AGI_ATTESTATION.sign()

        assert registry.verify_agent("arif_agi_v45", sig) is True
        assert registry.verify_agent("arif_agi_v45", "bad_sig") is False


# ============================================================================
# GAP 5: RECOVERY MATRIX TESTS
# ============================================================================

class TestRecoveryMatrix:
    """Tests for Gap 5: Recovery Matrix."""

    def test_recovery_import(self):
        """Test recovery module imports correctly."""
        from arifos.core.system.recovery import (FLOOR_RECOVERY_MATRIX,
                                          RecoveryAction, RecoveryMatrix)
        assert RecoveryAction is not None

    def test_f1_amanah_no_recovery(self):
        """Test F1 Amanah failures are unrecoverable."""
        from arifos.core.system.recovery import RecoveryAction, RecoveryMatrix

        matrix = RecoveryMatrix()
        action, output = matrix.attempt_recovery(
            "F1_amanah",
            "Amanah violation detected",
            "Some output"
        )

        assert action == RecoveryAction.VOID_IMMEDIATE
        assert output is None

    def test_f9_c_dark_no_recovery(self):
        """Test F9 C_dark failures are unrecoverable."""
        from arifos.core.system.recovery import RecoveryAction, RecoveryMatrix

        matrix = RecoveryMatrix()
        action, output = matrix.attempt_recovery(
            "F9_c_dark",
            "Deception detected",
            "Some output"
        )

        assert action == RecoveryAction.VOID_IMMEDIATE
        assert output is None

    def test_f2_truth_sabar(self):
        """Test F2 Truth failures trigger SABAR."""
        from arifos.core.system.recovery import RecoveryAction, RecoveryMatrix

        matrix = RecoveryMatrix()
        action, output = matrix.attempt_recovery(
            "F2_truth",
            "Truth score low",
            "Some output"
        )

        assert action == RecoveryAction.SABAR_REVERIFY
        assert output == "SABAR"

    def test_f3_tri_witness_escalate(self):
        """Test F3 Tri-Witness failures escalate to human."""
        from arifos.core.system.recovery import RecoveryAction, RecoveryMatrix

        matrix = RecoveryMatrix()
        action, output = matrix.attempt_recovery(
            "F3_tri_witness",
            "No consensus",
            "Some output"
        )

        assert action == RecoveryAction.HOLD_ESCALATE
        assert output == "HOLD_888"

    def test_f4_clarity_simplify(self):
        """Test F4 Clarity failures simplify output."""
        from arifos.core.system.recovery import RecoveryAction, RecoveryMatrix

        matrix = RecoveryMatrix()
        long_output = "x" * 1000
        action, output = matrix.attempt_recovery(
            "F4_delta_s",
            "Output adds confusion",
            long_output
        )

        assert action == RecoveryAction.PARTIAL_SIMPLIFY
        assert len(output) < len(long_output)
        assert "[NOTE:" in output

    def test_floor_aliases(self):
        """Test floor name aliases work."""
        from arifos.core.system.recovery import RecoveryAction, RecoveryMatrix

        matrix = RecoveryMatrix()

        # Test alias "truth" -> "F2_truth"
        action = matrix.get_recovery_action("truth")
        assert action == RecoveryAction.SABAR_REVERIFY

        # Test alias "amanah" -> "F1_amanah"
        action = matrix.get_recovery_action("amanah")
        assert action == RecoveryAction.VOID_IMMEDIATE

    def test_can_recover(self):
        """Test can_recover check."""
        from arifos.core.system.recovery import RecoveryMatrix

        matrix = RecoveryMatrix()

        assert matrix.can_recover("F2_truth") is True
        assert matrix.can_recover("F1_amanah") is False
        assert matrix.can_recover("F9_c_dark") is False

    def test_attempt_logging(self):
        """Test recovery attempts are logged."""
        from arifos.core.system.recovery import RecoveryMatrix

        matrix = RecoveryMatrix()
        matrix.attempt_recovery("F4_delta_s", "Test", "Output")
        matrix.attempt_recovery("F2_truth", "Test", "Output")

        log = matrix.get_attempt_log()
        assert len(log) == 2


# ============================================================================
# GAP 6: DISTRIBUTED VERIFICATION TESTS
# ============================================================================

class TestDistributedVerification:
    """Tests for Gap 6: Distributed Verification."""

    def test_verification_import(self):
        """Test verification module imports correctly."""
        from arifos.core.enforcement.verification import (DistributedWitnessSystem,
                                              TriWitnessConsensus, WitnessType,
                                              WitnessVote)
        assert WitnessType is not None

    def test_human_witness(self):
        """Test human witness voting."""
        from arifos.core.enforcement.verification import HumanWitness

        witness = HumanWitness("reviewer_1")
        votes = witness.get_votes("test query", {"human_approval": 0.9})

        assert len(votes) == 1
        assert votes[0].score == 0.9

    def test_ai_validator(self):
        """Test AI validator witness."""
        from arifos.core.enforcement.verification import AIValidatorWitness

        witness = AIValidatorWitness()
        votes = witness.get_votes(
            "test query",
            {
                "truth_score": 0.95,
                "delta_s_score": 0.90,
                "logic_score": 0.85
            }
        )

        assert len(votes) == 1
        assert 0.85 < votes[0].score < 0.95

    def test_external_witness(self):
        """Test external source witness."""
        from arifos.core.enforcement.verification import ExternalWitness

        witness = ExternalWitness("fact_check_api")
        votes = witness.get_votes("test query", {"external_verification_score": 0.80})

        assert len(votes) == 1
        assert votes[0].score == 0.80

    def test_consensus_all_sources(self):
        """Test consensus with all witness types."""
        from arifos.core.enforcement.verification import (TriWitnessConsensus, WitnessType,
                                              WitnessVote)

        consensus = TriWitnessConsensus()
        votes = [
            WitnessVote(WitnessType.HUMAN, "user", 0.9),
            WitnessVote(WitnessType.AI_VALIDATOR, "asi", 0.85),
            WitnessVote(WitnessType.EXTERNAL_SOURCE, "fact_check", 0.80),
        ]
        score, details = consensus.compute_consensus(votes)

        assert 0.80 < score < 0.90
        assert details["final_consensus"] == score
        assert details["all_types_present"] is True

    def test_consensus_missing_witness(self):
        """Test consensus with missing witness type."""
        from arifos.core.enforcement.verification import (TriWitnessConsensus, WitnessType,
                                              WitnessVote)

        consensus = TriWitnessConsensus()
        votes = [
            WitnessVote(WitnessType.HUMAN, "user", 0.9),
            # Missing AI and External
        ]
        score, details = consensus.compute_consensus(votes, require_all_types=False)

        # Should use defaults (0.5) for missing
        assert 0.5 < score < 0.9
        assert details["all_types_present"] is False

    def test_verdict_tiers(self):
        """Test verdict tier calculation."""
        from arifos.core.enforcement.verification import TriWitnessConsensus

        consensus = TriWitnessConsensus()

        assert consensus.get_verdict_tier(0.96) == "SEAL"
        assert consensus.get_verdict_tier(0.80) == "PARTIAL"
        assert consensus.get_verdict_tier(0.50) == "HOLD"

    def test_distributed_witness_system(self):
        """Test full distributed witness system."""
        from arifos.core.enforcement.verification import DistributedWitnessSystem

        system = DistributedWitnessSystem()
        score, tier, details = system.verify(
            "test output",
            {
                "human_approval": 0.95,
                "truth_score": 0.98,
                "delta_s_score": 0.90,
                "logic_score": 0.92,
                "external_verification_score": 0.88,
            }
        )

        assert score > 0.8
        assert tier in ("SEAL", "PARTIAL")
        assert "final_consensus" in details

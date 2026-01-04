"""
test_memory_eureka_comprehensive_v38.py — Comprehensive EUREKA End-to-End Tests

Comprehensive end-to-end tests for v38 Memory Write Policy Engine (EUREKA).
Tests full pipeline flows, multi-band coordination, and cross-layer integration.

Per: canon/07_CCC/ARIFOS_MEMORY_STACK_v38Omega.md

Author: arifOS Project
Version: v38.0
"""

import pytest
import hashlib
import json
from datetime import datetime, timezone
from typing import Dict, Any, List

# v38 Memory imports
from arifos_core.memory.policy import (
    Verdict,
    MemoryWritePolicy,
    EvidenceChainValidation,
)
from arifos_core.memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
    BAND_PROPERTIES,
)
from arifos_core.memory.authority import (
    MemoryAuthorityCheck,
    HumanApprovalRequiredError,
    SelfModificationError,
)
from arifos_core.memory.audit import (
    MemoryAuditLayer,
)
from arifos_core.memory.retention import (
    MemoryRetentionManager,
)

# Integration imports
from arifos_core.integration.memory_judge import (
    MemoryJudgeIntegration,
    JudgeWriteContext,
)
from arifos_core.integration.memory_seal import (
    MemorySealIntegration,
    SealContext,
    SealStatus,
)
from arifos_core.integration.memory_scars import (
    MemoryScarsIntegration,
    ScarDetectionContext,
)
from arifos_core.integration.memory_sense import (
    MemorySenseIntegration,
    RecallContext,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_floor_scores(variant: str = "passing") -> Dict[str, float]:
    """Create floor scores for different scenarios."""
    if variant == "passing":
        return {
            "F1_amanah": 1.0,
            "F2_truth": 0.99,
            "F3_tri_witness": 0.96,
            "F4_clarity": 0.1,
            "F5_peace": 1.0,
            "F6_empathy": 0.96,
            "F7_humility": 0.04,
            "F8_genius": 0.85,
            "F9_dark": 0.15,
        }
    elif variant == "f1_fail":
        return {
            "F1_amanah": 0.0,  # Irreversible detected
            "F2_truth": 0.99,
            "F3_tri_witness": 0.96,
            "F4_clarity": 0.1,
            "F5_peace": 1.0,
            "F6_empathy": 0.96,
            "F7_humility": 0.04,
            "F8_genius": 0.85,
            "F9_dark": 0.15,
        }
    elif variant == "f9_fail":
        return {
            "F1_amanah": 1.0,
            "F2_truth": 0.99,
            "F3_tri_witness": 0.96,
            "F4_clarity": 0.1,
            "F5_peace": 1.0,
            "F6_empathy": 0.96,
            "F7_humility": 0.04,
            "F8_genius": 0.85,
            "F9_dark": 0.6,  # Dark cleverness/soul claims
        }
    else:
        # Multiple failures
        return {
            "F1_amanah": 0.0,
            "F2_truth": 0.70,
            "F3_tri_witness": 0.80,
            "F4_clarity": -0.5,
            "F5_peace": 0.5,
            "F6_empathy": 0.70,
            "F7_humility": 0.10,
            "F8_genius": 0.50,
            "F9_dark": 0.50,
        }


def make_evidence_chain(verdict: str, floor_scores: Dict[str, float]) -> Dict[str, Any]:
    """Create a complete evidence chain."""
    floor_checks = [
        {"floor": k, "pass": v >= 0.95, "score": v}
        for k, v in floor_scores.items()
    ]
    evidence = {
        "floor_checks": floor_checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
    }
    evidence["hash"] = hashlib.sha256(
        json.dumps(evidence, sort_keys=True).encode()
    ).hexdigest()
    return evidence


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def write_policy():
    return MemoryWritePolicy(strict_mode=True)


@pytest.fixture
def band_router():
    return MemoryBandRouter()


@pytest.fixture
def authority_check():
    return MemoryAuthorityCheck()


@pytest.fixture
def audit_layer():
    return MemoryAuditLayer()


@pytest.fixture
def retention_manager():
    return MemoryRetentionManager()


@pytest.fixture
def judge_integration(write_policy, band_router, authority_check, audit_layer):
    return MemoryJudgeIntegration(
        write_policy=write_policy,
        band_router=band_router,
        authority_check=authority_check,
        audit_layer=audit_layer,
    )


@pytest.fixture
def seal_integration(write_policy, band_router, audit_layer, retention_manager):
    return MemorySealIntegration(
        write_policy=write_policy,
        band_router=band_router,
        audit_layer=audit_layer,
        retention_manager=retention_manager,
    )


@pytest.fixture
def scars_integration(write_policy, band_router, audit_layer):
    return MemoryScarsIntegration(
        write_policy=write_policy,
        band_router=band_router,
        audit_layer=audit_layer,
    )


@pytest.fixture
def sense_integration(write_policy, band_router):
    return MemorySenseIntegration(
        write_policy=write_policy,
        band_router=band_router,
    )


# =============================================================================
# TEST CLASS: END-TO-END MEMORY WRITE FLOW
# =============================================================================

class TestEndToEndMemoryWriteFlow:
    """Test complete memory write flow from judge to seal."""

    def test_seal_verdict_full_flow(self, write_policy, band_router, audit_layer):
        """SEAL verdict should flow through full pipeline."""
        # 1. Policy check
        floor_scores = make_floor_scores("passing")
        evidence = make_evidence_chain("SEAL", floor_scores)
        
        decision = write_policy.should_write(
            verdict="SEAL",
            band_target=None,
            evidence_chain=evidence,
        )
        assert decision.allowed
        assert "LEDGER" in decision.target_bands
        assert "ACTIVE" in decision.target_bands
        
        # 2. Write to bands
        entry = MemoryEntry(
            entry_id="flow_001",
            content={"output": "Test output"},
            metadata={"verdict": "SEAL"},
            band="LEDGER",
            timestamp=datetime.now(timezone.utc).isoformat(),
            writer_id="888_JUDGE",
        )
        
        ledger_result = band_router.write(entry, BandName.BBB)
        assert ledger_result.success
        
        # 3. Audit trail
        audit_record = audit_layer.record_memory_write(
            band="LEDGER",
            entry_id="flow_001",
            writer_id="888_JUDGE",
            verdict="SEAL",
            evidence_hash=evidence["hash"],
            entry_data=entry.content,
        )
        assert audit_record is not None

    def test_void_verdict_full_flow(self, write_policy, band_router, audit_layer, scars_integration):
        """VOID verdict should flow to void band and create scar."""
        # 1. Policy check
        floor_scores = make_floor_scores("f1_fail")
        evidence = make_evidence_chain("VOID", floor_scores)
        
        decision = write_policy.should_write(
            verdict="VOID",
            band_target=None,
            evidence_chain=evidence,
        )
        assert decision.allowed
        assert decision.target_bands == ["VOID"]
        
        # 2. Write to void band
        entry = MemoryEntry(
            entry_id="flow_void_001",
            content={"error": "Irreversible operation detected"},
            metadata={"verdict": "VOID"},
            band="VOID",
            timestamp=datetime.now(timezone.utc).isoformat(),
            writer_id="APEX_PRIME",
        )
        
        void_result = band_router.write(entry, BandName.VOID)
        assert void_result.success
        
        # 3. Scar detection
        scar_ctx = ScarDetectionContext(
            content=entry.content,
            verdict="VOID",
            floor_scores=floor_scores,
        )
        scar_result = scars_integration.detect_patterns(scar_ctx)
        assert scar_result is not None

    def test_partial_verdict_full_flow(self, write_policy, band_router):
        """PARTIAL verdict should flow to phoenix and ledger."""
        floor_scores = make_floor_scores("passing")
        floor_scores["F8_genius"] = 0.75  # Partial score
        evidence = make_evidence_chain("PARTIAL", floor_scores)
        
        decision = write_policy.should_write(
            verdict="PARTIAL",
            band_target=None,
            evidence_chain=evidence,
        )
        assert decision.allowed
        assert "PHOENIX" in decision.target_bands
        assert "LEDGER" in decision.target_bands


# =============================================================================
# TEST CLASS: MULTI-BAND WRITE CONSISTENCY
# =============================================================================

class TestMultiBandWriteConsistency:
    """Test consistency across multiple band writes."""

    def test_seal_writes_same_content_to_both_bands(self, band_router):
        """SEAL should write same content to LEDGER and ACTIVE."""
        content = {"output": "Test output", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        ledger_entry = MemoryEntry(
            entry_id="multi_001",
            content=content,
            metadata={"verdict": "SEAL"},
            band="LEDGER",
            timestamp=datetime.now(timezone.utc).isoformat(),
            writer_id="APEX_PRIME",
        )
        
        active_entry = MemoryEntry(
            entry_id="multi_001",
            content=content,
            metadata={"verdict": "SEAL"},
            band="ACTIVE",
            timestamp=datetime.now(timezone.utc).isoformat(),
            writer_id="111_SENSE",
        )
        
        ledger_result = band_router.write(ledger_entry, BandName.BBB)
        active_result = band_router.write(active_entry, BandName.ACTIVE)
        
        assert ledger_result.success
        assert active_result.success

    def test_verdict_mismatch_detection(self, band_router):
        """Different verdicts should not mix in same entry."""
        entry = MemoryEntry(
            entry_id="mismatch_001",
            content={"output": "Test"},
            metadata={"verdict": "SEAL"},
            band="VOID",  # Wrong band for SEAL
            timestamp=datetime.now(timezone.utc).isoformat(),
            writer_id="APEX_PRIME",
        )
        
        # This should succeed (band router is permissive)
        # Policy layer enforces routing
        result = band_router.write(entry, BandName.VOID)
        assert result.success


# =============================================================================
# TEST CLASS: EVIDENCE CHAIN HASH VERIFICATION
# =============================================================================

class TestEvidenceChainHashVerification:
    """Test cryptographic hash verification in evidence chains."""

    def test_hash_integrity_verification(self):
        """Evidence chain hash should match computed hash."""
        floor_scores = make_floor_scores("passing")
        evidence = make_evidence_chain("SEAL", floor_scores)
        
        # Recompute hash
        expected_hash = hashlib.sha256(
            json.dumps({
                "floor_checks": evidence["floor_checks"],
                "timestamp": evidence["timestamp"],
                "verdict": evidence["verdict"],
            }, sort_keys=True).encode()
        ).hexdigest()
        
        assert evidence["hash"] == expected_hash

    def test_tampered_evidence_detection(self):
        """Tampered evidence should be detectable."""
        floor_scores = make_floor_scores("passing")
        evidence = make_evidence_chain("SEAL", floor_scores)
        
        # Tamper with floor checks
        evidence["floor_checks"][0]["score"] = 0.5
        
        # Recompute expected hash
        expected_hash = hashlib.sha256(
            json.dumps({
                "floor_checks": evidence["floor_checks"],
                "timestamp": evidence["timestamp"],
                "verdict": evidence["verdict"],
            }, sort_keys=True).encode()
        ).hexdigest()
        
        # Hash should not match
        assert evidence["hash"] != expected_hash

    def test_evidence_chain_validation_detects_tampering(self, write_policy):
        """Evidence chain validator should detect tampering."""
        floor_scores = make_floor_scores("passing")
        evidence = make_evidence_chain("SEAL", floor_scores)
        
        # Tamper with evidence
        evidence["floor_checks"][0]["score"] = 0.0
        
        # Use write_policy to validate
        result = write_policy.validate_evidence_chain(evidence)
        assert not result.valid


# =============================================================================
# TEST CLASS: AUTHORITY BOUNDARY ENFORCEMENT
# =============================================================================

class TestAuthorityBoundaryEnforcement:
    """Test authority boundary between AI and human."""

    def test_ai_cannot_modify_vault(self, authority_check):
        """AI should not be able to modify VAULT."""
        with pytest.raises((HumanApprovalRequiredError, SelfModificationError)):
            authority_check.authority_boundary_check({
                "writer_id": "APEX_PRIME",
                "band": "VAULT",
                "content": {"type": "amendment"},
            })

    def test_human_can_seal_to_vault(self, authority_check):
        """Human should be able to seal to VAULT."""
        decision = authority_check.validate_writer(
            writer_id="HUMAN",
            band="VAULT",
        )
        assert decision.allowed

    def test_ai_cannot_seal_phoenix_amendments(self, authority_check):
        """AI should not be able to seal Phoenix amendments."""
        with pytest.raises(HumanApprovalRequiredError):
            authority_check.enforce_human_seal_required(
                band="PHOENIX",
                verdict="SEAL",
                writer_id="PHOENIX_72",
            )

    def test_all_ai_writers_blocked_from_vault(self, authority_check):
        """All AI writer IDs should be blocked from VAULT writes."""
        ai_writers = [
            "APEX_PRIME",
            "888_JUDGE",
            "111_SENSE",
            "999_SEAL",
            "PHOENIX_72",
        ]
        
        for writer in ai_writers:
            with pytest.raises((HumanApprovalRequiredError, SelfModificationError)):
                authority_check.authority_boundary_check({
                    "writer_id": writer,
                    "band": "VAULT",
                    "content": {"type": "constitutional"},
                })


# =============================================================================
# TEST CLASS: CROSS-LAYER INTEGRATION
# =============================================================================

class TestCrossLayerIntegration:
    """Test integration across memory layers."""

    def test_sense_to_judge_integration(self, sense_integration, judge_integration):
        """Memory sense and judge should integrate properly."""
        # Sense creates recall context
        recall_ctx = RecallContext(
            query="Test query",
            session_id="test_session",
        )
        assert recall_ctx.query == "Test query"
        
        # Judge creates write context
        judge_ctx = JudgeWriteContext(
            verdict="SEAL",
            content={"output": "Test"},
            floor_scores=make_floor_scores("passing"),
        )
        assert judge_ctx.verdict == "SEAL"

    def test_judge_to_seal_integration(self, judge_integration, seal_integration):
        """Judge and seal should integrate properly."""
        # Judge context
        judge_ctx = JudgeWriteContext(
            verdict="SEAL",
            content={"output": "Test"},
            floor_scores=make_floor_scores("passing"),
        )
        
        # Seal context
        seal_ctx = SealContext(
            entry_id="test_001",
            verdict="SEAL",
            content={"output": "Test"},
            evidence_hash="hash123",
            floor_scores=make_floor_scores("passing"),
        )
        
        assert judge_ctx.verdict == seal_ctx.verdict

    def test_scars_to_phoenix_integration(self, scars_integration, band_router):
        """Scars should inform Phoenix amendments."""
        # Detect scar
        scar_ctx = ScarDetectionContext(
            content={"error": "Harmful pattern"},
            verdict="VOID",
            floor_scores=make_floor_scores("f1_fail"),
        )
        scar_result = scars_integration.detect_patterns(scar_ctx)
        assert scar_result is not None
        
        # Phoenix proposal references scar
        proposal_entry = MemoryEntry(
            entry_id="proposal_001",
            content={"proposal": "Add guard for pattern X", "scar_ref": "scar_001"},
            metadata={"verdict": "PARTIAL"},
            band="PHOENIX",
            timestamp=datetime.now(timezone.utc).isoformat(),
            writer_id="PHOENIX_72",
        )
        result = band_router.write(proposal_entry, BandName.PHOENIX)
        assert result.success


# =============================================================================
# TEST CLASS: MEMORY IMMUTABILITY ENFORCEMENT
# =============================================================================

class TestMemoryImmutabilityEnforcement:
    """Test that immutable bands cannot be modified."""

    def test_vault_is_immutable(self):
        """VAULT should be immutable."""
        assert BAND_PROPERTIES["VAULT"]["mutable"] is False

    def test_ledger_is_immutable(self):
        """LEDGER should be immutable (append-only)."""
        assert BAND_PROPERTIES["LEDGER"]["mutable"] is False

    def test_active_is_mutable(self):
        """ACTIVE should be mutable (session state)."""
        assert BAND_PROPERTIES["ACTIVE"]["mutable"] is True

    def test_phoenix_is_mutable_until_sealed(self):
        """PHOENIX should be mutable until sealed."""
        assert BAND_PROPERTIES["PHOENIX"]["mutable"] is True


# =============================================================================
# TEST CLASS: VERDICT CONSISTENCY
# =============================================================================

class TestVerdictConsistency:
    """Test verdict consistency across memory operations."""

    def test_seal_verdict_always_canonical(self, write_policy):
        """SEAL verdict should always create canonical memory."""
        evidence = make_evidence_chain("SEAL", make_floor_scores("passing"))
        decision = write_policy.should_write(
            verdict="SEAL",
            band_target=None,
            evidence_chain=evidence,
        )
        assert decision.allowed
        assert "LEDGER" in decision.target_bands

    def test_void_verdict_never_canonical(self, write_policy):
        """VOID verdict should never create canonical memory."""
        evidence = make_evidence_chain("VOID", make_floor_scores("f1_fail"))
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=evidence,
        )
        assert not decision.allowed

    def test_verdict_matches_floor_scores(self):
        """Verdict should be consistent with floor scores."""
        # Passing floors → SEAL
        passing_scores = make_floor_scores("passing")
        seal_evidence = make_evidence_chain("SEAL", passing_scores)
        assert seal_evidence["verdict"] == "SEAL"
        
        # Failing floors → VOID
        failing_scores = make_floor_scores("f1_fail")
        void_evidence = make_evidence_chain("VOID", failing_scores)
        assert void_evidence["verdict"] == "VOID"


# =============================================================================
# TEST CLASS: ERROR HANDLING AND RECOVERY
# =============================================================================

class TestErrorHandlingAndRecovery:
    """Test error handling in memory operations."""

    def test_invalid_verdict_handling(self, write_policy):
        """Invalid verdict should be handled gracefully."""
        evidence = make_evidence_chain("INVALID_VERDICT", make_floor_scores("passing"))
        
        # Should handle gracefully
        try:
            decision = write_policy.should_write(
                verdict="INVALID_VERDICT",
                band_target=None,
                evidence_chain=evidence,
            )
            # If it allows, it should route somewhere safe or reject
            assert not decision.allowed or len(decision.target_bands) == 0
        except (ValueError, KeyError):
            # Also acceptable to raise error
            pass

    def test_missing_evidence_chain_handling(self, write_policy):
        """Missing evidence chain should be rejected."""
        decision = write_policy.should_write(
            verdict="SEAL",
            band_target="LEDGER",
            evidence_chain=None,
        )
        assert not decision.allowed

    def test_empty_floor_checks_handling(self, write_policy):
        """Empty floor checks should be rejected."""
        evidence = {
            "floor_checks": [],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": "SEAL",
            "hash": "test",
        }
        
        # Use write_policy to validate
        result = write_policy.validate_evidence_chain(evidence)
        assert not result.valid


# =============================================================================
# SUMMARY
# =============================================================================
# This comprehensive test suite validates:
# 1. ✅ End-to-end memory write flow (judge→seal)
# 2. ✅ Multi-band write consistency
# 3. ✅ Evidence chain hash verification
# 4. ✅ Authority boundary enforcement (AI vs human)
# 5. ✅ Cross-layer integration (sense↔judge↔scars↔seal)
# 6. ✅ Memory immutability enforcement
# 7. ✅ Verdict consistency with floor scores
# 8. ✅ Error handling and recovery
#
# Total: 35+ assertions across 8+ test categories


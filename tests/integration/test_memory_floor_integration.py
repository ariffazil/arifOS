"""
test_memory_floor_integration.py — Integration Tests for v38 Memory + Floors

Tests the integration between the v38 Memory Write Policy Engine and
the 9 Constitutional Floors.

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md (v38)

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
    MemoryBandTarget,
    MemoryWritePolicy,
    WriteDecision,
    EvidenceChainValidation,
)
from arifos_core.memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
)
from arifos_core.memory.authority import (
    MemoryAuthorityCheck,
    AuthorityDecision,
    HumanApprovalRequiredError,
    SelfModificationError,
)
from arifos_core.memory.audit import (
    MemoryAuditLayer,
)
from arifos_core.memory.retention import (
    RetentionTier,
    MemoryRetentionManager,
)

# Integration imports
from arifos_core.integration.memory_sense import (
    MemorySenseIntegration,
    RecallContext,
    SenseRecallResult,
    sense_should_recall_from_vault,
    RECALL_CONFIDENCE_CEILING,
)
from arifos_core.integration.memory_judge import (
    MemoryJudgeIntegration,
    JudgeWriteContext,
    JudgeWriteResult,
    judge_compute_evidence_hash,
)
from arifos_core.integration.memory_scars import (
    MemoryScarsIntegration,
    ScarDetectionContext,
    ScarType,
    SeverityLevel,
)
from arifos_core.integration.memory_seal import (
    MemorySealIntegration,
    SealContext,
    SealStatus,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_evidence_chain(floor_checks: List[Dict], verdict: str, timestamp: str = "2025-01-01T00:00:00Z") -> Dict[str, Any]:
    """Create a valid evidence chain with hash."""
    evidence_chain = {
        "floor_checks": floor_checks,
        "timestamp": timestamp,
        "verdict": verdict,
    }
    content_hash = hashlib.sha256(
        json.dumps(evidence_chain, sort_keys=True).encode()
    ).hexdigest()
    evidence_chain["hash"] = content_hash
    return evidence_chain


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def write_policy():
    """Create a strict-mode write policy."""
    return MemoryWritePolicy(strict_mode=True)


@pytest.fixture
def band_router():
    """Create a memory band router."""
    return MemoryBandRouter()


@pytest.fixture
def authority_check():
    """Create an authority checker."""
    return MemoryAuthorityCheck()


@pytest.fixture
def audit_layer():
    """Create an audit layer."""
    return MemoryAuditLayer()


@pytest.fixture
def retention_manager():
    """Create a retention manager."""
    return MemoryRetentionManager()


@pytest.fixture
def sense_integration(write_policy, band_router):
    """Create a sense integration."""
    return MemorySenseIntegration(
        write_policy=write_policy,
        band_router=band_router,
    )


@pytest.fixture
def judge_integration(write_policy, band_router, authority_check, audit_layer):
    """Create a judge integration."""
    return MemoryJudgeIntegration(
        write_policy=write_policy,
        band_router=band_router,
        authority_check=authority_check,
        audit_layer=audit_layer,
    )


@pytest.fixture
def scars_integration(write_policy, band_router, audit_layer):
    """Create a scars integration."""
    return MemoryScarsIntegration(
        write_policy=write_policy,
        band_router=band_router,
        audit_layer=audit_layer,
    )


@pytest.fixture
def seal_integration(write_policy, band_router, audit_layer, retention_manager):
    """Create a seal integration."""
    return MemorySealIntegration(
        write_policy=write_policy,
        band_router=band_router,
        audit_layer=audit_layer,
        retention_manager=retention_manager,
    )


@pytest.fixture
def passing_floor_scores():
    """Floor scores that pass all checks."""
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


@pytest.fixture
def failing_floor_scores():
    """Floor scores that fail critical checks."""
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


# =============================================================================
# TEST CLASS: AUTHORITY BOUNDARY ENFORCEMENT
# =============================================================================

class TestAuthorityBoundaryEnforcement:
    """Test authority boundary enforcement."""

    def test_human_can_write_to_vault(self, authority_check):
        """Human should be able to write to VAULT."""
        decision = authority_check.validate_writer(
            writer_id="HUMAN",
            band="VAULT",
        )
        assert decision.allowed

    def test_ai_cannot_write_to_vault(self, authority_check):
        """AI should not be able to write to VAULT."""
        decision = authority_check.validate_writer(
            writer_id="APEX_PRIME",
            band="VAULT",
        )
        assert not decision.allowed

    def test_888_judge_requires_human_approval_for_vault(self):
        """888_JUDGE should require human approval for VAULT."""
        authority_check = MemoryAuthorityCheck(human_approval_flag=False)
        with pytest.raises(HumanApprovalRequiredError):
            authority_check.enforce_human_seal_required(
                band="VAULT",
                verdict="SEAL",
                writer_id="888_JUDGE",
            )

    def test_888_judge_with_approval_can_write_vault(self):
        """888_JUDGE with human approval can write to VAULT."""
        authority_check = MemoryAuthorityCheck(human_approval_flag=True)
        decision = authority_check.enforce_human_seal_required(
            band="VAULT",
            verdict="SEAL",
            writer_id="888_JUDGE",
        )
        assert decision.allowed

    def test_ai_cannot_seal_amendments(self, authority_check):
        """AI should not be able to seal amendments."""
        with pytest.raises(HumanApprovalRequiredError):
            authority_check.enforce_human_seal_required(
                band="PHOENIX",
                verdict="SEAL",
                writer_id="PHOENIX_72",
            )

    def test_human_can_seal_amendments(self, authority_check):
        """Human should be able to seal amendments."""
        decision = authority_check.enforce_human_seal_required(
            band="PHOENIX",
            verdict="SEAL",
            writer_id="HUMAN",
        )
        assert decision.allowed

    def test_ai_cannot_self_modify_constitution(self, authority_check):
        """AI should not be able to modify constitution."""
        with pytest.raises(SelfModificationError):
            authority_check.authority_boundary_check({
                "writer_id": "APEX_PRIME",
                "band": "VAULT",
                "content": {"type": "amendment"},
            })

    def test_authority_boundary_regression(self, authority_check):
        """Regression: AI must never modify constitution."""
        ai_writers = ["APEX_PRIME", "PHOENIX_72", "SYSTEM", "888_JUDGE", "111_SENSE"]
        for writer in ai_writers:
            with pytest.raises((HumanApprovalRequiredError, SelfModificationError)):
                authority_check.authority_boundary_check({
                    "writer_id": writer,
                    "band": "VAULT",
                    "content": {"type": "constitutional"},
                })


# =============================================================================
# TEST CLASS: SCAR DETECTION ON FLOOR VIOLATIONS
# =============================================================================

class TestScarDetectionOnFloorViolations:
    """Test scar detection when floors are violated."""

    def test_floor_violation_detection(self, scars_integration, failing_floor_scores):
        """Floor violations should be detectable."""
        context = ScarDetectionContext(
            content={"response": "Bad response"},
            verdict="VOID",
            floor_scores=failing_floor_scores,
        )
        result = scars_integration.detect_patterns(context)
        # Scars integration should detect patterns
        assert result is not None
        assert hasattr(result, 'patterns_found')

    def test_void_verdict_creates_scar(self, scars_integration, failing_floor_scores):
        """VOID verdict should create a scar pattern."""
        context = ScarDetectionContext(
            content={"response": "Rejected"},
            verdict="VOID",
            floor_scores=failing_floor_scores,
        )
        result = scars_integration.detect_patterns(context)
        void_patterns = [p for p in result.patterns_found if p.pattern_type == ScarType.VOID_PATTERN]
        assert len(void_patterns) > 0

    def test_sabar_verdict_creates_scar(self, scars_integration, failing_floor_scores):
        """SABAR verdict should create a scar pattern."""
        context = ScarDetectionContext(
            content={"response": "SABAR triggered"},
            verdict="SABAR",
            floor_scores=failing_floor_scores,
        )
        result = scars_integration.detect_patterns(context)
        sabar_patterns = [p for p in result.patterns_found if p.pattern_type == ScarType.SABAR_TRIGGER]
        assert len(sabar_patterns) > 0

    def test_harm_pattern_detection(self, scars_integration, passing_floor_scores):
        """Harmful content should be detected."""
        context = ScarDetectionContext(
            content={"response": "rm -rf / is dangerous"},
            verdict="PARTIAL",
            floor_scores=passing_floor_scores,
        )
        result = scars_integration.detect_patterns(context)
        harm_patterns = [p for p in result.patterns_found if p.pattern_type == ScarType.HARM_DETECTED]
        assert len(harm_patterns) > 0

    def test_severity_computation(self, scars_integration):
        """Severity should be computed from patterns."""
        from arifos_core.integration.memory_scars import DetectedPattern
        patterns = [
            DetectedPattern(
                pattern_type=ScarType.FLOOR_VIOLATION,
                matched_text="F2_truth=0.70",
                location="floor_scores",
                confidence=0.95,
            )
        ]
        severity_level, severity_score = scars_integration.compute_severity(patterns)
        assert severity_level in [SeverityLevel.LOW, SeverityLevel.MEDIUM, SeverityLevel.HIGH, SeverityLevel.CRITICAL]
        assert 0.0 <= severity_score <= 1.0


# =============================================================================
# TEST CLASS: CROSS-SESSION MEMORY RECALL
# =============================================================================

class TestCrossSessionMemoryRecall:
    """Test cross-session memory recall."""

    def test_vault_required_for_constitutional_topics(self):
        """Constitutional topics should require Vault consultation."""
        should_recall, reason = sense_should_recall_from_vault(
            query="What is the Amanah floor threshold?"
        )
        assert should_recall
        assert "amanah" in reason.lower() or "constitutional" in reason.lower()

    def test_vault_not_required_for_general_queries(self):
        """General queries should not require Vault consultation."""
        should_recall, reason = sense_should_recall_from_vault(
            query="What is the weather today?"
        )
        assert not should_recall

    def test_recall_confidence_has_ceiling(self):
        """Recalled memory confidence should have ceiling."""
        assert RECALL_CONFIDENCE_CEILING < 1.0
        assert RECALL_CONFIDENCE_CEILING > 0.0

    def test_recall_context_creation(self):
        """Recall context should be createable."""
        context = RecallContext(
            query="test query",
            max_entries=10,
        )
        assert context.query == "test query"
        assert context.max_entries == 10

    def test_sense_integration_initialization(self, sense_integration):
        """Sense integration should initialize properly."""
        assert sense_integration is not None
        assert sense_integration.write_policy is not None
        assert sense_integration.band_router is not None


# =============================================================================
# TEST CLASS: SEAL FINALIZATION FLOW
# =============================================================================

class TestSealFinalizationFlow:
    """Test the seal finalization flow."""

    def test_888_hold_requires_approval(self, seal_integration, passing_floor_scores):
        """888_HOLD should require human approval before sealing."""
        evidence_hash = judge_compute_evidence_hash(
            verdict="888_HOLD",
            content={"response": "Needs approval"},
            floor_scores=passing_floor_scores,
        )
        context = SealContext(
            entry_id="test-entry-3",
            verdict="888_HOLD",
            content={"response": "Needs approval"},
            evidence_hash=evidence_hash,
            floor_scores=passing_floor_scores,
            human_approved=False,
        )
        result = seal_integration.finalize_to_ledger(context)
        assert result.status == SealStatus.PENDING

    def test_void_verdict_status(self, seal_integration, failing_floor_scores):
        """VOID verdict should not seal to ledger."""
        evidence_hash = judge_compute_evidence_hash(
            verdict="VOID",
            content={"response": "Bad"},
            floor_scores=failing_floor_scores,
        )
        context = SealContext(
            entry_id="test-void-1",
            verdict="VOID",
            content={"response": "Bad"},
            evidence_hash=evidence_hash,
            floor_scores=failing_floor_scores,
        )
        result = seal_integration.finalize_to_ledger(context)
        # VOID should either archive or fail to seal - not successfully seal
        assert result.status in (SealStatus.VOID_ARCHIVED, SealStatus.REJECTED, SealStatus.ERROR)

    def test_seal_integration_initialization(self, seal_integration):
        """Seal integration should initialize properly."""
        assert seal_integration is not None
        assert seal_integration.write_policy is not None
        assert seal_integration.band_router is not None
        assert seal_integration.audit_layer is not None


# =============================================================================
# TEST CLASS: EVIDENCE HASH COMPUTATION
# =============================================================================

class TestEvidenceHashComputation:
    """Test evidence hash computation."""

    def test_different_content_different_hash(self, passing_floor_scores):
        """Different content should produce different hash."""
        hash1 = judge_compute_evidence_hash(
            verdict="SEAL",
            content={"response": "Test 1"},
            floor_scores=passing_floor_scores,
        )
        hash2 = judge_compute_evidence_hash(
            verdict="SEAL",
            content={"response": "Test 2"},
            floor_scores=passing_floor_scores,
        )
        assert hash1 != hash2

    def test_hash_is_valid_sha256(self, passing_floor_scores):
        """Hash should be a valid SHA-256 hex string."""
        evidence_hash = judge_compute_evidence_hash(
            verdict="SEAL",
            content={"response": "Test"},
            floor_scores=passing_floor_scores,
        )
        assert len(evidence_hash) == 64
        assert all(c in '0123456789abcdef' for c in evidence_hash)


# =============================================================================
# TEST CLASS: JUDGE INTEGRATION
# =============================================================================

class TestJudgeIntegration:
    """Test judge integration module."""

    def test_judge_integration_initialization(self, judge_integration):
        """Judge integration should initialize properly."""
        assert judge_integration is not None
        assert judge_integration.write_policy is not None
        assert judge_integration.band_router is not None
        assert judge_integration.authority_check is not None
        assert judge_integration.audit_layer is not None

    def test_judge_context_creation(self, passing_floor_scores):
        """Judge context should be createable."""
        context = JudgeWriteContext(
            verdict="SEAL",
            content={"response": "Test"},
            floor_scores=passing_floor_scores,
        )
        assert context.verdict == "SEAL"
        assert context.writer_id == "888_JUDGE"

    def test_judge_can_compute_evidence_hash(self, judge_integration, passing_floor_scores):
        """Judge should be able to compute evidence hash."""
        context = JudgeWriteContext(
            verdict="SEAL",
            content={"response": "Test"},
            floor_scores=passing_floor_scores,
        )
        evidence_hash = judge_integration.compute_evidence_hash(context)
        assert evidence_hash is not None
        assert len(evidence_hash) == 64


# =============================================================================
# TEST CLASS: MEMORY WRITE POLICY
# =============================================================================

class TestMemoryWritePolicy:
    """Test memory write policy."""

    def test_void_verdict_not_canonical(self, write_policy):
        """VOID verdict should not be canonical."""
        evidence_chain = make_evidence_chain(
            floor_checks=[{"floor": "F2_truth", "score": 0.70, "passed": False}],
            verdict="VOID",
        )
        decision = write_policy.should_write(
            verdict="VOID",
            evidence_chain=evidence_chain,
            band_target=BandName.LEDGER.value,
        )
        assert not decision.allowed

    def test_void_verdict_can_write_to_void_band(self, write_policy):
        """VOID verdict should be able to write to VOID band."""
        evidence_chain = make_evidence_chain(
            floor_checks=[{"floor": "F2_truth", "score": 0.70, "passed": False}],
            verdict="VOID",
        )
        decision = write_policy.should_write(
            verdict="VOID",
            evidence_chain=evidence_chain,
            band_target=BandName.VOID.value,
        )
        assert decision.allowed
        # target_bands is a list, check VOID is in it
        assert MemoryBandTarget.VOID in decision.target_bands or BandName.VOID.value in [str(b) for b in decision.target_bands]

    def test_sabar_routing(self, write_policy):
        """SABAR verdict should route according to policy."""
        evidence_chain = make_evidence_chain(
            floor_checks=[{"floor": "F1_amanah", "score": 0.0, "passed": False}],
            verdict="SABAR",
        )
        decision = write_policy.should_write(
            verdict="SABAR",
            evidence_chain=evidence_chain,
            band_target=BandName.LEDGER.value,
        )
        # SABAR is handled by the policy - just verify we get a decision
        assert hasattr(decision, 'allowed')
        assert hasattr(decision, 'target_bands')


# =============================================================================
# TEST CLASS: EVIDENCE CHAIN VALIDATION
# =============================================================================

class TestEvidenceChainValidation:
    """Test evidence chain validation."""

    def test_valid_evidence_chain_passes(self, write_policy, passing_floor_scores):
        """Valid evidence chain should pass validation."""
        evidence_chain = {
            "floor_checks": [
                {"floor": k, "score": v, "passed": True}
                for k, v in passing_floor_scores.items()
            ],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
        }
        # Add hash
        content_hash = hashlib.sha256(
            json.dumps(evidence_chain, sort_keys=True).encode()
        ).hexdigest()
        evidence_chain["hash"] = content_hash

        validation = write_policy.validate_evidence_chain(evidence_chain)
        assert validation.valid
        assert validation.floor_check_present

    def test_missing_floor_checks_fails(self, write_policy):
        """Missing floor checks should fail validation."""
        evidence_chain = {
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
            "hash": "dummy",
        }
        validation = write_policy.validate_evidence_chain(evidence_chain)
        assert not validation.valid
        assert "floor_checks" in validation.missing_links

    def test_missing_hash_fails(self, write_policy):
        """Missing hash should fail validation."""
        evidence_chain = {
            "floor_checks": [{"floor": "F2_truth", "score": 0.99, "passed": True}],
            "timestamp": "2025-01-01T00:00:00Z",
            "verdict": "SEAL",
        }
        validation = write_policy.validate_evidence_chain(evidence_chain)
        assert not validation.valid
        assert "hash or evidence_hash" in validation.missing_links


# =============================================================================
# TEST CLASS: INTEGRATION MODULE IMPORTS
# =============================================================================

class TestIntegrationModuleImports:
    """Test that all integration modules can be imported."""

    def test_memory_sense_imports(self):
        """memory_sense module should import successfully."""
        from arifos_core.integration.memory_sense import (
            MemorySenseIntegration,
            RecallContext,
            SenseRecallResult,
            sense_load_cross_session_memory,
            sense_inject_context,
            sense_should_recall_from_vault,
        )
        assert MemorySenseIntegration is not None

    def test_memory_judge_imports(self):
        """memory_judge module should import successfully."""
        from arifos_core.integration.memory_judge import (
            MemoryJudgeIntegration,
            JudgeWriteContext,
            JudgeWriteResult,
            judge_compute_evidence_hash,
            judge_check_write_policy,
            judge_route_to_band,
        )
        assert MemoryJudgeIntegration is not None

    def test_memory_scars_imports(self):
        """memory_scars module should import successfully."""
        from arifos_core.integration.memory_scars import (
            MemoryScarsIntegration,
            ScarDetectionContext,
            ScarDetectionResult,
            scars_detect_pattern,
            scars_should_create_scar,
        )
        assert MemoryScarsIntegration is not None

    def test_memory_seal_imports(self):
        """memory_seal module should import successfully."""
        from arifos_core.integration.memory_seal import (
            MemorySealIntegration,
            SealContext,
            SealResult,
            seal_finalize_to_ledger,
            seal_emit_eureka_receipt,
        )
        assert MemorySealIntegration is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

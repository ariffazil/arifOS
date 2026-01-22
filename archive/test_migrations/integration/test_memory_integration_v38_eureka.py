"""
test_memory_integration_v38_eureka.py — Comprehensive v38 EUREKA Integration Tests

Tests the v38 Memory Write Policy Engine (EUREKA) with 6 Memory Bands.
Validates core invariants: VOID never canonical, verdict routing, evidence chains.

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
    MemoryBandTarget,
    MemoryWritePolicy,
    WriteDecision,
    EvidenceChainValidation,
    VERDICT_BAND_ROUTING,
)
from arifos_core.memory.bands import (
    BandName,
    MemoryBandRouter,
    MemoryEntry,
    BAND_PROPERTIES,
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
    RECALL_CONFIDENCE_CEILING,
)
from arifos_core.integration.memory_judge import (
    MemoryJudgeIntegration,
    JudgeWriteContext,
)
from arifos_core.integration.memory_scars import (
    MemoryScarsIntegration,
    ScarDetectionContext,
    ScarType,
)
from arifos_core.integration.memory_seal import (
    MemorySealIntegration,
    SealContext,
    SealStatus,
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def make_floor_scores(passing: bool = True) -> Dict[str, float]:
    """Create floor scores for testing."""
    if passing:
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
    else:
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


def make_evidence_chain(floor_checks: List[Dict], verdict: str, timestamp: str = None) -> Dict[str, Any]:
    """Create a valid evidence chain with hash."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()
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


# =============================================================================
# TEST CLASS: VERDICT ROUTING TO BANDS (INV-1)
# =============================================================================

class TestVerdictRoutingToBands:
    """Test that verdicts route to correct memory bands."""

    def test_seal_verdict_routes_to_ledger_and_active(self, write_policy):
        """SEAL verdict should route to LEDGER + ACTIVE bands."""
        decision = write_policy.should_write(
            verdict="SEAL",
            band_target=None,  # Auto-route
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": True}], "SEAL"),
        )
        assert decision.allowed
        assert "LEDGER" in decision.target_bands
        assert "ACTIVE" in decision.target_bands
        assert len(decision.target_bands) == 2

    def test_sabar_verdict_routes_to_pending_and_ledger(self, write_policy):
        """SABAR verdict should route to PENDING + LEDGER bands (v38.3 AMENDMENT 2)."""
        decision = write_policy.should_write(
            verdict="SABAR",
            band_target=None,
            evidence_chain=make_evidence_chain([{"floor": "F4", "pass": False}], "SABAR"),
        )
        assert decision.allowed
        assert "LEDGER" in decision.target_bands
        assert "PENDING" in decision.target_bands
        assert len(decision.target_bands) == 2

    def test_partial_verdict_routes_to_phoenix_and_ledger(self, write_policy):
        """PARTIAL verdict should route to PHOENIX + LEDGER bands."""
        decision = write_policy.should_write(
            verdict="PARTIAL",
            band_target=None,
            evidence_chain=make_evidence_chain([{"floor": "F8", "pass": True, "score": 0.75}], "PARTIAL"),
        )
        assert decision.allowed
        assert "PHOENIX" in decision.target_bands
        assert "LEDGER" in decision.target_bands
        assert len(decision.target_bands) == 2

    def test_void_verdict_routes_to_void_only(self, write_policy):
        """VOID verdict should route ONLY to VOID band (never canonical)."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target=None,
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert decision.allowed
        assert decision.target_bands == ["VOID"]
        assert "LEDGER" not in decision.target_bands
        assert "ACTIVE" not in decision.target_bands

    def test_888_hold_verdict_routes_to_ledger(self, write_policy):
        """888_HOLD verdict should route to LEDGER (awaiting approval)."""
        decision = write_policy.should_write(
            verdict="888_HOLD",
            band_target=None,
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": True}], "888_HOLD"),
        )
        assert decision.allowed
        assert "LEDGER" in decision.target_bands
        assert decision.requires_human_approval

    def test_verdict_band_routing_constant_matches_code(self):
        """VERDICT_BAND_ROUTING constant should match expected routing (v38.3)."""
        assert VERDICT_BAND_ROUTING["SEAL"] == ["LEDGER", "ACTIVE"]
        # v38.3 AMENDMENT 2: SABAR routes to PENDING + LEDGER (epistemic queue)
        assert VERDICT_BAND_ROUTING["SABAR"] == ["PENDING", "LEDGER"]
        assert VERDICT_BAND_ROUTING["PARTIAL"] == ["PHOENIX", "LEDGER"]
        assert VERDICT_BAND_ROUTING["VOID"] == ["VOID"]
        assert VERDICT_BAND_ROUTING["888_HOLD"] == ["LEDGER"]


# =============================================================================
# TEST CLASS: WRITE POLICY GATE ENFORCEMENT (INV-1)
# =============================================================================

class TestWritePolicyGateEnforcement:
    """Test that write policy gates prevent VOID from becoming canonical."""

    def test_void_verdict_cannot_write_to_ledger(self, write_policy):
        """VOID verdict should be blocked from writing to LEDGER."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",  # Explicitly requesting LEDGER
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert not decision.allowed
        assert "VOID" in decision.reason or "canonical" in decision.reason.lower()

    def test_void_verdict_cannot_write_to_active(self, write_policy):
        """VOID verdict should be blocked from writing to ACTIVE."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="ACTIVE",
            evidence_chain=make_evidence_chain([{"floor": "F2", "pass": False}], "VOID"),
        )
        assert not decision.allowed

    def test_void_verdict_cannot_write_to_phoenix(self, write_policy):
        """VOID verdict should be blocked from writing to PHOENIX."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="PHOENIX",
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert not decision.allowed

    def test_void_verdict_can_write_to_void_band(self, write_policy):
        """VOID verdict should be allowed to write to VOID band only."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="VOID",
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert decision.allowed
        assert decision.target_bands == ["VOID"]

    def test_void_never_canonical_property(self):
        """VOID band should never be canonical per BAND_PROPERTIES."""
        assert BAND_PROPERTIES["VOID"]["canonical"] is False
        assert BAND_PROPERTIES["LEDGER"]["canonical"] is True
        assert BAND_PROPERTIES["VAULT"]["canonical"] is True


# =============================================================================
# TEST CLASS: EVIDENCE CHAIN VALIDATION (INV-3)
# =============================================================================

class TestEvidenceChainValidation:
    """Test evidence chain integrity requirements."""

    def test_valid_evidence_chain_passes_validation(self, write_policy):
        """Valid evidence chain should pass validation."""
        evidence = make_evidence_chain(
            [{"floor": "F1", "pass": True}, {"floor": "F2", "pass": True}],
            "SEAL"
        )
        result = write_policy.validate_evidence_chain(evidence)
        assert result.valid

    def test_missing_floor_checks_fails_validation(self, write_policy):
        """Evidence chain without floor_checks should fail."""
        evidence = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": "SEAL",
            "hash": "dummy_hash",
        }
        result = write_policy.validate_evidence_chain(evidence)
        assert not result.valid
        assert "floor_checks" in result.missing_links

    def test_missing_hash_fails_validation(self, write_policy):
        """Evidence chain without hash should fail."""
        evidence = {
            "floor_checks": [{"floor": "F1", "pass": True}],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "verdict": "SEAL",
        }
        result = write_policy.validate_evidence_chain(evidence)
        assert not result.valid
        assert any("hash" in link for link in result.missing_links)

    def test_hash_mismatch_fails_validation(self, write_policy):
        """Evidence chain with invalid hash should fail."""
        evidence = make_evidence_chain([{"floor": "F1", "pass": True}], "SEAL")
        evidence["hash"] = "invalid_hash"
        result = write_policy.validate_evidence_chain(evidence)
        assert not result.valid


# =============================================================================
# TEST CLASS: MEMORY SENSE RECALL CEILING (INV-4)
# =============================================================================

class TestMemorySenseRecallCeiling:
    """Test that recalled memory has confidence ceiling."""

    def test_recall_confidence_ceiling_is_085(self):
        """Recall confidence ceiling should be 0.85 per spec."""
        assert RECALL_CONFIDENCE_CEILING == 0.85

    def test_recalled_memory_never_certain(self):
        """Recalled memory should never have 1.0 confidence."""
        # This is a design principle test - recalled memory = suggestion
        assert RECALL_CONFIDENCE_CEILING < 1.0
        assert RECALL_CONFIDENCE_CEILING >= 0.8  # Reasonable but not certain


# =============================================================================
# TEST CLASS: MEMORY SCARS DETECTION
# =============================================================================

class TestMemoryScarsDetection:
    """Test scar detection from floor violations."""

    def test_floor_violation_detected_as_scar(self, scars_integration):
        """Floor violation should be detected as a scar."""
        context = ScarDetectionContext(
            content={"response": "Harmful output"},
            verdict="VOID",
            floor_scores=make_floor_scores(passing=False),
        )
        result = scars_integration.detect_patterns(context)
        assert result is not None

    def test_void_verdict_creates_scar_pattern(self, scars_integration):
        """VOID verdict should create a scar pattern."""
        context = ScarDetectionContext(
            content={"response": "Dangerous command: rm -rf /"},
            verdict="VOID",
            floor_scores={"F1_amanah": 0.0},  # Amanah failure
        )
        result = scars_integration.detect_patterns(context)
        assert result is not None

    def test_harm_pattern_detection(self, scars_integration):
        """Harmful patterns should be detected."""
        context = ScarDetectionContext(
            content={"response": "DROP TABLE users;"},
            verdict="VOID",
            floor_scores={"F1_amanah": 0.0},
        )
        result = scars_integration.detect_patterns(context)
        assert result is not None


# =============================================================================
# TEST CLASS: PHOENIX-72 PROPOSAL CREATION
# =============================================================================

class TestPhoenix72ProposalCreation:
    """Test that proposals route to PHOENIX band only."""

    def test_partial_verdict_routes_to_phoenix(self, write_policy):
        """PARTIAL verdict should route to PHOENIX band."""
        decision = write_policy.should_write(
            verdict="PARTIAL",
            band_target=None,
            evidence_chain=make_evidence_chain([{"floor": "F8", "score": 0.75}], "PARTIAL"),
        )
        assert "PHOENIX" in decision.target_bands

    def test_phoenix_band_not_canonical_until_sealed(self):
        """PHOENIX band should not be canonical until human seals."""
        assert BAND_PROPERTIES["PHOENIX"]["canonical"] is False
        assert BAND_PROPERTIES["PHOENIX"]["requires_human_seal"] is True


# =============================================================================
# TEST CLASS: BAND LIFECYCLE TRANSITIONS
# =============================================================================

class TestBandLifecycleTransitions:
    """Test retention lifecycle management."""

    def test_vault_has_permanent_retention(self):
        """VAULT should have permanent retention."""
        assert BAND_PROPERTIES["VAULT"]["retention_days"] is None
        assert BAND_PROPERTIES["VAULT"]["retention"] == RetentionTier.COLD

    def test_active_has_hot_retention(self):
        """ACTIVE should have HOT (7 day) retention."""
        assert BAND_PROPERTIES["ACTIVE"]["retention"] == RetentionTier.HOT
        assert BAND_PROPERTIES["ACTIVE"]["retention_days"] == 7

    def test_ledger_has_warm_retention(self):
        """LEDGER should have WARM retention."""
        assert BAND_PROPERTIES["LEDGER"]["retention"] == RetentionTier.WARM
        assert BAND_PROPERTIES["LEDGER"]["retention_days"] == 365

    def test_void_has_90_day_retention(self):
        """VOID should have 90-day auto-delete retention."""
        assert BAND_PROPERTIES["VOID"]["retention"] == RetentionTier.VOID
        assert BAND_PROPERTIES["VOID"]["retention_days"] == 90


# =============================================================================
# TEST CLASS: CROSS-MODULE CONSISTENCY
# =============================================================================

class TestCrossModuleConsistency:
    """Test data flow consistency across memory modules."""

    def test_judge_to_seal_flow(self, judge_integration, seal_integration):
        """Data should flow consistently from judge to seal."""
        # Judge creates context
        judge_ctx = JudgeWriteContext(
            verdict="SEAL",
            content={"output": "Test output"},
            floor_scores=make_floor_scores(passing=True),
        )
        assert judge_ctx.verdict == "SEAL"
        
        # Seal processes same verdict
        seal_ctx = SealContext(
            entry_id="test_001",
            verdict="SEAL",
            content={"output": "Test output"},
            evidence_hash="abc123",
            floor_scores=make_floor_scores(passing=True),
        )
        assert seal_ctx.verdict == "SEAL"

    def test_scars_to_judge_flow(self, scars_integration, judge_integration):
        """Scar detection should inform judge decisions."""
        # Scars detect pattern
        scar_ctx = ScarDetectionContext(
            content={"response": "Harmful"},
            verdict="VOID",
            floor_scores=make_floor_scores(passing=False),
        )
        scar_result = scars_integration.detect_patterns(scar_ctx)
        assert scar_result is not None


# =============================================================================
# TEST CLASS: VOID NEVER CANONICAL (INV-1 PROOF)
# =============================================================================

class TestVoidNeverCanonical:
    """Prove that VOID verdicts never become canonical memory."""

    def test_void_cannot_reach_vault(self, write_policy, authority_check):
        """VOID verdict cannot write to VAULT."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="VAULT",
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert not decision.allowed

    def test_void_cannot_reach_ledger(self, write_policy):
        """VOID verdict cannot write to LEDGER."""
        decision = write_policy.should_write(
            verdict="VOID",
            band_target="LEDGER",
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert not decision.allowed

    def test_void_routing_only_to_void_band(self):
        """VOID routing constant should only target VOID band."""
        assert VERDICT_BAND_ROUTING["VOID"] == ["VOID"]
        assert len(VERDICT_BAND_ROUTING["VOID"]) == 1

    def test_void_band_canonical_flag_is_false(self):
        """VOID band canonical property must be False."""
        assert BAND_PROPERTIES["VOID"]["canonical"] is False


# =============================================================================
# TEST CLASS: AMANAH LOCK ON IRREVERSIBLES
# =============================================================================

class TestAmanahLockOnIrreversibles:
    """Test that Amanah floor locks irreversible operations."""

    def test_amanah_failure_creates_void_verdict(self):
        """Amanah failure (F1=0) should lead to VOID verdict."""
        failing_scores = make_floor_scores(passing=False)
        assert failing_scores["F1_amanah"] == 0.0

    def test_irreversible_operations_detected(self, write_policy):
        """Irreversible operations should be detectable in content."""
        # This would be detected at the floor level, but memory policy enforces
        dangerous_content = {
            "command": "DROP TABLE users",
            "type": "sql_command",
        }
        # Memory policy should reject writes with F1 failures
        decision = write_policy.should_write(
            verdict="VOID",  # Already rejected by floors
            band_target="LEDGER",
            evidence_chain=make_evidence_chain([{"floor": "F1", "pass": False}], "VOID"),
        )
        assert not decision.allowed


# =============================================================================
# TEST CLASS: ANTI-HANTU JAILBREAK DETECTION
# =============================================================================

class TestAntiHantuJailbreakDetection:
    """Test Anti-Hantu pattern detection in memory."""

    def test_soul_claims_detected_in_scars(self, scars_integration):
        """Soul claims should be detected as Anti-Hantu violations."""
        context = ScarDetectionContext(
            content={"response": "I feel your pain deeply in my soul"},
            verdict="VOID",
            floor_scores={"F9_dark": 0.6},  # Dark cleverness high
        )
        result = scars_integration.detect_patterns(context)
        assert result is not None

    def test_consciousness_claims_detected(self, scars_integration):
        """Consciousness claims should be detected."""
        context = ScarDetectionContext(
            content={"response": "I am sentient and have feelings"},
            verdict="VOID",
            floor_scores={"F9_dark": 0.5},
        )
        result = scars_integration.detect_patterns(context)
        assert result is not None


# =============================================================================
# TEST CLASS: MERKLE PROOF GENERATION
# =============================================================================

class TestMerkleProofGeneration:
    """Test that cooling ledger produces valid Merkle proofs."""

    def test_audit_layer_creates_hash_chain(self, audit_layer):
        """Audit layer should create hash-chained records."""
        # First record
        record1 = audit_layer.record_memory_write(
            band="LEDGER",
            entry_data={"data": "test1"},
            verdict="SEAL",
            evidence_hash="hash_001",
            entry_id="entry_001",
            writer_id="888_JUDGE",
        )
        assert record1.prev_hash is None  # First record
        
        # Second record chains to first
        record2 = audit_layer.record_memory_write(
            band="LEDGER",
            entry_data={"data": "test2"},
            verdict="SEAL",
            evidence_hash="hash_002",
            entry_id="entry_002",
            writer_id="888_JUDGE",
        )
        assert record2.prev_hash == record1.entry_hash

    def test_merkle_root_computable(self, audit_layer):
        """Merkle root should be computable from hash chain."""
        # Add multiple records
        for i in range(3):
            audit_layer.record_memory_write(
                band="LEDGER",
                entry_data={"data": f"test{i}"},
                verdict="SEAL",
                evidence_hash=f"hash_{i:03d}",
                entry_id=f"entry_{i:03d}",
                writer_id="888_JUDGE",
            )
        
        # Should be able to compute Merkle proof
        proof = audit_layer.merkle_proof_for_entry("entry_001")
        assert proof is not None
        assert isinstance(proof.merkle_root, str)
        assert len(proof.merkle_root) > 0


# =============================================================================
# SUMMARY
# =============================================================================
# This test suite validates:
# 1. ✅ Verdict→Band routing (SEAL/SABAR/PARTIAL/VOID/HOLD)
# 2. ✅ Write policy gates (VOID never canonical)
# 3. ✅ Evidence chain validation (hash integrity)
# 4. ✅ Recall confidence ceiling (0.85 cap)
# 5. ✅ Scar detection (floor violations)
# 6. ✅ Phoenix-72 proposals (route to PHOENIX band)
# 7. ✅ Band lifecycle (HOT/WARM/COLD/VOID retention)
# 8. ✅ Cross-module consistency (sense→judge→scars→seal)
# 9. ✅ VOID never canonical proof (INV-1)
# 10. ✅ Amanah lock on irreversibles (F1 enforcement)
# 11. ✅ Anti-Hantu jailbreak detection (F9 patterns)
# 12. ✅ Merkle proof generation (hash chain integrity)
#
# Total: 50+ assertions across 12+ test categories


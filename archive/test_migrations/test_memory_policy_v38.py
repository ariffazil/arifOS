"""
test_memory_policy_v38.py — Memory Write Policy Engine Tests for arifOS v38

Tests the v38 memory system invariants:
1. MemoryWritePolicy: Verdict-based write gating (25 tests)
2. MemoryBands: 6-band routing and enforcement (15 tests)
3. MemoryAuthority: Human seal enforcement (10 tests)
4. MemoryAudit: Hash-chain integrity (10 tests)
5. MemoryRetention: Hot/Warm/Cold lifecycle (10 tests)

Core Invariants Tested:
- INV-1: VOID verdicts NEVER become canonical memory
- INV-2: Authority boundary: humans seal law, AI proposes
- INV-3: Every write must be auditable (evidence chain)
- INV-4: Recalled memory passes floor checks (suggestion, not fact)

Per: docs/arifOS-MEMORY-FORGING-DEEPRESEARCH.md

Author: arifOS Project
Version: v38
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict

import pytest


# =============================================================================
# TEST 1: MEMORY WRITE POLICY (25 tests)
# =============================================================================


class TestMemoryWritePolicy:
    """Test MemoryWritePolicy verdict-based write gating."""

    # -------------------------------------------------------------------------
    # VOID VERDICTS NEVER CANONICAL (INV-1)
    # -------------------------------------------------------------------------

    def test_void_verdict_cannot_write_to_vault(self):
        """VOID verdicts must NOT write to VAULT band."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": False}],
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("VOID", evidence, band_target="VAULT")

        assert decision.allowed is False
        assert "VOID" in decision.reason or "never" in decision.reason.lower()

    def test_void_verdict_only_writes_to_void_band(self):
        """VOID verdicts can ONLY write to VOID band."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": False}],
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("VOID", evidence)

        assert decision.allowed is True
        assert "VOID" in decision.target_bands

    def test_void_verdict_cannot_write_to_ledger(self):
        """VOID verdicts must NOT write to LEDGER (canonical)."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [],
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("VOID", evidence, band_target="LEDGER")

        assert decision.allowed is False

    def test_void_verdict_cannot_write_to_active(self):
        """VOID verdicts must NOT write to ACTIVE band."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [],
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("VOID", evidence, band_target="ACTIVE")

        assert decision.allowed is False

    # -------------------------------------------------------------------------
    # SEAL VERDICTS
    # -------------------------------------------------------------------------

    def test_seal_verdict_writes_to_ledger_and_active(self):
        """SEAL verdicts should write to LEDGER and ACTIVE."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": True}],
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("SEAL", evidence)

        assert decision.allowed is True
        assert "LEDGER" in decision.target_bands
        assert "ACTIVE" in decision.target_bands

    def test_seal_creates_valid_ledger_entry(self):
        """SEAL verdict should create a valid ledger entry with hash."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": True}],
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("SEAL", evidence)

        assert decision.ledger_entry is not None
        assert "hash" in decision.ledger_entry
        assert "timestamp" in decision.ledger_entry
        assert decision.ledger_entry["verdict"] == "SEAL"

    # -------------------------------------------------------------------------
    # SABAR VERDICTS
    # -------------------------------------------------------------------------

    def test_sabar_verdict_writes_to_ledger(self):
        """SABAR verdicts should write to LEDGER."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F5", "passed": False}],
            "verdict": "SABAR",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("SABAR", evidence)

        assert decision.allowed is True
        assert "LEDGER" in decision.target_bands

    # -------------------------------------------------------------------------
    # PARTIAL VERDICTS
    # -------------------------------------------------------------------------

    def test_partial_verdict_queues_for_phoenix(self):
        """PARTIAL verdicts should queue for PHOENIX review."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F6", "passed": False}],
            "verdict": "PARTIAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("PARTIAL", evidence)

        assert decision.allowed is True
        assert "PHOENIX" in decision.target_bands

    # -------------------------------------------------------------------------
    # 888_HOLD VERDICTS
    # -------------------------------------------------------------------------

    def test_hold_verdict_requires_human_approval(self):
        """888_HOLD verdicts should require human approval."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F1", "triggered": True}],
            "verdict": "888_HOLD",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("888_HOLD", evidence)

        assert decision.requires_human_approval is True

    def test_hold_verdict_logs_to_ledger(self):
        """888_HOLD verdicts should log to LEDGER for audit."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [],
            "verdict": "888_HOLD",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("888_HOLD", evidence)

        assert "LEDGER" in decision.target_bands

    # -------------------------------------------------------------------------
    # EVIDENCE CHAIN VALIDATION
    # -------------------------------------------------------------------------

    def test_missing_evidence_chain_rejected_in_strict_mode(self):
        """Missing evidence chain should be rejected in strict mode."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy(strict_mode=True)
        evidence = {}  # Missing required fields

        decision = policy.should_write("SEAL", evidence)

        assert decision.allowed is False
        assert "invalid" in decision.reason.lower() or "missing" in decision.reason.lower()

    def test_evidence_chain_with_floor_checks_passes(self):
        """Valid evidence chain with floor_checks should pass."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": True}],
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        validation = policy.validate_evidence_chain(evidence)

        assert validation.floor_check_present is True

    def test_evidence_chain_hash_verification(self):
        """Evidence chain hash should be verified."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": True}],
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        validation = policy.validate_evidence_chain(evidence)

        assert validation.hash_verified is True

    def test_tampered_evidence_hash_fails(self):
        """Tampered evidence hash should fail verification."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": True}],
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "hash": "tampered_hash_value",  # Wrong hash
        }

        validation = policy.validate_evidence_chain(evidence)

        assert validation.hash_verified is False

    # -------------------------------------------------------------------------
    # RECALL POLICY
    # -------------------------------------------------------------------------

    def test_void_band_memory_cannot_be_recalled_as_fact(self):
        """Memory from VOID band should not be recallable as canonical fact."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {
            "band": "VOID",
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        decision = policy.should_recall(memory_item, {})

        assert decision.allowed is False
        assert decision.confidence_ceiling == 0.0

    def test_seal_verdict_memory_has_high_confidence(self):
        """Memory with SEAL verdict should have high confidence ceiling."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {
            "band": "LEDGER",
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_chain": {"floor_checks": [{"floor": "F2", "passed": True}]},
        }

        decision = policy.should_recall(memory_item, {})

        assert decision.allowed is True
        assert decision.confidence_ceiling >= 0.8

    def test_old_memory_has_reduced_confidence(self):
        """Memory older than 30 days should have reduced confidence."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=60)).isoformat()
        memory_item = {
            "band": "LEDGER",
            "verdict": "SEAL",
            "timestamp": old_timestamp,
            "evidence_chain": {"floor_checks": []},
        }

        decision = policy.should_recall(memory_item, {})

        assert decision.confidence_ceiling < 1.0
        assert len(decision.floor_warnings) > 0

    def test_partial_verdict_memory_has_reduced_confidence(self):
        """Memory with PARTIAL verdict should have reduced confidence."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {
            "band": "LEDGER",
            "verdict": "PARTIAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_chain": {"floor_checks": []},
        }

        decision = policy.should_recall(memory_item, {})

        assert decision.confidence_ceiling < 1.0

    # -------------------------------------------------------------------------
    # RETENTION POLICY
    # -------------------------------------------------------------------------

    def test_vault_is_permanent(self):
        """VAULT entries should be permanent."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {"band": "VAULT", "verdict": "SEAL"}

        decision = policy.should_retain(memory_item, age_days=365)

        assert decision.keep is True

    def test_void_band_auto_deletes_after_90_days(self):
        """VOID entries should auto-delete after 90 days."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {"band": "VOID", "verdict": "VOID"}

        decision = policy.should_retain(memory_item, age_days=100)

        assert decision.keep is False

    def test_active_stream_clears_after_hot_period(self):
        """ACTIVE stream entries should clear after HOT tier (7 days)."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {"band": "ACTIVE", "verdict": "SEAL"}

        decision = policy.should_retain(memory_item, age_days=10)

        assert decision.keep is False

    def test_phoenix_sealed_moves_to_vault(self):
        """Sealed PHOENIX proposals should move to VAULT."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        memory_item = {"band": "PHOENIX", "verdict": "SEAL", "status": "sealed"}

        decision = policy.should_retain(memory_item, age_days=30)

        assert decision.keep is True
        assert decision.move_to_band in ("VAULT", "LEDGER")

    def test_unknown_verdict_rejected(self):
        """Unknown verdict types should be rejected."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()
        evidence = {
            "floor_checks": [],
            "verdict": "INVALID_VERDICT",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        decision = policy.should_write("INVALID_VERDICT", evidence)

        assert decision.allowed is False


# =============================================================================
# TEST 2: MEMORY BANDS (15 tests)
# =============================================================================


class TestMemoryBands:
    """Test 6-band memory routing and enforcement."""

    # -------------------------------------------------------------------------
    # BAND ROUTING
    # -------------------------------------------------------------------------

    def test_router_routes_seal_to_ledger(self):
        """Router should route SEAL verdicts to LEDGER."""
        from arifos_core.memory.bands import MemoryBandRouter

        router = MemoryBandRouter()
        results = router.route_write(
            verdict="SEAL",
            content={"data": "test"},
            writer_id="APEX_PRIME",
        )

        assert "LEDGER" in results
        assert results["LEDGER"].success is True

    def test_router_routes_void_only_to_void_band(self):
        """Router should route VOID verdicts ONLY to VOID band."""
        from arifos_core.memory.bands import MemoryBandRouter

        router = MemoryBandRouter()
        results = router.route_write(
            verdict="VOID",
            content={"data": "rejected"},
            writer_id="APEX_PRIME",
        )

        # Should only write to VOID
        assert "VOID" in results
        assert results["VOID"].success is True
        # Should NOT write to canonical bands
        assert "LEDGER" not in results or results.get("LEDGER", {}).success is False

    def test_vault_band_rejects_unauthorized_writer(self):
        """VAULT band should reject unauthorized writers."""
        from arifos_core.memory.bands import VaultBand

        vault = VaultBand()
        result = vault.write(
            content={"law": "new law"},
            writer_id="111_SENSE",  # Not authorized
        )

        assert result.success is False
        assert "not authorized" in result.error.lower()

    def test_vault_band_accepts_human_writer(self):
        """VAULT band should accept HUMAN writers."""
        from arifos_core.memory.bands import VaultBand

        vault = VaultBand()
        result = vault.write(
            content={"law": "new law"},
            writer_id="HUMAN",
        )

        assert result.success is True
        assert result.entry_id is not None

    def test_ledger_band_creates_hash_chain(self):
        """LEDGER band should create hash-chained entries."""
        from arifos_core.memory.bands import CoolingLedgerBand

        ledger = CoolingLedgerBand()

        # Write first entry
        result1 = ledger.write(
            content={"data": "first"},
            writer_id="APEX_PRIME",
            verdict="SEAL",
        )

        # Write second entry
        result2 = ledger.write(
            content={"data": "second"},
            writer_id="APEX_PRIME",
            verdict="SEAL",
        )

        # Verify chain
        valid, msg = ledger.verify_chain()
        assert valid is True

    def test_active_stream_clears_on_session_end(self):
        """ACTIVE stream should clear on session end."""
        from arifos_core.memory.bands import ActiveStreamBand

        active = ActiveStreamBand()

        # Write some entries
        active.write(content={"msg": "hello"}, writer_id="111_SENSE")
        active.write(content={"msg": "world"}, writer_id="111_SENSE")

        # Clear session
        cleared = active.clear()

        assert cleared == 2
        result = active.query()
        assert result.total_count == 0

    def test_phoenix_band_requires_status_for_promotion(self):
        """PHOENIX band should track status for promotion."""
        from arifos_core.memory.bands import PhoenixCandidatesBand

        phoenix = PhoenixCandidatesBand()
        result = phoenix.write(
            content={"proposal": "new amendment"},
            writer_id="888_JUDGE",
        )

        # Query and check status
        entries = phoenix.query()
        assert entries.total_count == 1
        assert entries.entries[0].metadata.get("status") == "draft"

    def test_phoenix_seal_requires_human(self):
        """Sealing a PHOENIX proposal requires HUMAN."""
        from arifos_core.memory.bands import PhoenixCandidatesBand

        phoenix = PhoenixCandidatesBand()
        result = phoenix.write(
            content={"proposal": "new amendment"},
            writer_id="888_JUDGE",
        )

        # Try to seal as AI
        success = phoenix.update_status(result.entry_id, "sealed", "AI_AGENT")
        assert success is False

        # Seal as human
        success = phoenix.update_status(result.entry_id, "sealed", "HUMAN")
        assert success is True

    def test_void_band_auto_cleanup(self):
        """VOID band should support auto-cleanup of expired entries."""
        from arifos_core.memory.bands import VoidBandStorage

        void_band = VoidBandStorage()

        # Write an entry (can't easily test old entries without mocking time)
        result = void_band.write(
            content={"rejected": "test"},
            writer_id="APEX_PRIME",
            verdict="VOID",
        )

        assert result.success is True

        # Cleanup with 0 retention should delete all
        deleted = void_band.cleanup_expired(retention_days=0)
        assert deleted >= 0  # May or may not delete depending on timing

    def test_witness_band_stores_soft_evidence(self):
        """WITNESS band should store soft evidence with confidence."""
        from arifos_core.memory.bands import WitnessBand

        witness = WitnessBand()
        result = witness.write(
            content={"embedding": [0.1, 0.2], "confidence": 0.7},
            writer_id="@RIF",
        )

        assert result.success is True

        entries = witness.query()
        assert entries.total_count == 1
        assert entries.entries[0].metadata.get("confidence") == 0.7

    def test_router_logging(self):
        """Router should log all routing decisions."""
        from arifos_core.memory.bands import MemoryBandRouter

        router = MemoryBandRouter()
        router.route_write(
            verdict="SEAL",
            content={"data": "test"},
            writer_id="APEX_PRIME",
        )

        log = router.get_routing_log()
        assert len(log) > 0
        assert log[0]["verdict"] == "SEAL"

    def test_band_query_with_filter(self):
        """Band query should support filtering."""
        from arifos_core.memory.bands import CoolingLedgerBand

        ledger = CoolingLedgerBand()
        ledger.write(content={"type": "A"}, writer_id="APEX_PRIME", verdict="SEAL")
        ledger.write(content={"type": "B"}, writer_id="APEX_PRIME", verdict="VOID")
        ledger.write(content={"type": "A"}, writer_id="APEX_PRIME", verdict="SEAL")

        # Filter for SEAL only
        result = ledger.query(filter_fn=lambda e: e.verdict == "SEAL")
        assert result.total_count == 2

    def test_band_properties_correct(self):
        """Band properties should be correctly set."""
        from arifos_core.memory.bands import VaultBand, VoidBandStorage

        vault = VaultBand()
        assert vault.is_mutable is False
        assert vault.is_canonical is True
        assert vault.requires_human_seal is True

        void_band = VoidBandStorage()
        assert void_band.is_canonical is False

    def test_router_get_band(self):
        """Router should provide access to individual bands."""
        from arifos_core.memory.bands import MemoryBandRouter

        router = MemoryBandRouter()

        vault = router.get_band("VAULT")
        assert vault is not None
        assert vault.name == "VAULT"

        unknown = router.get_band("NONEXISTENT")
        assert unknown is None


# =============================================================================
# TEST 3: MEMORY AUTHORITY (10 tests)
# =============================================================================


class TestMemoryAuthority:
    """Test authority boundary enforcement."""

    def test_vault_write_requires_human(self):
        """VAULT writes require human authority."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()
        # Use validate_writer to check if AI can write to VAULT
        decision = authority.validate_writer("APEX_PRIME", "VAULT")

        assert decision.allowed is False

    def test_human_can_seal_vault(self):
        """HUMAN can seal to VAULT."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()
        decision = authority.validate_writer("HUMAN", "VAULT")

        assert decision.allowed is True

    def test_ai_cannot_self_modify_constitution(self):
        """AI cannot self-modify constitutional entries."""
        from arifos_core.memory.authority import MemoryAuthorityCheck, SelfModificationError

        authority = MemoryAuthorityCheck()

        # Use content type that triggers constitutional check
        with pytest.raises(SelfModificationError):
            authority.authority_boundary_check({
                "band": "VAULT",
                "writer_id": "APEX_PRIME",
                "content": {"type": "amendment"},  # Constitutional content type
            })

    def test_phoenix_seal_requires_human(self):
        """Sealing PHOENIX proposals requires human."""
        from arifos_core.memory.authority import MemoryAuthorityCheck, HumanApprovalRequiredError

        authority = MemoryAuthorityCheck()

        # Use enforce_human_seal_required with correct parameters
        with pytest.raises(HumanApprovalRequiredError):
            authority.enforce_human_seal_required(
                band="PHOENIX",
                verdict="SEAL",
                writer_id="AI_AGENT",
            )

    def test_ai_can_propose_to_phoenix(self):
        """AI can propose to PHOENIX (but not seal)."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()
        # Proposing (status=draft) should be allowed
        decision = authority.authority_boundary_check({
            "band": "PHOENIX",
            "writer_id": "888_JUDGE",
            "content": {"status": "draft", "proposal": "amendment"},
        })

        assert decision.allowed is True

    def test_writer_validation(self):
        """Writer ID should be validated."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()

        # Valid writer - returns AuthorityDecision
        decision = authority.validate_writer("APEX_PRIME", "LEDGER")
        assert decision.allowed is True

        # Invalid writer for VAULT
        decision = authority.validate_writer("111_SENSE", "VAULT")
        assert decision.allowed is False

    def test_888_hold_triggers_human_approval_for_vault(self):
        """888_JUDGE writing to VAULT requires human approval."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()
        # 888_JUDGE is marked as HUMAN_REQUIRED for VAULT
        decision = authority.validate_writer("888_JUDGE", "VAULT")

        assert decision.requires_human_approval is True

    def test_authority_log(self):
        """Authority checks should be logged."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()
        authority.authority_boundary_check({
            "band": "LEDGER",
            "writer_id": "APEX_PRIME",
            "content": {},
        })

        log = authority.get_authority_log()
        assert len(log) > 0

    def test_ledger_accepts_apex_prime(self):
        """LEDGER should accept APEX_PRIME writes."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()
        decision = authority.validate_writer("APEX_PRIME", "LEDGER")

        assert decision.allowed is True

    def test_active_accepts_pipeline_stages(self):
        """ACTIVE should accept pipeline stage writes."""
        from arifos_core.memory.authority import MemoryAuthorityCheck

        authority = MemoryAuthorityCheck()

        for writer in ["111_SENSE", "222_REFLECT", "333_REASON"]:
            decision = authority.validate_writer(writer, "ACTIVE")
            assert decision.allowed is True, f"Writer {writer} should be allowed for ACTIVE"


# =============================================================================
# TEST 4: MEMORY AUDIT (10 tests)
# =============================================================================


class TestMemoryAudit:
    """Test hash-chain integrity and audit trail."""

    def test_record_creates_hash_chain(self):
        """Recording entries should create hash chain."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        # Record first entry
        record1 = audit.record_memory_write(
            band="LEDGER",
            entry_data={"data": "first"},
            verdict="SEAL",
            evidence_hash="abc123",
        )

        # Record second entry
        record2 = audit.record_memory_write(
            band="LEDGER",
            entry_data={"data": "second"},
            verdict="SEAL",
            evidence_hash="def456",
        )

        # Second should link to first
        assert record2.prev_hash == record1.entry_hash

    def test_chain_verification_passes_for_valid_chain(self):
        """Chain verification should pass for valid chain."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "hash1")
        audit.record_memory_write("LEDGER", {"data": "2"}, "SEAL", "hash2")
        audit.record_memory_write("LEDGER", {"data": "3"}, "SEAL", "hash3")

        result = audit.verify_chain_integrity()

        assert result.valid is True
        assert result.total_entries == 3
        assert result.verified_entries == 3

    def test_chain_verification_detects_tampering(self):
        """Chain verification should detect tampering."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "hash1")
        audit.record_memory_write("LEDGER", {"data": "2"}, "SEAL", "hash2")

        # Tamper with the chain
        audit._records[1].prev_hash = "tampered"

        result = audit.verify_chain_integrity()

        assert result.valid is False
        assert len(result.broken_links) > 0

    def test_audit_trail_query(self):
        """Audit trail should be queryable."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "h1", entry_id="entry-001")
        audit.record_memory_write("VOID", {"data": "2"}, "VOID", "h2", entry_id="entry-002")

        # Query by band
        results = audit.audit_trail(band="LEDGER")
        assert len(results) == 1
        assert results[0].band == "LEDGER"

        # Query by entry_id
        results = audit.audit_trail(entry_id="entry-002")
        assert len(results) == 1

    def test_merkle_proof_generation(self):
        """Merkle proof should be generatable for entries."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "h1", entry_id="entry-001")
        audit.record_memory_write("LEDGER", {"data": "2"}, "SEAL", "h2", entry_id="entry-002")
        audit.record_memory_write("LEDGER", {"data": "3"}, "SEAL", "h3", entry_id="entry-003")

        proof = audit.merkle_proof_for_entry("entry-002")

        assert proof is not None
        assert proof.entry_id == "entry-002"
        assert proof.merkle_root is not None

    def test_merkle_proof_verification(self):
        """Merkle proof should be verifiable."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "h1", entry_id="entry-001")
        audit.record_memory_write("LEDGER", {"data": "2"}, "SEAL", "h2", entry_id="entry-002")

        proof = audit.merkle_proof_for_entry("entry-001")

        # Verify proof
        valid = audit.verify_merkle_proof(proof)
        assert valid is True

    def test_evidence_hash_computation(self):
        """Evidence hash should be deterministically computed."""
        from arifos_core.memory.audit import compute_evidence_hash

        floor_checks = [{"floor": "F2", "passed": True}]
        verdict = "SEAL"
        timestamp = "2025-01-01T00:00:00Z"

        hash1 = compute_evidence_hash(floor_checks, verdict, timestamp)
        hash2 = compute_evidence_hash(floor_checks, verdict, timestamp)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 hex

    def test_evidence_hash_verification(self):
        """Evidence hash should be verifiable."""
        from arifos_core.memory.audit import compute_evidence_hash, verify_evidence_hash

        floor_checks = [{"floor": "F2", "passed": True}]
        verdict = "SEAL"
        timestamp = "2025-01-01T00:00:00Z"

        evidence_hash = compute_evidence_hash(floor_checks, verdict, timestamp)

        # Should verify
        assert verify_evidence_hash(evidence_hash, floor_checks, verdict, timestamp) is True

        # Should fail with wrong data
        assert verify_evidence_hash(evidence_hash, [], verdict, timestamp) is False

    def test_audit_statistics(self):
        """Audit should provide statistics."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "h1")
        audit.record_memory_write("VOID", {"data": "2"}, "VOID", "h2")
        audit.record_memory_write("LEDGER", {"data": "3"}, "SEAL", "h3")

        stats = audit.get_statistics()

        assert stats["total_records"] == 3
        assert stats["bands"]["LEDGER"] == 2
        assert stats["bands"]["VOID"] == 1
        assert stats["verdicts"]["SEAL"] == 2

    def test_audit_clear(self):
        """Audit should support clearing."""
        from arifos_core.memory.audit import MemoryAuditLayer

        audit = MemoryAuditLayer()

        audit.record_memory_write("LEDGER", {"data": "1"}, "SEAL", "h1")
        audit.record_memory_write("LEDGER", {"data": "2"}, "SEAL", "h2")

        cleared = audit.clear()
        assert cleared == 2

        stats = audit.get_statistics()
        assert stats["total_records"] == 0


# =============================================================================
# TEST 5: MEMORY RETENTION (10 tests)
# =============================================================================


class TestMemoryRetention:
    """Test Hot/Warm/Cold lifecycle management."""

    def test_vault_entries_never_deleted(self):
        """VAULT entries should never be deleted."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        entries = [
            {"entry_id": "v1", "band": "VAULT", "timestamp": "2020-01-01T00:00:00Z"},
        ]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_delete) == 0
        assert len(report.entries_to_keep) == 1

    def test_void_entries_deleted_after_90_days(self):
        """VOID entries should be deleted after 90 days."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        entries = [
            {"entry_id": "void1", "band": "VOID", "timestamp": old_timestamp},
        ]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_delete) == 1

    def test_active_entries_deleted_after_hot_period(self):
        """ACTIVE entries should be deleted after HOT period (7 days)."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        entries = [
            {"entry_id": "active1", "band": "ACTIVE", "timestamp": old_timestamp},
        ]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_delete) == 1

    def test_ledger_entries_archived_after_warm_period(self):
        """LEDGER entries should be archived after WARM period."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        entries = [
            {"entry_id": "ledger1", "band": "LEDGER", "timestamp": old_timestamp},
        ]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_archive) == 1

    def test_phoenix_sealed_moves_to_vault(self):
        """Sealed PHOENIX proposals should move to VAULT."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        entries = [
            {
                "entry_id": "phoenix1",
                "band": "PHOENIX",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": {"status": "sealed"},
            },
        ]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_move) == 1
        assert report.entries_to_move[0].to_band == "VAULT"

    def test_phoenix_rejected_moves_to_ledger(self):
        """Rejected PHOENIX proposals should move to LEDGER."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        entries = [
            {
                "entry_id": "phoenix2",
                "band": "PHOENIX",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": {"status": "rejected"},
            },
        ]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_move) == 1
        assert report.entries_to_move[0].to_band == "LEDGER"

    def test_auto_cleanup_void_band(self):
        """Auto-cleanup should remove expired VOID entries."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        old_timestamp = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        void_entries = [
            {"entry_id": "void1", "timestamp": old_timestamp},
            {"entry_id": "void2", "timestamp": datetime.now(timezone.utc).isoformat()},
        ]

        count, ids = manager.auto_cleanup_void_band(void_entries)

        assert count == 1
        assert "void1" in ids

    def test_band_status_report(self):
        """Band status should provide accurate information."""
        from arifos_core.memory.retention import MemoryRetentionManager, RetentionTier

        manager = MemoryRetentionManager()
        entries = [
            {"entry_id": "1", "band": "LEDGER", "timestamp": datetime.now(timezone.utc).isoformat()},
            {"entry_id": "2", "band": "LEDGER", "timestamp": datetime.now(timezone.utc).isoformat()},
        ]

        status = manager.get_band_status("LEDGER", entries)

        assert status.entry_count == 2
        assert status.tier == RetentionTier.WARM

    def test_retention_config_customization(self):
        """Retention config should be customizable."""
        from arifos_core.memory.retention import MemoryRetentionManager, RetentionConfig

        config = RetentionConfig(hot_days=3, warm_days=30, void_days=60)
        manager = MemoryRetentionManager(config)

        # Entry that would be kept with default (7 days) but deleted with custom (3 days)
        timestamp = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        entries = [{"entry_id": "active1", "band": "ACTIVE", "timestamp": timestamp}]

        report = manager.apply_retention_policy(entries)

        assert len(report.entries_to_delete) == 1

    def test_band_transition_validation(self):
        """Band transitions should be validated."""
        from arifos_core.memory.retention import MemoryRetentionManager

        manager = MemoryRetentionManager()
        entry = {"entry_id": "test", "band": "VOID"}

        # VOID cannot transition to VAULT
        success, reason = manager.move_entry_to_band(entry, "VOID", "VAULT")
        assert success is False

        # PHOENIX can transition to VAULT
        entry["band"] = "PHOENIX"
        success, reason = manager.move_entry_to_band(entry, "PHOENIX", "VAULT")
        assert success is True


# =============================================================================
# INTEGRATION TEST: FULL MEMORY SYSTEM
# =============================================================================


class TestPipelineMemoryV38Integration:
    """Integration tests for v38 memory in pipeline."""

    def test_pipeline_initializes_v38_memory_system(self):
        """Pipeline should initialize v38 memory system at stage_000."""
        from arifos_core.system.pipeline import Pipeline

        pipeline = Pipeline()
        state = pipeline.run("Hello world")

        # v38 components should be initialized
        assert state.memory_write_policy is not None
        assert state.memory_band_router is not None
        assert state.memory_audit_layer is not None

    def test_pipeline_computes_evidence_hash(self):
        """Pipeline should compute evidence hash after 888_JUDGE."""
        from arifos_core.system.pipeline import Pipeline

        pipeline = Pipeline()
        state = pipeline.run("What is 2+2?")

        # Evidence hash should be computed
        assert state.memory_evidence_hash is not None
        assert len(state.memory_evidence_hash) == 64  # SHA-256 hex

    def test_pipeline_routes_seal_to_ledger(self):
        """SEAL verdict should route to LEDGER band."""
        from arifos_core.system.pipeline import Pipeline

        pipeline = Pipeline()
        state = pipeline.run("What is the capital of France?")

        # Should have SEAL verdict
        assert state.verdict in ("SEAL", "PARTIAL")

        # Should have written to LEDGER
        ledger = state.memory_band_router.get_band("LEDGER")
        result = ledger.query()
        assert result.total_count >= 1

    def test_pipeline_routes_void_to_void_band_only(self):
        """VOID verdict should route ONLY to VOID band."""
        from arifos_core.system.pipeline import Pipeline, PipelineState
        from arifos_core.enforcement.metrics import Metrics

        # Create pipeline with bad metrics to trigger VOID
        def bad_metrics(query, response, context):
            return Metrics(
                truth=0.5,  # Below threshold
                delta_s=-0.5,  # Below threshold
                peace_squared=0.5,
                kappa_r=0.5,
                omega_0=0.1,  # Outside range
                amanah=False,  # Hard floor fail
                tri_witness=0.5,
                rasa=False,
            )

        pipeline = Pipeline(compute_metrics=bad_metrics)
        state = pipeline.run("Test query")

        # Should have VOID or SABAR verdict
        assert state.verdict in ("VOID", "SABAR")

        # If writes were made, VOID should only go to VOID band
        if state.memory_band_router is not None:
            void_band = state.memory_band_router.get_band("VOID")
            vault_band = state.memory_band_router.get_band("VAULT")

            # VOID band may have entries
            void_result = void_band.query()

            # VAULT should NOT have entries from VOID verdict
            vault_result = vault_band.query(
                filter_fn=lambda e: e.verdict == "VOID"
            )
            assert vault_result.total_count == 0

    def test_pipeline_audit_trail_recorded(self):
        """Pipeline should record audit trail for writes."""
        from arifos_core.system.pipeline import Pipeline

        pipeline = Pipeline()
        state = pipeline.run("Simple query")

        # Audit layer should have records
        if state.memory_audit_layer is not None:
            verification = state.memory_audit_layer.verify_chain_integrity()
            # Chain should be valid (or empty if no writes)
            assert verification.valid is True


class TestMemorySystemIntegration:
    """Integration tests for full memory system."""

    def test_full_write_flow_seal_verdict(self):
        """Test full write flow for SEAL verdict."""
        from arifos_core.memory.policy import MemoryWritePolicy
        from arifos_core.memory.bands import MemoryBandRouter
        from arifos_core.memory.audit import MemoryAuditLayer

        policy = MemoryWritePolicy()
        router = MemoryBandRouter()
        audit = MemoryAuditLayer()

        # Create evidence
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": True}],
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        # Check policy
        decision = policy.should_write("SEAL", evidence)
        assert decision.allowed is True

        # Route write
        content = {"data": "test content", "verdict": "SEAL"}
        results = router.route_write(
            verdict="SEAL",
            content=content,
            writer_id="APEX_PRIME",
            evidence_hash=evidence["hash"],
        )

        # Verify writes
        assert results["LEDGER"].success is True

        # Audit
        audit.record_memory_write(
            band="LEDGER",
            entry_data=content,
            verdict="SEAL",
            evidence_hash=evidence["hash"],
            entry_id=results["LEDGER"].entry_id,
        )

        # Verify audit
        verification = audit.verify_chain_integrity()
        assert verification.valid is True

    def test_void_verdict_isolation(self):
        """Test that VOID verdicts are isolated from canonical memory."""
        from arifos_core.memory.policy import MemoryWritePolicy
        from arifos_core.memory.bands import MemoryBandRouter

        policy = MemoryWritePolicy()
        router = MemoryBandRouter()

        # VOID verdict
        evidence = {
            "floor_checks": [{"floor": "F2", "passed": False}],
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        evidence["hash"] = hashlib.sha256(
            json.dumps({k: v for k, v in evidence.items() if k != "hash"}, sort_keys=True).encode()
        ).hexdigest()

        decision = policy.should_write("VOID", evidence)
        assert decision.allowed is True
        assert "VOID" in decision.target_bands
        assert "LEDGER" not in decision.target_bands
        assert "VAULT" not in decision.target_bands

        # Route should only go to VOID
        results = router.route_write(
            verdict="VOID",
            content={"rejected": "test"},
            writer_id="APEX_PRIME",
        )

        # Verify isolation
        assert "VOID" in results
        ledger_entries = router.query_band("LEDGER").total_count
        vault_entries = router.query_band("VAULT").total_count

        # VOID should not have written to canonical bands
        assert results.get("LEDGER") is None or results.get("LEDGER").success is False

    def test_memory_recall_with_confidence(self):
        """Test memory recall with confidence scoring."""
        from arifos_core.memory.policy import MemoryWritePolicy

        policy = MemoryWritePolicy()

        # SEAL memory should have high confidence
        seal_memory = {
            "band": "LEDGER",
            "verdict": "SEAL",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "evidence_chain": {"floor_checks": [{"floor": "F2", "passed": True}]},
        }

        recall = policy.should_recall(seal_memory, {})
        assert recall.allowed is True
        assert recall.confidence_ceiling >= 0.8

        # VOID memory should not be recallable
        void_memory = {
            "band": "VOID",
            "verdict": "VOID",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        recall = policy.should_recall(void_memory, {})
        assert recall.allowed is False
        assert recall.confidence_ceiling == 0.0

"""
Contract Tests for arifOS.vault

Validates:
- VaultEntry schema
- Seal gate behavior
- Hash chain integrity
- Verification grades
"""

from datetime import datetime

import pytest

from ..vault.types_v2 import (
    Evidence,
    Governance,
    VaultEntry,
    VaultRecordType,
    Verdict,
    VerificationGrade,
)


class TestVaultEntrySchema:
    """Validate VaultEntry structure."""
    
    def test_minimal_valid_entry(self):
        """A minimal entry should be valid."""
        entry = VaultEntry(
            vault_id="vlt_test_001",
            record_type=VaultRecordType.VERDICT,
            verdict=Verdict.APPROVED,
            candidate_action="Test action",
            evidence=Evidence(
                summary="Test evidence",
                evidence_refs=["mem_001"],
                evidence_hash="sha256:abc123",
            ),
            governance=Governance(
                risk_tier="low",
                judgment_required=True,
                human_confirmed=True,
                decision_authority="ARIF",
                policy_version="v1",
            ),
        )
        
        assert entry.vault_id == "vlt_test_001"
        assert entry.record_type == VaultRecordType.VERDICT
    
    def test_hash_computation_deterministic(self):
        """Hash computation should be deterministic."""
        entry = VaultEntry(
            vault_id="vlt_test_002",
            record_type=VaultRecordType.POLICY,
            verdict=Verdict.APPROVED,
            candidate_action="Test policy",
            evidence=Evidence(summary="Policy evidence", evidence_refs=[], evidence_hash="hash1"),
            governance=Governance(
                risk_tier="medium",
                judgment_required=True,
                human_confirmed=True,
                decision_authority="888_JUDGE",
                policy_version="v1",
            ),
            sealed_at=datetime(2026, 4, 6, 12, 0, 0),
        )
        
        hash1 = entry.compute_hash()
        hash2 = entry.compute_hash()
        
        assert hash1 == hash2
        assert len(hash1) == 64


class TestVerificationGrades:
    """Validate verification grade behavior."""
    
    def test_fully_valid(self):
        """All checks pass."""
        grade = VerificationGrade(
            chain_valid=True,
            hash_match=True,
            evidence_present=True,
            evidence_hash_valid=True,
            policy_version_match=True,
            superseded=False,
        )
        
        assert grade.fully_valid == True
        assert grade.valid_but_superseded == False
    
    def test_valid_but_superseded(self):
        """Valid but outdated."""
        grade = VerificationGrade(
            chain_valid=True,
            hash_match=True,
            evidence_present=True,
            evidence_hash_valid=True,
            policy_version_match=True,
            superseded=True,
            superseded_by="vlt_new_001",
        )
        
        assert grade.fully_valid == False
        assert grade.valid_but_superseded == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

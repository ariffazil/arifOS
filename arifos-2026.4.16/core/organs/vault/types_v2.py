"""
Vault Types v2 — With Verification Grades

Verification grades:
- chain_valid
- hash_match
- evidence_present
- policy_version_match
- superseded
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class VaultRecordType(Enum):
    """Types of vault records."""
    VERDICT = "verdict"
    POLICY = "policy"
    RELEASE = "release"
    OVERRIDE = "override"
    AUDIT = "audit"


class Verdict(Enum):
    """Possible verdicts."""
    APPROVED = "Approved"
    PARTIAL = "Partial"
    PAUSE = "Pause"
    VOID = "Void"
    HOLD = "Hold"


@dataclass
class Evidence:
    """Evidence supporting the vault entry."""
    summary: str
    evidence_refs: list[str]
    evidence_hash: str


@dataclass
class Governance:
    """Governance metadata for the decision."""
    risk_tier: str
    judgment_required: bool
    human_confirmed: bool
    decision_authority: str
    policy_version: str


@dataclass
class Integrity:
    """Cryptographic integrity proofs."""
    prev_hash: str
    record_hash: str
    merkle_root: Optional[str] = None


@dataclass
class VaultLineage:
    """Lineage tracking for vault entries."""
    session_id: str
    derived_from: list[str] = field(default_factory=list)
    supersedes: Optional[str] = None


@dataclass
class VerificationGrade:
    """
    Granular verification grades.
    
    Not just pass/fail — detailed audit truth.
    """
    chain_valid: bool = False
    hash_match: bool = False
    evidence_present: bool = False
    evidence_hash_valid: bool = False
    policy_version_match: bool = False
    superseded: bool = False
    superseded_by: Optional[str] = None
    
    @property
    def fully_valid(self) -> bool:
        """All critical checks pass."""
        return (
            self.chain_valid and
            self.hash_match and
            self.evidence_present and
            self.policy_version_match and
            not self.superseded
        )
    
    @property
    def valid_but_superseded(self) -> bool:
        """Valid but no longer current."""
        return (
            self.chain_valid and
            self.hash_match and
            self.superseded
        )
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "chain_valid": self.chain_valid,
            "hash_match": self.hash_match,
            "evidence_present": self.evidence_present,
            "evidence_hash_valid": self.evidence_hash_valid,
            "policy_version_match": self.policy_version_match,
            "superseded": self.superseded,
            "superseded_by": self.superseded_by,
            "fully_valid": self.fully_valid,
            "valid_but_superseded": self.valid_but_superseded,
        }


@dataclass
class VaultEntry:
    """
    The canonical vault record v2.
    """
    vault_id: str
    record_type: VaultRecordType
    
    # The judgment
    verdict: Verdict
    candidate_action: str
    
    # Supporting evidence
    evidence: Evidence
    
    # Governance context
    governance: Governance
    
    # Timing
    sealed_at: datetime = field(default_factory=datetime.utcnow)
    
    # Integrity
    integrity: Optional[Integrity] = None
    
    # Lineage
    lineage: VaultLineage = field(default_factory=lambda: VaultLineage(session_id=""))
    
    def compute_hash(self) -> str:
        """Compute canonical hash of this entry."""
        import hashlib
        import json
        
        content = {
            "vault_id": self.vault_id,
            "record_type": self.record_type.value,
            "verdict": self.verdict.value,
            "candidate_action": self.candidate_action,
            "evidence": {
                "summary": self.evidence.summary,
                "evidence_refs": self.evidence.evidence_refs,
                "evidence_hash": self.evidence.evidence_hash,
            },
            "governance": {
                "risk_tier": self.governance.risk_tier,
                "decision_authority": self.governance.decision_authority,
                "policy_version": self.governance.policy_version,
            },
            "sealed_at": self.sealed_at.isoformat(),
            "lineage": {
                "session_id": self.lineage.session_id,
                "derived_from": self.lineage.derived_from,
            },
        }
        
        return hashlib.sha256(
            json.dumps(content, sort_keys=True).encode()
        ).hexdigest()
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "vault_id": self.vault_id,
            "record_type": self.record_type.value,
            "verdict": self.verdict.value,
            "candidate_action": self.candidate_action,
            "evidence": {
                "summary": self.evidence.summary,
                "evidence_refs": self.evidence.evidence_refs,
                "evidence_hash": self.evidence.evidence_hash,
            },
            "governance": {
                "risk_tier": self.governance.risk_tier,
                "judgment_required": self.governance.judgment_required,
                "human_confirmed": self.governance.human_confirmed,
                "decision_authority": self.governance.decision_authority,
                "policy_version": self.governance.policy_version,
            },
            "sealed_at": self.sealed_at.isoformat(),
            "integrity": {
                "prev_hash": self.integrity.prev_hash if self.integrity else None,
                "record_hash": self.integrity.record_hash if self.integrity else None,
                "merkle_root": self.integrity.merkle_root if self.integrity else None,
            },
            "lineage": {
                "session_id": self.lineage.session_id,
                "derived_from": self.lineage.derived_from,
                "supersedes": self.lineage.supersedes,
            },
        }


@dataclass
class SealReceipt:
    """Receipt for a successful vault seal."""
    vault_id: str
    record_hash: str
    merkle_root: Optional[str]
    timestamp: datetime
    immutable: bool = True


@dataclass
class VerifyReport:
    """Report from vault verification with grades."""
    vault_id: str
    grade: VerificationGrade
    errors: list[str] = field(default_factory=list)
    
    @property
    def valid(self) -> bool:
        """Quick check: is this entry valid?"""
        return self.grade.fully_valid or self.grade.valid_but_superseded
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "vault_id": self.vault_id,
            "valid": self.valid,
            "grade": self.grade.to_dict(),
            "errors": self.errors,
        }

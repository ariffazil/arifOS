"""
Vault Types — The Immutable Record Schema

Each vault entry answers:
- What happened?
- Why was it allowed / held / refused?
- What evidence supported it?
- Who had authority?
- What rule-set was in force?
- Can the record be verified later?
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class VaultRecordType(Enum):
    """Types of vault records."""
    VERDICT = "verdict"       # Final judgment
    POLICY = "policy"         # Policy decision
    RELEASE = "release"       # Release milestone
    OVERRIDE = "override"     # 888_JUDGE override
    AUDIT = "audit"           # Audit event


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
    evidence_refs: list[str]  # References to memory records, docs, etc.
    evidence_hash: str  # SHA256 of evidence content


@dataclass
class Governance:
    """Governance metadata for the decision."""
    risk_tier: str  # low, medium, high, critical
    judgment_required: bool
    human_confirmed: bool
    decision_authority: str  # Who made the decision
    policy_version: str  # Which constitution version was in force


@dataclass
class Integrity:
    """Cryptographic integrity proofs."""
    prev_hash: str  # Hash of previous vault entry
    record_hash: str  # Hash of this record
    merkle_root: Optional[str] = None  # Periodic Merkle root


@dataclass
class VaultLineage:
    """Lineage tracking for vault entries."""
    session_id: str
    derived_from: list[str]  # Parent records (memory or vault)
    supersedes: Optional[str] = None  # Previous version if superseded


@dataclass
class VaultEntry:
    """
    The canonical vault record.
    
    Immutable once sealed. Never edited — only superseded by new entry.
    """
    vault_id: str
    record_type: VaultRecordType
    
    # The judgment
    verdict: Verdict
    candidate_action: str  # What was being judged
    
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
    
    def compute_hash(self) -> str:
        """Compute canonical hash of this entry."""
        import hashlib
        import json
        
        # Hash everything except integrity itself
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
    """Report from vault verification."""
    vault_id: str
    valid: bool
    chain_continuity: bool
    hash_match: bool
    superseded: bool
    superseded_by: Optional[str]
    errors: list[str] = field(default_factory=list)

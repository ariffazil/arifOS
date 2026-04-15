"""
Memory Types v2 — Hardened with Confidence Classes and Provenance

Adds:
- Confidence classes (observed, derived, inferred, asserted_by_human, sealed_from_vault)
- Source weighting
- Vault-backed marking
- Contested status
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MemoryType(Enum):
    """The four lanes of memory."""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    CONSTITUTIONAL = "constitutional"


class ConfidenceClass(Enum):
    """
    How was this memory established?
    
    Prevents semantic drift by tracking provenance.
    """
    OBSERVED = "observed"                    # Directly witnessed
    DERIVED = "derived"                      # Logically derived from other memories
    INFERRED = "inferred"                    # Probabilistic inference
    ASSERTED_BY_HUMAN = "asserted_by_human"  # Explicit human statement
    SEALED_FROM_VAULT = "sealed_from_vault"  # Promoted from vault (highest trust)


class ConfidenceWeight:
    """Weights for confidence classes in retrieval ranking."""
    OBSERVED = 0.7
    DERIVED = 0.5
    INFERRED = 0.3
    ASSERTED_BY_HUMAN = 0.9
    SEALED_FROM_VAULT = 1.0  # Vault-backed is maximum confidence


class MemoryOrigin(Enum):
    """Where did this memory come from?"""
    USER = "user"
    SYSTEM = "system"
    TOOL = "tool"
    DERIVED = "derived"


class Visibility(Enum):
    PRIVATE = "private"
    SHARED = "shared"
    PUBLIC = "public"


class Sensitivity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RetentionClass(Enum):
    """Memory lifecycle classes."""
    EPHEMERAL = "ephemeral"
    SESSION = "session"
    PROJECT = "project"
    DURABLE = "durable"
    CONSTITUTIONAL = "constitutional"


class ContestedStatus(Enum):
    """Status when memory conflicts with authority."""
    UNCONTESTED = "uncontested"
    CONTESTED = "contested"  # Human stated conflicting thing
    SUPERSEDED = "superseded"  # Newer memory replaces this
    VAULT_OVERRULES = "vault_overrules"  # Vault has different truth


@dataclass
class Source:
    """Provenance: where did this memory come from?"""
    origin: MemoryOrigin
    session_id: Optional[str] = None
    message_ref: Optional[str] = None
    tool_ref: Optional[str] = None
    vault_ref: Optional[str] = None  # If sealed_from_vault


@dataclass
class Scope:
    """Who can see this and in what context?"""
    owner: str = "ARIF"
    visibility: Visibility = Visibility.PRIVATE
    domain: str = "arifOS"
    project: Optional[str] = None


@dataclass
class Governance:
    """Can we trust this memory? Should we keep it?"""
    confidence: float = 0.0  # [0.0, 1.0]
    confidence_class: ConfidenceClass = ConfidenceClass.INFERRED
    sensitivity: Sensitivity = Sensitivity.LOW
    requires_confirmation: bool = False
    promotable_to_vault: bool = False
    revocable: bool = True
    contested: ContestedStatus = ContestedStatus.UNCONTESTED
    superseded_by: Optional[str] = None  # memory_id of replacement


@dataclass
class DecayPolicy:
    """Lane-specific decay rules."""
    decay_type: str  # "expire", "fade", "consolidate", "never"
    half_life_hours: Optional[float] = None  # For fade
    expires_at: Optional[datetime] = None  # For expire
    consolidation_threshold: Optional[int] = None  # For consolidate (access count)


@dataclass
class Time:
    """Temporal tracking for lifecycle management."""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None
    access_count: int = 0


@dataclass
class Retrieval:
    """How do we find this memory again?"""
    embedding_id: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    recency_score: float = 0.0
    importance_score: float = 0.0
    vault_backed: bool = False  # True if from vault seal
    source_weight: float = 0.5  # Based on confidence_class


@dataclass
class Lineage:
    """Where did this come from and what did it replace?"""
    derived_from: list[str] = field(default_factory=list)
    supersedes: Optional[str] = None
    superseded_by: Optional[str] = None
    vault_seal_ref: Optional[str] = None  # Link to vault if promoted


@dataclass
class MemoryRecord:
    """
    The canonical memory envelope v2 — hardened.
    """
    memory_id: str
    memory_type: MemoryType
    
    # Content
    title: str
    content: str
    summary: Optional[str] = None
    
    # Metadata
    source: Source = field(default_factory=Source)
    scope: Scope = field(default_factory=Scope)
    governance: Governance = field(default_factory=Governance)
    decay_policy: DecayPolicy = field(default_factory=lambda: DecayPolicy(decay_type="fade"))
    time: Time = field(default_factory=Time)
    retrieval: Retrieval = field(default_factory=Retrieval)
    lineage: Lineage = field(default_factory=Lineage)
    
    # Lane-specific extensions
    lane_data: dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set derived fields."""
        # Set source weight from confidence class
        weight_map = {
            ConfidenceClass.OBSERVED: ConfidenceWeight.OBSERVED,
            ConfidenceClass.DERIVED: ConfidenceWeight.DERIVED,
            ConfidenceClass.INFERRED: ConfidenceWeight.INFERRED,
            ConfidenceClass.ASSERTED_BY_HUMAN: ConfidenceWeight.ASSERTED_BY_HUMAN,
            ConfidenceClass.SEALED_FROM_VAULT: ConfidenceWeight.SEALED_FROM_VAULT,
        }
        self.retrieval.source_weight = weight_map.get(
            self.governance.confidence_class, 0.5
        )
        self.retrieval.vault_backed = (
            self.governance.confidence_class == ConfidenceClass.SEALED_FROM_VAULT
        )
    
    def mark_contested(self, contesting_memory_id: str, authority: str = "human"):
        """Mark this memory as contested by newer authority."""
        self.governance.contested = ContestedStatus.CONTESTED
        self.lane_data["contested_by"] = contesting_memory_id
        self.lane_data["contested_at"] = datetime.utcnow().isoformat()
        self.lane_data["contested_by_authority"] = authority
    
    def mark_superseded(self, new_memory_id: str):
        """Mark this memory as superseded by newer version."""
        self.governance.contested = ContestedStatus.SUPERSEDED
        self.governance.superseded_by = new_memory_id
        self.lineage.superseded_by = new_memory_id
    
    def mark_vault_overrules(self, vault_id: str):
        """Mark that vault has different truth."""
        self.governance.contested = ContestedStatus.VAULT_OVERRULES
        self.lane_data["vault_overrules"] = vault_id
    
    def apply_decay(self) -> bool:
        """
        Apply decay policy. Returns True if memory should be removed.
        """
        policy = self.decay_policy
        
        if policy.decay_type == "never":
            return False  # Constitutional
        
        if policy.decay_type == "expire":
            if policy.expires_at and datetime.utcnow() > policy.expires_at:
                return True
        
        elif policy.decay_type == "fade":
            # Reduce recency score
            self.retrieval.recency_score *= 0.95
            if self.retrieval.recency_score < 0.1:
                return True
        
        elif policy.decay_type == "consolidate":
            # Semantic: consolidate if accessed enough
            if policy.consolidation_threshold:
                if self.time.access_count >= policy.consolidation_threshold:
                    # Mark as durable, don't delete
                    self.decay_policy.decay_type = "never"
        
        return False
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type.value,
            "title": self.title,
            "content": self.content,
            "summary": self.summary,
            "source": {
                "origin": self.source.origin.value,
                "session_id": self.source.session_id,
                "message_ref": self.source.message_ref,
                "tool_ref": self.source.tool_ref,
                "vault_ref": self.source.vault_ref,
            },
            "scope": {
                "owner": self.scope.owner,
                "visibility": self.scope.visibility.value,
                "domain": self.scope.domain,
                "project": self.scope.project,
            },
            "governance": {
                "confidence": self.governance.confidence,
                "confidence_class": self.governance.confidence_class.value,
                "sensitivity": self.governance.sensitivity.value,
                "requires_confirmation": self.governance.requires_confirmation,
                "promotable_to_vault": self.governance.promotable_to_vault,
                "revocable": self.governance.revocable,
                "contested": self.governance.contested.value,
                "superseded_by": self.governance.superseded_by,
            },
            "decay_policy": {
                "decay_type": self.decay_policy.decay_type,
                "half_life_hours": self.decay_policy.half_life_hours,
                "expires_at": self.decay_policy.expires_at.isoformat() if self.decay_policy.expires_at else None,
            },
            "time": {
                "created_at": self.time.created_at.isoformat() if self.time.created_at else None,
                "updated_at": self.time.updated_at.isoformat() if self.time.updated_at else None,
                "expires_at": self.time.expires_at.isoformat() if self.time.expires_at else None,
                "access_count": self.time.access_count,
            },
            "retrieval": {
                "embedding_id": self.retrieval.embedding_id,
                "keywords": self.retrieval.keywords,
                "entities": self.retrieval.entities,
                "recency_score": self.retrieval.recency_score,
                "importance_score": self.retrieval.importance_score,
                "vault_backed": self.retrieval.vault_backed,
                "source_weight": self.retrieval.source_weight,
            },
            "lineage": {
                "derived_from": self.lineage.derived_from,
                "supersedes": self.lineage.supersedes,
                "superseded_by": self.lineage.superseded_by,
                "vault_seal_ref": self.lineage.vault_seal_ref,
            },
            "lane_data": self.lane_data,
        }


@dataclass
class WriteReceipt:
    """Confirmation of memory write."""
    memory_id: str
    stored: bool
    embedding_created: bool
    expires_at: Optional[datetime]
    superseded_older: Optional[str] = None  # If this superseded an older memory


@dataclass
class MemoryQuery:
    """Query for memory retrieval."""
    query: str
    memory_types: Optional[list[MemoryType]] = None
    scopes: Optional[list[str]] = None
    limit: int = 10
    min_confidence: float = 0.5
    prefer_vault_backed: bool = True  # Boost vault-backed memories
    recency_weight: float = 0.2
    semantic_weight: float = 0.4
    source_weight: float = 0.4  # NEW: weight by confidence class

"""
Canonical Memory Types — The Memory Record Schema

Every memory record uses one canonical envelope.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class MemoryType(Enum):
    """The four lanes of memory."""
    WORKING = "working"           # Current session, short TTL
    EPISODIC = "episodic"         # Event/history, timestamped
    SEMANTIC = "semantic"         # Stable knowledge, distilled
    CONSTITUTIONAL = "constitutional"  # Core rules, read often, write rarely


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
    EPHEMERAL = "ephemeral"       # Scratch/temporary, short TTL
    SESSION = "session"           # Current work, expires after session
    PROJECT = "project"           # Active architecture, retain while active
    DURABLE = "durable"           # Stable doctrine, keep until revoked
    CONSTITUTIONAL = "constitutional"  # Core laws, keep unless sovereign changes


@dataclass
class Source:
    """Provenance: where did this memory come from?"""
    origin: MemoryOrigin
    session_id: Optional[str] = None
    message_ref: Optional[str] = None
    tool_ref: Optional[str] = None


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
    sensitivity: Sensitivity = Sensitivity.LOW
    requires_confirmation: bool = False
    promotable_to_vault: bool = False  # Can this become a vault record?
    revocable: bool = True  # Can this memory be deleted/forgotten?


@dataclass
class Time:
    """Temporal tracking for lifecycle management."""
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    last_accessed_at: Optional[datetime] = None


@dataclass
class Retrieval:
    """How do we find this memory again?"""
    embedding_id: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)
    recency_score: float = 0.0
    importance_score: float = 0.0


@dataclass
class Lineage:
    """Where did this come from and what did it replace?"""
    derived_from: list[str] = field(default_factory=list)  # parent memory_ids
    supersedes: Optional[str] = None  # memory this replaces
    superseded_by: Optional[str] = None  # memory that replaces this


@dataclass
class MemoryRecord:
    """
    The canonical memory envelope.
    
    All memory lanes use this schema. What differs is:
    - memory_type (which lane)
    - retention policy (how long it lives)
    - retrieval weights (how we find it)
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
    time: Time = field(default_factory=Time)
    retrieval: Retrieval = field(default_factory=Retrieval)
    lineage: Lineage = field(default_factory=Lineage)
    
    # Lane-specific extensions
    lane_data: dict[str, Any] = field(default_factory=dict)
    
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
            },
            "scope": {
                "owner": self.scope.owner,
                "visibility": self.scope.visibility.value,
                "domain": self.scope.domain,
                "project": self.scope.project,
            },
            "governance": {
                "confidence": self.governance.confidence,
                "sensitivity": self.governance.sensitivity.value,
                "requires_confirmation": self.governance.requires_confirmation,
                "promotable_to_vault": self.governance.promotable_to_vault,
                "revocable": self.governance.revocable,
            },
            "time": {
                "created_at": self.time.created_at.isoformat() if self.time.created_at else None,
                "updated_at": self.time.updated_at.isoformat() if self.time.updated_at else None,
                "expires_at": self.time.expires_at.isoformat() if self.time.expires_at else None,
                "last_accessed_at": self.time.last_accessed_at.isoformat() if self.time.last_accessed_at else None,
            },
            "retrieval": {
                "embedding_id": self.retrieval.embedding_id,
                "keywords": self.retrieval.keywords,
                "entities": self.retrieval.entities,
                "recency_score": self.retrieval.recency_score,
                "importance_score": self.retrieval.importance_score,
            },
            "lineage": {
                "derived_from": self.lineage.derived_from,
                "supersedes": self.lineage.supersedes,
                "superseded_by": self.lineage.superseded_by,
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


@dataclass
class MemoryQuery:
    """Query for memory retrieval."""
    query: str
    memory_types: Optional[list[MemoryType]] = None
    scopes: Optional[list[str]] = None
    limit: int = 10
    min_confidence: float = 0.5
    recency_weight: float = 0.3
    semantic_weight: float = 0.7

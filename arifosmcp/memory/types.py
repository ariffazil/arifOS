from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
from uuid import UUID, uuid4

class MemoryType(str, Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    POLICY = "policy"

class RetentionClass(str, Enum):
    TRANSIENT = "transient"
    REVIEWABLE = "reviewable"
    DURABLE = "durable"
    IMMUTABLE_AUDIT = "immutable_audit"

class MemoryStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUPERSEDED = "superseded"

class Authority(str, Enum):
    EXPLICIT_USER = "explicit_user"
    SYSTEM_INFERRED = "system_inferred"
    DOCUMENT = "document"
    UNKNOWN = "unknown"

class EmbeddingStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"

@dataclass
class MemoryCandidate:
    type: MemoryType
    subject: Optional[str]
    content: str
    summary: Optional[str]
    source_type: str
    source_ref: Dict[str, Any]
    confidence: float = 0.0
    authority: Authority = Authority.UNKNOWN
    sensitivity: float = 0.0
    consent_level: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    hash: Optional[str] = None

@dataclass
class MemoryRecord:
    memory_id: UUID = field(default_factory=uuid4)
    tenant_id: str = "default"
    actor_id: str = "anonymous"
    session_id: str = "unknown"
    project_id: Optional[str] = None
    
    type: MemoryType = MemoryType.WORKING
    subject: Optional[str] = None
    content: str = ""
    summary: Optional[str] = None
    
    source_type: str = "unknown"
    source_ref: Dict[str, Any] = field(default_factory=dict)
    
    confidence: float = 0.0
    authority: Authority = Authority.UNKNOWN
    sensitivity: float = 0.0
    consent_level: Optional[str] = None
    
    freshness_ts: datetime = field(default_factory=datetime.utcnow)
    last_validated_ts: Optional[datetime] = None
    
    retention_class: RetentionClass = RetentionClass.TRANSIENT
    expires_at: Optional[datetime] = None
    revocable: bool = True
    status: MemoryStatus = MemoryStatus.ACTIVE
    
    supersedes: Optional[UUID] = None
    superseded_by: Optional[UUID] = None
    
    tags: List[str] = field(default_factory=list)
    embedding_status: EmbeddingStatus = EmbeddingStatus.PENDING
    
    hash: str = ""
    version: int = 1
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AuditEvent:
    audit_id: UUID = field(default_factory=uuid4)
    memory_id: Optional[UUID] = None
    event_type: str = "UNKNOWN"
    actor_id: str = "unknown"
    session_id: str = "unknown"
    payload: Dict[str, Any] = field(default_factory=dict)
    hash: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

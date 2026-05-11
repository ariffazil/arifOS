from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
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
    subject: str | None
    content: str
    summary: str | None
    source_type: str
    source_ref: dict[str, Any]
    confidence: float = 0.0
    authority: Authority = Authority.UNKNOWN
    sensitivity: float = 0.0
    consent_level: str | None = None
    tags: list[str] = field(default_factory=list)
    hash: str | None = None


@dataclass
class MemoryRecord:
    memory_id: UUID = field(default_factory=uuid4)
    tenant_id: str = "default"
    actor_id: str = "anonymous"
    session_id: str = "unknown"
    project_id: str | None = None

    type: MemoryType = MemoryType.WORKING
    subject: str | None = None
    content: str = ""
    summary: str | None = None

    source_type: str = "unknown"
    source_ref: dict[str, Any] = field(default_factory=dict)

    confidence: float = 0.0
    authority: Authority = Authority.UNKNOWN
    sensitivity: float = 0.0
    consent_level: str | None = None

    freshness_ts: datetime = field(default_factory=datetime.utcnow)
    last_validated_ts: datetime | None = None

    retention_class: RetentionClass = RetentionClass.TRANSIENT
    expires_at: datetime | None = None
    revocable: bool = True
    status: MemoryStatus = MemoryStatus.ACTIVE

    supersedes: UUID | None = None
    superseded_by: UUID | None = None

    tags: list[str] = field(default_factory=list)
    embedding_status: EmbeddingStatus = EmbeddingStatus.PENDING

    hash: str = ""
    version: int = 1

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AuditEvent:
    audit_id: UUID = field(default_factory=uuid4)
    memory_id: UUID | None = None
    event_type: str = "UNKNOWN"
    actor_id: str = "unknown"
    session_id: str = "unknown"
    payload: dict[str, Any] = field(default_factory=dict)
    hash: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

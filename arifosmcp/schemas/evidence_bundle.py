"""
arifosmcp/schemas/evidence_bundle.py — Canonical EvidenceBundle Schema
═══════════════════════════════════════════════════════════════════════════════

Canonical interface for the SENSE → INGEST → MEMORY pipeline.

Minimum contract that ALL EvidenceBundle-like objects must implement:
  bundle_id, session_id, actor_id, query/input, source/provider,
  claims, receipts, evidence_level, uncertainty, created_at, idempotency_key

Domain models (reality_models.py, contracts.py, etc.) may extend this
but must at minimum satisfy this interface.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceLevel(str, Enum):
    """Evidence determinism tier (L0-L6). Same as EvidenceLevel in evidence/schemas.py."""

    L0 = "L0"  # Offline / no result / contaminated
    L1 = "L1"  # Search snippets only
    L2 = "L2"  # URL ingested
    L3 = "L3"  # Multi-source verified
    L4 = "L4"  # Browser-grade inspection
    L5 = "L5"  # Primary + Corroborated + Archived
    L6 = "L6"  # Reproducible data / direct measurement


class IngestStatus(str, Enum):
    """Result of an ingest operation."""

    SUCCESS = "success"  # Both backends wrote
    PARTIAL_SUCCESS = "partial_success"  # One backend wrote
    SKIPPED = "skipped"  # dry_run=True or empty bundle
    BLOCKED_AUTH_REQUIRED = "blocked_auth_required"  # Not authorized for permanent write
    FAILED = "failed"  # Both backends failed


class ClaimSchema(BaseModel):
    """Atomic claim extracted from evidence."""

    claim_type: str = "statement"  # fact | interpretation | prediction
    text: str
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 1.0
    source_claim_id: str | None = None  # links to source content


class EntitySchema(BaseModel):
    """Named entity extracted from evidence."""

    entity_id: str = Field(default_factory=lambda: f"entity-{uuid.uuid4().hex[:8]}")
    name: str
    type: str | None = None  # PERSON, ORG, LOC, etc.
    aliases: list[str] = Field(default_factory=list)
    source_claim_ids: list[str] = Field(default_factory=list)
    confidence: float = 1.0


class RelationSchema(BaseModel):
    """Typed relationship between two entities or an entity and a value."""

    subject: str
    predicate: str
    object: str | None = None
    relation_type: str | None = None  # works_for, located_in, etc.
    source_claim_id: str | None = None  # links to supporting claim
    confidence: float = 1.0


class ReceiptSchema(BaseModel):
    """Evidence receipt — proof that an observation was made."""

    receipt_id: str = Field(default_factory=lambda: f"receipt://bundle/{uuid.uuid4().hex[:12]}")
    provider: str  # minimax, brave, exa, tavily, firecrawl, ddgs
    bridge: str = "mcp_http_sse"  # how it was retrieved
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    urls_returned: int = 0
    urls_ingested: int = 0  # 0 = snippets only (L1)
    independent_sources_compared: int = 0
    max_evidence_level: EvidenceLevel = EvidenceLevel.L0
    void_flags: list[str] = Field(default_factory=list)  # snippets_only, no_full_page, etc.
    risk_flags: list[str] = Field(default_factory=list)


class CanonicalEvidenceBundle(BaseModel):
    """
    Canonical interface for ALL evidence bundles in the arifOS kernel.

    This is the minimum contract. Domain implementations (reality_models.py,
    contracts.py, etc.) may extend fields but must satisfy this interface.

    Design rules:
    - Never return naked results — always wrap in EvidenceBundle
    - Bundle IS the receipt — receipt IS the bundle
    - No ingest without idempotency key
    - No observation without session_id + actor_id binding
    """

    # ── Identity ──────────────────────────────────────────────────────────
    bundle_id: str = Field(default_factory=lambda: f"eb-{uuid.uuid4().hex[:8]}")
    session_id: str = "global"
    actor_id: str = "anonymous"

    # ── Source ──────────────────────────────────────────────────────────
    query: str = ""
    mode: str = "search"  # search | fetch | ingest | compass
    provider: str = "unknown"  # minimax | brave | exa | tavily | ddgs | firecrawl
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # ── Evidence content ─────────────────────────────────────────────────
    claims: list[ClaimSchema] = Field(default_factory=list)
    receipts: list[ReceiptSchema] = Field(default_factory=list)
    void_flags: list[str] = Field(
        default_factory=list
    )  # snippets_only, no_cross_verification, etc.
    risk_flags: list[str] = Field(default_factory=list)

    # ── Quality metadata ─────────────────────────────────────────────────
    evidence_level: EvidenceLevel = EvidenceLevel.L0
    confidence: float = 0.0  # 0.0-1.0
    uncertainty: float = 0.05  # omega_0 uncertainty band

    # ── Graph enrichment (RELATE — Phase 3) ─────────────────────────────
    entities: list[EntitySchema] = Field(default_factory=list)
    relations: list[RelationSchema] = Field(default_factory=list)

    # ── Persistence contract ────────────────────────────────────────────
    idempotency_key: str | None = None  # sha256(session_id + query + provider + bucket)
    ingested: bool = False  # Has this bundle been written to memory?
    ingest_attempted_at: str | None = None

    # ── Pydantic config ─────────────────────────────────────────────────
    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    # ── Helpers ─────────────────────────────────────────────────────────

    def compute_idempotency_key(
        self,
        timestamp_bucket_hours: int = 1,
    ) -> str:
        """
        Compute deterministic idempotency key.

        Uses session_id + query + provider + hour-bucket to produce
        a key that is stable within the bucket but unique across queries.

        Args:
            timestamp_bucket_hours: Size of the time bucket (default 1h).
                Use 24 for daily deduplication.
        """
        # Normalize timestamp to hour bucket
        ts = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        bucket = ts.replace(minute=0, second=0, microsecond=0)
        if timestamp_bucket_hours > 1:
            bucket = bucket.replace(hour=bucket.hour - (bucket.hour % timestamp_bucket_hours))

        key_input = f"{self.session_id}::{self.query}::{self.provider}::{bucket.isoformat()}"
        return hashlib.sha256(key_input.encode()).hexdigest()[:32]

    def ensure_idempotency_key(self) -> None:
        """Compute and assign idempotency_key if not set."""
        if not self.idempotency_key:
            self.idempotency_key = self.compute_idempotency_key()

    def to_memory_content(self) -> dict[str, Any]:
        """
        Serialize bundle for memory store.

        The content field in memory_store.store() receives this structure.
        """
        self.ensure_idempotency_key()
        return {
            "bundle_id": self.bundle_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "query": self.query,
            "mode": self.mode,
            "provider": self.provider,
            "created_at": self.created_at,
            "evidence_level": self.evidence_level.value,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "claims_count": len(self.claims),
            "receipts_count": len(self.receipts),
            "void_flags": self.void_flags,
            "entities_count": len(self.entities),
            "relations_count": len(self.relations),
            "idempotency_key": self.idempotency_key,
            "claims": [c.model_dump(mode="json") for c in self.claims],
            "receipts": [r.model_dump(mode="json") for r in self.receipts],
            "entities": [e.model_dump(mode="json") for e in self.entities],
            "relations": [rel.model_dump(mode="json") for rel in self.relations],
        }


class IngestResult(BaseModel):
    """
    Result of an ingest_evidence_bundle() call.

    Returned to caller so they know what was written and to which backend.
    Authorization gates must ALL be True for permanent writes:
      - dry_run=False
      - authorized=True
      - session_verified=True
      - sovereign_ack=True
    """

    status: IngestStatus = IngestStatus.SKIPPED
    bundle_id: str | None = None
    memory_id: str | None = None  # from memory_store.store()
    qdrant_written: bool = False
    postgres_written: bool = False
    idempotency_key: str | None = None
    dry_run: bool = True
    authorized: bool = False  # Phase 2: caller must explicitly authorize
    session_verified: bool = False  # Phase 2: session is verified
    sovereign_ack: bool = False  # Phase 2: human sovereign ack obtained
    blocked_reason: str | None = None  # Phase 2: why auth was blocked
    error: str | None = None
    backend_errors: dict[str, str] = Field(default_factory=dict)
    recall_verified: bool = False  # Phase 2: bundle was recalled after write
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    model_config = {"extra": "forbid", "str_strip_whitespace": True}

    def compute_status(self) -> IngestStatus:
        """Derive ingest status from backend write results and auth state."""
        if self.dry_run:
            return IngestStatus.SKIPPED
        # Phase 2: check authorization gates
        if not (self.authorized and self.session_verified and self.sovereign_ack):
            return IngestStatus.BLOCKED_AUTH_REQUIRED
        if self.qdrant_written and self.postgres_written:
            return IngestStatus.SUCCESS
        if self.qdrant_written or self.postgres_written:
            return IngestStatus.PARTIAL_SUCCESS
        return IngestStatus.FAILED

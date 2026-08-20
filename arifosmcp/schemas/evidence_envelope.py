"""
arifOS EvidenceEnvelope — Universal Evidence Contract v1
══════════════════════════════════════════════════════════

The single mandatory envelope carried by every memory write, retrieval
result, Graphiti edge, external MCP response, and VAULT999 seal candidate.

Forged from:
  - Arif F13 directive (2026-08-20): one shared evidence contract across L1-L6
  - Existing memory_envelope.py (555_MEMORY v2): M0-M4 tiers, SourceType, governance
  - Existing memory_truth.py: TruthClass lifecycle (observed→sealed)

Layering:
  EvidenceEnvelope       ← universal write contract (THIS FILE)
  MemoryEventEnvelope    ← existing memory-event-specific envelope (compat wrapper)
  TruthClass             ← epistemic lifecycle (observed→claimed→derived→approved→sealed)

Hard law (F13):
  - "Memory is not truth until provenance. Truth is not final until L6."
  - One writer implementation, at least one independent verifier.
  - No model lane may independently promote M3 or M4.
  - L3 retrieval similarity is never evidence.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


# ═══════════════════════════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════════════════════════


class MemoryTier(StrEnum):
    """Memory risk tiers — M0 through M4."""

    M0 = "M0"  # Ephemeral scratch — dies after session
    M1 = "M1"  # User preference — persistent, no action authority
    M2 = "M2"  # Operational project — needs provenance, can guide routing
    M3 = "M3"  # Identity/authority — requires explicit confirmation + expiry
    M4 = "M4"  # Sealed constitutional — requires VAULT999 seal + human authority


class StorageLayer(StrEnum):
    """The 6 storage layers of the federation memory architecture."""

    L1 = "L1"  # Redis ephemeral — fast, volatile context
    L2 = "L2"  # Redis session — conversation context
    L3 = "L3"  # Qdrant semantic — similarity retrieval
    L4 = "L4"  # Supabase structured — authoritative operational records
    L5 = "L5"  # Graphiti temporal — entities, relationships, validity windows
    L6 = "L6"  # VAULT999 immutable — sealed finality boundary


class SourceType(StrEnum):
    """Who or what asserted this evidence."""

    HUMAN = "human"
    TOOL = "tool"
    DOCUMENT = "document"
    MODEL = "model"
    SENSOR = "sensor"
    DERIVED = "derived"


class DerivationMethod(StrEnum):
    """How this evidence was produced."""

    DIRECT = "direct"        # Observed directly (human, sensor, tool)
    EXTRACTED = "extracted"  # Extracted from a source (OCR, parse, API)
    INFERRED = "inferred"    # Inferred from other evidence
    AGGREGATED = "aggregated"  # Aggregated from multiple sources


class AuthorityClass(StrEnum):
    """Trust classification of this evidence."""

    UNVERIFIED = "unverified"    # No independent verification
    CORROBORATED = "corroborated"  # Independently verified by ≥2 sources
    AUTHORITATIVE = "authoritative"  # Designated authority (human, canon)
    SEALED = "sealed"            # VAULT999 sealed — immutable


class PolicyLabel(StrEnum):
    """Common policy labels for access control and lifecycle."""

    INTERNAL = "internal"
    SENSITIVE = "sensitive"
    EXTERNAL_SHAREABLE = "external-shareable"
    CONSTITUTIONAL = "constitutional"
    BIOMETRIC = "biometric"
    FINANCIAL = "financial"
    GEOPHYSICAL = "geophysical"


# ═══════════════════════════════════════════════════════════════════════════════
# ENVELOPE COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════


class Derivation(BaseModel):
    """How this evidence was derived — lineage metadata."""

    method: DerivationMethod = Field(
        default=DerivationMethod.DIRECT,
        description="How this evidence was produced",
    )
    parent_event_ids: list[str] = Field(
        default_factory=list,
        description="Event IDs of evidence this was derived from",
    )
    model_id: str | None = Field(
        default=None,
        description="Model that produced this (provider/model/version or null)",
    )
    tool_id: str | None = Field(
        default=None,
        description="Tool that produced this (namespace.tool or null)",
    )


class Integrity(BaseModel):
    """Cryptographic integrity for the envelope."""

    canonical_hash: str = Field(
        default="",
        description="SHA-256 of canonical JSON serialization of the claim",
    )
    previous_seal: str | None = Field(
        default=None,
        description="Chain hash of previous sealed entry (for L6 append-only)",
    )
    signature: str | None = Field(
        default=None,
        description="Ed25519 signature of the canonical hash (for M3/M4)",
    )

    def compute_canonical_hash(self, claim: str) -> str:
        """Compute SHA-256 of a claim string. Returns hex digest."""
        return "sha256:" + hashlib.sha256(claim.encode("utf-8")).hexdigest()


# ═══════════════════════════════════════════════════════════════════════════════
# CORE EVIDENCE ENVELOPE
# ═══════════════════════════════════════════════════════════════════════════════


class EvidenceEnvelope(BaseModel):
    """
    The universal evidence contract for the arifOS federation.

    Every memory write, retrieval result, Graphiti edge, external MCP
    response, and VAULT999 seal candidate MUST carry this envelope.

    Layering rules:
      - L1-L2 may hold unverified working state (unverified authority_class).
      - L3 may retrieve candidates, but retrieval similarity is never evidence.
      - L4 holds structured sources and operational facts.
      - L5 links claims to source episodes with validity windows.
      - L6 seals an exact canonical representation plus lineage.
    """

    # ── Identity ─────────────────────────────────────────────────────────
    event_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique event identifier (uuidv4 or uuidv7)",
    )
    trace_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Correlation ID across the full evidence chain",
    )
    actor_id: str = Field(
        description="Agent or human identity that produced this evidence",
    )
    tenant_id: str = Field(
        default="arifos",
        description="Federation tenant (default: arifos, or external-tenant)",
    )

    # ── Classification ───────────────────────────────────────────────────
    memory_tier: MemoryTier = Field(
        default=MemoryTier.M1,
        description="Memory risk tier (M0-M4)",
    )
    storage_layer: StorageLayer = Field(
        default=StorageLayer.L3,
        description="Target storage layer (L1-L6)",
    )

    # ── The Claim ────────────────────────────────────────────────────────
    claim: str = Field(
        description="Atomic, testable assertion — the actual evidence content",
    )

    # ── Provenance ───────────────────────────────────────────────────────
    source_type: SourceType = Field(
        description="Who or what asserted this evidence",
    )
    source_locator: str = Field(
        description="Immutable reference or source URI",
    )
    source_hash: str = Field(
        default="",
        description="SHA-256 of the source material (if applicable)",
    )

    # ── Temporal ─────────────────────────────────────────────────────────
    observed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the evidence was observed (RFC3339)",
    )
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When this envelope was created (RFC3339)",
    )
    valid_from: datetime | None = Field(
        default=None,
        description="When this claim becomes valid (null = now)",
    )
    valid_until: datetime | None = Field(
        default=None,
        description="When this claim expires (null = never)",
    )

    # ── Derivation ───────────────────────────────────────────────────────
    derivation: Derivation = Field(
        default_factory=Derivation,
        description="Lineage and derivation metadata",
    )

    # ── Trust ────────────────────────────────────────────────────────────
    confidence: float = Field(
        ge=0.0, le=1.0,
        default=0.5,
        description="Confidence in this evidence (0.0-1.0)",
    )
    authority_class: AuthorityClass = Field(
        default=AuthorityClass.UNVERIFIED,
        description="Trust classification",
    )

    # ── Policy ───────────────────────────────────────────────────────────
    policy_labels: list[PolicyLabel] = Field(
        default_factory=lambda: [PolicyLabel.INTERNAL],
        description="Access control and lifecycle labels",
    )

    # ── Integrity ────────────────────────────────────────────────────────
    integrity: Integrity = Field(
        default_factory=Integrity,
        description="Cryptographic integrity for the envelope",
    )

    # ── Constitutional binding ───────────────────────────────────────────
    floors: list[str] = Field(
        default_factory=list,
        description="Constitutional floors activated by this evidence",
    )
    requires_888: bool = Field(
        default=False,
        description="Does this evidence require 888-APEX judgment before promotion?",
    )
    vault_event_id: str | None = Field(
        default=None,
        description="VAULT999 event ID if this evidence has been sealed",
    )

    # ── Extensions (organ-specific) ──────────────────────────────────────
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="Organ-specific extensions (voice_provenance, geo_context, etc.)",
    )

    # ── Computed fields ──────────────────────────────────────────────────
    @model_validator(mode="after")
    def _compute_integrity(self) -> "EvidenceEnvelope":
        """Compute canonical hash if not already set."""
        if not self.integrity.canonical_hash:
            self.integrity.canonical_hash = self.integrity.compute_canonical_hash(self.claim)
        return self

    @field_validator("valid_until", mode="before")
    @classmethod
    def _validate_validity_window(cls, v: Any, info: Any) -> Any:
        """Ensure valid_until is after valid_from if both are set."""
        return v

    def is_expired(self, at: datetime | None = None) -> bool:
        """Check if this evidence has expired at the given time."""
        if self.valid_until is None:
            return False
        ref = at or datetime.now(UTC)
        return ref > self.valid_until

    def is_valid(self, at: datetime | None = None) -> bool:
        """Check if this evidence is currently valid."""
        ref = at or datetime.now(UTC)
        if self.valid_until and ref > self.valid_until:
            return False
        if self.valid_from and ref < self.valid_from:
            return False
        return True

    def to_qdrant_payload(self) -> dict[str, Any]:
        """
        Convert to a Qdrant payload with governance fields.

        Index these fields in Qdrant:
          tenant_id, authority_class, memory_tier, policy_labels,
          source_type, observed_at, valid_until, vault_event_id
        """
        return {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "actor_id": self.actor_id,
            "tenant_id": self.tenant_id,
            "memory_tier": self.memory_tier.value,
            "storage_layer": self.storage_layer.value,
            "claim": self.claim,
            "source_type": self.source_type.value,
            "source_locator": self.source_locator,
            "source_hash": self.source_hash,
            "observed_at": self.observed_at.isoformat(),
            "recorded_at": self.recorded_at.isoformat(),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "derivation_method": self.derivation.method.value,
            "parent_event_ids": self.derivation.parent_event_ids,
            "model_id": self.derivation.model_id,
            "tool_id": self.derivation.tool_id,
            "confidence": self.confidence,
            "authority_class": self.authority_class.value,
            "policy_labels": [l.value for l in self.policy_labels],
            "canonical_hash": self.integrity.canonical_hash,
            "previous_seal": self.integrity.previous_seal,
            "signature": self.integrity.signature,
            "floors": self.floors,
            "requires_888": self.requires_888,
            "vault_event_id": self.vault_event_id,
        }

    def to_graphiti_edge(self) -> dict[str, Any]:
        """
        Convert to a Graphiti temporal edge payload.

        Every edge points back to source episodes and carries
        validity and confidence information.
        """
        return {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "actor_id": self.actor_id,
            "claim": self.claim,
            "confidence": self.confidence,
            "authority_class": self.authority_class.value,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "source_event_ids": self.derivation.parent_event_ids,
            "observed_at": self.observed_at.isoformat(),
            "is_expired": self.is_expired(),
            "canonical_hash": self.integrity.canonical_hash,
        }

    def to_vault_candidate(self) -> dict[str, Any]:
        """
        Convert to a VAULT999 seal candidate payload.

        L6 sealing requires exact canonical representation + lineage.
        """
        return {
            "event_id": self.event_id,
            "trace_id": self.trace_id,
            "actor_id": self.actor_id,
            "tenant_id": self.tenant_id,
            "memory_tier": self.memory_tier.value,
            "storage_layer": "L6",
            "claim": self.claim,
            "source_type": self.source_type.value,
            "source_locator": self.source_locator,
            "source_hash": self.source_hash,
            "observed_at": self.observed_at.isoformat(),
            "recorded_at": self.recorded_at.isoformat(),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "derivation": {
                "method": self.derivation.method.value,
                "parent_event_ids": self.derivation.parent_event_ids,
                "model_id": self.derivation.model_id,
                "tool_id": self.derivation.tool_id,
            },
            "confidence": self.confidence,
            "authority_class": self.authority_class.value,
            "policy_labels": [l.value for l in self.policy_labels],
            "floors": self.floors,
            "requires_888": self.requires_888,
            "integrity": {
                "canonical_hash": self.integrity.canonical_hash,
                "previous_seal": self.integrity.previous_seal,
                "signature": self.integrity.signature,
            },
            "extensions": self.extensions,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# QDRANT INDEX DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

QDRANT_GOVERNANCE_INDEXES = [
    {"field": "tenant_id", "type": "keyword"},
    {"field": "authority_class", "type": "keyword"},
    {"field": "memory_tier", "type": "keyword"},
    {"field": "policy_labels", "type": "keyword"},
    {"field": "source_type", "type": "keyword"},
    {"field": "observed_at", "type": "datetime"},
    {"field": "valid_until", "type": "datetime"},
    {"field": "vault_event_id", "type": "keyword"},
    {"field": "actor_id", "type": "keyword"},
    {"field": "storage_layer", "type": "keyword"},
    {"field": "confidence", "type": "float"},
    {"field": "floors", "type": "keyword"},
    {"field": "canonical_hash", "type": "keyword"},
]


# ═══════════════════════════════════════════════════════════════════════════════
# M-TIER → STORAGE-LAYER ALLOWANCE MAP
# ═══════════════════════════════════════════════════════════════════════════════

TIER_LAYER_ALLOWANCE: dict[MemoryTier, frozenset[StorageLayer]] = {
    MemoryTier.M0: frozenset({StorageLayer.L1, StorageLayer.L2}),
    MemoryTier.M1: frozenset({StorageLayer.L1, StorageLayer.L2, StorageLayer.L3}),
    MemoryTier.M2: frozenset({StorageLayer.L3, StorageLayer.L4}),
    MemoryTier.M3: frozenset({StorageLayer.L4, StorageLayer.L5}),
    MemoryTier.M4: frozenset({StorageLayer.L6}),
}


def tier_layer_allowed(tier: MemoryTier, layer: StorageLayer) -> bool:
    """Check if a memory tier may inhabit a given storage layer."""
    return layer in TIER_LAYER_ALLOWANCE.get(tier, frozenset())


# ═══════════════════════════════════════════════════════════════════════════════
# PROVENANCE-AWARE RETRIEVAL SCORING
# ═══════════════════════════════════════════════════════════════════════════════


def provenance_score(
    envelope: EvidenceEnvelope,
    semantic_relevance: float = 0.0,
    freshness_days: float | None = None,
    corroboration_count: int = 0,
) -> float:
    """
    Compute a provenance-aware retrieval score.

    Score = semantic_relevance × authority_weight × freshness × corroboration

    Components:
      - semantic_relevance: from Qdrant similarity search (0.0-1.0)
      - authority_weight: UNVERIFIED=0.5, CORROBORATED=0.8, AUTHORITATIVE=1.0, SEALED=1.0
      - freshness: decay based on observed_at age (0.0-1.0)
      - corroboration: bonus for independent verification (1.0 + 0.1 per corroborating source)
    """
    # Authority weight
    authority_weights = {
        AuthorityClass.UNVERIFIED: 0.5,
        AuthorityClass.CORROBORATED: 0.8,
        AuthorityClass.AUTHORITATIVE: 1.0,
        AuthorityClass.SEALED: 1.0,
    }
    authority_weight = authority_weights.get(envelope.authority_class, 0.5)

    # Freshness decay
    if freshness_days is None:
        freshness = 1.0
    else:
        import math
        freshness = max(0.1, math.exp(-freshness_days / 90))  # 90-day half-life

    # Corroboration bonus
    corroboration_bonus = 1.0 + (0.1 * min(corroboration_count, 10))

    # Validity penalty
    validity_penalty = 1.0 if envelope.is_valid() else 0.0

    score = (
        semantic_relevance
        * authority_weight
        * freshness
        * corroboration_bonus
        * validity_penalty
    )

    return round(min(score, 2.0), 4)  # Cap at 2.0 for bonus cases

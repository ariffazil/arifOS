"""
arifOS Record V1 Envelope — Canonical Record Schema
=====================================================

CloudEvents-inspired record envelope for arifOS federation records.
Defines the contract for arifos.record.v1 format: a versioned, schema-validated
envelope that wraps all arifOS records (receipts, seals, attestations, events).

Design principles (from CloudEvents v1.0 + Stripe date-pinned versioning):
  - specversion distinguishes envelope format from payload version
  - type carries semantic record type with optional version suffix
  - All fields are additive-only — new fields don't break old readers
  - dataschema is informational (URI to payload schema), not enforcement
  - source is a URI identifying the originating organ

Pattern: CloudEvents JSON envelope + Pydantic validation
Reference: CloudEvents spec v1.0, xRegistry message spec
Forged: 2026-07-29 — Gap 2 entropy remediation

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

# ── Canonical record type registry ──────────────────────────────────────────

CANONICAL_RECORD_TYPES = frozenset(
    {
        "arifos.record.v1.receipt",
        "arifos.record.v1.seal",
        "arifos.record.v1.attestation",
        "arifos.record.v1.event",
        "arifos.record.v1.session",
        "arifos.record.v1.verdict",
        "arifos.record.v1.cooling",
        "arifos.record.v1.scar",
    }
)


# ── Schema ───────────────────────────────────────────────────────────────────


class RecordV1Envelope(BaseModel):
    """
    Canonical arifos.record.v1 envelope.

    Every record flowing through the arifOS federation MUST conform to this
    schema. The envelope is the contract — the payload is the evidence.

    Specversion "1.0" identifies this envelope format. Future versions
    (1.1, 2.0) MUST be backward-compatible per Stripe additive-only policy.
    """

    # ── REQUIRED (CloudEvents core) ──
    specversion: Literal["1.0"] = Field(
        default="1.0",
        description="Envelope format version. Always '1.0' for this schema.",
    )
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique record ID (UUID v4).",
        min_length=8,
        max_length=64,
    )
    type: str = Field(
        ...,
        description=(
            "Semantic record type. MUST match pattern arifos.record.v<major>.<kind>. "
            "E.g. arifos.record.v1.receipt, arifos.record.v1.seal. "
            "New kinds MAY be added additively without breaking old readers."
        ),
        pattern=r"^arifos\.record\.v\d+\.[a-z_]+$",
    )
    source: str = Field(
        ...,
        description="Originating organ URI. E.g. arifos://kernel, aforge://executor, geox://earth.",
        min_length=3,
        max_length=256,
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of record creation.",
    )

    # ── REQUIRED (payload) ──
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Record payload. Schema determined by `type` and optionally validated against `dataschema`.",
    )

    # ── OPTIONAL (CloudEvents optional + arifOS extensions) ──
    dataschema: str | None = Field(
        default=None,
        description="URI to JSON Schema for payload validation. Informational.",
    )
    subject: str | None = Field(
        default=None,
        description="Subject of the record (e.g. agent_id, organ name).",
        max_length=128,
    )
    datacontenttype: str = Field(
        default="application/json",
        description="Content type of data. Default: application/json.",
    )
    receipt_id: str | None = Field(
        default=None,
        description="Linked receipt ID for cross-referencing.",
    )
    constitutional_chain_id: str | None = Field(
        default=None,
        description="Constitutional chain ID from arif_judge if this record has a verdict.",
    )
    session_id: str | None = Field(
        default=None,
        description="Governing session ID from arif_init.",
    )
    actor_id: str | None = Field(
        default=None,
        description="Actor who produced this record.",
    )

    # ── Metadata extensions (additive-only, CloudEvents extension pattern) ──
    tags: list[str] = Field(
        default_factory=list,
        description="Additive tags for filtering and discovery.",
    )
    previous_hash: str | None = Field(
        default=None,
        description="SHA-256 of previous record for hash-chain integrity.",
    )

    # ── Validators ──

    @field_validator("type")
    @classmethod
    def _check_type_is_registered(cls, v: str) -> str:
        """Warn on unregistered types but don't reject — additive evolution."""
        if v not in CANONICAL_RECORD_TYPES:
            import logging

            logging.getLogger(__name__).warning(
                "Record type %s is not in CANONICAL_RECORD_TYPES. "
                "This is acceptable for extension types but should be registered.",
                v,
            )
        return v

    @field_validator("timestamp")
    @classmethod
    def _validate_iso8601(cls, v: str) -> str:
        """Ensure timestamp is valid ISO 8601."""
        try:
            datetime.fromisoformat(v)
        except ValueError as e:
            raise ValueError(f"timestamp must be valid ISO 8601: {e}") from e
        return v

    @field_validator("previous_hash")
    @classmethod
    def _validate_sha256_hex(cls, v: str | None) -> str | None:
        """Ensure previous_hash is valid hex if present."""
        if v is not None and not re.fullmatch(r"^[0-9a-f]{64}$", v, re.IGNORECASE):
            raise ValueError("previous_hash must be a 64-character hex SHA-256 digest")
        return v


# ── Validation helpers ───────────────────────────────────────────────────────


def validate_record_envelope(data: dict[str, Any]) -> RecordV1Envelope:
    """
    Validate and normalize a dict into a RecordV1Envelope.

    Raises pydantic.ValidationError if the record doesn't conform.
    Use this as the single entry point for all record ingestion.

    Usage:
        try:
            record = validate_record_envelope(incoming_dict)
            # Process valid record...
        except ValidationError as e:
            # Reject or normalize via legacy_adapter
    """
    return RecordV1Envelope(**data)


def is_valid_record_envelope(data: dict[str, Any]) -> bool:
    """Non-throwing check: does this dict conform to record.v1 schema?"""
    try:
        validate_record_envelope(data)
        return True
    except Exception:
        return False


def create_record(
    type_: str,
    source: str,
    data: dict[str, Any],
    *,
    session_id: str | None = None,
    actor_id: str | None = None,
    receipt_id: str | None = None,
    constitutional_chain_id: str | None = None,
    previous_hash: str | None = None,
    tags: list[str] | None = None,
    **extra: Any,
) -> RecordV1Envelope:
    """
    Factory: create a valid RecordV1Envelope with defaults.

    This is the canonical way to create records — no manual dict construction.
    """
    return RecordV1Envelope(
        type=type_,
        source=source,
        data=data,
        session_id=session_id,
        actor_id=actor_id,
        receipt_id=receipt_id,
        constitutional_chain_id=constitutional_chain_id,
        previous_hash=previous_hash,
        tags=tags or [],
        **extra,
    )

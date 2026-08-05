"""
arifOS Legacy Record Adapter — Pre-V1 Format Normalization
===========================================================

Read-side normalization for records produced before arifos.record.v1.
Follows the DataHub internal schema registry pattern + Apache Avro
reader/writer schema resolution.

Design principles:
  - Writers always produce in current format (v1).
  - Readers handle ALL formats via normalizer registry.
  - Normalizers are pure functions: legacy_dict → RecordV1Envelope.
  - Version detection is automatic via _format or specversion field.
  - Unknown formats raise ValueError — fail loud, not silent corruption.

Pattern: MultiSchemaDeserializer<V1, V2> from Kafka Avro ecosystem.
         DataHub SchemaIdOrdinal + versioned schema mapping.
         CloudEvents specversion routing.

Forged: 2026-07-29 — Gap 4 entropy remediation

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from arifosmcp.abi.record_v1 import RecordV1Envelope

logger = logging.getLogger(__name__)

# ── Normalizer registry ─────────────────────────────────────────────────────
# Pattern: @register_normalizer("format_key") to add a migration
# Each normalizer: legacy_dict → dict (ready for RecordV1Envelope)

NORMALIZERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {}


def _safe_record_kind(prefix: str, format_name: str) -> str:
    """Build a schema-safe semantic kind while retaining the raw format in data."""
    fragment = "".join(
        character if character.isalpha() or character == "_" else "_"
        for character in format_name.lower()
    ).strip("_")
    return f"{prefix}_{fragment}" if fragment else prefix


def register_normalizer(from_version: str):
    """
    Decorator: register a pre-v1 format normalizer.

    Usage:
        @register_normalizer("pre-v1")
        def _normalize_legacy(record: dict) -> dict: ...
    """

    def decorator(fn: Callable[[dict[str, Any]], dict[str, Any]]):
        NORMALIZERS[from_version] = fn
        return fn

    return decorator


# ── Version detection ────────────────────────────────────────────────────────


def _detect_format(raw: dict[str, Any]) -> str:
    """
    Detect the format version of a raw record dict.

    Detection priority:
      1. _format field (explicit marker, e.g. "seal_receipt_v0")
      2. specversion field (CloudEvents-compatible, e.g. "1.0")
      3. Heuristic: presence of legacy fields → "pre-v1"
      4. Fallback: "unknown"

    Returns the format key used to look up a normalizer.
    """
    # Explicit format marker
    fmt = raw.get("_format", "")
    if fmt:
        return str(fmt)

    # CloudEvents specversion
    spec = raw.get("specversion", "")
    if spec:
        return spec

    # Heuristic detection of legacy formats
    if "seal_id" in raw or "receipt_sha" in raw or "vault_seq" in raw:
        return "seal_receipt_v0"
    if "agent_session" in raw and "actor" in raw:
        return "session_v0"
    if "claim_text" in raw and "evidence_for" in raw:
        return "claim_v0"
    # Broad legacy catch: kind + organ fields (pre-v1 general)
    if "kind" in raw or "organ" in raw:
        return "pre-v1"
    # verdict + actor without specversion = legacy
    if "verdict" in raw and "actor" in raw and "specversion" not in raw:
        return "pre-v1"

    return "unknown"


# ── Core normalization function ──────────────────────────────────────────────


def normalize_to_v1(raw: dict[str, Any], *, strict: bool = False) -> RecordV1Envelope:
    """
    Normalize any raw record dict into a RecordV1Envelope.

    Detection → Normalizer lookup → Transform → Validate.

    Args:
        raw: Raw record dict (any format).
        strict: If True, raise on unknown formats. If False, wrap as-is.

    Returns:
        Validated RecordV1Envelope.

    Raises:
        ValueError: If format is unknown and strict=True.
        ValidationError: If the normalized result doesn't pass schema validation.

    Pattern: DataHub SchemaRegistryServiceImpl.getSchemaForTopicAndVersion()
             with auto-fallback to legacy normalizer.
    """
    # Fast path: already v1
    if raw.get("specversion") == "1.0" and raw.get("type", "").startswith("arifos.record.v"):
        try:
            return RecordV1Envelope(**raw)
        except Exception:
            # Malformed v1 — fall through to normalizer
            pass

    fmt = _detect_format(raw)
    normalizer = NORMALIZERS.get(fmt)

    if normalizer is not None:
        try:
            normalized = normalizer(raw)
            # Ensure id meets min length (pad legacy short IDs)
            if "id" in normalized and len(normalized["id"]) < 8:
                normalized["id"] = f"legacy-{normalized['id']}"
            # Ensure source meets min length (pad short organ names)
            if "source" in normalized and len(normalized["source"]) < 3:
                normalized["source"] = f"arifos://{normalized['source']}"
            # Ensure type is set after normalization
            if "type" not in normalized:
                normalized["type"] = f"arifos.record.v1.{_safe_record_kind('migrated', fmt)}"
            return RecordV1Envelope(**normalized)
        except Exception as e:
            logger.error("Normalizer %s failed for record %s: %s", fmt, raw.get("id", "?"), e)
            raise

    if strict or (fmt == "unknown" and strict):
        raise ValueError(
            f"Unknown record format '{fmt}'. "
            f"Cannot normalize. Register a normalizer via @register_normalizer('{fmt}'). "
            f"Raw keys: {list(raw.keys())[:10]}"
        )

    # Non-strict unknown: wrap as generic event
    logger.warning(
        "Unknown format '%s' — wrapping as generic v1 event. Keys: %s", fmt, list(raw.keys())[:5]
    )
    return RecordV1Envelope(
        type=f"arifos.record.v1.{_safe_record_kind('unknown', fmt)}",
        source="arifos://kernel/legacy-adapter",
        data={"_raw": raw, "_format": fmt},
        tags=["legacy", "auto-wrapped"],
    )


# ── Built-in normalizers ─────────────────────────────────────────────────────


@register_normalizer("pre-v1")
def _normalize_generic_legacy(record: dict[str, Any]) -> dict[str, Any]:
    """
    Generic pre-v1 normalizer. Handles records that have no explicit format
    marker but were produced before the record.v1 envelope existed.

    Maps common legacy fields to v1 envelope fields.
    Detects record kind from content when `kind` field is absent.
    """
    # Detect semantic kind from content
    kind = record.get("kind", "unknown")
    if kind == "unknown":
        if "verdict" in record:
            kind = record["verdict"].lower()
        elif "claim_text" in record:
            kind = "claim"

    return {
        "specversion": "1.0",
        "id": record.get("id") or record.get("receipt_id") or record.get("seal_id") or str(uuid4()),
        "type": f"arifos.record.v1.{kind}",
        "source": record.get("source") or record.get("organ") or "arifos://kernel/legacy",
        "timestamp": record.get("ts")
        or record.get("timestamp")
        or record.get("created_at")
        or datetime.now(UTC).isoformat(),
        "data": {
            k: v
            for k, v in record.items()
            if k
            not in (
                "id",
                "receipt_id",
                "seal_id",
                "kind",
                "source",
                "organ",
                "ts",
                "timestamp",
                "created_at",
                "specversion",
                "type",
                "_format",
            )
        },
        "tags": ["legacy", "migrated-pre-v1"],
    }


@register_normalizer("seal_receipt_v0")
def _normalize_seal_receipt_v0(record: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize legacy seal_receipt_v0 format.
    Fields: seal_id, receipt_sha, vault_seq, verdict, actor, ts
    """
    return {
        "specversion": "1.0",
        "id": record.get("seal_id") or record.get("receipt_id") or str(uuid4()),
        "type": "arifos.record.v1.receipt",
        "source": "arifos://vault999/legacy-seal",
        "timestamp": record.get("ts") or datetime.now(UTC).isoformat(),
        "data": {
            "verdict": record.get("verdict") or record.get("verdict_issued", "UNKNOWN"),
            "actor": record.get("actor", "unknown"),
            "vault_seq": record.get("vault_seq", 0),
            "receipt_sha": record.get("receipt_sha", ""),
            "legacy_payload": {
                k: v
                for k, v in record.items()
                if k
                not in (
                    "seal_id",
                    "receipt_id",
                    "receipt_sha",
                    "vault_seq",
                    "verdict",
                    "actor",
                    "ts",
                )
            },
        },
        "receipt_id": record.get("receipt_id"),
        "tags": ["legacy", "seal-receipt-v0"],
    }


@register_normalizer("session_v0")
def _normalize_session_v0(record: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize legacy session_v0 format.
    Fields: agent_session, actor, intent, verdict, opened_at
    """
    return {
        "specversion": "1.0",
        "id": record.get("agent_session") or str(uuid4()),
        "type": "arifos.record.v1.session",
        "source": "arifos://kernel/legacy-session",
        "timestamp": record.get("opened_at") or datetime.now(UTC).isoformat(),
        "data": {
            "actor": record.get("actor", "unknown"),
            "intent": record.get("intent", ""),
            "verdict": record.get("verdict") or record.get("verdict_issued", "UNKNOWN"),
        },
        "actor_id": record.get("actor"),
        "session_id": (
            record.get("session_id")
            or record.get("agent_session")
            or record.get("session")
        ),
        "tags": ["legacy", "session-v0"],
    }


@register_normalizer("claim_v0")
def _normalize_claim_v0(record: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize legacy claim_v0 format (GEOX claims).
    Fields: claim_text, evidence_for, evidence_against, claim_type, truth_class
    """
    return {
        "specversion": "1.0",
        "id": record.get("claim_id") or str(uuid4()),
        "type": "arifos.record.v1.event",
        "source": "geox://earth/legacy-claim",
        "timestamp": record.get("created_at") or datetime.now(UTC).isoformat(),
        "data": {
            "claim_text": record.get("claim_text", ""),
            "claim_type": record.get("claim_type", "other"),
            "truth_class": record.get("truth_class", "INTERPRETATION"),
            "evidence_for": record.get("evidence_for", []),
            "evidence_against": record.get("evidence_against", []),
        },
        "tags": ["legacy", "claim-v0", "geox"],
    }


# ── Batch normalization ──────────────────────────────────────────────────────


def normalize_batch(
    records: list[dict[str, Any]], *, strict: bool = False
) -> list[RecordV1Envelope]:
    """
    Normalize a batch of raw records. Failed records are logged and skipped
    unless strict=True (raises immediately).

    Returns list of successfully normalized RecordV1Envelopes.
    """
    results: list[RecordV1Envelope] = []
    for i, raw in enumerate(records):
        try:
            results.append(normalize_to_v1(raw, strict=strict))
        except Exception as e:
            logger.warning("Batch normalization failed at index %d: %s", i, e)
            if strict:
                raise
    return results


# ── Adapter health ───────────────────────────────────────────────────────────


def adapter_status() -> dict[str, Any]:
    """Return adapter health: registered normalizers, supported formats."""
    return {
        "ready": True,
        "registered_formats": list(NORMALIZERS.keys()),
        "normalizer_count": len(NORMALIZERS),
        "detection_mode": "auto",
        "v1_schema": "arifos.record.v1",
    }

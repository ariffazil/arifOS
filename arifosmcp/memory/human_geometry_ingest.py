"""
Human Sovereign Geometry → arifOS L4 Ingestion
═══════════════════════════════════════════════

Reads the intake-ritual envelope from WELL and stores the canonical
sovereign geometry in arifOS memory at L4 (structured/canonical).

Identity data belongs in arifOS (identity/governance organ), not in
WELL (vitality organ). The envelope becomes a thin reference; canonical
data lives here.

DITEMPA BUKAN DIBERI — geometry is forged, not given.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from pathlib import Path
from uuid import uuid4

from .types import (
    Authority,
    MemoryRecord,
    MemoryType,
    RetentionClass,
)

logger = logging.getLogger(__name__)

ENVELOPE_PATH = Path("/root/WELL/envelopes/arif-envelope.json")

# The 5 axes of Human Sovereign Geometry
GEOMETRY_AXES = ["values", "direction", "scars", "shadow", "boundary"]

SUMMARY = (
    "Human Sovereign Geometry — 5-axis intake: "
    "Amanah, Direction, Scars, Shadow, Daulat"
)


def load_envelope(path: Path = ENVELOPE_PATH) -> dict:
    """Load the raw envelope JSON from WELL."""
    with open(path) as f:
        return json.load(f)


def extract_geometry(envelope: dict) -> dict:
    """Extract the 5-axis geometry, excluding vitality (belongs in WELL)."""
    planes = envelope.get("planes", {})
    geometry = {}
    for axis in GEOMETRY_AXES:
        if axis in planes:
            geometry[axis] = planes[axis]
    return geometry


def build_geometry_record(envelope: dict) -> MemoryRecord:
    """Build a MemoryRecord for sovereign geometry storage at L4."""
    geometry = extract_geometry(envelope)
    human_id = envelope.get("human_id", "arif")

    # Build structured content
    content_payload = {
        "human_id": human_id,
        "geometry": geometry,
        "identity": envelope.get("identity", {}),
        "interaction": envelope.get("planes", {}).get("interaction", {}),
        "consent_ledger": envelope.get("consent_ledger", []),
        "intake_timestamp": envelope.get("created_at"),
    }

    now = datetime.now(UTC)

    return MemoryRecord(
        memory_id=uuid4(),
        tenant_id="arifos",
        actor_id=human_id,
        session_id="intake_ritual",
        type=MemoryType.SOVEREIGN_GEOMETRY,
        subject=human_id,
        content=json.dumps(content_payload, indent=2, ensure_ascii=False),
        summary=SUMMARY,
        source_type="intake_ritual",
        source_ref={
            "envelope_path": str(ENVELOPE_PATH),
            "envelope_version": envelope.get("version", "unknown"),
        },
        confidence=1.0,  # self-declared, highest confidence
        authority=Authority.EXPLICIT_USER,
        sensitivity=0.9,  # soul-level data
        consent_level="until_revoked",
        tags=["sovereign_geometry", "intake_ritual", "human_identity", human_id],
        retention_class=RetentionClass.DURABLE,
        expires_at=None,  # never expires
        revocable=True,  # human can revoke
        freshness_ts=now,
        created_at=now,
        updated_at=now,
    )


def build_vitality_reference_record(human_id: str = "arif") -> MemoryRecord:
    """Build a pointer record that references WELL for vitality data.

    This avoids duplicating vitality state — the canonical vitality
    store is WELL/state.json, not arifOS memory.
    """
    now = datetime.now(UTC)

    return MemoryRecord(
        memory_id=uuid4(),
        tenant_id="arifos",
        actor_id=human_id,
        session_id="intake_ritual",
        type=MemoryType.SEMANTIC,
        subject=human_id,
        content=json.dumps(
            {
                "human_id": human_id,
                "vitality_source": "WELL",
                "vitality_ref": "WELL/state.json#operator_id=arif",
                "note": (
                    "Vitality data lives in WELL (vitality organ). "
                    "Do NOT inline stale vitality here. "
                    "Query well_validate_vitality or well_readiness for live data."
                ),
            },
            indent=2,
        ),
        summary=f"Vitality reference pointer for {human_id} → WELL organ",
        source_type="intake_ritual",
        source_ref={"well_state": "WELL/state.json", "operator_id": human_id},
        confidence=1.0,
        authority=Authority.EXPLICIT_USER,
        sensitivity=0.5,
        consent_level="until_revoked",
        tags=["vitality_reference", "well_organ", human_id],
        retention_class=RetentionClass.DURABLE,
        expires_at=None,
        freshness_ts=now,
        created_at=now,
        updated_at=now,
    )


def ingest_geometry(envelope_path: Path = ENVELOPE_PATH) -> dict:
    """Full ingestion pipeline: load envelope → build records → return for L4 store.

    Returns a dict with both records and metadata for the caller to persist.
    In production the caller (MemoryIngestionService or direct L4 client) handles
    the actual Supabase write.
    """
    envelope = load_envelope(envelope_path)
    human_id = envelope.get("human_id", "arif")

    geometry_record = build_geometry_record(envelope)
    vitality_ref_record = build_vitality_reference_record(human_id)

    logger.info(
        "Sovereign geometry ingested for %s: geometry_id=%s vitality_ref_id=%s",
        human_id,
        geometry_record.memory_id,
        vitality_ref_record.memory_id,
    )

    return {
        "human_id": human_id,
        "geometry_record": geometry_record,
        "vitality_ref_record": vitality_ref_record,
        "axes_count": len(GEOMETRY_AXES),
        "summary": SUMMARY,
        "status": "ready_for_l4_store",
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = ingest_geometry()
    print(f"✓ Geometry ingested for {result['human_id']}")
    print(f"  Geometry record ID: {result['geometry_record'].memory_id}")
    print(f"  Vitality ref ID:    {result['vitality_ref_record'].memory_id}")
    print(f"  Axes: {result['axes_count']}")
    print(f"  Summary: {result['summary']}")
    print(f"  Status: {result['status']}")

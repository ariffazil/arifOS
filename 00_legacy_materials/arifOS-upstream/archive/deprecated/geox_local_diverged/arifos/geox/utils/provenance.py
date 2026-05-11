"""
GEOX Provenance Utilities
DITEMPA BUKAN DIBERI

Helper functions for building, verifying, and merging provenance records.
Supports arifOS F1 (Amanah/Reversibility) and F11 (Authority) compliance.

All functions operate on the ProvenanceRecord Pydantic v2 model from
geox_schemas. Import this module to construct provenance records
without manually populating every field.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Literal

from arifos.geox.geox_schemas import ProvenanceRecord

# Default floor check template — all True means fully compliant
_DEFAULT_FLOOR_CHECK: dict[str, bool] = {
    "F1_amanah": True,
    "F2_truth": True,
    "F4_clarity": True,
    "F7_humility": True,
    "F9_anti_hantu": True,
    "F11_authority": True,
    "F13_sovereign": True,
}


# ---------------------------------------------------------------------------
# build_provenance()
# ---------------------------------------------------------------------------


def build_provenance(
    source_id: str,
    source_type: Literal["LEM", "VLM", "sensor", "simulator", "human", "literature"],
    confidence: float,
    citation: str | None = None,
    checksum: str | None = None,
    timestamp: datetime | None = None,
    floor_overrides: dict[str, bool] | None = None,
) -> ProvenanceRecord:
    """
    Build a ProvenanceRecord with sensible defaults.

    This is the standard factory for creating provenance records
    throughout the GEOX pipeline. All tool adapters and synthesisers
    should use this function rather than constructing ProvenanceRecord
    objects manually.

    Args:
        source_id:       Unique identifier for the data source.
        source_type:     Category of source (LEM, VLM, sensor, etc.).
        confidence:      Source confidence score [0.0, 1.0].
        citation:        Human-readable citation string (for literature).
        checksum:        SHA-256 hex digest of raw data bytes.
        timestamp:       UTC timestamp; defaults to datetime.now(UTC).
        floor_overrides: Dict of floor_id → bool to override defaults.
                         Only provide floors that differ from all-True.

    Returns:
        ProvenanceRecord with all fields populated.

    Example:
        prov = build_provenance(
            "LEM-MALAY-2024-001",
            "LEM",
            confidence=0.82,
        )
        prov = build_provenance(
            "HUTCHISON-1996",
            "literature",
            confidence=0.70,
            citation="Hutchison (1996), Geology of NW Borneo.",
        )
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    floor_check = dict(_DEFAULT_FLOOR_CHECK)
    if floor_overrides:
        floor_check.update(floor_overrides)

    # F11 Authority: if source_type is 'human' without citation, flag
    if source_type == "human" and not citation:
        floor_check["F11_authority"] = False

    return ProvenanceRecord(
        source_id=source_id.strip(),
        source_type=source_type,
        timestamp=timestamp,
        confidence=max(0.0, min(1.0, confidence)),
        checksum=checksum,
        citation=citation,
        floor_check=floor_check,
    )


# ---------------------------------------------------------------------------
# compute_checksum()
# ---------------------------------------------------------------------------


def compute_checksum(data: Any) -> str:
    """
    Compute a SHA-256 checksum of arbitrary data.

    Serialises the data to a canonical JSON string (sorted keys,
    no extra whitespace) before hashing. Handles non-serialisable
    objects by converting to string representation.

    Args:
        data: Any Python object. Typically a dict, list, or Pydantic model.

    Returns:
        64-character hex string (SHA-256).

    Example:
        checksum = compute_checksum({"velocity_ms": 2450.0, "depth_m": 2500.0})
        prov = build_provenance("LEM-001", "LEM", 0.82, checksum=checksum)
    """

    def _default_serialiser(obj: Any) -> str:
        if hasattr(obj, "model_dump"):
            return obj.model_dump(mode="json")
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    canonical = json.dumps(
        data, sort_keys=True, separators=(",", ":"), default=_default_serialiser
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# verify_provenance_chain()
# ---------------------------------------------------------------------------


def verify_provenance_chain(chain: list[ProvenanceRecord]) -> bool:
    """
    Verify the integrity of a provenance chain.

    Checks:
      1. Chain is non-empty.
      2. All records have valid source_id (non-empty).
      3. Confidence values are in [0.0, 1.0].
      4. Timestamps are valid datetime objects.
      5. No duplicate source_ids (each source appears once).
      6. F1 Amanah flag is True for all records (traceability).
      7. F9 Anti-Hantu: no records with zero confidence (phantom data).

    Args:
        chain: Ordered list of ProvenanceRecord objects.

    Returns:
        True if the chain passes all checks, False otherwise.

    Note:
        Does NOT verify checksums against raw data (that requires
        the original data, which is not stored in the chain).
        For checksum verification, use compute_checksum() and compare.
    """
    if not chain:
        return False

    seen_ids: set[str] = set()

    for record in chain:
        # Check source_id non-empty
        if not record.source_id or not record.source_id.strip():
            return False

        # Check confidence in range
        if not (0.0 <= record.confidence <= 1.0):
            return False

        # Check timestamp is a valid datetime
        if not isinstance(record.timestamp, datetime):
            return False

        # Check for duplicate source_ids
        if record.source_id in seen_ids:
            return False
        seen_ids.add(record.source_id)

        # F1 Amanah: traceability flag must be True
        if not record.floor_check.get("F1_amanah", True):
            return False

        # F9 Anti-Hantu: zero confidence means phantom data
        if record.confidence == 0.0:
            return False

    return True


# ---------------------------------------------------------------------------
# merge_provenances()
# ---------------------------------------------------------------------------


def merge_provenances(records: list[ProvenanceRecord]) -> ProvenanceRecord:
    """
    Merge multiple ProvenanceRecords into a single aggregate record.

    The merged record represents the combined provenance of all inputs.
    Confidence is computed as the arithmetic mean of all input confidences.
    Timestamps use the most recent record's timestamp.
    Floor checks: a floor passes the merged record only if it passes
    in ALL input records (logical AND).

    Source type is set to the most common type in the inputs.
    Source ID is a synthetic composite.

    Args:
        records: List of ProvenanceRecord objects to merge. Must be non-empty.

    Returns:
        A single ProvenanceRecord representing the aggregate.

    Raises:
        ValueError: If records list is empty.

    Example:
        merged = merge_provenances([prov_lem, prov_vlm, prov_rag])
    """
    if not records:
        raise ValueError("Cannot merge an empty list of ProvenanceRecords.")

    if len(records) == 1:
        return records[0]

    # Aggregate confidence (arithmetic mean)
    avg_confidence = sum(r.confidence for r in records) / len(records)

    # Most recent timestamp
    latest_ts = max(r.timestamp for r in records)

    # Most common source_type
    type_counts: dict[str, int] = {}
    for r in records:
        type_counts[r.source_type] = type_counts.get(r.source_type, 0) + 1
    dominant_type = max(type_counts, key=type_counts.__getitem__)

    # Synthetic composite source_id
    id_parts = [r.source_id[:8] for r in records[:5]]
    composite_id = f"MERGED-{'-'.join(id_parts)}"

    # Floor check: AND across all records
    merged_floors: dict[str, bool] = dict(_DEFAULT_FLOOR_CHECK)
    for floor_id in merged_floors:
        merged_floors[floor_id] = all(
            r.floor_check.get(floor_id, True) for r in records
        )

    # Combine citations
    citations = [r.citation for r in records if r.citation]
    merged_citation = " | ".join(citations[:3]) if citations else None
    if len(citations) > 3:
        merged_citation = (merged_citation or "") + f" | [+{len(citations)-3} more]"

    return ProvenanceRecord(
        source_id=composite_id,
        source_type=dominant_type,  # type: ignore[arg-type]
        timestamp=latest_ts,
        confidence=round(avg_confidence, 4),
        checksum=None,  # Cannot compute checksum for merged records
        citation=merged_citation,
        floor_check=merged_floors,
    )

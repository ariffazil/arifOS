"""
Human Sovereign Geometry — Recall Helper
═════════════════════════════════════════

Recalls sovereign geometry from L4 and returns it with proper
epistemic labels. References WELL for vitality data (never inlines
stale vitality).

DITEMPA BUKAN DIBERI — recall is governed, not assumed.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, UTC
from typing import Any, Optional

from .types import MemoryType

logger = logging.getLogger(__name__)

# Epistemic labels for each geometry axis
AXIS_EPISTEMIC_LABELS: dict[str, str] = {
    "values": "DECLARED — self-reported sacred value. Treat as sovereign truth.",
    "direction": "DECLARED — stated life-building intent. Do not reinterpret.",
    "scars": "DECLARED — formative events as reported by the sovereign. "
             "Never infer additional trauma or minimize reported impact.",
    "shadow": "DECLARED — self-reported stress response. "
              "Under pressure, give space. Don't rush, fix, or suggest.",
    "boundary": "DECLARED — sovereign territory. "
                "Hard constraints on what the system must never decide or infer.",
}


@dataclass
class SovereignGeometry:
    """Structured recall result for a human's sovereign geometry."""

    human_id: str
    axes: dict[str, Any]
    identity: dict[str, Any]
    interaction: dict[str, Any]
    epistemic_labels: dict[str, str]
    vitality_ref: str
    consent_level: str
    intake_timestamp: Optional[str]
    recalled_at: str
    memory_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Return full geometry as a dict with epistemic labels attached."""
        return {
            "human_id": self.human_id,
            "axes": self.axes,
            "identity": self.identity,
            "interaction": self.interaction,
            "epistemic_labels": self.epistemic_labels,
            "vitality_ref": self.vitality_ref,
            "consent_level": self.consent_level,
            "intake_timestamp": self.intake_timestamp,
            "recalled_at": self.recalled_at,
            "memory_id": self.memory_id,
        }

    def axis(self, name: str) -> Optional[Any]:
        """Get a single axis by name, with epistemic label."""
        if name not in self.axes:
            return None
        return {
            "data": self.axes[name],
            "epistemic_label": self.epistemic_labels.get(name, "UNKNOWN"),
        }

    def summary(self) -> str:
        """One-line human-readable summary."""
        axes_names = ", ".join(self.axes.keys())
        return (
            f"Sovereign geometry for {self.human_id}: "
            f"[{axes_names}] | consent={self.consent_level} | "
            f"vitality→{self.vitality_ref}"
        )


def recall_geometry(
    human_id: str,
    memory_store: Any = None,
) -> Optional[SovereignGeometry]:
    """Recall sovereign geometry from L4 memory.

    Args:
        human_id: The human whose geometry to recall.
        memory_store: Optional L4 store client. If None, returns None
                      (caller must provide store or use recall_from_record).

    Returns:
        SovereignGeometry if found, None otherwise.
    """
    if memory_store is None:
        logger.warning(
            "No memory_store provided. Use recall_from_record() with an "
            "existing MemoryRecord, or pass a store client."
        )
        return None

    # In production: query L4 (Supabase) for the geometry record
    # SELECT * FROM memory_records
    #   WHERE type = 'sovereign_geometry'
    #   AND subject = %s
    #   AND status = 'active'
    #   ORDER BY created_at DESC LIMIT 1
    raise NotImplementedError(
        "L4 store query not yet implemented. "
        "Use recall_from_record() with a MemoryRecord from the store."
    )


def recall_from_record(
    record: Any,
    human_id: str = "arif",
) -> SovereignGeometry:
    """Build SovereignGeometry from an existing MemoryRecord.

    Use this when you already have the record from L4.
    """
    content = json.loads(record.content) if isinstance(record.content, str) else record.content

    axes = content.get("geometry", {})

    return SovereignGeometry(
        human_id=human_id,
        axes=axes,
        identity=content.get("identity", {}),
        interaction=content.get("interaction", {}),
        epistemic_labels=AXIS_EPISTEMIC_LABELS,
        vitality_ref="WELL/state.json#operator_id=" + human_id,
        consent_level=content.get("consent_ledger", [{}])[0].get(
            "expiry", "unknown"
        ) if content.get("consent_ledger") else "unknown",
        intake_timestamp=content.get("intake_timestamp"),
        recalled_at=datetime.now(UTC).isoformat(),
        memory_id=str(record.memory_id) if hasattr(record, "memory_id") else None,
    )


if __name__ == "__main__":
    # Demo: load from envelope directly for testing
    from .human_geometry_ingest import load_envelope, build_geometry_record

    envelope = load_envelope()
    record = build_geometry_record(envelope)
    geo = recall_from_record(record, human_id="arif")

    print(geo.summary())
    print()
    for axis_name in geo.axes:
        info = geo.axis(axis_name)
        print(f"  [{axis_name}] {info['epistemic_label']}")
    print()
    print(f"Vitality reference: {geo.vitality_ref}")
    print("(Query WELL for live vitality data — do not inline stale data)")

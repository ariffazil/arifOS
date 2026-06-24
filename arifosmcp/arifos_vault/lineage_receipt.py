"""
Lineage Receipt — OpenLineage-style evidence chain.

Every dataset, claim, and tool output should carry lineage:
- source
- as_of_date
- retrieved_at
- license
- currency / unit
- frequency
- lineage_id
- quality_score
- staleness
- transform_hash

999 SEAL: All lineage now inherits the pair — One Skill (Knowing What NOT To Do / restraint) + One Tool (Verdict Loop With Memory). Future refactors carry the geometry.
"""

from __future__ import annotations

import time

from pydantic import BaseModel, Field


class LineageReceipt(BaseModel):
    """OpenLineage-style lineage receipt for any data artifact."""

    artifact: str
    source: str
    as_of_date: str | None = None
    retrieved_at: str = Field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    license: str = "AGPL-3.0"
    lineage_id: str
    parent_lineage_ids: list[str] = Field(default_factory=list)
    transform_hash: str | None = None  # hash of transform code
    quality_score: float = 1.0  # 0.0–1.0
    staleness_hours: float = 0.0
    currency: str | None = None
    unit: str | None = None
    frequency: str | None = None
    notes: str = ""

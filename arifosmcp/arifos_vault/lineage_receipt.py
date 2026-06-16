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
"""

from __future__ import annotations

import time
from typing import Optional

from pydantic import BaseModel, Field


class LineageReceipt(BaseModel):
    """OpenLineage-style lineage receipt for any data artifact."""

    artifact: str
    source: str
    as_of_date: Optional[str] = None
    retrieved_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    license: str = "AGPL-3.0"
    lineage_id: str
    parent_lineage_ids: list[str] = Field(default_factory=list)
    transform_hash: Optional[str] = None  # hash of transform code
    quality_score: float = 1.0  # 0.0–1.0
    staleness_hours: float = 0.0
    currency: Optional[str] = None
    unit: Optional[str] = None
    frequency: Optional[str] = None
    notes: str = ""

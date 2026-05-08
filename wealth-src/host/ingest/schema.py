"""
Ingest schema — every datum is an observation with provenance, timing, and uncertainty.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class DataRecord:
    source_system: str
    series_id: str
    entity_code: str
    observation_time: str  # ISO date/time of the observed value
    release_time: Optional[str] = None
    retrieval_time: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    frequency: Optional[str] = None  # annual, quarterly, monthly, weekly, daily, intraday
    revision_flag: bool = False
    vintage_id: Optional[str] = None
    methodology_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence_band: Optional[List[float]] = None
    bus: str = "slow"  # slow, daily, fast, archive

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def now() -> str:
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_record(r: DataRecord) -> List[str]:
    flags = []
    if not r.source_system:
        flags.append("MISSING_SOURCE_SYSTEM")
    if not r.series_id:
        flags.append("MISSING_SERIES_ID")
    if not r.entity_code:
        flags.append("MISSING_ENTITY_CODE")
    if not r.observation_time:
        flags.append("MISSING_OBSERVATION_TIME")
    if r.value is not None and not isinstance(r.value, (int, float)):
        flags.append("INVALID_VALUE_TYPE")
    if r.retrieval_time is None:
        flags.append("MISSING_RETRIEVAL_TIME")
    return flags

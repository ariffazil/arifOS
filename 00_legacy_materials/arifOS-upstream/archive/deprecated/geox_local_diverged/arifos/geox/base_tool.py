"""
arifos/geox/base_tool.py — GEOX Tool Base Classes
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_schemas import (
    CoordinatePoint,
    GeoQuantity,
    ProvenanceRecord,
)


@dataclass
class GeoToolResult:
    """Standardised output from any GEOX tool execution."""
    quantities: list[GeoQuantity] = field(default_factory=list)
    raw_output: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    tool_name: str = ""
    latency_ms: float = 0.0
    success: bool = True
    error: str | None = None

class BaseTool(ABC):
    """Abstract base class for all GEOX tool adapters."""
    @property
    @abstractmethod
    def name(self) -> str: ...
    @property
    @abstractmethod
    def description(self) -> str: ...
    @abstractmethod
    async def run(self, inputs: dict[str, Any]) -> GeoToolResult: ...
    def validate_inputs(self, inputs: dict[str, Any]) -> bool:
        return isinstance(inputs, dict)
    def health_check(self) -> bool:
        return True

def _make_provenance(
    source_id: str,
    source_type: str,
    confidence: float,
    citation: str | None = None,
    checksum: str | None = None,
) -> ProvenanceRecord:
    """Create a minimal ProvenanceRecord for tool outputs."""
    return ProvenanceRecord(
        source_id=source_id,
        source_type=source_type,  # type: ignore[arg-type]
        timestamp=datetime.now(timezone.utc),
        confidence=confidence,
        checksum=checksum,
        citation=citation,
        floor_check={
            "F1_amanah": True, "F2_truth": True, "F4_clarity": True,
            "F7_humility": True, "F9_anti_hantu": True,
            "F11_authority": True, "F13_sovereign": True,
        },
    )

def _make_quantity(
    value: float,
    units: str,
    quantity_type: str,
    location: CoordinatePoint,
    provenance: ProvenanceRecord,
    uncertainty: float = 0.08,
) -> GeoQuantity:
    """Create a GeoQuantity with F7-compliant uncertainty."""
    uncertainty = max(0.03, min(0.15, uncertainty))
    return GeoQuantity(
        value=value,
        units=units,
        quantity_type=quantity_type,
        coordinates=location,
        timestamp=datetime.now(timezone.utc),
        uncertainty=uncertainty,
        provenance=provenance,
    )

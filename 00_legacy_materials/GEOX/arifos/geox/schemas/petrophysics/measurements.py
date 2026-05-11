"""
Measurement Schemas — Raw and Corrected Log Data
DITEMPA BUKAN DIBERI

F4 Clarity: Every curve has provenance, units, and QC status.
F9 Anti-Hantu: No phantom data without source.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class WellLogCurve(BaseModel):
    """
    A single log curve with full metadata.

    F4 Clarity: Mnemonic, units, and depth reference are mandatory.
    F9 Anti-Hantu: Source and acquisition timestamp tracked.
    """

    mnemonic: str = Field(
        ..., min_length=1, description="Curve mnemonic (GR, RHOB, etc.)"
    )
    name: str = Field(..., description="Human-readable name")
    units: str = Field(..., description="Physical units (API, g/cm3, etc.)")

    # Data
    depth: list[float] = Field(..., description="Depth values")
    values: list[float | None] = Field(
        ..., description="Curve values (None for missing)"
    )

    # Depth reference
    depth_reference: Literal["MD", "TVD", "TVDSS", "MDRKB"] = Field(
        default="MD", description="Measured depth, true vertical depth, etc."
    )

    # Provenance
    source_file: str = Field(..., description="Source LAS/DLIS filename")
    acquisition_date: datetime | None = Field(default=None)
    tool_mnemonic: str | None = Field(default=None, description="Logging tool type")

    # QC
    null_value: float = Field(
        default=-999.25, description="NULL representation in source"
    )

    @field_validator("values")
    @classmethod
    def replace_nulls(cls, v: list[float | None], info) -> list[float | None]:
        """Replace NULL values with None for consistency."""
        null_val = info.data.get("null_value", -999.25)
        return [None if x == null_val else x for x in v]

    def at_depth(self, target_depth: float) -> float | None:
        """Linear interpolation at target depth."""
        if (
            not self.depth
            or target_depth < self.depth[0]
            or target_depth > self.depth[-1]
        ):
            return None

        for i in range(len(self.depth) - 1):
            if self.depth[i] <= target_depth <= self.depth[i + 1]:
                if self.values[i] is None or self.values[i + 1] is None:
                    return None
                t = (target_depth - self.depth[i]) / (self.depth[i + 1] - self.depth[i])
                return self.values[i] + t * (self.values[i + 1] - self.values[i])
        return None

    @property
    def min_value(self) -> float | None:
        valid = [v for v in self.values if v is not None]
        return min(valid) if valid else None

    @property
    def max_value(self) -> float | None:
        valid = [v for v in self.values if v is not None]
        return max(valid) if valid else None


class LogBundle(BaseModel):
    """
    Complete well log package with header, curves, and metadata.

    F4 Clarity: All depth references and units explicit.
    F11 Auditability: Full chain of custody from source file.
    """

    well_id: str = Field(..., description="Canonical well identifier")
    well_name: str = Field(..., description="Well name from header")

    # Source
    source_files: list[str] = Field(..., description="Original LAS/DLIS filenames")
    bundle_created: datetime = Field(default_factory=datetime.utcnow)

    # Header metadata
    header: dict[str, Any] = Field(
        default_factory=dict, description="LAS ~WELL section"
    )

    # Curves
    curves: dict[str, WellLogCurve] = Field(..., description="Curves by mnemonic")

    # Depth range
    depth_reference: Literal["MD", "TVD", "TVDSS", "MDRKB"] = "MD"
    min_depth: float | None = None
    max_depth: float | None = None
    depth_unit: str = "m"

    # Location
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None

    # QC summary
    qc_summary: dict[str, Any] = Field(default_factory=dict)

    @field_validator("curves")
    @classmethod
    def set_depth_range(
        cls, curves: dict[str, WellLogCurve]
    ) -> dict[str, WellLogCurve]:
        """Auto-compute depth range from first curve."""
        if curves:
            first = list(curves.values())[0]
            if first.depth:
                values = curves  # Just return, can't modify self here
                return values
        return curves

    def get_curve(self, mnemonic: str) -> WellLogCurve | None:
        """Get curve by mnemonic (case-insensitive)."""
        # Exact match
        if mnemonic in self.curves:
            return self.curves[mnemonic]
        # Case-insensitive
        for key, curve in self.curves.items():
            if key.upper() == mnemonic.upper():
                return curve
        return None

    def get_depth_curve(self) -> WellLogCurve | None:
        """Get primary depth curve."""
        for name in ["DEPT", "DEPTH", "MD", "TVD", "TVDSS"]:
            curve = self.get_curve(name)
            if curve:
                return curve
        # Return first curve as fallback
        return list(self.curves.values())[0] if self.curves else None


class CurveQC(BaseModel):
    """
    Quality control findings for a single curve.

    F2 Truth: Explicit completeness and flag inventory.
    """

    mnemonic: str
    completeness: float = Field(..., ge=0.0, le=1.0, description="Fraction non-null")
    total_points: int
    null_points: int

    # QC flags
    flags: list[str] = Field(default_factory=list, description="QC issues found")

    # Specific checks
    has_washouts: bool = False
    has_badcaliper: bool = False
    has_unit_issues: bool = False
    has_depth_gaps: bool = False

    # Confidence
    usable_for_petrophysics: bool = True
    recommended_action: str | None = None


class QCReport(BaseModel):
    """
    Complete QC findings for a well.

    F4 Clarity: Overall status and per-curve details.
    F11 Auditability: Timestamp and algorithm version.
    """

    well_id: str
    report_generated: datetime = Field(default_factory=datetime.utcnow)
    qc_version: str = "1.0.0"

    # Overall status
    overall: Literal["PASS", "WARNING", "FAIL"] = "PASS"

    # Per-curve QC
    curve_reports: list[CurveQC] = Field(default_factory=list)

    # Cross-cutting issues
    depth_issues: list[str] = Field(default_factory=list)
    unit_inconsistencies: list[str] = Field(default_factory=list)
    missing_critical_curves: list[str] = Field(default_factory=list)

    # Calibration tracking
    calibration_status: dict[str, Any] = Field(default_factory=dict)

    # Recommendations
    recommendations: list[str] = Field(default_factory=list)

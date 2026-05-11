"""
GEOX Neutral Render Primitives — DITEMPA BUKAN DIBERI

Neutral render primitives that abstract away renderer-specific details.
This layer prevents renderer lock-in and lets GEOX swap cigvis for
another renderer without changing semantic contracts.

Primitive types:
- VolumeSlicePrimitive
- SurfacePrimitive
- FaultPrimitive
- WellTrajectoryPrimitive
- PointSetPrimitive
- AxisPrimitive
- LegendPrimitive
- AnnotationPrimitive
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class SliceDirection(str, Enum):
    """Direction for volume slice."""

    INLINE = "inline"
    CROSSLINE = "crossline"
    TIMESLICE = "timeslice"
    DEPTH_SLICE = "depth_slice"


@dataclass
class RenderColor:
    """RGBA color for rendering."""

    r: float = 0.5
    g: float = 0.5
    b: float = 0.5
    a: float = 1.0

    def to_hex(self) -> str:
        """Convert to hex color string."""
        return f"#{int(self.r * 255):02x}{int(self.g * 255):02x}{int(self.b * 255):02x}"

    @classmethod
    def from_hex(cls, hex_str: str) -> "RenderColor":
        """Create from hex string like '#ff0000'."""
        hex_str = hex_str.lstrip("#")
        return cls(
            r=int(hex_str[0:2], 16) / 255,
            g=int(hex_str[2:4], 16) / 255,
            b=int(hex_str[4:6], 16) / 255,
        )


@dataclass
class Vector3:
    """3D vector/coordinate."""

    x: float
    y: float
    z: float


@dataclass
class BoundingBox:
    """3D bounding box for scene."""

    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float


@dataclass
class VolumeSlicePrimitive:
    """
    A 2D slice through a 3D volume.

    Used for seismic inline, crossline, time slice, or depth slice views.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    data: Any = None
    direction: SliceDirection = SliceDirection.INLINE
    slice_value: int | float = 0
    bbox: BoundingBox | None = None
    cmap: str = "gray"
    clim: tuple[float, float] = (0.0, 1.0)
    opacity: float = 1.0
    visible: bool = True
    x_axis_label: str = "Distance"
    x_axis_unit: str = "km"
    y_axis_label: str = "Time/Depth"
    y_axis_unit: str = "ms"
    provenance: str = ""
    is_observed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SurfacePrimitive:
    """
    A horizon or other geological surface.

    Can be rendered as mesh, points, or lines.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    vertices: list[Vector3] = field(default_factory=list)
    triangles: list[tuple[int, int, int]] = field(default_factory=list)
    color: RenderColor = field(default_factory=lambda: RenderColor())
    opacity: float = 0.7
    wireframe: bool = False
    bbox: BoundingBox | None = None
    age: str | None = None
    formation: str | None = None
    provenance: str = ""
    is_observed: bool = True
    is_interpreted: bool = False
    confidence: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class FaultPrimitive:
    """
    A fault surface or trace.

    Can be rendered as mesh, lines, or points.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    vertices: list[Vector3] = field(default_factory=list)
    triangles: list[tuple[int, int, int]] = field(default_factory=list)
    color: RenderColor = field(default_factory=lambda: RenderColor(r=1.0, g=0.0, b=0.0))
    opacity: float = 0.8
    trace_points: list[Vector3] = field(default_factory=list)
    dip_degrees: float | None = None
    strike_degrees: float | None = None
    throw_m: float | None = None
    bbox: BoundingBox | None = None
    provenance: str = ""
    is_observed: bool = True
    is_inferred: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WellTrajectoryPrimitive:
    """
    A well path with trajectory and optional curves.

    Rendered as a 3D tube or line with markers.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    well_id: str = ""
    trajectory: list[Vector3] = field(default_factory=list)
    md_values: list[float] = field(default_factory=list)
    tvd_values: list[float] = field(default_factory=list)
    color: RenderColor = field(default_factory=lambda: RenderColor(r=0.0, g=0.8, b=0.0))
    radius: float = 50.0
    show_markers: bool = True
    marker_interval: float = 500.0
    bbox: BoundingBox | None = None
    formation_tops: dict[str, float] = field(default_factory=dict)
    provenance: str = ""
    is_observed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class PointSetPrimitive:
    """
    A set of 3D points.

    Used for point-based attributes, analytes, or sparse data.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    points: list[Vector3] = field(default_factory=list)
    values: list[float] = field(default_factory=list)
    color: RenderColor = field(default_factory=lambda: RenderColor())
    point_size: float = 5.0
    cmap: str = "viridis"
    bbox: BoundingBox | None = None
    provenance: str = ""
    is_observed: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UnitPolygonPrimitive:
    """
    A geological unit polygon on cross section.

    2D polygon with fill and label.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    unit_name: str = ""
    formation_age: str | None = None
    lithology: str | None = None
    points_2d: list[tuple[float, float]] = field(default_factory=list)
    color: RenderColor = field(default_factory=lambda: RenderColor(r=0.7, g=0.7, b=0.7))
    opacity: float = 0.6
    bbox: BoundingBox | None = None
    provenance: str = ""
    is_observed: bool = True
    is_interpreted: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UncertaintyZonePrimitive:
    """
    A region of uncertain interpretation.

    Rendered as semi-transparent zone with hatching or pattern.
    """

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    uncertainty_type: str = ""
    polygon_2d: list[tuple[float, float]] = field(default_factory=list)
    color: RenderColor = field(default_factory=lambda: RenderColor(r=1.0, g=1.0, b=0.0, a=0.3))
    pattern: str = "hatching"
    bbox: BoundingBox | None = None
    confidence: float = 0.5
    explanation: str = ""
    provenance: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AxisPrimitive:
    """2D or 3D axis with labels and ticks."""

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    orientation: str = "horizontal"
    label: str = ""
    unit: str = ""
    min_value: float = 0.0
    max_value: float = 1.0
    scale: str = "linear"
    ticks: list[float] = field(default_factory=list)
    tick_labels: list[str] = field(default_factory=list)


@dataclass
class LegendEntry:
    """Entry in a rendered legend."""

    label: str
    color: RenderColor
    line_style: str = "solid"
    marker: str | None = None


@dataclass
class LegendPrimitive:
    """A rendered legend with entries."""

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    entries: list[LegendEntry] = field(default_factory=list)
    position: str = "top_right"
    visible: bool = True


@dataclass
class AnnotationPrimitive:
    """Text annotation on the scene."""

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    text: str = ""
    position: tuple[float, float] = (0.0, 0.0)
    font_size: int = 12
    color: RenderColor = field(default_factory=lambda: RenderColor())
    bold: bool = False
    visible: bool = True


@dataclass
class QC_BadgePrimitive:
    """QC status badge overlay."""

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    badge_type: str = ""
    text: str = ""
    position: str = "top_left"
    color: RenderColor = field(default_factory=lambda: RenderColor(r=0.0, g=1.0, b=0.0))
    visible: bool = True


@dataclass
class ScaleBarPrimitive:
    """Scale bar with length and unit."""

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    length_value: float = 1.0
    unit: str = "km"
    position: str = "bottom_left"
    visible: bool = True


@dataclass
class VerticalExaggerationBadge:
    """Vertical exaggeration indicator."""

    primitive_id: str = field(default_factory=lambda: str(uuid4()))
    exaggeration: float = 1.0
    position: str = "top_left"
    visible: bool = True


@dataclass
class SceneMetadata:
    """Metadata for the entire scene."""

    scene_id: str = field(default_factory=lambda: str(uuid4()))
    title: str = ""
    datum: str = "MSL"
    vertical_unit: str = "m"
    horizontal_unit: str = "km"
    vertical_exaggeration: float = 1.0
    coordinate_reference: str = "WGS84"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    provenance: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class NeutralScene:
    """
    Neutral renderable scene composed of primitives.

    This is the output of the scene compiler and the input
    to any renderer adapter.
    """

    metadata: SceneMetadata = field(default_factory=SceneMetadata)
    volume_slices: list[VolumeSlicePrimitive] = field(default_factory=list)
    surfaces: list[SurfacePrimitive] = field(default_factory=list)
    faults: list[FaultPrimitive] = field(default_factory=list)
    wells: list[WellTrajectoryPrimitive] = field(default_factory=list)
    point_sets: list[PointSetPrimitive] = field(default_factory=list)
    unit_polygons: list[UnitPolygonPrimitive] = field(default_factory=list)
    uncertainty_zones: list[UncertaintyZonePrimitive] = field(default_factory=list)
    axes: list[AxisPrimitive] = field(default_factory=list)
    legends: list[LegendPrimitive] = field(default_factory=list)
    annotations: list[AnnotationPrimitive] = field(default_factory=list)
    qc_badges: list[QC_BadgePrimitive] = field(default_factory=list)
    scale_bar: ScaleBarPrimitive | None = None
    ve_badge: VerticalExaggerationBadge | None = None
    bbox: BoundingBox | None = None

    def get_primitive_count(self) -> int:
        """Return total count of all primitives."""
        return (
            len(self.volume_slices)
            + len(self.surfaces)
            + len(self.faults)
            + len(self.wells)
            + len(self.point_sets)
            + len(self.unit_polygons)
            + len(self.uncertainty_zones)
        )

"""
GEOX Renderers Module — DITEMPA BUKAN DIBERI

Renderer adapters for GEOX visualization.

Architecture:
  Canonical state → SceneCompiler → RendererAdapter → cigvis

Renderers:
  - base: Abstract base and contracts
  - primitives: Neutral render primitives
  - scene_compiler: Canonical state → neutral primitives
  - cigvis_adapter: cigvis node builder
  - export: Static snapshot export
"""

from arifos.geox.renderers.base import (
    RenderMode,
    RenderResult,
    RenderSession,
    RendererAdapter,
)
from arifos.geox.renderers.primitives import (
    AnnotationPrimitive,
    AxisPrimitive,
    BoundingBox,
    LegendEntry,
    LegendPrimitive,
    NeutralScene,
    PointSetPrimitive,
    QC_BadgePrimitive,
    RenderColor,
    ScaleBarPrimitive,
    SceneMetadata,
    SliceDirection,
    SurfacePrimitive,
    UnitPolygonPrimitive,
    Vector3,
    VerticalExaggerationBadge,
    VolumeSlicePrimitive,
    WellTrajectoryPrimitive,
    UncertaintyZonePrimitive,
)
from arifos.geox.renderers.scene_compiler import SceneCompiler
from arifos.geox.renderers.export import RenderExporter

__all__ = [
    # Base
    "RendererAdapter",
    "RenderSession",
    "RenderResult",
    "RenderMode",
    # Primitives
    "NeutralScene",
    "VolumeSlicePrimitive",
    "SurfacePrimitive",
    "FaultPrimitive",
    "WellTrajectoryPrimitive",
    "PointSetPrimitive",
    "UnitPolygonPrimitive",
    "UncertaintyZonePrimitive",
    "AxisPrimitive",
    "LegendPrimitive",
    "LegendEntry",
    "AnnotationPrimitive",
    "QC_BadgePrimitive",
    "ScaleBarPrimitive",
    "VerticalExaggerationBadge",
    "RenderColor",
    "Vector3",
    "BoundingBox",
    "SliceDirection",
    "SceneMetadata",
    # Compiler
    "SceneCompiler",
    # Export
    "RenderExporter",
]

CIGVIS_AVAILABLE = True
try:
    from arifos.geox.renderers.cigvis_adapter import (
        CigvisAdapter,
        StaticCigvisRenderer,
        InteractiveCigvisRenderer,
    )

    __all__.extend(
        [
            "CigvisAdapter",
            "StaticCigvisRenderer",
            "InteractiveCigvisRenderer",
        ]
    )
except ImportError:
    pass

"""
GEOX Volume Context Module — DITEMPA BUKAN DIBERI

Volume context for 3D geophysical visualization.

Used when GEOX graduates into linked 2D/3D section-slice
comparisons or volumetric previews.

Cigvis is strongest here:
- VolumeContextView
- MultiCanvasCompareView
- horizon/fault/well overlays
- synchronized navigation
"""

from arifos.geox.volume_context.schemas import (
    VolumeContextRequest,
    VolumeContextResponse,
    VolumeContextState,
    SliceOverlayType,
    HorizonOverlay,
    FaultOverlay,
    WellOverlay,
    VolumeSceneUpdate,
    VolumeCompareRequest,
    VolumeCompareResponse,
)
from arifos.geox.volume_context.builders import (
    VolumeSceneBuilder,
    CrossSectionBuilder,
)

__all__ = [
    # Schemas
    "VolumeContextRequest",
    "VolumeContextResponse",
    "VolumeContextState",
    "SliceOverlayType",
    "HorizonOverlay",
    "FaultOverlay",
    "WellOverlay",
    "VolumeSceneUpdate",
    "VolumeCompareRequest",
    "VolumeCompareResponse",
    # Builders
    "VolumeSceneBuilder",
    "CrossSectionBuilder",
]

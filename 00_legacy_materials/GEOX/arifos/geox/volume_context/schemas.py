"""
GEOX Volume Context Schemas — DITEMPA BUKAN DIBERI

Schemas for volume context and 3D scene management.

Volume context is used when GEOX graduates into linked 2D/3D
section-slice comparisons or volumetric previews.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class VolumeContextState(str, Enum):
    """State of volume context session."""

    IDLE = "idle"
    LOADING = "loading"
    SCENE_BUILT = "scene_built"
    RENDERING = "rendering"
    READY = "ready"
    ERROR = "error"


class SliceOverlayType(str, Enum):
    """Types of overlays available for volume slices."""

    AMPLITUDE = "amplitude"
    HORIZON = "horizon"
    FAULT = "fault"
    ATTRIBUTE = "attribute"
    UNCERTAINTY = "uncertainty"


class VolumeContextRequest(BaseModel):
    """Request to open a volume context view."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    basin: str = Field(..., description="Sedimentary basin name")
    survey_name: str | None = Field(None, description="3D survey name")
    inline_range: tuple[int, int] | None = Field(None)
    crossline_range: tuple[int, int] | None = Field(None)
    time_range_ms: tuple[float, float] | None = Field(None)
    depth_range_m: tuple[float, float] | None = Field(None)
    requested_overlays: list[SliceOverlayType] = Field(default_factory=list)
    link_to_section: str | None = Field(None, description="Section ID to link to")
    requester_id: str = Field(..., description="Requesting user or system")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VolumeContextResponse(BaseModel):
    """Response from volume context view."""

    success: bool
    context_id: str = Field(default_factory=lambda: str(uuid4()))
    state: VolumeContextState = Field(default=VolumeContextState.IDLE)
    scene_url: str | None = Field(None, description="URL for interactive view")
    snapshot_path: str | None = Field(None, description="Path to snapshot PNG")
    bounding_box: dict[str, float] | None = Field(None)
    available_slices: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    session_id: str | None = Field(None)
    ttl_seconds: int = Field(default=300)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HorizonOverlay(BaseModel):
    """Horizon surface overlay for volume context."""

    horizon_id: str
    name: str
    color: str = Field(default="#0000FF", pattern="^#[0-9A-Fa-f]{6}$")
    opacity: float = Field(default=0.7, ge=0.0, le=1.0)
    show_surface: bool = True
    show_contours: bool = False


class FaultOverlay(BaseModel):
    """Fault overlay for volume context."""

    fault_id: str
    name: str | None = None
    color: str = Field(default="#FF0000", pattern="^#[0-9A-Fa-f]{6}$")
    opacity: float = Field(default=0.8, ge=0.0, le=1.0)
    show_mesh: bool = False
    show_trace: bool = True


class WellOverlay(BaseModel):
    """Well overlay for volume context."""

    well_id: str
    name: str
    show_trajectory: bool = True
    show_markers: bool = True
    show_tops: bool = True
    color: str = Field(default="#00FF00", pattern="^#[0-9A-Fa-f]{6}$")


class VolumeSceneUpdate(BaseModel):
    """Update to an active volume context scene."""

    update_id: str = Field(default_factory=lambda: str(uuid4()))
    context_id: str = Field(...)
    action: str = Field(..., description="add_horizon, remove_horizon, add_fault, ...")
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VolumeCompareRequest(BaseModel):
    """Request to compare multiple volume views."""

    request_id: str = Field(default_factory=lambda: str(uuid4()))
    context_ids: list[str] = Field(..., description="Context IDs to compare")
    sync_cameras: bool = Field(default=True)
    sync_cursor: bool = Field(default=True)
    overlay_same_horizons: bool = Field(default=True)
    requester_id: str = Field(...)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VolumeCompareResponse(BaseModel):
    """Response from volume comparison."""

    success: bool
    compare_id: str = Field(default_factory=lambda: str(uuid4()))
    scene_urls: list[str] = Field(default_factory=list)
    synchronized: bool
    common_horizons: list[str] = Field(default_factory=list)
    diverging_areas: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

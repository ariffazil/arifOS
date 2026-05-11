"""
GEOX Volume Context Builders — DITEMPA BUKAN DIBERI

Builders for volume context scenes.

Constructs volume context scenes from seismic data,
horizons, faults, wells, and other geophysical data.
"""

from __future__ import annotations

from typing import Any

from arifos.geox.renderers.scene_compiler import SceneCompiler


class VolumeSceneBuilder:
    """
    Builds volume context scenes for cigvis rendering.

    Builds from:
    - Seismic volume data
    - Horizon surfaces
    - Fault geometries
    - Well trajectories
    - Attribute volumes
    """

    def __init__(self):
        self.compiler = SceneCompiler()
        self._scene_data: dict[str, Any] = {}

    def reset(self) -> "VolumeSceneBuilder":
        """Reset the builder state."""
        self._scene_data = {}
        return self

    def set_bounding_box(
        self,
        min_x: float,
        max_x: float,
        min_y: float,
        max_y: float,
        min_z: float,
        max_z: float,
    ) -> "VolumeSceneBuilder":
        """Set the 3D bounding box."""
        self._scene_data["bbox"] = {
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "min_z": min_z,
            "max_z": max_z,
        }
        return self

    def set_seismic_volume(
        self,
        data: Any,
        inline_start: int,
        inline_end: int,
        crossline_start: int,
        crossline_end: int,
        time_samples: list[float],
    ) -> "VolumeSceneBuilder":
        """
        Set the seismic volume data.

        Args:
            data: 3D numpy array (inline, crossline, time)
            inline_start: First inline
            inline_end: Last inline
            crossline_start: First crossline
            crossline_end: Last crossline
            time_samples: Time depth values for each sample
        """
        self._scene_data["seismic_volume"] = {
            "data": data,
            "inline_range": (inline_start, inline_end),
            "crossline_range": (crossline_start, crossline_end),
            "time_samples": time_samples,
        }
        return self

    def add_horizon(
        self,
        horizon_id: str,
        name: str,
        vertices: list[tuple[float, float, float]],
        color: str = "#0000FF",
        opacity: float = 0.7,
    ) -> "VolumeSceneBuilder":
        """Add a horizon surface."""
        if "horizons" not in self._scene_data:
            self._scene_data["horizons"] = []

        self._scene_data["horizons"].append(
            {
                "horizon_id": horizon_id,
                "name": name,
                "vertices": vertices,
                "color": color,
                "opacity": opacity,
            }
        )
        return self

    def add_fault(
        self,
        fault_id: str,
        name: str | None = None,
        vertices: list[tuple[float, float, float]] | None = None,
        trace_points: list[tuple[float, float, float]] | None = None,
        color: str = "#FF0000",
        opacity: float = 0.8,
    ) -> "VolumeSceneBuilder":
        """Add a fault geometry."""
        if "faults" not in self._scene_data:
            self._scene_data["faults"] = []

        self._scene_data["faults"].append(
            {
                "fault_id": fault_id,
                "name": name or f"Fault {fault_id}",
                "vertices": vertices or [],
                "trace_points": trace_points or [],
                "color": color,
                "opacity": opacity,
            }
        )
        return self

    def add_well(
        self,
        well_id: str,
        name: str,
        trajectory: list[tuple[float, float, float]],
        formation_tops: dict[str, float] | None = None,
        color: str = "#00FF00",
    ) -> "VolumeSceneBuilder":
        """Add a well trajectory."""
        if "wells" not in self._scene_data:
            self._scene_data["wells"] = []

        self._scene_data["wells"].append(
            {
                "well_id": well_id,
                "name": name,
                "trajectory": trajectory,
                "formation_tops": formation_tops or {},
                "color": color,
            }
        )
        return self

    def build(self) -> dict[str, Any]:
        """Build the volume context scene."""
        return self._scene_data.copy()


class CrossSectionBuilder:
    """
    Builds cross-section scenes from geological data.

    Cross sections are INTERPRETED earth model products.
    Must always distinguish observed vs inferred.
    """

    def __init__(self):
        self.compiler = SceneCompiler()
        self._scene_data: dict[str, Any] = {"state_type": "cross_section"}

    def reset(self) -> "CrossSectionBuilder":
        """Reset the builder state."""
        self._scene_data = {"state_type": "cross_section"}
        return self

    def set_profile(
        self,
        profile_id: str,
        name: str,
        points: list[tuple[float, float, float]],
        total_length_km: float,
    ) -> "CrossSectionBuilder":
        """Set the profile line."""
        self._scene_data["profile_id"] = profile_id
        self._scene_data["profile_name"] = name
        self._scene_data["profile_points"] = [
            {
                "distance_km": p[0],
                "elevation_m": p[1],
                "lat": p[2],
                "lon": p[3] if len(p) > 3 else 0,
            }
            for p in points
        ]
        self._scene_data["total_length_km"] = total_length_km
        return self

    def add_unit(
        self,
        unit_id: str,
        name: str,
        polygon_points: list[tuple[float, float]],
        formation_age: str | None = None,
        lithology: str | None = None,
        color: str = "#808080",
        is_observed: bool = True,
    ) -> "CrossSectionBuilder":
        """Add a geological unit polygon."""
        if "units" not in self._scene_data:
            self._scene_data["units"] = []

        self._scene_data["units"].append(
            {
                "unit_id": unit_id,
                "unit_name": name,
                "polygon_coords": [
                    {"distance_km": p[0], "elevation_m": p[1]} for p in polygon_points
                ],
                "formation_age": formation_age,
                "lithology": lithology,
                "color": color,
                "is_observed": is_observed,
                "is_interpreted": not is_observed,
            }
        )
        return self

    def add_well(
        self,
        well_id: str,
        name: str,
        location_km: float,
        ground_elevation_m: float,
        total_depth_m: float,
        formation_tops: list[dict[str, Any]] | None = None,
    ) -> "CrossSectionBuilder":
        """Add a well column."""
        if "wells" not in self._scene_data:
            self._scene_data["wells"] = []

        self._scene_data["wells"].append(
            {
                "well_id": well_id,
                "well_name": name,
                "profile_distance_km": location_km,
                "ground_elevation_m": ground_elevation_m,
                "total_depth_m": total_depth_m,
                "formation_tops": formation_tops or [],
                "trajectory": [],
                "is_observed": True,
            }
        )
        return self

    def add_fault(
        self,
        fault_id: str,
        name: str | None = None,
        trace_points: list[tuple[float, float]] | None = None,
        is_observed: bool = True,
    ) -> "CrossSectionBuilder":
        """Add a fault trace."""
        if "faults" not in self._scene_data:
            self._scene_data["faults"] = []

        self._scene_data["faults"].append(
            {
                "fault_id": fault_id,
                "fault_name": name or f"Fault {fault_id}",
                "trace_points": [
                    {"distance_km": p[0], "elevation_m": p[1], "lat": 0, "lon": 0}
                    for p in (trace_points or [])
                ],
                "is_observed": is_observed,
                "is_inferred": not is_observed,
            }
        )
        return self

    def add_uncertainty_zone(
        self,
        zone_id: str,
        uncertainty_type: str,
        polygon_points: list[tuple[float, float]],
        confidence: float,
        explanation: str,
    ) -> "CrossSectionBuilder":
        """Add an uncertainty zone."""
        if "uncertainty_zones" not in self._scene_data:
            self._scene_data["uncertainty_zones"] = []

        self._scene_data["uncertainty_zones"].append(
            {
                "zone_id": zone_id,
                "uncertainty_type": uncertainty_type,
                "polygon": [{"x": p[0], "y": p[1]} for p in polygon_points],
                "confidence": confidence,
                "explanation": explanation,
            }
        )
        return self

    def set_vertical_exaggeration(self, ve: float) -> "CrossSectionBuilder":
        """Set vertical exaggeration factor."""
        self._scene_data["vertical_exaggeration"] = ve
        return self

    def build(self) -> dict[str, Any]:
        """Build the cross-section scene."""
        return self._scene_data.copy()

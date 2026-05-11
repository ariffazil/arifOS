"""
GEOX Scene Compiler — DITEMPA BUKAN DIBERI

Compiles canonical GEOX state into neutral render primitives.

Canonical state types:
- GeoXDisplayState → 2D display scene
- GeoXCrossSectionState → Cross-section scene
- GeoXSeismicSectionState → Seismic section scene
- GeoXTriAppState → Multi-view coordinated scene

Output: NeutralScene with primitives ready for any renderer adapter.
"""

from __future__ import annotations

from typing import Any

from arifos.geox.renderers.primitives import (
    BoundingBox,
    LegendEntry,
    LegendPrimitive,
    NeutralScene,
    QC_BadgePrimitive,
    RenderColor,
    SceneMetadata,
    ScaleBarPrimitive,
    SliceDirection,
    SurfacePrimitive,
    UnitPolygonPrimitive,
    Vector3,
    VerticalExaggerationBadge,
    VolumeSlicePrimitive,
    WellTrajectoryPrimitive,
)


class SceneCompiler:
    """
    Compiles canonical GEOX state into neutral primitives.

    This is the middle layer between GEOX semantic state and
    renderer-specific implementations.
    """

    def compile(self, canonical_state: dict[str, Any]) -> NeutralScene:
        """
        Dispatch compilation based on state type.

        Args:
            canonical_state: GeoXDisplayState, GeoXCrossSectionState,
                          GeoXSeismicSectionState, or GeoXTriAppState

        Returns:
            Neutral renderable scene
        """
        state_type = canonical_state.get("state_type", "")

        if state_type == "cross_section":
            return self.compile_cross_section(canonical_state)
        elif state_type == "seismic_section":
            return self.compile_seismic_section(canonical_state)
        elif state_type == "tri_app":
            return self.compile_tri_app(canonical_state)
        elif state_type == "display":
            return self.compile_display(canonical_state)
        else:
            return self.compile_generic(canonical_state)

    def compile_cross_section(self, state: dict[str, Any]) -> NeutralScene:
        """
        Compile GeoXCrossSectionState to neutral scene.

        Cross sections are INTERPRETED earth model products.
        Must distinguish observed vs inferred.
        """
        scene = NeutralScene()

        metadata = state.get("metadata", {})
        scene.metadata = SceneMetadata(
            title=state.get("profile_name", "Cross Section"),
            vertical_unit=state.get("vertical_unit", "m"),
            vertical_exaggeration=state.get("vertical_exaggeration", 1.0),
            provenance=[metadata.get("source", "unknown")],
        )

        if state.get("vertical_exaggeration", 1.0) != 1.0:
            scene.ve_badge = VerticalExaggerationBadge(
                exaggeration=state.get("vertical_exaggeration", 1.0),
                visible=True,
            )
            scene.metadata.warnings.append(
                f"Vertical exaggeration {state.get('vertical_exaggeration')}x applied"
            )

        wells_data = state.get("wells", [])
        for well in wells_data:
            scene.wells.append(self.compile_well(well))

        faults_data = state.get("faults", [])
        for fault in faults_data:
            scene.surfaces.append(self.compile_fault_surface(fault))

        units_data = state.get("units", [])
        for unit in units_data:
            scene.unit_polygons.append(self.compile_unit_polygon(unit))

        uncertainty_zones = state.get("uncertainty_zones", [])
        for zone in uncertainty_zones:
            scene.uncertainty_zones.append(self.compile_uncertainty_zone(zone))

        profile_points = state.get("profile_points", [])
        if profile_points:
            scene.bbox = self.compute_bbox_from_points(profile_points)

        scene.scale_bar = ScaleBarPrimitive(
            length_value=self.estimate_scale_length(state),
            unit="km",
            visible=True,
        )

        scene.legends.append(self.build_legend(units_data, wells_data, faults_data))

        return scene

    def compile_seismic_section(self, state: dict[str, Any]) -> NeutralScene:
        """
        Compile GeoXSeismicSectionState to neutral scene.

        Seismic sections are OBSERVATIONAL sensor products.
        QC badges must be prominent.
        """
        scene = NeutralScene()

        metadata = state.get("metadata", {})
        scene.metadata = SceneMetadata(
            title=state.get("section_name", "Seismic Section"),
            vertical_unit="ms" if "TWT" in str(state.get("vertical_unit", "")) else "m",
            provenance=[metadata.get("source", "seismic")],
        )

        image_data = state.get("image_data")
        if image_data is not None:
            direction = state.get("direction", "inline")
            slice_dir = SliceDirection.INLINE
            if direction == "crossline":
                slice_dir = SliceDirection.CROSSLINE
            elif direction == "timeslice":
                slice_dir = SliceDirection.TIMESLICE

            scene.volume_slices.append(
                VolumeSlicePrimitive(
                    name=state.get("section_name", "Seismic"),
                    data=image_data,
                    direction=slice_dir,
                    cmap=state.get("cmap", "gray"),
                    clim=state.get("clim", (0.0, 1.0)),
                    provenance=metadata.get("source", "seismic"),
                    is_observed=True,
                )
            )

        detected_reflectors = state.get("detected_reflectors", [])
        for reflector in detected_reflectors:
            scene.surfaces.append(self.compile_reflector_surface(reflector))

        detected_faults = state.get("detected_faults", [])
        for fault in detected_faults:
            scene.surfaces.append(self.compile_fault_surface(fault))

        quality = state.get("image_quality", "unknown")
        if quality != "good":
            scene.qc_badges.append(
                QC_BadgePrimitive(
                    badge_type="quality",
                    text=f"Quality: {quality}",
                    color=(
                        RenderColor(r=1.0, g=1.0, b=0.0)
                        if quality == "fair"
                        else RenderColor(r=1.0, g=0.0, b=0.0)
                    ),
                    visible=True,
                )
            )

        polarity = state.get("polarity", "unknown")
        if polarity == "unknown":
            scene.qc_badges.append(
                QC_BadgePrimitive(
                    badge_type="polarity",
                    text="POLARITY UNKNOWN",
                    color=RenderColor(r=1.0, g=0.0, b=0.0),
                    visible=True,
                )
            )
            scene.metadata.warnings.append(
                "Polarity unknown - quantitative measurements disabled"
            )

        if state.get("stretch_artifacts", False):
            scene.metadata.warnings.append("Stretch artifacts detected")

        return scene

    def compile_tri_app(self, state: dict[str, Any]) -> NeutralScene:
        """
        Compile GeoXTriAppState for multi-view coordinated scene.

        Used for linking Map + Cross Section + Seismic Section.
        """
        scene = NeutralScene()

        scene.metadata = SceneMetadata(
            title="Volume Context View",
        )

        cross_section = state.get("cross_section_state")
        if cross_section:
            cross_scene = self.compile_cross_section(cross_section)
            scene.wells.extend(cross_scene.wells)
            scene.surfaces.extend(cross_scene.surfaces)
            scene.unit_polygons.extend(cross_scene.unit_polygons)
            scene.uncertainty_zones.extend(cross_scene.uncertainty_zones)

        seismic_section = state.get("seismic_section_state")
        if seismic_section:
            seismic_scene = self.compile_seismic_section(seismic_section)
            scene.volume_slices.extend(seismic_scene.volume_slices)
            scene.surfaces.extend(seismic_scene.surfaces)

        if scene.bbox is None:
            scene.bbox = BoundingBox(
                min_x=0, max_x=100, min_y=0, max_y=10, min_z=-5000, max_z=0
            )

        return scene

    def compile_display(self, state: dict[str, Any]) -> NeutralScene:
        """Compile generic GeoXDisplayState."""
        scene = NeutralScene()
        scene.metadata = SceneMetadata(title=state.get("display_id", "Display"))

        layers = state.get("layers", [])
        for layer in layers:
            if layer.get("layer_type") == "seismic":
                scene.volume_slices.append(
                    VolumeSlicePrimitive(
                        name="Seismic Layer",
                        visible=layer.get("visible", True),
                        opacity=layer.get("opacity", 1.0),
                    )
                )

        return scene

    def compile_generic(self, state: dict[str, Any]) -> NeutralScene:
        """Fallback compilation for unknown state types."""
        scene = NeutralScene()
        scene.metadata = SceneMetadata(title="Unknown Scene")
        scene.metadata.warnings.append(f"Unknown state_type: {state.get('state_type')}")
        return scene

    def compile_well(self, well_data: dict[str, Any]) -> WellTrajectoryPrimitive:
        """Compile well data to trajectory primitive."""
        trajectory_points = []
        for pt in well_data.get("trajectory", []):
            trajectory_points.append(
                Vector3(x=pt.get("x", 0), y=pt.get("y", 0), z=pt.get("z", 0))
            )

        formation_tops = {}
        for top in well_data.get("formation_tops", []):
            if isinstance(top, dict):
                formation_tops[top.get("name", "unknown")] = top.get("depth_m", 0)

        return WellTrajectoryPrimitive(
            name=well_data.get("well_name", "Unknown Well"),
            well_id=well_data.get("well_id", ""),
            trajectory=trajectory_points,
            formation_tops=formation_tops,
            provenance=well_data.get("source", "well_log"),
            is_observed=True,
        )

    def compile_fault_surface(self, fault_data: dict[str, Any]) -> SurfacePrimitive:
        """Compile fault to surface primitive."""
        vertices = []
        for pt in fault_data.get("trace_points", []):
            if isinstance(pt, dict):
                vertices.append(
                    Vector3(x=pt.get("x", 0), y=pt.get("y", 0), z=pt.get("z", 0))
                )

        fault_color = RenderColor(r=1.0, g=0.0, b=0.0)
        is_inferred = fault_data.get("is_observed", True) is False

        return SurfacePrimitive(
            name=fault_data.get("fault_name", "Fault"),
            vertices=vertices,
            color=fault_color,
            opacity=0.8 if is_inferred else 1.0,
            provenance=fault_data.get("source", "seismic"),
            is_observed=fault_data.get("is_observed", True),
            is_interpreted=is_inferred,
        )

    def compile_reflector_surface(
        self, reflector_data: dict[str, Any]
    ) -> SurfacePrimitive:
        """Compile horizon reflector to surface primitive."""
        vertices = []
        for pt in reflector_data.get("points", []):
            if isinstance(pt, dict):
                vertices.append(
                    Vector3(x=pt.get("x", 0), y=pt.get("y", 0), z=pt.get("z", 0))
                )

        return SurfacePrimitive(
            name=reflector_data.get("name", "Horizon"),
            vertices=vertices,
            color=RenderColor(r=0.0, g=0.0, b=1.0),
            provenance=reflector_data.get("source", "seismic"),
            is_observed=True,
            is_interpreted=True,
            confidence=reflector_data.get("confidence", 0.8),
        )

    def compile_unit_polygon(self, unit_data: dict[str, Any]) -> UnitPolygonPrimitive:
        """Compile geological unit to polygon primitive."""
        points_2d = []
        for pt in unit_data.get("polygon_coords", []):
            if isinstance(pt, dict):
                points_2d.append((pt.get("distance_km", 0), pt.get("elevation_m", 0)))
            elif isinstance(pt, (list, tuple)) and len(pt) >= 2:
                points_2d.append((pt[0], pt[1]))

        color_str = unit_data.get("color", "#808080")
        color = (
            RenderColor.from_hex(color_str)
            if isinstance(color_str, str)
            else RenderColor()
        )

        return UnitPolygonPrimitive(
            name=unit_data.get("unit_name", "Unknown Unit"),
            unit_name=unit_data.get("unit_name", ""),
            formation_age=unit_data.get("formation_age"),
            lithology=unit_data.get("lithology"),
            points_2d=points_2d,
            color=color,
            provenance=unit_data.get("source", "geological_model"),
            is_observed=unit_data.get("is_observed", True),
            is_interpreted=unit_data.get("is_interpreted", False),
        )

    def compile_uncertainty_zone(
        self, zone_data: dict[str, Any]
    ) -> UncertaintyZonePrimitive:
        """Compile uncertainty zone to primitive."""
        polygon_2d = []
        for pt in zone_data.get("polygon", []):
            if isinstance(pt, dict):
                polygon_2d.append((pt.get("x", 0), pt.get("y", 0)))

        return UncertaintyZonePrimitive(
            name=zone_data.get("zone_id", "Uncertainty Zone"),
            uncertainty_type=zone_data.get("uncertainty_type", "unknown"),
            polygon_2d=polygon_2d,
            confidence=zone_data.get("confidence", 0.5),
            explanation=zone_data.get("explanation", ""),
            provenance="geological_interpretation",
        )

    def compute_bbox_from_points(self, points: list[dict[str, Any]]) -> BoundingBox:
        """Compute bounding box from list of points."""
        if not points:
            return BoundingBox(
                min_x=0, max_x=100, min_y=0, max_y=10, min_z=-5000, max_z=0
            )

        xs = [
            p.get("x", p.get("distance_km", 0)) for p in points if isinstance(p, dict)
        ]
        ys = [
            p.get("y", p.get("elevation_m", 0)) for p in points if isinstance(p, dict)
        ]
        zs = [p.get("z", 0) for p in points if isinstance(p, dict)]

        return BoundingBox(
            min_x=min(xs) if xs else 0,
            max_x=max(xs) if xs else 100,
            min_y=min(ys) if ys else 0,
            max_y=max(ys) if ys else 10,
            min_z=min(zs) if zs else -5000,
            max_z=max(zs) if zs else 0,
        )

    def estimate_scale_length(self, state: dict[str, Any]) -> float:
        """Estimate appropriate scale bar length."""
        length_km = state.get("total_length_km", 100)
        if length_km > 50:
            return 10.0
        elif length_km > 20:
            return 5.0
        elif length_km > 10:
            return 2.0
        else:
            return 1.0

    def build_legend(
        self,
        units: list[dict[str, Any]],
        wells: list[dict[str, Any]],
        faults: list[dict[str, Any]],
    ) -> LegendPrimitive:
        """Build standard geological legend."""
        legend = LegendPrimitive(title="Legend")

        for unit in units:
            color_str = unit.get("color", "#808080")
            color = (
                RenderColor.from_hex(color_str)
                if isinstance(color_str, str)
                else RenderColor()
            )
            legend.entries.append(
                LegendEntry(
                    label=unit.get("unit_name", "Unit"),
                    color=color,
                )
            )

        for well in wells:
            legend.entries.append(
                LegendEntry(
                    label=well.get("well_name", "Well"),
                    color=RenderColor(r=0.0, g=0.8, b=0.0),
                    marker="circle",
                )
            )

        for fault in faults:
            legend.entries.append(
                LegendEntry(
                    label=fault.get("fault_name", "Fault"),
                    color=RenderColor(r=1.0, g=0.0, b=0.0),
                    line_style="dashed",
                )
            )

        return legend

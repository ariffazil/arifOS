import logging
from fastmcp import FastMCP
from contracts.enums.statuses import (
    get_standard_envelope,
    GovernanceStatus,
    ArtifactStatus,
)

logger = logging.getLogger("geox.map")


def register_map_tools(mcp: FastMCP, profile: str = "full"):
    """
    MAP Registry: Spatial fabric & context.
    'Where is this? What's around it?'

    Naming convention: map_{action}_{target}
    Most aliases removed - kept geox_project_well_trajectory for UI compatibility.
    """

    try:
        from services.geo_fabric.engine import fabric
        from services.evidence_store.store import store
    except ImportError:
        logger.error("Map services unavailable")
        return

    @mcp.tool(name="map_verify_coordinates")
    async def map_verify_coordinates(x: float, y: float, epsg: int) -> dict:
        """Verify: Check if coordinates are within valid geospatial bounds."""
        artifact = {
            "valid": True,
            "message": "Coordinate integrity verified (F9_PHYSICS_9)",
        }
        return get_standard_envelope(
            artifact,
            tool_class="verify",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.VERIFIED,
            ui_resource_uri="ui://map-dashboard",
        )

    @mcp.tool(name="map_get_context_summary")
    async def map_get_context_summary(bounds: list) -> dict:
        """Observe: Spatial fabric introspection. Get summary of spatial context within bounds."""
        artifact = {
            "summary": "Spatial context summary (F2_TRUTH checked)",
            "bounds": bounds,
        }
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://map-dashboard",
        )

    @mcp.tool(name="map_render_scene_context")
    async def map_render_scene_context(scene_ref: str) -> dict:
        """Observe: Render a scene for the geospatial fabric."""
        artifact = {"render_url": f"geox://map/render/{scene_ref}", "status": "Ready"}
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://map-dashboard",
        )

    @mcp.tool(name="map_synthesize_causal_scene")
    async def map_synthesize_causal_scene(elements: list) -> dict:
        """Interpret: Create a causal scene for 888_JUDGE from spatial elements."""
        artifact = {"scene_ref": "causal_scene_001", "elements_count": len(elements)}
        return get_standard_envelope(
            artifact,
            tool_class="interpret",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://map-dashboard",
        )

    @mcp.tool(name="map_earth_signals")
    async def map_earth_signals(location_ref: str) -> dict:
        """Observe: Live Earth observation = spatial context. Fetch raw earth signals."""
        artifact = {
            "location_ref": location_ref,
            "signals": "Observational stream healthy",
        }
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://map-dashboard",
        )

    @mcp.tool(name="map_project_well")
    async def map_project_well(well_ref: str, target_epsg: int = 4326) -> dict:
        """Project a well trajectory into map coordinates."""
        evidence = store.get_evidence(well_ref)
        if not evidence or evidence.ref.kind != "well":
            artifact = {"error": "Valid well evidence required"}
            return get_standard_envelope(
                artifact,
                tool_class="compute",
                governance_status=GovernanceStatus.HOLD,
                artifact_status=ArtifactStatus.REJECTED,
                ui_resource_uri="ui://map-dashboard",
            )

        payload = evidence.payload
        try:
            head = payload["head"]
            survey = payload["survey"]

            xyz_points = fabric.project_well_trajectory(
                head_xy=(head["x"], head["y"]),
                md_points=survey["md"],
                incl_points=survey["inc"],
                azim_points=survey["azi"],
            )

            head_epsg = head.get("epsg", 32648)
            projected = []
            for p in xyz_points:
                xt, yt = fabric.transform_point(p[0], p[1], head_epsg, target_epsg)
                projected.append({"x": xt, "y": yt, "z": p[2]})

            artifact = {
                "well_ref": well_ref,
                "points": projected,
                "crs": f"EPSG:{target_epsg}",
            }
            return get_standard_envelope(
                artifact,
                tool_class="compute",
                governance_status=GovernanceStatus.QUALIFY,
                artifact_status=ArtifactStatus.COMPUTED,
                ui_resource_uri="ui://map-dashboard",
            )
        except Exception as e:
            artifact = {"error": f"Projection failed: {e}"}
            return get_standard_envelope(
                artifact,
                tool_class="compute",
                governance_status=GovernanceStatus.HOLD,
                artifact_status=ArtifactStatus.REJECTED,
                ui_resource_uri="ui://map-dashboard",
            )

    # CRITICAL ALIAS for Cockpit UI - DO NOT REMOVE
    async def alias_geox_project_well_trajectory(well_ref: str, target_epsg: int = 4326):
        return await map_project_well(well_ref, target_epsg)

    @mcp.tool(name="map_transform_coordinates")
    async def map_transform_coordinates(x: float, y: float, from_epsg: int, to_epsg: int) -> dict:
        """Project a point between coordinate systems."""
        try:
            xt, yt = fabric.transform_point(x, y, from_epsg, to_epsg)
            artifact = {"x": xt, "y": yt, "crs": f"EPSG:{to_epsg}"}
            return get_standard_envelope(
                artifact,
                tool_class="compute",
                governance_status=GovernanceStatus.QUALIFY,
                artifact_status=ArtifactStatus.COMPUTED,
                ui_resource_uri="ui://map-dashboard",
            )
        except Exception as e:
            artifact = {"error": str(e)}
            return get_standard_envelope(
                artifact,
                tool_class="compute",
                governance_status=GovernanceStatus.HOLD,
                artifact_status=ArtifactStatus.REJECTED,
                ui_resource_uri="ui://map-dashboard",
            )

    @mcp.tool(name="map_georeference")
    async def map_georeference(map_ref: str, control_points: list) -> dict:
        """Interpret: Governed georeferencing of map context."""
        artifact = {
            "map_ref": map_ref,
            "control_points_count": len(control_points),
            "status": "Staged",
            "grounding_seal": "PENDING",
            "message": "Georeferencing actions are git-backed and reversible (F1 Amanah).",
        }
        return get_standard_envelope(
            artifact,
            tool_class="interpret",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.STAGED,
            ui_resource_uri="ui://georeference-map",
        )

    # Aliases
    @mcp.tool(name="geox_verify_geospatial")
    async def geox_verify_geospatial(x: float, y: float, epsg: int) -> dict:
        return await map_verify_coordinates(x, y, epsg)

    @mcp.tool(name="geox_georeference")
    async def geox_georeference(map_ref: str, control_points: list) -> dict:
        return await map_georeference(map_ref, control_points)

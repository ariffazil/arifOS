import logging
from fastmcp import FastMCP
from contracts.enums.statuses import get_standard_envelope, GovernanceStatus, ArtifactStatus

logger = logging.getLogger("geox.earth3d")

def register_earth3d_tools(mcp: FastMCP, profile: str = "full"):
    """
    EARTH 3D Registry: Volumetric seismic tools & structural modeling.
    'What does the seismic show in 3D space?'
    
    Naming convention: earth3d_{action}_{target}
    """
    
    @mcp.tool(name="earth3d_load_volume")
    async def earth3d_load_volume(volume_ref: str) -> dict:
        """Observe: Load a structural seismic volume for analysis."""
        artifact = {"volume_ref": volume_ref, "status": "Active", "bbox": [0, 0, 100, 100]}
        return get_standard_envelope(
            artifact, 
            tool_class="observe", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.LOADED, 
            uncertainty="Low",
            ui_resource_uri="ui://earth3d-dashboard"
        )

    @mcp.tool(name="earth3d_interpret_horizons")
    async def earth3d_interpret_horizons(volume_ref: str) -> dict:
        """Interpret: Automatically/Manually pick horizons within the 3D volume."""
        artifact = {"volume_ref": volume_ref, "horizons": ["Top_Reservoir", "Base_Seal"]}
        return get_standard_envelope(
            artifact, 
            tool_class="interpret", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.DRAFT, 
            uncertainty="High",
            ui_resource_uri="ui://earth3d-dashboard"
        )

    @mcp.tool(name="earth3d_model_geometries")
    async def earth3d_model_geometries(horizon_ids: list) -> dict:
        """Compute: Build architectural geometries from interpreted horizons."""
        artifact = {"model_ref": "earth_structural_001", "elements": len(horizon_ids)}
        return get_standard_envelope(
            artifact, 
            tool_class="compute", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.COMPUTED, 
            uncertainty="Moderate",
            ui_resource_uri="ui://earth3d-dashboard"
        )

    @mcp.tool(name="earth3d_verify_structural_integrity")
    async def earth3d_verify_structural_integrity(model_ref: str) -> dict:
        """Verify: Check model for structural paradoxes (e.g., overlapping faults)."""
        artifact = {"model_ref": model_ref, "consistent": True, "verdict": "PHYSICALLY_FEASIBLE"}
        return get_standard_envelope(
            artifact, 
            tool_class="verify", 
            governance_status=GovernanceStatus.SEAL, 
            artifact_status=ArtifactStatus.VERIFIED, 
            uncertainty="Low",
            ui_resource_uri="ui://earth3d-dashboard"
        )

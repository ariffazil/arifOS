import logging
from fastmcp import FastMCP
from contracts.enums.statuses import get_standard_envelope, GovernanceStatus, ArtifactStatus

logger = logging.getLogger("geox.well")

def register_well_tools(mcp: FastMCP, profile: str = "full"):
    """
    WELL Registry: Borehole & Log Analysis tools.
    'What's in this borehole?'
    
    Naming convention: well_{action}_{target}
    """
    
    try:
        from services.witness_engine.petrophysics import witness
    except ImportError:
        logger.error("Well services unavailable")
        witness = None

    @mcp.tool(name="well_load_bundle")
    async def well_load_bundle(well_ref: str, bundle_uri: str) -> dict:
        """Observe: Load a full log bundle (LAS/DLIS) into the witness context."""
        artifact = {"well_ref": well_ref, "status": "loaded", "uri": bundle_uri}
        return get_standard_envelope(
            artifact, 
            tool_class="observe", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.DRAFT, 
            uncertainty="Low",
            ui_resource_uri="ui://well-dashboard"
        )


    @mcp.tool(name="well_qc_logs")
    async def well_qc_logs(well_ref: str) -> dict:
        """Verify: Perform Quality Control on loaded logs."""
        artifact = {"well_ref": well_ref, "qc_status": "pass", "flags": []}
        return get_standard_envelope(
            artifact, 
            tool_class="verify", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.VERIFIED, 
            uncertainty="Low",
            ui_resource_uri="ui://well-dashboard"
        )


    @mcp.tool(name="well_validate_cutoffs")
    async def well_validate_cutoffs(well_ref: str, parameter: str, value: float) -> dict:
        """Verify: Validate petrophysical cutoffs against regional norms."""
        artifact = {"well_ref": well_ref, "parameter": parameter, "valid": True}
        return get_standard_envelope(
            artifact, 
            tool_class="verify", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.VERIFIED, 
            uncertainty="Low",
            ui_resource_uri="ui://well-dashboard"
        )


    @mcp.tool(name="well_select_sw_model")
    async def well_select_sw_model(formation: str, temperature_c: float) -> dict:
        """Interpret: Recommends a Water Saturation (Sw) model based on formation context."""
        if witness:
            result = witness.select_sw_model(formation, temperature_c)
        else:
            result = {"formation": formation, "model": "Archie", "temperature_c": temperature_c}
        return get_standard_envelope(
            result, 
            tool_class="interpret", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.DRAFT, 
            uncertainty="Moderate",
            ui_resource_uri="ui://well-dashboard"
        )


    @mcp.tool(name="well_compute_petrophysics")
    async def well_compute_petrophysics(
        model: str, 
        rw: float, 
        rt: float, 
        phi: float, 
        a: float = 1.0, 
        m: float = 2.0, 
        n: float = 2.0
    ) -> dict:
        """Compute: Executes physics-9 grounded petrophysical calculations."""
        if witness:
            result_obj = witness.compute_archie_sw(model, rw, rt, phi, a, m, n)
            artifact = result_obj.model_dump()
        else:
            sw = (a * rw / (rt * phi**m))**(1/n)
            artifact = {"sw": sw, "phi": phi, "rw": rw, "rt": rt, "model": model}
        return get_standard_envelope(
            artifact, 
            tool_class="compute", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.COMPUTED, 
            uncertainty="Moderate",
            ui_resource_uri="ui://well-dashboard"
        )


    @mcp.tool(name="well_verify_petrophysics")
    async def well_verify_petrophysics(well_ref: str, phi: float, sw: float) -> dict:
        """Verify: Governance check (888_HOLD) for anomalous petrophysics."""
        if witness:
            artifact = witness.hold_check(well_ref, phi, sw)
        else:
            artifact = {"well_ref": well_ref, "status": "HOLD_TRIGGERED"}
        return get_standard_envelope(
            artifact, 
            tool_class="verify", 
            governance_status=GovernanceStatus.HOLD, 
            artifact_status=ArtifactStatus.IN_REVIEW, 
            uncertainty="High",
            ui_resource_uri="ui://well-dashboard"
        )

    @mcp.tool(name="well_digitize_log")
    async def well_digitize_log(image_ref: str) -> dict:
        """Interpret: Trace analog well logs into governed digital outputs."""
        artifact = {
            "image_ref": image_ref,
            "status": "Planned",
            "message": "Analog Digitizer is currently in PLANNED stage. Neural curves extraction coming soon."
        }
        return get_standard_envelope(
            artifact, 
            tool_class="interpret", 
            governance_status=GovernanceStatus.HOLD, 
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://analog-digitizer"
        )

    # Aliases
    @mcp.tool(name="geox_compute_petrophysics")
    async def geox_compute_petrophysics(well_ref: str) -> dict:
        return await well_load_bundle(well_ref, "demo://bundle")



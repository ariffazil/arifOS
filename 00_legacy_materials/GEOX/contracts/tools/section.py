import logging
from fastmcp import FastMCP
from contracts.enums.statuses import get_standard_envelope, GovernanceStatus, ArtifactStatus

logger = logging.getLogger("geox.section")


def register_section_tools(mcp: FastMCP, profile: str = "full"):
    """
    SECTION Registry: 2D stratigraphic correlation tools.
    Cross-well analysis and profile synthesis.

    Naming convention: section_{action}_{target}
    Aliases removed - use canonical names only.
    """

    @mcp.tool(name="section_interpret_strata")
    async def section_interpret_strata(section_ref: str) -> dict:
        """Interpret: Correlate stratigraphic units across multiple wells in a section."""
        artifact = {
            "section_ref": section_ref,
            "units": ["Oligocene", "Miocene_Lower"],
            "status": "Interpolated",
        }
        return get_standard_envelope(
            artifact,
            tool_class="interpret",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://section-dashboard",
        )

    @mcp.tool(name="section_observe_well_correlation")
    async def section_observe_well_correlation(well_refs: list) -> dict:
        """Observe: Fetch raw correlation data between specified wells."""
        artifact = {"well_refs": well_refs, "correlation_indices": [0.92, 0.85, 0.77]}
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.LOADED,
            ui_resource_uri="ui://section-dashboard",
        )

    @mcp.tool(name="section_synthesize_profile")
    async def section_synthesize_profile(start_coord: tuple, end_coord: tuple) -> dict:
        """Compute: Synthesize a 2D vertical profile from the Earth model."""
        artifact = {"profile_ref": "profile_syn_001", "length_km": 15.5}
        return get_standard_envelope(
            artifact,
            tool_class="compute",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.COMPUTED,
            ui_resource_uri="ui://section-dashboard",
        )

    @mcp.tool(name="section_audit_attributes")
    async def section_audit_attributes(feature_ref: str) -> dict:
        """Verify: Audit the transform-chain for extracted seismic features."""
        # Mock audit logic based on seismic_feature_extract.py
        artifact = {
            "feature_ref": feature_ref,
            "transform_chain": ["AGC", "Normalization", "FeatureDetection"],
            "porosity_phi": 0.22,
            "permeability_k": 1000 * (0.22**3),  # Kozeny-Carman order-of-magnitude proxy
            "seal": "DITEMPA_BUKAN_DIBERI",
        }
        return get_standard_envelope(
            artifact,
            tool_class="verify",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.VERIFIED,
            ui_resource_uri="ui://attribute-audit",
        )

    @mcp.tool(name="section_vision_review")
    async def section_vision_review(image_ref: str) -> dict:
        """Interpret: Governed VLM seismic interpretation review."""
        artifact = {
            "image_ref": image_ref,
            "fault_probability": 0.85,
            "validation_probe": "7-day_cycle_active",
            "falsification_seal": "PENDING",
            "message": "Falsification Seal requires 48hr validation against ground truth.",
        }
        return get_standard_envelope(
            artifact,
            tool_class="interpret",
            governance_status=GovernanceStatus.HOLD,
            artifact_status=ArtifactStatus.IN_REVIEW,
            ui_resource_uri="ui://vision-review",
        )

    # Aliases
    @mcp.tool(name="geox_load_seismic_line")
    async def geox_load_seismic_line(start_coord: tuple, end_coord: tuple) -> dict:
        return await section_synthesize_profile(start_coord, end_coord)

    @mcp.tool(name="geox_audit_attributes")
    async def geox_audit_attributes(feature_ref: str) -> dict:
        return await section_audit_attributes(feature_ref)

    @mcp.tool(name="geox_vision_review")
    async def geox_vision_review(image_ref: str) -> dict:
        return await section_vision_review(image_ref)

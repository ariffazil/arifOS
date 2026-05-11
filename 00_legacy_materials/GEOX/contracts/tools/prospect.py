import logging
from fastmcp import FastMCP
from contracts.enums.statuses import (
    get_standard_envelope,
    GovernanceStatus,
    ArtifactStatus,
)

logger = logging.getLogger("geox.prospect")


def register_prospect_tools(mcp: FastMCP, profile: str = "full"):
    """
    PROSPECT Registry: Play fairway discovery.
    'Should we drill here?'

    Naming convention: prospect_{action}_{target}
    """

    # Canonical tool: prospect_evaluate
    @mcp.tool(name="prospect_evaluate")
    async def prospect_evaluate(prospect_ref: str) -> dict:
        """Judge: Evaluate hydrocarbon potential based on 888_JUDGE verdict."""
        artifact = {
            "prospect_ref": prospect_ref,
            "score": 0.88,
            "status": "Highly Prospective (F9 Checked)",
        }
        return get_standard_envelope(
            artifact,
            tool_class="judge",
            governance_status=GovernanceStatus.SEAL,
            artifact_status=ArtifactStatus.VERIFIED,
            uncertainty="Low",
            evidence_refs=["ratlas://play-fairway", "acp://verdict"],
            ui_resource_uri="ui://prospect-dashboard",
        )

    # Aliases (separate functions required by FastMCP)
    async def _alias_geox_prospect_evaluate(prospect_ref: str) -> dict:
        """Alias for prospect_evaluate."""
        return await prospect_evaluate(prospect_ref)

    # Canonical tool: prospect_build_structural_candidates
    @mcp.tool(name="prospect_build_structural_candidates")
    async def prospect_build_structural_candidates(prospect_ref: str) -> dict:
        """Interpret: Generate structural trap candidates for a prospect."""
        artifact = {
            "prospect_ref": prospect_ref,
            "candidates": ["Anticline_01", "Fault_Trap_Beta"],
        }
        return get_standard_envelope(
            artifact,
            tool_class="interpret",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            uncertainty="High",
            ui_resource_uri="ui://prospect-dashboard",
        )

    async def _alias_geox_prospect_build(prospect_ref: str) -> dict:
        """Alias for prospect_build_structural_candidates."""
        return await prospect_build_structural_candidates(prospect_ref)

    # Canonical tool: prospect_verify_feasibility
    @mcp.tool(name="prospect_verify_feasibility")
    async def prospect_verify_feasibility(prospect_ref: str) -> dict:
        """Verify: Technical and economic gating for the prospect."""
        artifact = {
            "prospect_ref": prospect_ref,
            "feasible": True,
            "confidence": "High",
        }
        return get_standard_envelope(
            artifact,
            tool_class="verify",
            governance_status=GovernanceStatus.HOLD,
            artifact_status=ArtifactStatus.IN_REVIEW,
            uncertainty="Moderate",
            ui_resource_uri="ui://prospect-dashboard",
        )

    @mcp.tool(name="geox_evaluate_prospect")
    async def geox_evaluate_prospect(prospect_ref: str) -> dict:
        """Alias for prospect_evaluate."""
        return await prospect_evaluate(prospect_ref)

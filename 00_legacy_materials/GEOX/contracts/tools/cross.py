import logging
from typing import Optional
from fastmcp import FastMCP
from contracts.enums.statuses import (
    get_standard_envelope,
    GovernanceStatus,
    ArtifactStatus,
    Dimension,
)

logger = logging.getLogger("geox.cross")


def register_cross_tools(mcp: FastMCP, profile: str = "full"):
    """
    CROSS Registry: Evidence & Dimension introspection.
    The glue between dimensions.

    Naming convention: cross_{action}_{target}
    Aliases maintained via separate wrapper functions (FastMCP limitation).
    """

    try:
        from services.evidence_store.store import store
    except ImportError:
        logger.error("Cross services unavailable")
        return

    async def geox_cross_evidence_list(kind: Optional[str] = None) -> dict:
        """Observe: List and filter evidence from the Sovereign Ledger."""
        refs = store.list_evidence(kind=kind)
        artifact = [ref.model_dump() for ref in refs]
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.LOADED,
            ui_resource_uri="ui://cross-dashboard",
        )

    # Alias wrapper (FastMCP limitation: only last decorator registers)
    @mcp.tool(name="cross_evidence_list")
    async def cross_evidence_list(kind: Optional[str] = None) -> dict:
        return await geox_cross_evidence_list(kind)

    async def geox_cross_evidence_get(evidence_ref: str) -> dict:
        """Observe: Fetch full evidence object including spatial context and payload."""
        obj = store.get_evidence(evidence_ref)
        if not obj:
            artifact = {"error": f"Evidence {evidence_ref} not found."}
            return get_standard_envelope(
                artifact,
                tool_class="observe",
                governance_status=GovernanceStatus.HOLD,
                artifact_status=ArtifactStatus.REJECTED,
                ui_resource_uri="ui://cross-dashboard",
            )
        artifact = obj.model_dump()
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.LOADED,
            ui_resource_uri="ui://cross-dashboard",
        )

    # Alias wrapper
    @mcp.tool(name="cross_evidence_get")
    async def cross_evidence_get(evidence_ref: str) -> dict:
        return await geox_cross_evidence_get(evidence_ref)

    async def geox_cross_dimension_list() -> dict:
        """Observe: What dimensions are currently active in this profile?"""
        artifact = {"profile": profile, "dimensions": [d.value for d in Dimension]}
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.VERIFIED,
            ui_resource_uri="ui://cross-dashboard",
        )

    # Alias wrapper
    @mcp.tool(name="cross_dimension_list")
    async def cross_dimension_list() -> dict:
        return await geox_cross_dimension_list()

    # CRITICAL: UI registry endpoint - DO NOT REMOVE
    async def geox_cross_get_tools_registry() -> dict:
        """Observe: Returns the architectural TOOLS_REGISTRY for UI synchronization."""
        artifact = {
            "dimensions": {
                "prospect": {
                    "name": "Prospecting",
                    "description": "Play Fairway Discovery",
                },
                "well": {"name": "Well", "description": "Borehole Truth Channel"},
                "section": {"name": "Section", "description": "2D Correlation"},
                "earth3d": {"name": "Earth 3D", "description": "Volumetric Seismic"},
                "time4d": {"name": "Time 4D", "description": "Basin Evolution"},
                "physics": {"name": "Physics", "description": "Sovereign Verification"},
                "map": {"name": "Map", "description": "Spatial Fabric"},
                "cross": {"name": "Cross", "description": "Dimension Introspection"},
            },
            "apps": [
                {"id": "prospect-ui", "name": "Prospect UI", "dim": "prospect"},
                {"id": "well-desk", "name": "Well Desk", "dim": "well"},
                {"id": "section-canvas", "name": "Section Canvas", "dim": "section"},
                {"id": "earth-volume", "name": "Earth Volume", "dim": "earth3d"},
                {"id": "chronos-history", "name": "Chronos History", "dim": "time4d"},
                {"id": "judge-console", "name": "Judge Console", "dim": "physics"},
                {"id": "map-layer", "name": "Map Layer", "dim": "map"},
            ],
            "version": "2.0.0-UNIFIED-SPEC",
        }
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.VERIFIED,
            ui_resource_uri="ui://cross-dashboard",
        )

    # Legacy alias for UI compatibility
    async def geox_get_tools_registry() -> dict:
        return await geox_cross_get_tools_registry()

    # PRIMARY: Canonical health endpoint
    async def geox_cross_health() -> dict:
        """Observe: Sovereign health check for all platform services."""
        artifact = {
            "status": "healthy",
            "registry": "unified",
            "profile": profile,
            "dimensions": [d.value for d in Dimension],
        }
        return get_standard_envelope(
            artifact,
            tool_class="observe",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.VERIFIED,
            ui_resource_uri="ui://cross-dashboard",
        )

    # Alias wrappers (FastMCP limitation)
    @mcp.tool(name="cross_health")
    async def cross_health() -> dict:
        return await geox_cross_health()

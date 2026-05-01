import logging
from fastmcp import FastMCP
from contracts.enums.statuses import get_standard_envelope, GovernanceStatus, ArtifactStatus

logger = logging.getLogger("geox.dashboard")

def register_dashboard_tools(mcp: FastMCP, profile: str = "full"):
    """
    DASHBOARD Registry: Entry point for MCP Apps UI.
    """
    
    async def dashboard_open(target: str = "main") -> dict:
        """Observe: Open the unified GEOX Kitchen Sink dashboard."""
        artifact = {
            "view": "kitchen_sink",
            "active_dimensions": ["well", "prospect", "map"],
            "session_id": "geox-live-001"
        }
        return get_standard_envelope(
            artifact, 
            tool_class="observe", 
            governance_status=GovernanceStatus.QUALIFY, 
            artifact_status=ArtifactStatus.USABLE,
            ui_resource_uri="ui://geox-dashboard"
        )

    # Legacy alias for backward compatibility
    async def legacy_open_dashboard():
        return await dashboard_open()

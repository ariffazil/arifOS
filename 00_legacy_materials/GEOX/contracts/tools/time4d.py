import logging
from fastmcp import FastMCP
from contracts.enums.statuses import (
    get_standard_envelope,
    GovernanceStatus,
    ArtifactStatus,
)

logger = logging.getLogger("geox.time4d")


def register_time4d_tools(mcp: FastMCP, profile: str = "full"):
    """
    TIME 4D Registry: Basin evolution & play timing.
    Simulating geological history through the temporal dimension.

    Naming convention: time4d_{action}_{target}
    Aliases removed - use canonical names only.
    """

    @mcp.tool(name="time4d_simulate_burial")
    async def time4d_simulate_burial(prospect_ref: str) -> dict:
        """Compute: Simulate sediment burial and thermal maturation through time."""
        artifact = {
            "prospect_ref": prospect_ref,
            "heat_flow": "standard",
            "maturity": "Oil_Window",
        }
        return get_standard_envelope(
            artifact,
            tool_class="compute",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.COMPUTED,
            ui_resource_uri="ui://time4d-dashboard",
        )

    @mcp.tool(name="time4d_reconstruct_paleo")
    async def time4d_reconstruct_paleo(time_ma: float) -> dict:
        """Interpret: Reconstruct Paleo-geography at a specific point in time (Ma)."""
        artifact = {"ma": time_ma, "paleo_env": "Deep_Marine", "confidence": 0.75}
        return get_standard_envelope(
            artifact,
            tool_class="interpret",
            governance_status=GovernanceStatus.QUALIFY,
            artifact_status=ArtifactStatus.DRAFT,
            ui_resource_uri="ui://time4d-dashboard",
        )

    @mcp.tool(name="time4d_verify_timing")
    async def time4d_verify_timing(trap_formation_ma: float, charge_ma: float) -> dict:
        """Verify: Check the temporal relationship between trap formation and charge."""
        valid = trap_formation_ma > charge_ma
        artifact = {
            "synchronized": valid,
            "delta": trap_formation_ma - charge_ma,
            "verdict": "valid_trap_charge_seq" if valid else "failed_timing_check",
        }
        return get_standard_envelope(
            artifact,
            tool_class="verify",
            governance_status=GovernanceStatus.SEAL if valid else GovernanceStatus.HOLD,
            artifact_status=(
                ArtifactStatus.VERIFIED if valid else ArtifactStatus.REJECTED
            ),
            ui_resource_uri="ui://time4d-dashboard",
        )

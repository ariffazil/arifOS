from __future__ import annotations
import json
from fastmcp import FastMCP

SURFACE_MAP = {
    "arifos_agent_surface_map": {
        "mcp_tools": [
            "arifos_init",
            "arifos_observe",
            "arifos_think",
            "arifos_route",
            "arifos_judge",
            "arifos_act",
            "arifos_seal"
        ],
        "mcp_resources": [
            "arifos://doctrine/floors",
            "arifos://registry/organs",
            "arifos://state/latest",
            "arifos://receipts/latest",
            "arifos://mcp/surface-map"
        ],
        "a2a_agent_card": {
            "name": "arifOS Kernel",
            "role": "constitutional governance router",
            "exposes_internal_tools": False,
            "default_authority": "observe_only",
            "irreversible_actions": "f13_required"
        },
        "fastmcp_build_rules": [
            "strict_pydantic_models",
            "approval_gate_for_mutations",
            "conformance_test_before_publish",
            "ttl_on_state_outputs",
            "boring_tool_descriptions"
        ]
    }
}

def register_surface_map(mcp: FastMCP) -> list[str]:
    @mcp.resource("arifos://mcp/surface-map")
    def get_surface_map() -> str:
        """Return the canonical arifOS Agent Surface Map showing tools, resources, and rules."""
        return json.dumps(SURFACE_MAP, indent=2)

    return ["arifos://mcp/surface-map"]

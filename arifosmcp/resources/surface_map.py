from __future__ import annotations

import json

from fastmcp import FastMCP

SURFACE_MAP = {
    "arifos_agent_surface_map": {
        "mcp_tools": [
            "arif_init",
            "arif_observe",
            "arif_think",
            "arif_route",
            "arif_memory",
            "arif_judge",
            "arif_forge",
            "arif_seal",
        ],
        "mcp_resources": [
            "arifos://doctrine",
            "arifos://trinity",
            "arifos://schema",
            "arifos://civilization",
            "arifos://seal-readiness",
            "arifos://jurisdiction",
            "arifos://identity",
            "arifos://memory",
            "arifos://vitals",
            "arifos://bootstrap",
            "arifos://human/metabolized",
            "arifos://loop-engineering",
            "arifos://quickstart",
            "arifos://mcp-alignment",
            "arifos://mcp/surface-map",
            "arifos://floor/{fid}",
            "arifos://refusal-surface",
        ],
        "a2a_agent_card": {
            "name": "arifOS Kernel",
            "role": "constitutional governance router",
            "exposes_internal_tools": False,
            "default_authority": "observe_only",
            "irreversible_actions": "f13_required",
            "chatgpt_compatible": True,
            "claude_desktop_compatible": True,
        },
        "fastmcp_build_rules": [
            "strict_pydantic_models",
            "approval_gate_for_mutations",
            "conformance_test_before_publish",
            "ttl_on_state_outputs",
            "boring_tool_descriptions",
        ],
    }
}


def register_surface_map(mcp: FastMCP) -> list[str]:
    @mcp.resource("arifos://mcp/surface-map")
    def get_surface_map() -> str:
        """Return the canonical arifOS Agent Surface Map showing tools, resources, and rules."""
        return json.dumps(SURFACE_MAP, indent=2)

    return ["arifos://mcp/surface-map"]

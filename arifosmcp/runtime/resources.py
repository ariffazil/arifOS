"""
arifosmcp/runtime/resources_v2.py — arifOS MCP v2 Resources

Resources are read-only constitutional documents.
They provide grounding, policy, schemas, governance.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE DATA
# ═══════════════════════════════════════════════════════════════════════════════

FLOORS_SPEC: dict[str, dict[str, Any]] = {
    "F1": {
        "name": "AMANAH",
        "principle": "Non-contradiction & Reversibility",
        "question": "Can this be undone?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F2": {
        "name": "TRUTH",
        "principle": "Evidence Grounding",
        "question": "Is this grounded in evidence?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F3": {
        "name": "TRI-WITNESS",
        "principle": "Theory-Constitution-Intent Alignment",
        "question": "Do theory, constitution, intent agree?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F4": {
        "name": "CLARITY",
        "principle": "Uncertainty Reduction",
        "question": "Does this reduce confusion?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F5": {
        "name": "PEACE²",
        "principle": "Non-Destruction",
        "question": "Does this destroy anything?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F6": {
        "name": "EMPATHY",
        "principle": "Dignity Preservation",
        "question": "Does this show understanding?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F7": {
        "name": "HUMILITY",
        "principle": "Uncertainty Acknowledgment",
        "question": "Are uncertainties acknowledged?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F8": {
        "name": "GENIUS",
        "principle": "System Health",
        "question": "Does this maintain system health?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F9": {
        "name": "ETHICS",
        "principle": "Non-Manipulation",
        "question": "Is this manipulative or deceptive?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F10": {
        "name": "CONSCIENCE",
        "principle": "Consciousness Claims",
        "question": "Is this claiming consciousness?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
    "F11": {
        "name": "AUDITABILITY",
        "principle": "Inspectability",
        "question": "Is this logged and inspectable?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F12": {
        "name": "RESILIENCE",
        "principle": "Safe Failure",
        "question": "Does this fail safely?",
        "type": "SOFT",
        "blocks_on_failure": False,
    },
    "F13": {
        "name": "ADAPTABILITY",
        "principle": "Safety Preservation",
        "question": "Do updates preserve safety?",
        "type": "HARD",
        "blocks_on_failure": True,
    },
}

VERDICT_SPEC: dict[str, Any] = {
    "verdicts": {
        "SEAL": {
            "code": 0,
            "description": "Execute immediately",
            "color": "#2ecc71",
            "action": "PROCEED",
        },
        "PARTIAL": {
            "code": 101,
            "range": "101-499",
            "description": "Execute with notes",
            "color": "#f1c40f",
            "action": "PROCEED_WITH_CAUTION",
        },
        "CAUTION": {
            "code": 500,
            "range": "500-899",
            "description": "Execute with warnings",
            "color": "#e67e22",
            "action": "PROCEED_WITH_WARNINGS",
        },
        "HOLD": {
            "code": -1,
            "description": "Awaiting human",
            "color": "#9b59b6",
            "action": "HUMAN_REVIEW_REQUIRED",
        },
        "SABAR": {
            "code": -2,
            "description": "Wait and retry",
            "color": "#3498db",
            "action": "DEFER_RETRY",
        },
        "VOID": {
            "code": 999,
            "description": "Blocked",
            "color": "#e74c3c",
            "action": "BLOCK",
        },
    },
    "required_fields": [
        "verdict",
        "floors_triggered",
        "confidence",
        "reasoning_class",
    ],
    "output_schema": {
        "type": "object",
        "required": ["verdict", "floors_triggered", "confidence", "reasoning_class"],
        "properties": {
            "verdict": {"type": "string", "enum": ["SEAL", "PARTIAL", "VOID", "HOLD"]},
            "floors_triggered": {"type": "array", "items": {"type": "string"}},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reasoning_class": {"type": "string", "enum": ["constitutional", "safety", "uncertainty"]},
            "evidence_hash": {"type": "string"},
            "timestamp": {"type": "string", "format": "date-time"},
        },
    },
}

SYSTEM_CAPABILITIES: dict[str, Any] = {
    "name": "ARIFOS MCP",
    "version": "2.0.0",
    "namespace": "arifos",
    "constitutional_floors": 13,
    "tools": {
        "public": ["arifos_init", "arifos_route", "arifos_judge", "arifos_forge"],
        "internal": ["arifos_sense", "arifos_mind", "arifos_heart", "arifos_ops", "arifos_memory", "arifos_vault", "arifos_vps_monitor"],
        "total": 11,
    },
    "mcp_version": "2025-11-25",
    "schema_registry": {
        "version": "2.0.0",
        "resources": [
            "arifos://schema/master",
            "arifos://schema/tools",
            "arifos://schema/tool/{tool_id}",
            "arifos://schema/stages",
            "arifos://schema/trinity",
            "arifos://schema/routing-guide",
        ],
        "stages": ["000_INIT", "111_SENSE", "333_MIND", "444_ROUTER", "555_MEMORY", "666_HEART", "777_OPS", "888_JUDGE", "999_VAULT", "FORGE_010"],
        "trinity": {
            "Δ": "Discernment - Reality, reasoning, execution",
            "Ψ": "Sovereignty - Session, routing, judgment, seal",
            "Ω": "Stability - Memory, safety, thermodynamics",
        },
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# V2 RESOURCE REGISTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def register_v2_resources(mcp: FastMCP) -> list[str]:
    """Register all v2 resources using arifos:// scheme."""
    
    @mcp.resource("arifos://governance/floors")
    def governance_floors() -> dict[str, Any]:
        return FLOORS_SPEC

    @mcp.resource("arifos://governance/verdict")
    def governance_verdict_spec() -> dict[str, Any]:
        return VERDICT_SPEC

    @mcp.resource("arifos://system/capabilities")
    def system_capabilities() -> dict[str, Any]:
        return SYSTEM_CAPABILITIES

    # ═══════════════════════════════════════════════════════════════════════════
    # CONTEXT-RICH TOOL REGISTRY RESOURCES
    # ═══════════════════════════════════════════════════════════════════════════
    
    from arifosmcp.schema import get_registry
    
    registry = get_registry()
    
    @mcp.resource("arifos://schema/master")
    def schema_master() -> dict[str, Any]:
        """Complete arifOS master schema with stages, Trinity, and transitions."""
        return registry.master_schema or {}
    
    @mcp.resource("arifos://schema/tools")
    def schema_tools() -> dict[str, Any]:
        """All tool context packets with full semantic metadata."""
        return registry.tool_packets
    
    @mcp.resource("arifos://schema/tool/{tool_id}")
    def schema_tool(tool_id: str) -> dict[str, Any]:
        """Context packet for a specific tool (e.g., arifos.mind)."""
        packet = registry.get_tool_packet(tool_id)
        if packet:
            return packet
        return {"error": f"Tool {tool_id} not found", "available": list(registry.tool_packets.keys())}
    
    @mcp.resource("arifos://schema/stages")
    def schema_stages() -> dict[str, Any]:
        """Governance stage definitions and transitions."""
        master = registry.master_schema or {}
        return {
            "stage_order": master.get("stage_order", []),
            "stages": master.get("stages", {}),
            "transitions": master.get("transitions", {})
        }
    
    @mcp.resource("arifos://schema/trinity")
    def schema_trinity() -> dict[str, Any]:
        """Trinity lane definitions (Δ Discernment, Ψ Sovereignty, Ω Stability)."""
        master = registry.master_schema or {}
        return master.get("trinity", {})
    
    @mcp.resource("arifos://schema/envelopes")
    def schema_envelopes() -> dict[str, Any]:
        """Shared request/response envelope schemas."""
        return {
            "request": registry.get_request_schema(),
            "response": registry.get_response_schema(),
            "context_packet": registry.get_context_packet_schema()
        }
    
    @mcp.resource("arifos://schema/alias-map")
    def schema_alias_map() -> dict[str, Any]:
        """Mapping from public aliases to backing tools."""
        return registry.get_alias_map()
    
    @mcp.resource("arifos://schema/tool-summary")
    def schema_tool_summary() -> list[dict[str, Any]]:
        """Compact summary of all tools for quick reference."""
        return registry.get_tool_summary()
    
    @mcp.resource("arifos://schema/chatgpt-guide/{tool_id}")
    def schema_chatgpt_guide(tool_id: str) -> dict[str, Any]:
        """ChatGPT-specific usage guidance for a tool."""
        guidance = registry.get_chatgpt_guidance(tool_id)
        if guidance:
            return guidance
        return {"error": f"No guidance for {tool_id}"}
    
    @mcp.resource("arifos://schema/routing-guide")
    def schema_routing_guide() -> dict[str, Any]:
        """Complete routing guidance for stage transitions."""
        return registry.get_routing_guide()

    registered = [
        "arifos://governance/floors",
        "arifos://governance/verdict",
        "arifos://system/capabilities",
        # Schema registry resources
        "arifos://schema/master",
        "arifos://schema/tools",
        "arifos://schema/tool/{tool_id}",
        "arifos://schema/stages",
        "arifos://schema/trinity",
        "arifos://schema/envelopes",
        "arifos://schema/alias-map",
        "arifos://schema/tool-summary",
        "arifos://schema/chatgpt-guide/{tool_id}",
        "arifos://schema/routing-guide",
    ]
    logger.info(f"Registered {len(registered)} v2 resources.")
    return registered


# ═══════════════════════════════════════════════════════════════════════════════
# LEGACY UTILITY STUBS (backward compat for tools_internal + rest_routes)
# ═══════════════════════════════════════════════════════════════════════════════

def apex_tools_html_rows() -> str:
    """HTML rows for apex tools table (stub — rendered dynamically)."""
    return ""


def apex_tools_markdown_table() -> str:
    """Markdown table of apex tools (stub — rendered dynamically)."""
    return ""


def manifest_resources() -> list[dict]:
    """Return registered resource URIs (stub for stdio compat)."""
    return [
        {"uri": "arifos://governance/floors", "name": "Constitutional Floors"},
        {"uri": "arifos://governance/verdict", "name": "Verdict Specification"},
        {"uri": "arifos://system/capabilities", "name": "System Capabilities"},
        {"uri": "arifos://schema/master", "name": "Master Schema"},
        {"uri": "arifos://schema/tools", "name": "Tool Schemas"},
    ]


async def read_resource_content(uri: str) -> str:
    """Read resource content by URI (stub — returns empty for unknown URIs)."""
    return ""


def register_resources(mcp: "FastMCP") -> None:  # type: ignore[name-defined]
    """Alias for register_v2_resources — backward compat."""
    register_v2_resources(mcp)

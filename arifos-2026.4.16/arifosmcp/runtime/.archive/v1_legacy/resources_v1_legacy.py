# arifOS Enterprise Resources v2
from __future__ import annotations
import json
from fastmcp import FastMCP

def register_resources(mcp: FastMCP) -> None:
    """Register read-only contextual data (constitution) and schema registry."""
    # Register schema resources (context-rich tool registry)
    register_schema_resources(mcp)

    @mcp.resource("arifos://governance/floors")
    def governance_floors() -> str:
        """The 13 Constitutional Floors of arifOS."""
        return json.dumps({
            "F1": "Amanah: All actions must be reversible.",
            "F2": "Truth: Grounding in evidence; no hallucinations.",
            "F3": "Tri-Witness: Consensus between Physics, Math, and Language.",
            "F4": "ΔS Clarity: Entropy reduction in decision making.",
            "F5": "Peace²: Lyapunov stability in execution.",
            "F6": "Empathy: Protection of the weakest stakeholder.",
            "F7": "Humility: Calibrated uncertainty (Ω0 target 0.04).",
            "F8": "Genius: Coherence and structured forging.",
            "F9": "Anti-Hantu: No dark patterns or deceptive logic.",
            "F10": "Ontology: No claims of consciousness or personhood.",
            "F11": "Authority: Strict identity and permission gating.",
            "F12": "Resilience: Graceful failure and adversarial defense.",
            "F13": "Sovereign: Ultimate human veto (888 Judge)."
        }, indent=2)

    @mcp.resource("arifos://governance/verdict-spec")
    def verdict_spec() -> str:
        """Canonical verdict output specification."""
        return json.dumps({
            "verdicts": ["SEAL", "HOLD", "VOID", "PARTIAL"],
            "required_fields": [
                "verdict",
                "floors_triggered",
                "confidence",
                "reasoning_class"
            ]
        }, indent=2)

    @mcp.resource("arifos://system/capabilities")
    def system_capabilities() -> str:
        """Machine-readable capability map."""
        return json.dumps({
            "namespace": "arifos.v2",
            "version": "2.0.0",
            "tools_public": ["arifos.v2.init", "arifos.v2.route", "arifos.v2.judge"],
            "tools_internal": ["sense", "mind", "heart", "ops", "memory", "vault"],
            "transports": ["streamable-http", "stdio"]
        }, indent=2)

    @mcp.resource("arifos://system/architecture")
    def system_architecture() -> str:
        """High-level system design and pipeline logic."""
        return """# arifOS Architecture v2
        
Golden Path: init → route → [sense | mind | heart] → ops → judge → vault

1. **init**: Session establishment.
2. **route**: Lanes selection.
3. **Internal Subsystems**: Specialized logic blocks.
4. **judge**: Constitutional synthesis.
5. **vault**: Immutable persistence.
"""

    @mcp.resource("arifos://compliance/mapping")
    def compliance_mapping() -> str:
        """Mapping of floors to global standards."""
        return json.dumps({
            "SOC2": ["F2", "F9", "F11"],
            "ISO42001": ["F4", "F6", "F12"],
            "Nusantara-Standard": ["F1", "F7", "F13"]
        }, indent=2)

# Helper functions for HTML rendering (backward compat)
def apex_tools_html_rows(): return ""
def apex_tools_markdown_table(): return ""


# ═══════════════════════════════════════════════════════════════════════════════
# CONTEXT-RICH TOOL REGISTRY RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

def register_schema_resources(mcp: FastMCP) -> None:
    """Register schema registry resources for semantic tool discovery."""
    from arifosmcp.schema import get_registry
    
    registry = get_registry()
    
    @mcp.resource("arifos://schema/master")
    def schema_master() -> str:
        """Complete arifOS master schema with stages, Trinity, and transitions."""
        schema = registry.master_schema
        if schema:
            return json.dumps(schema, indent=2)
        return json.dumps({"error": "Schema not loaded"})
    
    @mcp.resource("arifos://schema/tools")
    def schema_tools() -> str:
        """All tool context packets with full semantic metadata."""
        packets = registry.tool_packets
        return json.dumps(packets, indent=2)
    
    @mcp.resource("arifos://schema/tool/{tool_id}")
    def schema_tool(tool_id: str) -> str:
        """Context packet for a specific tool (e.g., arifos.mind)."""
        packet = registry.get_tool_packet(tool_id)
        if packet:
            return json.dumps(packet, indent=2)
        return json.dumps({"error": f"Tool {tool_id} not found", "available": list(registry.tool_packets.keys())})
    
    @mcp.resource("arifos://schema/stages")
    def schema_stages() -> str:
        """Governance stage definitions and transitions."""
        master = registry.master_schema or {}
        return json.dumps({
            "stage_order": master.get("stage_order", []),
            "stages": master.get("stages", {}),
            "transitions": master.get("transitions", {})
        }, indent=2)
    
    @mcp.resource("arifos://schema/trinity")
    def schema_trinity() -> str:
        """Trinity lane definitions (Δ Discernment, Ψ Sovereignty, Ω Stability)."""
        master = registry.master_schema or {}
        return json.dumps(master.get("trinity", {}), indent=2)
    
    @mcp.resource("arifos://schema/envelopes")
    def schema_envelopes() -> str:
        """Shared request/response envelope schemas."""
        return json.dumps({
            "request": registry.get_request_schema(),
            "response": registry.get_response_schema(),
            "context_packet": registry.get_context_packet_schema()
        }, indent=2)
    
    @mcp.resource("arifos://schema/alias-map")
    def schema_alias_map() -> str:
        """Mapping from public aliases to backing tools."""
        return json.dumps(registry.get_alias_map(), indent=2)
    
    @mcp.resource("arifos://schema/tool-summary")
    def schema_tool_summary() -> str:
        """Compact summary of all tools for quick reference."""
        return json.dumps(registry.get_tool_summary(), indent=2)
    
    @mcp.resource("arifos://schema/chatgpt-guide/{tool_id}")
    def schema_chatgpt_guide(tool_id: str) -> str:
        """ChatGPT-specific usage guidance for a tool."""
        guidance = registry.get_chatgpt_guidance(tool_id)
        if guidance:
            return json.dumps(guidance, indent=2)
        return json.dumps({"error": f"No guidance for {tool_id}"})
    
    @mcp.resource("arifos://schema/routing-guide")
    def schema_routing_guide() -> str:
        """Complete routing guidance for stage transitions."""
        return json.dumps(registry.get_routing_guide(), indent=2)

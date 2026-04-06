# arifOS Enterprise Resources v2
from __future__ import annotations
import json
from fastmcp import FastMCP

def register_resources(mcp: FastMCP) -> None:
    """Register read-only contextual data (constitution)."""

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

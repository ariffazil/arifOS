"""
arifosmcp/runtime/prompts.py — arifOS Functional Task Templates

Canonical prompt templates for arifOS MCP.
Rewritten as explicit task templates rather than identities.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import logging
from fastmcp import FastMCP

logger = logging.getLogger(__name__)

def register_prompts(mcp: FastMCP) -> None:
    """Wire the functional arifOS prompts onto *mcp*."""

    @mcp.prompt("prompt_init_anchor")
    def prompt_init_anchor(actor_id: str, intent: str) -> str:
        """Start a governed arifOS session template."""
        return (
            f"Initialize constitutional session for actor '{actor_id}' with intent: '{intent}'. "
            "Establish identity binding and retrieve the initial telemetry seed."
        )

    @mcp.prompt("prompt_sense_reality")
    def prompt_sense_reality(query: str) -> str:
        """Gather evidence and ground in present reality template."""
        return (
            f"Ground the following query in physical reality: '{query}'. "
            "Verify facts, check temporal state, and gather earth-witness evidence."
        )

    @mcp.prompt("prompt_reason_synthesis")
    def prompt_reason_synthesis(task: str) -> str:
        """Structured reasoning with uncertainty bands template."""
        return (
            f"Perform first-principles reasoning for task: '{task}'. "
            "Provide structured synthesis with explicit uncertainty (Ω₀) and clarity (ΔS) metrics."
        )

    @mcp.prompt("prompt_critique_safety")
    def prompt_critique_safety(proposal: str) -> str:
        """Safety, dignity, and adversarial critique template."""
        return (
            f"Red-team the following proposal for ethical risks: '{proposal}'. "
            "Simulate consequence scenarios and evaluate against floors F5, F6, and F9."
        )

    @mcp.prompt("prompt_route_kernel")
    def prompt_route_kernel(request: str) -> str:
        """Choose metabolic tool path and next lane template."""
        return (
            f"Determine the correct metabolic lane for request: '{request}'. "
            "Route through stages 000-999 based on risk and task type."
        )

    @mcp.prompt("prompt_memory_recall")
    def prompt_memory_recall(query: str) -> str:
        """Pull governed memory for engineering tasks template."""
        return (
            f"Retrieve relevant engineering context from vector memory for: '{query}'. "
            "Ensure F10/F2 verification of recalled knowledge."
        )

    @mcp.prompt("prompt_estimate_ops")
    def prompt_estimate_ops(action: str) -> str:
        """Compute costs, capacity, and timelines template."""
        return (
            f"Estimate thermodynamic costs and operational capacity for: '{action}'. "
            "Analyze entropy drift and resource requirements."
        )

    @mcp.prompt("prompt_judge_verdict")
    def prompt_judge_verdict(task: str, risk_tier: str, telemetry_json: str | None = None) -> str:
        """Produce final constitutional verdict block template."""
        base = f"Render a final constitutional verdict for task '{task}' at risk tier '{risk_tier}'."
        if telemetry_json:
            base += f" Use provided telemetry: {telemetry_json}"
        return base + " Return SEAL, PARTIAL, VOID, or 888_HOLD with floor-by-floor justification."

    @mcp.prompt("prompt_human_explainer")
    def prompt_human_explainer(verdict: str, reasoning: str) -> str:
        """Translate machine verdict into plain human explanation template."""
        return (
            f"Translate the following {verdict} verdict into plain human language: '{reasoning}'. "
            "Highlight the specific constitutional floors (F1-F13) that drove this decision."
        )

    @mcp.prompt("prompt_vault_record")
    def prompt_vault_record(decision: str, evidence: str) -> str:
        """Prepare immutable vault logging narrative and JSON template."""
        return (
            f"Prepare a canonical vault record for decision: '{decision}'. "
            f"Bundle evidence: '{evidence}' and format for Merkle-hashed ledger sealing."
        )

    logger.info("Registered functional arifOS prompts.")

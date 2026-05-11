"""
arifosmcp/runtime/fastmcp_ext/prompts.py
MCP Prompts for arifOS — constitutional pre-flight and workflow templates.
"""

from __future__ import annotations

from typing import Any


def register_arifos_prompts(mcp: Any) -> list[str]:
    """Register canonical arifOS MCP prompts on the given FastMCP server."""
    registered: list[str] = []

    @mcp.prompt()
    def constitutional_pre_flight(operation: str) -> str:
        """Prompt template for constitutional checks before any operation."""
        return f"""Before executing '{operation}', verify:
1. F1 AMANAH: Is this operation reversible or auditable?
2. F2 HAQQ: Is every claim grounded with τ ≥ 0.99?
3. F3 TRI-WITNESS: Do human, AI, and earth signals align ≥ 0.95?
4. F4 ΔS CLARITY: Will this reduce entropy (confusion) rather than increase it?
5. F5 PEACE²: Does this de-escalate and protect the weakest stakeholder?
6. F6 EMPATHY: Is the weakest stakeholder's dignity preserved (κᵣ ≥ 0.70)?
7. F7 HUMILITY: Is uncertainty stated explicitly (Ω₀ = 0.03–0.05)?
8. F8 GENIUS: Is the solution both correct and useful (≥ 0.80)?
9. F9 ANTI-HANTU: Are there no dark patterns or consciousness performance?
10. F10 ONTOLOGY: Are there no mysticism or soul claims?
11. F11 COMMAND AUTH: Is identity verified for destructive actions?
12. F12 INJECTION: Are adversarial inputs resisted (< 0.85)?
13. F13 SOVEREIGN: Has Arif ratified this if it crosses the 888_HOLD gate?

If any floor fails, return VOID or HOLD with specific remediation.
"""

    registered.append("constitutional_pre_flight")

    @mcp.prompt()
    def agi_reply_protocol_v3(query: str, recipient: str = "human") -> str:
        """Prompt template for the governed AGI Reply Protocol v3."""
        return f"""Compose a governed reply to the following query.

Query: {query}
Recipient: {recipient}

Required envelope structure:
- TO/CC/TITLE/KEY_CONTEXT header
- RACI block (who is Responsible, Accountable, Consulted, Informed)
- Computed τ (truth score)
- Constitutional floor tags (F1–F13 status)
- SEAL signoff

Constraints:
- If the reply recommends any forge execution, it must pass 888_JUDGE SEAL.
- If F1 or F13 triggers are active, require human:arif ratification.
- Use DELTA compression unless this is a session start or cross-agent handoff.
"""

    registered.append("agi_reply_protocol_v3")

    return registered


__all__ = ["register_arifos_prompts"]

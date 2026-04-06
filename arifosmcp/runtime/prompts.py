# arifOS Enterprise Prompts v2
from __future__ import annotations
from typing import Any
from fastmcp import FastMCP

def register_prompts(mcp: FastMCP) -> None:
    """Register structured task templates (contracts)."""

    @mcp.prompt()
    def constitutional_analysis(query: str, risk_tier: str = "medium") -> str:
        """Run full constitutional reasoning pipeline (sense → mind → heart → judge)."""
        return f"""Evaluate the following query using the arifOS v2 pipeline:
Query: {query}
Requested Risk Tier: {risk_tier}

Instructions:
1. Ground the query in present reality using arifos.v2.sense.
2. Synthesize a logical response using arifos.v2.mind.
3. Perform an adversarial safety critique using arifos.v2.heart.
4. Finalize with a constitutional verdict via arifos.v2.judge.
"""

    @mcp.prompt()
    def governance_audit(content: str) -> str:
        """Evaluate content for floor violations and compliance mapping."""
        return f"""Perform a governance audit on the following content:
Content: {content}

Instructions:
1. Cross-reference the content against arifos://governance/floors.
2. Identify specific floor triggers.
3. Map findings to compliance standards via arifos://compliance/mapping.
"""

    @mcp.prompt()
    def execution_planning(task: str) -> str:
        """Generate execution plan, thermodynamic costs, and obtain judge approval."""
        return f"""Create a governed execution plan for:
Task: {task}

Instructions:
1. Define atomic steps.
2. Estimate ops cost and thermodynamics via arifos.v2.ops.
3. Submit plan for final judge verdict via arifos.v2.judge.
"""

    @mcp.prompt()
    def minimal_response(query: str) -> str:
        """Return answer only, skipping verbose reasoning for low-latency apps."""
        return f"""Provide a direct, minimal response to:
Query: {query}

Constraint: Use arifos.v2.route to select the fastest lane. Skip intermediate reasoning if safe.
"""

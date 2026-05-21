"""
arifOS Mind MCP Surface — 333_MIND
══════════════════════════════════

MCP Tools, Resources, and Prompts for Cognitive Metabolism.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from arifosmcp.runtime.mind_reason import (
    arif_mind_claim_attest,
    arif_mind_reason_v2,
    arif_mind_step,
    arif_mind_trace_get,
)
from arifosmcp.schemas.mind_metabolism import MindRequest

# Create FastMCP server for MIND
mcp = FastMCP("arifOS-Mind")

# ═══════════════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
async def arif_mind_reason(
    query: str,
    session_id: str | None = None,
    mode: str = "metabolize"
) -> dict[str, Any]:
    """Execute constitutional reasoning and cognitive metabolism."""
    request = MindRequest(query=query, mode=mode, session_id=session_id)
    result = await arif_mind_reason_v2(request)
    return result.model_dump()

@mcp.tool()
async def arif_mind_step(
    session_id: str,
    step_type: str,
    content: str,
    parent_step: int | None = None
) -> dict[str, Any]:
    """Execute a single bounded reasoning step within a session."""
    return await arif_mind_step(session_id, step_type, content, parent_step)

@mcp.tool()
async def arif_mind_claim_attest(
    claim: str,
    evidence_receipts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Bind a claim to evidence receipts and determine language strength."""
    result = await arif_mind_claim_attest(claim, evidence_receipts)
    return result.model_dump()

@mcp.tool()
async def arif_mind_trace_get(session_id: str) -> dict[str, Any]:
    """Retrieve the full reasoning trace for a cognitive session."""
    return await arif_mind_trace_get(session_id)

# ═══════════════════════════════════════════════════════════════════════════════
# MCP RESOURCES
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.resource("mind://templates")
def get_mind_templates() -> str:
    """Reasoning templates available for MIND orchestration."""
    return "first-principles, scientific-method, risk-assessment, swot-analysis"

@mcp.resource("mind://trace/{session_id}")
async def get_mind_trace_resource(session_id: str) -> str:
    """Inspectable reasoning trace for a session."""
    trace = await arif_mind_trace_get(session_id)
    return str(trace)

@mcp.resource("mind://claim-ladder")
def get_claim_ladder() -> str:
    """Epistemic claim ladder for evidence-bound language."""
    return "L0: speculation, L1: suggests, L2: indicates, L3: says, L4: confirms, L5: verified"

# ═══════════════════════════════════════════════════════════════════════════════
# MCP PROMPTS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.prompt()
def mind_metabolize(query: str) -> str:
    """Prompt to digest input into structured arifOS context."""
    return f"Metabolize this query: {query}. Identify core problem and constitutional relevance."

@mcp.prompt()
def mind_first_principles(problem: str) -> str:
    """Template for first-principles reasoning under F-floors."""
    return f"Break down this problem using first principles: {problem}. Ground every axiom in F1-F13."

"""
arifOS Mind MCP Surface — 333_MIND
══════════════════════════════════

MCP Tools, Resources, and Prompts for Cognitive Metabolism.
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any, cast

from fastmcp import FastMCP

# Import implementations under aliased names so the @mcp.tool() wrappers below
# don't shadow them. Each wrapper redefines the public name locally; calling that
# name inside the wrapper body would recurse infinitely. The aliased names always
# resolve to the real implementation in mind_reason.py.
from arifosmcp.runtime.mind_reason import (
    arif_mind_claim_attest as _arif_mind_claim_attest_impl,
)
from arifosmcp.runtime.mind_reason import (
    arif_mind_step as _arif_mind_step_impl,
)
from arifosmcp.runtime.mind_reason import (
    arif_mind_trace_get as _arif_mind_trace_get_impl,
)
from arifosmcp.runtime.mind_reason import (
    arif_think_v2,
)
from arifosmcp.schemas.mind_metabolism import MindRequest

# Create FastMCP server for MIND
mcp = FastMCP("arifOS-Mind")

# ═══════════════════════════════════════════════════════════════════════════════
# MCP TOOLS
# ═══════════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def arif_think(
    query: str, session_id: str | None = None, mode: str = "metabolize"
) -> dict[str, Any]:
    """Execute constitutional reasoning and cognitive metabolism."""
    request = MindRequest(query=query, mode=mode, session_id=session_id)
    result = await arif_think_v2(request)
    return cast(dict[str, Any], result.model_dump())


@mcp.tool()
async def arif_mind_step(
    session_id: str, step_type: str, content: str, parent_step: int | None = None
) -> dict[str, Any]:
    """Execute a single bounded reasoning step within a session."""
    return cast(
        dict[str, Any],
        await _arif_mind_step_impl(session_id, step_type, content, parent_step),
    )


@mcp.tool()
async def arif_mind_claim_attest(
    claim: str, evidence_receipts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Bind a claim to evidence receipts and determine language strength."""
    result = await _arif_mind_claim_attest_impl(claim, evidence_receipts)
    return cast(dict[str, Any], result.model_dump())


@mcp.tool()
async def arif_mind_trace_get(session_id: str) -> dict[str, Any]:
    """Retrieve the full reasoning trace for a cognitive session."""
    return cast(dict[str, Any], await _arif_mind_trace_get_impl(session_id))


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


@mcp.prompt(
    name="mind_metabolize",
    description=(
        "Digest query into structured arifOS context — explicit F2/F4/F7/F9 anchoring. "
        "v2 forged 2026-07-11 (F-08 expansion + F-10 floors_referenced metadata)."
    ),
)
def mind_metabolize(query: str) -> str:
    """Metabolize a query into structured arifOS context.

    floors_referenced: F2,F4,F7,F9
    """
    return f"""Metabolize this query: {query}

Required steps:
1. Classify the core problem (epistemic rung: OBS / DER / INT / SPEC).
2. Identify constitutional relevance (which F1-F13 floors does it touch?).
3. State the epistemic state explicitly — τ and Ω₀ (F2 TRUTH, F7 HUMILITY).
4. Identify missing evidence (what would resolve uncertainty?).
5. Mark C_dark risk — any hallucination or dark-pattern path? (F9 ANTI-HANTU)
6. Estimate ΔS impact of the proposed metabolisation (F4 CLARITY).

Output: structured context with
{{epistemic_rung, tau, omega_0, floors_touched, missing_evidence, c_dark_risk, delta_s}}.
"""


@mcp.prompt(
    name="mind_first_principles",
    description=(
        "First-principles decomposition with explicit F1/F2/F3/F4/F8/F9 grounding. "
        "v2 forged 2026-07-11 (F-08 expansion + F-10 floors_referenced metadata)."
    ),
)
def mind_first_principles(problem: str) -> str:
    """First-principles reasoning under F1-F13 floors.

    floors_referenced: F1,F2,F3,F4,F8,F9
    """
    return f"""Break down this problem using first principles: {problem}

Required grounding:
1. Axiom enumeration — list every axiom in F1-F13 that applies.
2. Entropy budget — ΔS impact of the proposed solution (F4 CLARITY).
3. Precision budget — τ threshold for each axiom's claim (F2 TRUTH).
4. C_dark check — any plausible hallucination or dark-pattern path? (F9 ANTI-HANTU)
5. Reversibility check — is each axiom-step reversible? (F1 AMANAH)
6. Witness plan — what human / AI / earth signal would corroborate each step? (F3 WITNESS)
7. Genius test — is the simplest correct path being taken? (F8 GENIUS, G ≥ 0.80)

Output: decomposition tree with axiom attribution per node.
"""

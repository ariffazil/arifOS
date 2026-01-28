"""
ARIF SERVER (v52.4.0) - The Architect (Nexus)
Entanglement of Mind (Logic) and Heart (Empathy).

Responsibility:
    - agi_genius: Sense -> Think -> Atlas (Mind)
    - asi_act: Evidence -> Empathy -> Act (Heart)

Architecture:
    - Transport: SSE (Scalable, Remote-ready)
    - Behavior: Neural/Symbolic processing
    - Note: Heavy compute. May hang. Isolated from AXIS.

If ARIF hangs or crashes, AXIS will recover the session via Loop Bootstrap.

DITEMPA BUKAN DIBERI
"""

from typing import Dict, Any, Optional, List
from fastmcp import FastMCP
import logging

# Core Imports
from arifos.mcp.tools.mcp_aaa import mcp_agi_genius, mcp_asi_act
from arifos.core.enforcement.metrics import OMEGA_0_MIN

logger = logging.getLogger(__name__)

# Initialize ARIF Server
mcp = FastMCP("ARIF", dependencies=["pydantic"])


# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool()
async def arif_agi_genius(
    action: str,
    query: str = "",
    session_id: str = "",
    thought: str = "",
    draft: str = "",
    truth_score: float = 1.0,
    context: Optional[Dict[str, Any]] = None,
    axioms: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    AGI GENIUS: The Mind (Delta).

    Reasoning, logic, and truth evaluation.

    Actions:
        - sense: Lane classification + truth threshold (111)
        - think: Deep reasoning with constitutional constraints (222)
        - reflect: Clarity/entropy checking (222)
        - atlas: Meta-cognition & governance mapping (333)
        - forge: Clarity refinement + humility injection (777)
        - evaluate: Floor evaluation (F2 + F6)
        - full: Complete AGI pipeline (sense -> think -> atlas -> forge)

    Args:
        action: One of sense, think, reflect, atlas, forge, evaluate, full
        query: User query or topic
        session_id: Session ID from 000_init
        thought: Thought to process
        draft: Draft text for evaluation
        truth_score: Current truth score
        context: Additional context
        axioms: Axioms for atlas mapping

    Returns:
        GeniusResult with reasoning, truth_score, entropy_delta
    """
    return await mcp_agi_genius(
        action=action,
        query=query,
        session_id=session_id,
        thought=thought,
        draft=draft,
        truth_score=truth_score,
        context=context,
        axioms=axioms,
    )


@mcp.tool()
async def arif_asi_act(
    action: str,
    text: str = "",
    session_id: str = "",
    query: str = "",
    proposal: str = "",
    stakeholders: Optional[List[str]] = None,
    agi_result: Optional[Dict[str, Any]] = None,
    sources: Optional[List[str]] = None,
    witness_request_id: str = "",
    approval: bool = False,
    reason: str = "",
) -> Dict[str, Any]:
    """
    ASI ACT: The Heart (Omega).

    Empathy, safety, and action alignment.

    Actions:
        - evidence: Truth grounding via sources (444)
        - empathize: Power-aware recalibration (555)
        - align: Constitutional veto gates (666)
        - act: Execution with tri-witness gating (666)
        - witness: Collect tri-witness signatures (333)
        - evaluate: Floor evaluation (F3 + F4 + F5)
        - full: Complete ASI pipeline

    Args:
        action: One of evidence, empathize, align, act, witness, evaluate, full
        text: Text to process
        session_id: Session ID from 000_init
        query: User query
        proposal: Proposed action
        stakeholders: List of stakeholders for empathy analysis
        agi_result: Result from agi_genius for alignment
        sources: Evidence sources
        witness_request_id: ID for witness request
        approval: Approval flag for witness action
        reason: Reason for action

    Returns:
        ActResult with peace_squared, kappa_r, witness_status
    """
    return await mcp_asi_act(
        action=action,
        text=text,
        session_id=session_id,
        query=query,
        proposal=proposal,
        stakeholders=stakeholders,
        agi_result=agi_result,
        sources=sources,
        witness_request_id=witness_request_id,
        approval=approval,
        reason=reason,
    )


@mcp.tool()
def arif_ping() -> Dict[str, Any]:
    """
    Health check for ARIF server.

    Returns status, role, and tool availability.
    """
    # Verify core tools are importable
    tools_available = True
    try:
        from arifos.mcp.tools.mcp_aaa import mcp_agi_genius, mcp_asi_act
    except ImportError:
        tools_available = False

    return {
        "status": "ready" if tools_available else "degraded",
        "role": "ARIF",
        "version": "v52.4.0",
        "omega_0": OMEGA_0_MIN,
        "tools": ["arif_agi_genius", "arif_asi_act"],
        "tools_available": tools_available,
    }


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    import sys

    # ARIF runs on SSE for scalability/timeout management
    transport = "sse" if len(sys.argv) > 1 and sys.argv[1] == "sse" else "stdio"
    mcp.run(transport=transport)

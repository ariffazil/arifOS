"""
APEX SERVER (v52.4.0) - The Summit (Judge)
Detached Constitutional Observer.

Responsibility:
    - apex_judge: Verdict & Proof (Soul)

Architecture:
    - Transport: SSE (Isolated)
    - Loop Mode: Can accept session_token for validation
    - Isolation: Independent of AXIS and ARIF

The final arbiter. If AGI (truth) and ASI (care) conflict,
APEX synthesizes a paradox resolution.

DITEMPA BUKAN DIBERI
"""

from typing import Dict, Any, Optional
from fastmcp import FastMCP
import logging

# Core Imports
from arifos.mcp.tools.mcp_aaa import mcp_apex_judge
from arifos.core.enforcement.metrics import OMEGA_0_MIN

logger = logging.getLogger(__name__)

# Initialize APEX Server
mcp = FastMCP("APEX", dependencies=["pydantic"])


# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool()
async def apex_judge(
    action: str,
    query: str = "",
    response: str = "",
    session_id: str = "",
    verdict: Optional[str] = None,
    session_token: Optional[str] = None,
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    data: str = "",
) -> Dict[str, Any]:
    """
    APEX JUDGE: The Soul (Psi).

    Final constitutional verdict and cryptographic proof.

    Actions:
        - eureka: Paradox synthesis (Truth AND Care) (777)
        - judge: Final constitutional verdict (888)
        - proof: Cryptographic sealing (889)
        - entropy: Constitutional entropy measurement
        - parallelism: Parallelism proof (Agent Zero)
        - full: Complete APEX pipeline

    Args:
        action: One of eureka, judge, proof, entropy, parallelism, full
        query: Original user query
        response: Generated response to judge
        session_id: Session ID from 000_init
        verdict: Proposed verdict (for proof action)
        session_token: Token from 000_init (for validation in strict mode)
        agi_result: Result from agi_genius
        asi_result: Result from asi_act
        data: Data for cryptographic proof

    Returns:
        JudgeResult with verdict, consensus_score, proof_hash
    """
    return await mcp_apex_judge(
        action=action,
        query=query,
        response=response,
        session_id=session_id,
        verdict=verdict,
        agi_result=agi_result,
        asi_result=asi_result,
        data=data,
    )


@mcp.tool()
def apex_ping() -> Dict[str, Any]:
    """
    Health check for APEX server.

    Returns status, role, and tool availability.
    """
    # Verify core tool is importable
    tool_available = True
    try:
        from arifos.mcp.tools.mcp_aaa import mcp_apex_judge
    except ImportError:
        tool_available = False

    return {
        "status": "ready" if tool_available else "degraded",
        "role": "APEX",
        "version": "v52.4.0",
        "omega_0": OMEGA_0_MIN,
        "tools": ["apex_judge"],
        "tool_available": tool_available,
    }


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    import sys

    # APEX runs on SSE for isolation
    transport = "sse" if len(sys.argv) > 1 and sys.argv[1] == "sse" else "stdio"
    mcp.run(transport=transport)

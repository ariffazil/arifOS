"""
MCP Tool 888: JUDGE

Final verdict aggregation via decision tree.

Constitutional role:
- Aggregates verdicts from tools 222, 444, 555, 666, 777
- Applies veto cascade (any VOID -> VOID)
- Emits final verdict: SEAL, PARTIAL, VOID, SABAR, HOLD

This is the constitutional judiciary - the final decision maker.
"""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict

from arifos_core.mcp.models import VerdictResponse


def aggregate_verdicts(verdicts: Dict[str, str]) -> str:
    """
    Aggregate tool verdicts into final verdict using decision tree.

    Decision tree:
    - If any VOID -> VOID (veto cascade)
    - Else if all PASS -> SEAL
    - Else if any PARTIAL -> PARTIAL
    - Else -> SABAR (fallback)

    HOLD is only emitted if explicitly signaled.

    Args:
        verdicts: Dict of tool_id -> verdict

    Returns:
        Final verdict: SEAL, PARTIAL, VOID, SABAR, or HOLD
    """
    if not verdicts:
        return "VOID"  # No verdicts to aggregate
    
    verdict_values = list(verdicts.values())
    
    # Veto cascade: any VOID -> VOID
    if "VOID" in verdict_values:
        return "VOID"
    
    # Check for explicit HOLD signal
    if "HOLD" in verdict_values:
        return "HOLD"
    
    # All PASS -> SEAL
    if all(v == "PASS" for v in verdict_values):
        return "SEAL"
    
    # Any PARTIAL -> PARTIAL
    if "PARTIAL" in verdict_values:
        return "PARTIAL"
    
    # Any SABAR -> SABAR
    if "SABAR" in verdict_values:
        return "SABAR"
    
    # Fallback
    return "SABAR"


def assign_confidence_band(verdicts: Dict[str, str]) -> float:
    """
    Assign final confidence based on verdict distribution.

    Args:
        verdicts: Dict of tool_id -> verdict

    Returns:
        Confidence score [0.0, 1.0]
    """
    if not verdicts:
        return 0.0
    
    verdict_values = list(verdicts.values())
    pass_count = verdict_values.count("PASS")
    total_count = len(verdict_values)
    
    # Confidence = ratio of PASS verdicts
    return pass_count / total_count if total_count > 0 else 0.0


async def mcp_888_judge(request: Dict[str, Any]) -> VerdictResponse:
    """
    MCP Tool 888: JUDGE - Final verdict aggregation.

    Decision tree:
    - If any VOID -> VOID
    - Else if all PASS -> SEAL
    - Else if any PARTIAL -> PARTIAL
    - Else -> SABAR

    Args:
        request: {
            "verdicts": {
                "222": "PASS",
                "444": "PASS|PARTIAL|VOID",
                "555": "PASS|PARTIAL",
                "666": "PASS|VOID",
                "777": "PASS"
            }
        }

    Returns:
        VerdictResponse with final verdict: SEAL, PARTIAL, VOID, SABAR, HOLD
    """
    verdicts = request.get("verdicts", {})
    
    if not isinstance(verdicts, dict):
        return VerdictResponse(
            verdict="VOID",
            reason="Invalid verdicts input",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    
    final_verdict = aggregate_verdicts(verdicts)
    confidence = assign_confidence_band(verdicts)
    
    # Generate reason
    if final_verdict == "SEAL":
        reason = "All constitutional floors passed. Response approved for execution."
    elif final_verdict == "VOID":
        void_tools = [k for k, v in verdicts.items() if v == "VOID"]
        reason = f"Constitutional violation detected by tools: {', '.join(void_tools)}"
    elif final_verdict == "PARTIAL":
        partial_tools = [k for k, v in verdicts.items() if v == "PARTIAL"]
        reason = f"Partial approval with caveats from tools: {', '.join(partial_tools)}"
    elif final_verdict == "HOLD":
        reason = "Human review required. Execution suspended pending approval."
    else:  # SABAR
        reason = "Awaiting signal to proceed. Constitutional pause activated."
    
    return VerdictResponse(
        verdict=final_verdict,
        reason=reason,
        side_data={
            "input_verdicts": verdicts,
            "confidence": confidence,
            "tools_checked": list(verdicts.keys())
        },
        timestamp=datetime.now(timezone.utc).isoformat()
    )


def mcp_888_judge_sync(request: Dict[str, Any]) -> VerdictResponse:
    return asyncio.run(mcp_888_judge(request))

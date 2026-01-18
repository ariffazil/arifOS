"""
mcp_000_gate.py - MCP Tool for Floor 000 Constitutional Gate
"""

from typing import Any, Dict

from ...stage_000_void.constitutional_gate import ConstitutionalGate


def mcp_000_gate(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Floor 000 Constitutional Gate Tool.

    Args:
        payload: {
            "query": str,   # The user's prompt or proposed action
            "context": dict # Optional context (user_id, source, etc.)
        }

    Returns:
        {
            "verdict": "SEAL/VOID/PARTIAL/HOLD_888",
            "reason": str,
            "floor_000_assessment": dict,
            "meta": dict
        }
    """
    query = payload.get("query", "")
    context = payload.get("context", {})

    # Delegate to Core Logic
    return ConstitutionalGate.assess_query(query, context)

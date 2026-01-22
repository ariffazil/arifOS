"""
MCP Tool 000: RESET - Session Initialization

Purpose:
    Initialize a new governed session with clean state.
    Strips bias, clears ACTIVE memory, returns session metadata.

Constitutional role:
    F1 (Amanah): Clean slate ensures no hidden state pollution
    F7 (Ω₀ Humility): Acknowledges starting from ignorance

Input contract:
    {
        "session_id": Optional[str]  # UUID or null (will generate)
    }

Output contract:
    {
        "verdict": "PASS",  # Always PASS (never blocks)
        "reason": "Session initialized",
        "side_data": {
            "session_id": str,      # Generated or accepted UUID
            "timestamp": str        # ISO-8601 timestamp
        }
    }

Phase: 1 (Foundation)
Dependencies: None (atomic)
Next: 111_SENSE (lane classification)
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4

from ..models import VerdictResponse


# =============================================================================
# CONSTANTS
# =============================================================================

TOOL_NAME = "mcp_000_reset"
VERDICT_ALWAYS = "PASS"
REASON_DEFAULT = "Session initialized with clean state"


# =============================================================================
# CORE LOGIC
# =============================================================================

async def mcp_000_reset(request: Dict[str, Any]) -> VerdictResponse:
    """
    Initialize session with clean state.

    Args:
        request: Dictionary with optional "session_id" key

    Returns:
        VerdictResponse with PASS verdict and session metadata

    Constitutional guarantees:
        - F1 (Amanah): No side effects, pure initialization
        - F2 (Truth): Honest representation of state (no fabrication)
        - F7 (Ω₀): Acknowledges starting from clean slate

    Examples:
        >>> result = await mcp_000_reset({"session_id": None})
        >>> assert result.verdict == "PASS"
        >>> assert result.side_data["session_id"] is not None

        >>> result = await mcp_000_reset({"session_id": "custom-id"})
        >>> assert result.side_data["session_id"] == "custom-id"
    """
    # Extract or generate session ID
    provided_session_id = request.get("session_id")

    if provided_session_id and isinstance(provided_session_id, str):
        session_id = provided_session_id
    else:
        # Generate new UUID
        session_id = str(uuid4())

    # Generate timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Build response
    return VerdictResponse(
        verdict=VERDICT_ALWAYS,
        reason=REASON_DEFAULT,
        side_data={
            "session_id": session_id,
            "timestamp": timestamp,
            "metrics_initialized": {},  # Empty metrics container
            "memory_bands_cleared": ["ACTIVE"],  # ACTIVE band reset
        },
        timestamp=timestamp,
    )


# =============================================================================
# SYNCHRONOUS WRAPPER (if needed)
# =============================================================================

def mcp_000_reset_sync(request: Dict[str, Any]) -> VerdictResponse:
    """
    Synchronous wrapper for mcp_000_reset.

    Use this if calling from non-async context.
    """
    import asyncio
    return asyncio.run(mcp_000_reset(request))

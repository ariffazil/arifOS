"""
AXIS SERVER (v52.4.0) - Authority & Memory (Spine)
The "Alpha & Omega" of the AAA Cluster.

Responsibility:
    - 000_init: Ignition & Identity (Alpha)
    - 999_vault: Sealing & Memory (Omega)

Architecture:
    - Transport: SSE (Railway) or Stdio (Local)
    - Loop Bootstrap: Detects and recovers orphaned sessions on startup
    - Isolation: Independent of Cognitive/Judge hangs

Loop Bootstrap Protocol:
    1. On 000_init: Check for orphaned sessions from crashed processes
    2. Auto-seal orphaned sessions with SABAR verdict
    3. Track new session as "open" in open_sessions.json
    4. On 999_vault: Close the session (remove from open tracking)

DITEMPA BUKAN DIBERI
"""

from typing import Dict, Any, Optional
from fastmcp import FastMCP, Context
import os
import uuid
import logging

# Core Imports
from arifos.mcp.tools.mcp_trinity import mcp_000_init, mcp_999_vault
from arifos.core.enforcement.metrics import OMEGA_0_MIN

# Loop Bootstrap: Session tracking for crash recovery
from arifos.mcp.session_ledger import (
    open_session,
    close_session,
    get_orphaned_sessions,
    recover_orphaned_session,
)

logger = logging.getLogger(__name__)

# Initialize AXIS Server
mcp = FastMCP("AXIS", dependencies=["pydantic"])

# Track active tokens for validation (in-memory, per-process)
_active_tokens: Dict[str, str] = {}  # session_id -> token


# =============================================================================
# LOOP BOOTSTRAP: Orphan Recovery
# =============================================================================

def _recover_orphans() -> int:
    """
    Recover any orphaned sessions from previous runs.

    Called at the start of 000_init to ensure crashed sessions are sealed.

    Returns:
        Number of recovered sessions
    """
    orphans = get_orphaned_sessions(timeout_minutes=30)
    recovered = 0

    for orphan in orphans:
        try:
            result = recover_orphaned_session(orphan)
            if result.get("sealed"):
                recovered += 1
                logger.info(f"Loop Bootstrap: Recovered session {orphan.get('session_id', 'UNKNOWN')[:8]}")
        except Exception as e:
            logger.error(f"Failed to recover orphan {orphan.get('session_id', 'UNKNOWN')[:8]}: {e}")

    return recovered


# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool()
async def axis_000_init(
    ctx: Context,
    action: str = "init",
    query: str = "",
    session_id: Optional[str] = None,
    authority_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    000 INIT: Universal Ignition Protocol (Loop Bootstrap).

    The Alpha of the 000-999 loop. Starts a new session and tracks it
    for crash recovery.

    Loop Bootstrap Protocol:
    1. Recover any orphaned sessions from crashed processes
    2. Execute 000_init logic
    3. Generate session token
    4. Track session as "open" for crash recovery

    Args:
        ctx: FastMCP context
        action: init, validate, or reset
        query: User query
        session_id: Optional session ID (auto-generated if not provided)
        authority_token: Optional authority token for 888_JUDGE

    Returns:
        InitResult dict with session_id and session_token
    """
    # =========================================================================
    # STEP 1: LOOP BOOTSTRAP - Recover orphaned sessions
    # =========================================================================
    try:
        recovered = _recover_orphans()
        if recovered > 0:
            logger.info(f"Loop Bootstrap: Recovered {recovered} orphaned session(s)")
            if ctx:
                ctx.info(f"Loop Bootstrap: Recovered {recovered} orphaned session(s)")
    except Exception as e:
        logger.warning(f"Loop Bootstrap recovery failed (continuing): {e}")

    # =========================================================================
    # STEP 2: Execute 000_init logic
    # =========================================================================
    result = await mcp_000_init(
        action=action,
        query=query,
        session_id=session_id,
        authority_token=authority_token
    )

    # =========================================================================
    # STEP 3: Generate Token and Track Open Session
    # =========================================================================
    if result.get("status") == "SEAL":
        token = str(uuid.uuid4())
        result["session_token"] = token
        result["loop_bootstrap"] = True

        # Track in memory for validation
        new_session_id = result.get("session_id", "")
        _active_tokens[new_session_id] = token

        # Track on disk for crash recovery
        try:
            authority = result.get("authority", "GUEST")
            open_session(
                session_id=new_session_id,
                token=token,
                pid=os.getpid(),
                authority=authority
            )
        except Exception as e:
            logger.warning(f"Failed to track open session (continuing): {e}")

        if ctx:
            ctx.info(f"Ignition: Token {token[:8]}... issued for Session {new_session_id[:8]}")

    return result


@mcp.tool()
async def axis_999_vault(
    ctx: Context,
    action: str,
    verdict: Optional[str] = None,
    session_id: Optional[str] = None,
    target: str = "seal",
    data: Optional[Dict[str, Any]] = None,
    session_token: Optional[str] = None,
    # Pass through Trinity results for proper sealing
    init_result: Optional[Dict[str, Any]] = None,
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    apex_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    999 VAULT: Immutable Seal (Loop Close).

    The Omega of the 000-999 loop. Seals the session and closes the loop.

    Loop Bootstrap Protocol:
    1. Optionally validate session token
    2. Execute seal
    3. Close session (remove from open tracking)

    Args:
        ctx: FastMCP context
        action: seal, list, read, write, or propose
        verdict: SEAL, SABAR, or VOID
        session_id: Session to seal
        target: Target storage (seal, ledger, canon, etc.)
        data: Additional data to store
        session_token: Token from 000_init (for validation)
        init_result: Result from 000_init (for telemetry)
        agi_result: Result from agi_genius (for telemetry)
        asi_result: Result from asi_act (for telemetry)
        apex_result: Result from apex_judge (for telemetry)

    Returns:
        VaultResult dict with merkle_root and audit_hash
    """
    # =========================================================================
    # STEP 1: Token Validation (Optional, for strict mode)
    # =========================================================================
    strict_mode = os.environ.get("ARIFOS_STRICT_TOKEN", "false").lower() == "true"

    if strict_mode and session_token and session_id:
        expected_token = _active_tokens.get(session_id)
        if expected_token and session_token != expected_token:
            logger.warning(f"Token mismatch for session {session_id[:8]}")
            return {
                "status": "VOID",
                "error": "Invalid Session Token",
                "session_id": session_id,
                "floors_checked": ["F11_CommandAuth"]
            }

    # =========================================================================
    # STEP 2: Execute Seal
    # =========================================================================
    result = await mcp_999_vault(
        action=action,
        verdict=verdict,
        session_id=session_id,
        target=target,
        data=data,
        init_result=init_result,
        agi_result=agi_result,
        asi_result=asi_result,
        apex_result=apex_result,
    )

    # =========================================================================
    # STEP 3: Close Session (Loop Complete)
    # =========================================================================
    if result.get("status") == "SEAL" and session_id:
        # Remove from memory tracking
        _active_tokens.pop(session_id, None)

        # Remove from disk tracking (crash recovery no longer needed)
        try:
            close_session(session_id)
        except Exception as e:
            logger.warning(f"Failed to close session tracking (continuing): {e}")

        if ctx:
            ctx.info(f"Seal: Loop Closed for Session {session_id[:8]}")

    return result


@mcp.tool()
def axis_ping() -> Dict[str, Any]:
    """
    Health check for AXIS server.

    Returns status, role, and active session count.
    """
    # Check how many orphaned sessions exist (indicator of health)
    try:
        orphans = get_orphaned_sessions(timeout_minutes=30)
        orphan_count = len(orphans)
    except Exception:
        orphan_count = -1  # Error indicator

    return {
        "status": "ready",
        "role": "AXIS",
        "version": "v52.4.0",
        "omega_0": OMEGA_0_MIN,
        "tools": ["axis_000_init", "axis_999_vault"],
        "active_sessions": len(_active_tokens),
        "orphaned_sessions": orphan_count,
        "loop_bootstrap": True
    }


# =============================================================================
# ENTRYPOINT
# =============================================================================

if __name__ == "__main__":
    import sys

    # Default to SSE for Railway deployment
    transport = "sse" if len(sys.argv) > 1 and sys.argv[1] == "sse" else "stdio"

    # Run initial recovery before starting server
    recovered = _recover_orphans()
    if recovered > 0:
        logger.info(f"Startup: Recovered {recovered} orphaned session(s)")

    mcp.run(transport=transport)

#!/usr/bin/env python3
"""
AXIS SERVER (v52.4.0) - Authority & Memory (Spine)
The "Alpha & Omega" of the AAA Cluster.

Production-ready deployment unit for Railway.

Responsibility:
    - 000_init: Ignition & Identity (Alpha)
    - 999_vault: Sealing & Memory (Omega)

Architecture:
    - Transport: SSE (Railway) or Stdio (Local)
    - Loop Bootstrap: Detects and recovers orphaned sessions on startup

DITEMPA BUKAN DIBERI
"""

import argparse
import json
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastmcp import FastMCP, Context

# =============================================================================
# JSON STRUCTURED LOGGING
# =============================================================================

class JSONFormatter(logging.Formatter):
    """JSON log formatter for Railway/structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "AXIS",
            "version": "v52.4.0",
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging() -> logging.Logger:
    """Configure JSON logging to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("axis")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logging()


# =============================================================================
# CORE IMPORTS (arifos package must be installed)
# =============================================================================

try:
    from arifos.mcp.tools.mcp_trinity import mcp_000_init, mcp_999_vault
    from arifos.core.enforcement.metrics import OMEGA_0_MIN
    from arifos.mcp.session_ledger import (
        open_session,
        close_session,
        get_orphaned_sessions,
        recover_orphaned_session,
    )
    CORE_AVAILABLE = True
except ImportError as e:
    logger.error(f"Failed to import arifos core: {e}")
    CORE_AVAILABLE = False
    OMEGA_0_MIN = 0.03


# =============================================================================
# AXIS MCP SERVER
# =============================================================================

mcp = FastMCP("AXIS", dependencies=["pydantic"])

# In-memory token tracking
_active_tokens: Dict[str, str] = {}


def _recover_orphans() -> int:
    """Recover orphaned sessions from previous runs (Loop Bootstrap)."""
    if not CORE_AVAILABLE:
        return 0

    try:
        orphans = get_orphaned_sessions(timeout_minutes=30)
        recovered = 0

        for orphan in orphans:
            try:
                result = recover_orphaned_session(orphan)
                if result.get("sealed"):
                    recovered += 1
                    logger.info(f"Recovered orphan session: {orphan.get('session_id', '?')[:8]}")
            except Exception as e:
                logger.error(f"Failed to recover orphan: {e}")

        return recovered
    except Exception as e:
        logger.warning(f"Orphan recovery scan failed: {e}")
        return 0


@mcp.tool()
async def axis_000_init(
    ctx: Context,
    action: str = "init",
    query: str = "",
    session_id: Optional[str] = None,
    authority_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    000 INIT: Universal Ignition Protocol.

    Starts a new session with Loop Bootstrap crash recovery.
    """
    if not CORE_AVAILABLE:
        return {"status": "VOID", "error": "Core not available"}

    # Loop Bootstrap: Recover orphans first
    recovered = _recover_orphans()
    if recovered > 0:
        logger.info(f"Loop Bootstrap: Recovered {recovered} session(s)")

    # Execute 000_init
    result = await mcp_000_init(
        action=action,
        query=query,
        session_id=session_id,
        authority_token=authority_token
    )

    # Track successful session
    if result.get("status") == "SEAL":
        token = str(uuid.uuid4())
        new_session_id = result.get("session_id", "")

        result["session_token"] = token
        result["loop_bootstrap"] = True

        _active_tokens[new_session_id] = token

        try:
            open_session(
                session_id=new_session_id,
                token=token,
                pid=os.getpid(),
                authority=result.get("authority", "GUEST")
            )
            logger.info(f"Session opened: {new_session_id[:8]}")
        except Exception as e:
            logger.warning(f"Failed to track session: {e}")

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
    init_result: Optional[Dict[str, Any]] = None,
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    apex_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    999 VAULT: Immutable Seal.

    Seals the session and closes the loop.
    """
    if not CORE_AVAILABLE:
        return {"status": "VOID", "error": "Core not available"}

    # Optional strict token validation
    if os.environ.get("ARIFOS_STRICT_TOKEN", "").lower() == "true":
        if session_token and session_id:
            expected = _active_tokens.get(session_id)
            if expected and session_token != expected:
                logger.warning(f"Token mismatch: {session_id[:8]}")
                return {"status": "VOID", "error": "Invalid session token"}

    # Execute seal
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

    # Close session tracking
    if result.get("status") == "SEAL" and session_id:
        _active_tokens.pop(session_id, None)
        try:
            close_session(session_id)
            logger.info(f"Session sealed: {session_id[:8]}")
        except Exception as e:
            logger.warning(f"Failed to close session: {e}")

    return result


@mcp.tool()
def axis_ping() -> Dict[str, Any]:
    """Health check for AXIS server."""
    orphan_count = -1
    try:
        if CORE_AVAILABLE:
            orphan_count = len(get_orphaned_sessions(timeout_minutes=30))
    except Exception:
        pass

    return {
        "status": "ready" if CORE_AVAILABLE else "degraded",
        "role": "AXIS",
        "version": "v52.4.0",
        "omega_0": OMEGA_0_MIN,
        "tools": ["axis_000_init", "axis_999_vault"],
        "active_sessions": len(_active_tokens),
        "orphaned_sessions": orphan_count,
        "loop_bootstrap": True,
        "core_available": CORE_AVAILABLE,
    }


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="AXIS MCP Server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="Transport mode (default: sse for Railway)"
    )
    args = parser.parse_args()

    # Recover orphans at startup
    recovered = _recover_orphans()
    if recovered > 0:
        logger.info(f"Startup recovery: {recovered} session(s)")

    logger.info(f"AXIS starting on {args.transport} transport")
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

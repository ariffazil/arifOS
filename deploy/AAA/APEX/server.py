#!/usr/bin/env python3
"""
APEX SERVER (v52.4.0) - The Summit (Judge)
Detached Constitutional Observer.

Production-ready deployment unit for Railway.

Responsibility:
    - apex_judge: Verdict & Proof (Soul)

Architecture:
    - Transport: SSE (Isolated)
    - Security: High isolation from AXIS and ARIF

DITEMPA BUKAN DIBERI
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

from fastmcp import FastMCP


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
            "service": "APEX",
            "version": "v52.4.0",
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging() -> logging.Logger:
    """Configure JSON logging to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("apex")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logging()


# =============================================================================
# CORE IMPORTS
# =============================================================================

try:
    from arifos.mcp.tools.mcp_trinity import mcp_apex_judge
    from arifos.core.enforcement.metrics import OMEGA_0_MIN
    CORE_AVAILABLE = True
    logger.info("arifos core loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import arifos core: {e}")
    CORE_AVAILABLE = False
    OMEGA_0_MIN = 0.03


# =============================================================================
# APEX MCP SERVER
# =============================================================================

mcp = FastMCP("APEX", dependencies=["pydantic"])


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

    Actions: eureka, judge, proof, entropy, parallelism, full
    """
    if not CORE_AVAILABLE:
        return {"status": "VOID", "error": "Core not available"}

    logger.info(f"apex_judge action={action} session={session_id[:8] if session_id else 'none'}")

    try:
        result = await mcp_apex_judge(
            action=action,
            query=query,
            response=response,
            session_id=session_id,
            verdict=verdict,
            agi_result=agi_result,
            asi_result=asi_result,
            data=data,
        )

        final_verdict = result.get("verdict", "unknown")
        logger.info(f"apex_judge completed: verdict={final_verdict}")
        return result
    except Exception as e:
        logger.error(f"apex_judge failed: {e}")
        return {"status": "VOID", "error": str(e)}


@mcp.tool()
def apex_ping() -> Dict[str, Any]:
    """Health check for APEX server."""
    return {
        "status": "ready" if CORE_AVAILABLE else "degraded",
        "role": "APEX",
        "version": "v52.4.0",
        "omega_0": OMEGA_0_MIN,
        "tools": ["apex_judge"],
        "core_available": CORE_AVAILABLE,
    }


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="APEX MCP Server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="Transport mode (default: sse for Railway)"
    )
    args = parser.parse_args()

    logger.info(f"APEX starting on {args.transport} transport")
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

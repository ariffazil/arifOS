#!/usr/bin/env python3
"""
ARIF SERVER (v52.4.0) - The Architect (Nexus)
Entanglement of Mind (Logic) and Heart (Empathy).

Production-ready deployment unit for Railway.

Responsibility:
    - agi_genius: Sense -> Think -> Atlas (Mind)
    - asi_act: Evidence -> Empathy -> Act (Heart)

Architecture:
    - Transport: SSE (Heavy compute, may hang)
    - Isolation: Independent from AXIS (crash-safe)

DITEMPA BUKAN DIBERI
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

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
            "service": "ARIF",
            "version": "v52.4.0",
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


def setup_logging() -> logging.Logger:
    """Configure JSON logging to stdout."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    logger = logging.getLogger("arif")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False

    return logger


logger = setup_logging()


# =============================================================================
# CORE IMPORTS
# =============================================================================

try:
    from arifos.mcp.tools.mcp_trinity import mcp_agi_genius, mcp_asi_act
    from arifos.core.enforcement.metrics import OMEGA_0_MIN
    CORE_AVAILABLE = True
    logger.info("arifos core loaded successfully")
except ImportError as e:
    logger.error(f"Failed to import arifos core: {e}")
    CORE_AVAILABLE = False
    OMEGA_0_MIN = 0.03


# =============================================================================
# ARIF MCP SERVER
# =============================================================================

mcp = FastMCP("ARIF", dependencies=["pydantic"])


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

    Actions: sense, think, reflect, atlas, forge, evaluate, full
    """
    if not CORE_AVAILABLE:
        return {"status": "VOID", "error": "Core not available"}

    logger.info(f"agi_genius action={action} session={session_id[:8] if session_id else 'none'}")

    try:
        result = await mcp_agi_genius(
            action=action,
            query=query,
            session_id=session_id,
            thought=thought,
            draft=draft,
            truth_score=truth_score,
            context=context,
            axioms=axioms,
        )
        logger.info(f"agi_genius completed: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"agi_genius failed: {e}")
        return {"status": "VOID", "error": str(e)}


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

    Actions: evidence, empathize, align, act, witness, evaluate, full
    """
    if not CORE_AVAILABLE:
        return {"status": "VOID", "error": "Core not available"}

    logger.info(f"asi_act action={action} session={session_id[:8] if session_id else 'none'}")

    try:
        result = await mcp_asi_act(
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
        logger.info(f"asi_act completed: {result.get('status', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"asi_act failed: {e}")
        return {"status": "VOID", "error": str(e)}


@mcp.tool()
def arif_ping() -> Dict[str, Any]:
    """Health check for ARIF server."""
    return {
        "status": "ready" if CORE_AVAILABLE else "degraded",
        "role": "ARIF",
        "version": "v52.4.0",
        "omega_0": OMEGA_0_MIN,
        "tools": ["arif_agi_genius", "arif_asi_act"],
        "core_available": CORE_AVAILABLE,
    }


# =============================================================================
# ENTRYPOINT
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="ARIF MCP Server")
    parser.add_argument(
        "--transport",
        choices=["sse", "stdio"],
        default="sse",
        help="Transport mode (default: sse for Railway)"
    )
    args = parser.parse_args()

    logger.info(f"ARIF starting on {args.transport} transport")
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()

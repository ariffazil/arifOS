"""
L4_MCP Server - MCP Entry Point (stdio & HTTP/SSE).

This module ties apex.verdict into the MCP server framework.
Compatible with the official MCP SDK: https://github.com/modelcontextprotocol

Only ONE tool is exposed: apex.verdict

Version: v45.1.2 (Phase 2B - Real Telemetry Integration)
"""

from __future__ import annotations
from typing import Any, Dict, Optional
import sys
import logging

from L4_MCP.apex.schema import ApexRequest, ApexResponse
from L4_MCP.apex.verdict import apex_verdict
from arifos_ledger.sqlite_store import SQLiteLedgerStore


# =============================================================================
# PHASE 2A FIX: Logging to stderr instead of stdout
# MCP protocol requires stdout to be pure JSON only
# =============================================================================
# Configure logging to stderr (not stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # ? Critical: Use stderr, not stdout
)
logger = logging.getLogger(__name__)


# Global ledger instance (configurable in production)
_ledger = SQLiteLedgerStore("cooling_ledger_l4.sqlite3")


def handle_apex_verdict_call(
    task: str,
    params: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> str:  # ? Changed return type to string (ASI format)
    """
    Handler to expose apex_verdict as an MCP tool.

    This is the ONLY externally available tool call.

    Phase 2A: Returns human-readable ASI format instead of JSON.

    Args:
        task: The proposed action (natural language or code)
        params: Optional parameters for the task
        context: Optional metadata/context

    Returns:
        Human-readable verdict explanation (ASI format)
    """
    req = ApexRequest(
        task=task,
        params=params or {},
        context=context or {},
        caller=None,  # Will be extracted from context
    )

    resp = apex_verdict(req, _ledger)

    # ========================================================================
    # PHASE 2A: ASI FORMAT OUTPUT (Human-Readable)
    # ========================================================================
    # Convert verdict to human-readable format

    verdict_emoji = {
        "SEAL": "?",
        "VOID": "??",
        "SABAR": "??",
        "HOLD_888": "??",
    }.get(resp.verdict.value, "?")

    verdict_title = {
        "SEAL": "ACTION APPROVED",
        "VOID": "ACTION BLOCKED",
        "SABAR": "ACTION PAUSED",
        "HOLD_888": "HUMAN REVIEW REQUIRED",
    }.get(resp.verdict.value, "VERDICT UNKNOWN")

    # Build human-readable output
    lines = [
        f"{verdict_emoji} {verdict_title}",
        "",
        resp.explanation,  # Use the explanation from verdict.py
        "",
    ]

    # Add floor details if triggered
    if resp.floor_triggered:
        lines.append("Constitutional Floors Triggered:")
        for floor in resp.floor_triggered:
            lines.append(f"  - {floor}")
        lines.append("")

    # Add required evidence if any
    if resp.required_evidence:
        lines.append("What would be needed to proceed:")
        for evidence in resp.required_evidence:
            lines.append(f"  - {evidence}")
        lines.append("")

    # Add constraints
    if resp.constraints:
        lines.append("Constraints Applied:")
        for constraint in resp.constraints:
            lines.append(f"  - {constraint}")
        lines.append("")

    # Add system health
    pulse_percentage = int(resp.apex_pulse * 100)
    lines.append(f"System Health: {pulse_percentage}% approval (apex_pulse: {resp.apex_pulse})")

    # Add audit trail
    lines.append(f"Audit Trail: Logged as {resp.cooling_ledger_id} at {resp.timestamp}")

    return "\n".join(lines)


# =============================================================================
# MCP SDK Integration (compatible with https://github.com/modelcontextprotocol)
# =============================================================================

try:
    from mcp.server.fastmcp import FastMCP

    # Initialize MCP server with L4 profile
    mcp = FastMCP("arifos-l4-authority")

    @mcp.tool()
    def apex_verdict_tool(
        task: str,
        params: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:  # ? Changed return type to string
        """
        Single constitutional authority gate for arifOS.

        Evaluates a proposed task against 9 constitutional floors (F1-F9)
        and returns a human-readable verdict explanation.

        Returns ASI format (human-readable) instead of machine JSON.

        Args:
            task: The proposed action to evaluate
            params: Optional parameters for the task
            context: Optional metadata (source, model, tenant, trust_level)

        Returns:
            Human-readable verdict explanation with:
            - Verdict (SEAL/VOID/SABAR/HOLD_888)
            - Why it was approved/blocked
            - Which floors triggered
            - What evidence would be needed
            - System health metrics
            - Audit trail ID
        """
        return handle_apex_verdict_call(task, params, context)

    def run_stdio():
        """Run the MCP server in stdio mode."""
        logger.info("L4_MCP stdio server starting...")
        mcp.run(transport='stdio')  # ? Correct FastMCP API

    def run_http(host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server in HTTP mode."""
        import uvicorn
        logger.info(f"L4_MCP HTTP server starting on {host}:{port}...")
        uvicorn.run(mcp.app, host=host, port=port)

except ImportError:
    # MCP SDK not installed - provide standalone function
    mcp = None

    def run_stdio():
        """MCP SDK not installed. Install with: pip install mcp"""
        raise ImportError("MCP SDK not installed. Install with: pip install mcp")

    def run_http(host: str = "0.0.0.0", port: int = 8000):
        """MCP SDK not installed. Install with: pip install mcp"""
        raise ImportError("MCP SDK not installed. Install with: pip install 'mcp[http]'")


# =============================================================================
# Standalone entry point
# =============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        run_http(port=port)
    else:
        run_stdio()

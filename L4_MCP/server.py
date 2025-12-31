"""
L4_MCP Server - MCP Entry Point (stdio & HTTP/SSE).

This module ties apex.verdict into the MCP server framework.
Compatible with the official MCP SDK: https://github.com/modelcontextprotocol

Only ONE tool is exposed: apex.verdict

Version: v45.1.0
"""

from __future__ import annotations
from typing import Any, Dict, Optional

from L4_MCP.apex.schema import ApexRequest, ApexResponse
from L4_MCP.apex.verdict import apex_verdict
from arifos_ledger.sqlite_store import SQLiteLedgerStore


# Global ledger instance (configurable in production)
_ledger = SQLiteLedgerStore("cooling_ledger_l4.sqlite3")


def handle_apex_verdict_call(
    task: str,
    params: Optional[Dict[str, Any]] = None,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Handler to expose apex_verdict as an MCP tool.

    This is the ONLY externally available tool call.

    Args:
        task: The proposed action (natural language or code)
        params: Optional parameters for the task
        context: Optional metadata/context

    Returns:
        Dict representation of ApexResponse
    """
    req = ApexRequest(
        task=task,
        params=params or {},
        context=context or {},
        caller=None,  # Will be extracted from context
    )

    resp = apex_verdict(req, _ledger)

    # Convert dataclass to dict for serialization
    return {
        "verdict": resp.verdict.value,
        "apex_pulse": resp.apex_pulse,
        "reason_codes": resp.reason_codes,
        "required_evidence": resp.required_evidence,
        "constraints": resp.constraints,
        "floor_triggered": resp.floor_triggered,
        "action_class": resp.action_class.value,
        "caller": {
            "source": resp.caller.source,
            "model": resp.caller.model,
            "tenant": resp.caller.tenant,
            "trust_level": resp.caller.trust_level,
        },
        "explanation": resp.explanation,
        "cooling_ledger_id": resp.cooling_ledger_id,
        "timestamp": resp.timestamp,
    }


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
    ) -> Dict[str, Any]:
        """
        Single constitutional authority gate for arifOS.

        Evaluates a proposed task against 9 constitutional floors (F1-F9)
        and returns a verdict: SEAL (approved), VOID (blocked),
        SABAR (pause), or HOLD_888 (human review required).

        Args:
            task: The proposed action to evaluate
            params: Optional parameters for the task
            context: Optional metadata (source, model, tenant, trust_level)

        Returns:
            Dict with verdict, explanation, evidence requirements, and audit ID
        """
        return handle_apex_verdict_call(task, params, context)

    def run_stdio():
        """Run the MCP server in stdio mode."""
        mcp.run_stdio()

    def run_http(host: str = "0.0.0.0", port: int = 8000):
        """Run the MCP server in HTTP mode."""
        import uvicorn

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
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--http":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        print(f"Starting L4_MCP HTTP server on port {port}...")
        run_http(port=port)
    else:
        print("Starting L4_MCP stdio server...")
        run_stdio()

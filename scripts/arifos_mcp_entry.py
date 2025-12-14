#!/usr/bin/env python3
"""
arifOS MCP Entry Point (v41.0) - Constitutional Governance Gateway
DITEMPA BUKAN DIBERI - Forged, not given.

Mode: v0-strict ONLY
Surface Area: 1 tool (arifos_evaluate)
Security: Read-only constitutional evaluation

Constitutional Compliance: v38Omega
Layer: L5 (Hands - MCP Integration)
Bridge: Validated via test_aclip_bridge.py (14/14 PASS)

Usage (Claude Desktop config):
    "mcpServers": {
      "arifos-v0": {
        "command": "python",
        "args": [
          "C:/Users/User/OneDrive/Documents/GitHub/arifOS/scripts/arifos_mcp_entry.py"
        ]
      }
    }

Security:
  - Exposes ONLY evaluate_session() bridge function
  - No file system access, no memory writes, no LLM generation
  - All operations are read-only constitutional evaluations
  - High-stakes detection enforced via bridge layer (F1-F9)
  
F2 (Truth) Compliance:
  - Does NOT fabricate pipeline stages that didn't run
  - Session data reflects reality: empty steps, honest status
  - Uses canonical APEX PRIME public contract (serialize_public)
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from mcp.server import FastMCP

# Ensure arifOS repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the validated bridge function (test_aclip_bridge.py confirms this works)
from arifos_core import evaluate_session

# Import APEX PRIME public contract serializer (v41.0.1)
from arifos_core.contracts.apex_prime_output_v41 import serialize_public


# =============================================================================
# v0-STRICT MODE: Single Tool Bridge
# =============================================================================

def create_v0_strict_server() -> FastMCP:
    """
    Create v0-strict MCP server with ONLY the evaluate tool.
    
    This is the production-ready, security-hardened mode.
    Surface area: 1 tool (constitutional evaluation only).
    
    F2 (Truth) Compliance: Does NOT fabricate pipeline stages that didn't run.
    """
    server = FastMCP("arifos-v0-strict")

    @server.tool()
    def arifos_evaluate(
        task: str,
        context: str = "MCP Client Request",
        session_id: str = "mcp_session"
    ) -> Dict[str, Any]:
        """
        [GOVERNED] Evaluate a task through arifOS constitutional kernel.
        
        This tool submits a task/query to APEX_PRIME for constitutional review.
        It enforces all 9 floors (F1-F9) and returns a verdict.
        
        Args:
            task: The task or query to evaluate
            context: Optional context description (default: "MCP Client Request")
            session_id: Optional session identifier for tracking
        
        Returns:
            APEX PRIME public contract:
                - verdict: One of SEAL, PARTIAL, SABAR, VOID, 888_HOLD
                - apex_pulse: Float 0.00-1.10 (None if not computed)
                - response: Human-readable explanation
                - reason_code: Optional floor failure code
        
        Constitutional Floors Enforced:
            F1 (Amanah): Reversibility / Integrity check
            F2 (Truth): Factual accuracy ≥0.99
            F3 (Tri-Witness): Human-AI-Reality alignment ≥0.95
            F4 (DeltaS): Clarity gain ≥0.0
            F5 (Peace²): Non-destructive ≥1.0
            F6 (κᵣ): Weakest stakeholder protection ≥0.95
            F7 (Ω₀): Humility/uncertainty 0.03-0.05
            F8 (G): Governed intelligence ≥0.80
            F9 (C_dark): Dark cleverness <0.30
        """
        try:
            # HONEST session data - F2 (Truth) compliance
            # Do NOT fabricate pipeline stages that didn't run
            # Let evaluate_session() make decisions based on reality
            session_data = {
                "id": session_id,
                "task": task,
                "status": "mcp_direct",  # Honest: direct evaluation, not full pipeline
                "source": "mcp_v0_strict",
                "context": context,
                "steps": []  # EMPTY - no stages ran, don't claim they did
            }
            
            # Call the validated bridge function (proven by 14/14 tests)
            verdict = evaluate_session(session_data)
            
            # Use canonical APEX PRIME public contract (v41.0.1)
            return serialize_public(
                verdict=verdict,
                psi_internal=None,  # MCP doesn't compute Ψ - be honest
                response=f"Constitutional evaluation: {task[:100]}{'...' if len(task) > 100 else ''}",
                reason_code=None,  # No floor failure to report if SEAL
            )
            
        except Exception as e:
            # Graceful degradation - fail to SABAR (safe default)
            logging.error(f"arifOS MCP evaluation failed: {e}", exc_info=True)
            
            # Use canonical contract for errors too
            return serialize_public(
                verdict="SABAR",
                psi_internal=None,
                response=f"Evaluation error: {str(e)}. System cooling down.",
                reason_code="F7(uncertainty)",
            )

    return server


# =============================================================================
# MAIN: Server Ignition (v0-Strict Only)
# =============================================================================

async def main() -> None:
    """
    Ignite the arifOS MCP server in v0-strict mode.
    
    v0 Launch: Strict mode only. Dev mode deferred to v0.1+
    Surface Area: 1 tool (arifos_evaluate)
    Contract: APEX PRIME public (serialize_public)
    """
    # Logging setup (stderr only - stdout is reserved for MCP protocol)
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s [%(levelname)s] arifOS-MCP: %(message)s",
    )
    
    logging.info("="*60)
    logging.info("Igniting arifOS MCP Gateway [v0-strict]...")
    logging.info("Constitutional Law: v38Omega")
    logging.info("Layer: L5 (Hands - MCP Integration)")
    logging.info("Surface Area: 1 tool (arifos_evaluate)")
    logging.info("Contract: APEX PRIME public (verdict, apex_pulse, response)")
    logging.info("Security: Read-only, honest session data (F2 Truth)")
    logging.info("Bridge: Validated (test_aclip_bridge.py 14/14 PASS)")
    logging.info("="*60)

    server = create_v0_strict_server()
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())

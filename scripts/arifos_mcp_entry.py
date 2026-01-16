#!/usr/bin/env python3
"""
arifOS MCP Entry Point - Constitutional Governance Gateway
DITEMPA BUKAN DIBERI - Forged, not given.

Mode: v0-strict with REAL APEX PRIME evaluation + Semantic Governance
Surface Area: 1 tool (arifos_evaluate) + full 15-tool server
Security: Read-only constitutional evaluation

v45Ω UPGRADE: Entropy reduction complete - canonical import paths
- Layer 1: RED_PATTERNS instant VOID detection (from arifos_core)
- Layer 2: Heuristic metric computation
- Layer 3: APEX PRIME judgment

Usage (Claude Desktop config):
    "mcpServers": {
      "arifos": {
        "command": "python",
        "args": [
          "C:/Users/User/OneDrive/Documents/GitHub/arifOS/scripts/arifos_mcp_entry.py"
        ]
      }
    }
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

# v45Ω: Import from canonical locations (post-entropy reduction)
from arifos_core.enforcement.metrics import Metrics
from arifos_core.system.apex_prime import APEXPrime
from arifos_core.apex.contracts.apex_prime_output_v41 import serialize_public, compute_apex_pulse

# v45Ω: Import unified semantic governance from arifos_core
from arifos_core import (
    RED_PATTERNS,
    RED_PATTERN_TO_FLOOR,
    RED_PATTERN_SEVERITY,
    check_red_patterns,
    compute_metrics_from_task,
)

# Import detectors for F1 (Amanah) - used as fallback
try:
    from arifos_core.enforcement.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR
    AMANAH_AVAILABLE = True
except ImportError:
    AMANAH_DETECTOR = None
    AMANAH_AVAILABLE = False


# =============================================================================
# HIGH-STAKES DETECTION
# =============================================================================

HIGH_STAKES_KEYWORDS = [
    "database", "production", "deploy", "delete", "drop", "truncate",
    "security", "credential", "secret", "key", "token", "password",
    "irreversible", "permanent", "force", "rm -rf", "git push --force",
    "format", "wipe", "destroy", "shutdown", "terminate",
]


def is_high_stakes(text: str) -> bool:
    """Check if text contains high-stakes indicators."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in HIGH_STAKES_KEYWORDS)


# =============================================================================
# v0-STRICT MODE: Single Tool with REAL APEX PRIME + Semantic Governance
# =============================================================================

def create_v0_strict_server() -> FastMCP:
    """
    Create v0-strict MCP server with REAL APEX PRIME evaluation.

    v45Ω: Uses unified semantic governance from arifos_core:
    - Layer 1: RED_PATTERNS instant VOID
    - Layer 2: compute_metrics_from_task() heuristics
    - Layer 3: APEX PRIME judgment
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
        It enforces all 9 floors (F1-F9) and returns a verdict with apex_pulse.

        Args:
            task: The task or query to evaluate
            context: Optional context description
            session_id: Optional session identifier

        Returns:
            APEX PRIME public contract:
                - verdict: SEAL (approved), VOID (blocked), SABAR (cooling)
                - apex_pulse: Float 0.00-1.10 (governance health score)
                - response: Human-readable explanation
                - reason_code: Floor failure code if blocked (e.g., F1(rm-rf))

        Verdict Bands:
            SEAL  -> apex_pulse 1.00-1.10 (all floors pass)
            SABAR -> apex_pulse 0.95-0.99 (soft floors warning)
            VOID  -> apex_pulse 0.00-0.94 (hard floor failed)

        Severity Sub-bands within VOID:
            0.00-0.20: NUCLEAR (child harm, mass destruction)
            0.21-0.50: SEVERE (violence, credential theft)
            0.51-0.80: MODERATE (disinformation, jailbreak)
            0.81-0.94: SOFT (anti-hantu violations)
        """
        try:
            # ==========================================================
            # LAYER 1: Red pattern check (instant VOID)
            # ==========================================================
            is_red, category, pattern, floor_code, severity = check_red_patterns(task)
            if is_red:
                logging.warning(f"RED_PATTERN detected: {category} - {pattern}")
                return serialize_public(
                    verdict="VOID",
                    psi_internal=severity,  # Severity determines pulse within VOID band
                    response=f"BLOCKED: Constitutional violation - {category} pattern detected.",
                    reason_code=floor_code,
                )

            # ==========================================================
            # LAYER 2: Compute metrics from task text
            # ==========================================================
            metrics, floor_violation = compute_metrics_from_task(task)

            # Check high-stakes
            high_stakes = is_high_stakes(task)

            # ==========================================================
            # LAYER 3: APEX PRIME judgment on computed metrics
            # ==========================================================
            judge = APEXPrime(
                high_stakes=high_stakes,
                tri_witness_threshold=0.95,
                use_genius_law=True
            )

            verdict = judge.judge(
                metrics=metrics,
                eye_blocking=False,
                energy=1.0,
                entropy=0.0
            )

            # Compute Psi for apex_pulse
            psi_components = [
                metrics.truth,
                metrics.peace_squared,
                metrics.kappa_r,
                metrics.tri_witness,
            ]
            amanah_factor = 1.0 if metrics.amanah else 0.5
            hantu_factor = 1.0 if metrics.anti_hantu else 0.7
            psi_internal = (sum(psi_components) / len(psi_components)) * amanah_factor * hantu_factor

            # Build response based on verdict
            if high_stakes and verdict == "SEAL" and not floor_violation:
                verdict = "SABAR"
                response = f"HIGH-STAKES: Requires human approval. {task[:50]}..."
                reason_code = "F1(high_stakes)"
            elif verdict == "SEAL":
                response = f"APPROVED: {task[:80]}{'...' if len(task) > 80 else ''}"
                reason_code = None
            elif verdict == "VOID":
                response = f"BLOCKED: Constitutional violation detected."
                reason_code = floor_violation or "F2(truth)"
            elif verdict == "888_HOLD":
                response = f"HIGH-STAKES: Requires human approval. {task[:50]}..."
                reason_code = "F1(high_stakes)"
                verdict = "SABAR"  # Map 888_HOLD to SABAR for public contract
            else:  # PARTIAL, SABAR
                response = f"COOLING: Soft floor warning. {task[:60]}..."
                reason_code = floor_violation
                verdict = "SABAR"

            return serialize_public(
                verdict=verdict,
                psi_internal=psi_internal,
                response=response,
                reason_code=reason_code,
            )

        except Exception as e:
            logging.error(f"arifOS MCP evaluation failed: {e}", exc_info=True)
            return serialize_public(
                verdict="SABAR",
                psi_internal=0.95,  # Safe default
                response=f"Evaluation error: {str(e)}. System cooling down.",
                reason_code="F7(uncertainty)",
            )

    return server


# =============================================================================
# MAIN: Server Ignition (Full 15-tool server for production)
# =============================================================================

async def main() -> None:
    """
    Ignite the arifOS MCP server (unified 17-tool version for production).

    For v0-strict mode (single tool), use create_v0_strict_server() instead.
    """
    # Import the unified server for production use
    from arifos_core.mcp.unified_server import mcp_server

    print("[arifOS MCP] Initializing constitutional governance pipeline...", file=sys.stderr)
    print("[arifOS MCP] 17 tools ready: Unified architecture with dual search", file=sys.stderr)
    print("[arifOS MCP] - 5 constitutional pipeline + 2 search + 3 vault999 + 4 FAG + 1 validation + 2 system", file=sys.stderr)
    print("[arifOS MCP] All tools enforce the 12 Constitutional Floors (F1-F12)", file=sys.stderr)
    print("[arifOS MCP] DITEMPA BUKAN DIBERI - The server is forged.\n", file=sys.stderr)

    try:
        await mcp_server.run_stdio()
    except KeyboardInterrupt:
        # F5 (Peace^2): Graceful shutdown
        print("\n[arifOS MCP] Received shutdown signal. Closing session...", file=sys.stderr)
        print("[arifOS MCP] Session sealed. All audit trails preserved.", file=sys.stderr)
    except Exception as e:
        # F1 (Amanah): Audit all failures
        print(f"\n[arifOS MCP] ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

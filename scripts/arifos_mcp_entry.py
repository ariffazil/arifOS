#!/usr/bin/env python3
"""
arifOS MCP Entry Point (v41.3) - Constitutional Governance Gateway
DITEMPA BUKAN DIBERI - Forged, not given.

Mode: v0-strict with REAL APEX PRIME evaluation + Semantic Governance
Surface Area: 1 tool (arifos_evaluate)
Security: Read-only constitutional evaluation

v41.3 UPGRADE: Unified semantic governance with 3 layers:
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
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from mcp.server import FastMCP

# Ensure arifOS repo root is on sys.path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import core components
from arifos_core.metrics import Metrics
from arifos_core.APEX_PRIME import APEXPrime
from arifos_core.contracts.apex_prime_output_v41 import serialize_public, compute_apex_pulse

# v41.3: Import unified semantic governance from arifos_core
from arifos_core import (
    RED_PATTERNS,
    RED_PATTERN_TO_FLOOR,
    RED_PATTERN_SEVERITY,
    check_red_patterns,
    compute_metrics_from_task,
)

# Import detectors for F1 (Amanah) - used as fallback
try:
    from arifos_core.floor_detectors.amanah_risk_detectors import AMANAH_DETECTOR
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

    v41.3: Uses unified semantic governance from arifos_core:
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
# MAIN: Server Ignition
# =============================================================================

async def main() -> None:
    """
    Ignite the arifOS MCP server with semantic governance.
    """
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stderr,
        format="%(asctime)s [%(levelname)s] arifOS-MCP: %(message)s",
    )

    logging.info("="*60)
    logging.info("Igniting arifOS MCP Gateway [v41.3]...")
    logging.info("Mode: v0-strict with Semantic Governance")
    logging.info("Layer 1: RED_PATTERNS instant VOID (%d categories)", len(RED_PATTERNS))
    logging.info("Layer 2: Heuristic metric computation")
    logging.info("Layer 3: APEX PRIME judgment")
    logging.info("Floors: F1-F9 enforced (Amanah, Anti-Hantu sovereign)")
    logging.info("Output: verdict + apex_pulse (0.00-1.10)")
    logging.info("="*60)

    server = create_v0_strict_server()
    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())

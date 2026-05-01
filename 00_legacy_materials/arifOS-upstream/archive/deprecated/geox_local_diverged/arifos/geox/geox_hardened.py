"""
arifos/geox/geox_hardened.py — Hardened GEOX Pipeline

This module integrates GEOX special tools with the arifOS governance layer:
- Thermodynamic analysis (delta_S)
- Dynamic Intelligence quantification (Genius Score)
- Constitutional Floor enforcement (13 Floors)
- Outcome Ledger integration (FORGED NOT GIVEN)
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any

from arifos.geox.geox_tools import GeoToolResult, ToolRegistry

# Sovereign Path Injection for arifOS alignment
ARIFOS_PATH = r"C:\ariffazil\arifOS"
ARIFOSMCP_PATH = os.path.join(ARIFOS_PATH, "arifosmcp")
ARIFOS_SITES = os.path.join(ARIFOSMCP_PATH, "sites")

if ARIFOS_SITES not in sys.path:
    sys.path.append(ARIFOS_SITES)
if ARIFOSMCP_PATH not in sys.path:
    sys.path.append(ARIFOS_PATH)
    sys.path.append(ARIFOSMCP_PATH)

logger = logging.getLogger("geox.hardened")

try:
    from arifosmcp.core.governance import get_governance_kernel
    from arifosmcp.core.shared.physics import delta_S, genius_score, humility_band
except ImportError:
    # Fallback/Shim if arifOS is genuinely missing (F9 Anti-Hantu warning)
    logger.warning("arifosmcp.core.shared.physics or governance not found. Using shims.")
    def delta_S(i: str, o: str) -> float:
        return 0.0
    def genius_score(**kwargs) -> float:
        return 0.0
    class HumilityShim:
        omega_0 = "UNKNOWN"
    def humility_band(c: float) -> Any:
        return HumilityShim()
    def get_governance_kernel(sid: str) -> Any:
        return None

from arifos.geox.governance import calculate_indices, get_verdict_advice


class HardenedGeoxAgent:
    """The hardened Geological Intelligence Agent for the arifOS Trinity."""

    def __init__(self, session_id: str = "anon_geo_session"):
        self.session_id = session_id
        self.registry = ToolRegistry.default_registry()
        self.kernel = get_governance_kernel(session_id)
        logger.info(f"HardenedGeoxAgent initialized [ID: {session_id}]")

    async def execute_tool(
        self,
        tool_name: str,
        params: dict[str, Any],
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute a geological tool with arifOS hardening."""
        start_time = datetime.now(timezone.utc)

        # 1. Fetch Tool
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return {
                "tool": tool_name,
                "payload": {"error": f"Tool {tool_name} not found in GEOX registry."},
                "verdict": "VOID",
                "risk_tier": "low"
            }

        # 2. Execution (The 'FORGE' step)
        try:
            result: GeoToolResult = await tool.execute(**params)
            payload = result.data
            notes = result.explanation
            verdict = "OK" if result.success else "VOID"
        except Exception as e:
            logger.exception(f"Tool {tool_name} failed execution.")
            payload = {"error": str(e)}
            notes = "Critical failure during geological forging."
            verdict = "VOID"

        # 3. Post-execution Measurement
        input_str = json.dumps(params, sort_keys=True, default=str)
        output_str = json.dumps(payload, sort_keys=True, default=str)
        ds = delta_S(input_str, output_str)

        # Update Kernel State if available
        indices = {}
        verdict_advice = "No kernel feedback"
        if self.kernel:
            # P0: Fix missing attribute error by calling the newly implemented method
            try:
                self.kernel.apply_temporal_grounding({"latency_ms": (datetime.now(timezone.utc) - start_time).total_seconds() * 1000})
                k_state = self.kernel.get_current_state()
                indices = calculate_indices(k_state)
                verdict_advice = get_verdict_advice(indices)
            except Exception as k_err:
                logger.error(f"Kernel sync failed: {k_err}")

        # 4. Genius Score Calculation (F8)
        g = indices.get("apex_readiness", genius_score(A=0.9, P=1.0, X=1.0, E=1.0 if ds <= 0 else 0.8))

        # 5. Geox Eureka: Goldilocks & Godellock (The Paradox Eureka)
        omega_obj = humility_band(0.9)
        omega = omega_obj.omega_0 if hasattr(omega_obj, "omega_0") else 0.032

        # Determine Habitability
        is_goldilocks = (ds <= 0) and (0.03 <= omega <= 0.05)
        is_godellock = (omega < 0.03)

        # 6. Construct Envelope (F11 Authority)
        envelope = {
            "version": "v2026.3.27-GEOX",
            "session": self.session_id,
            "tool": tool_name,
            "timestamp": start_time.isoformat(),
            "duration_ms": int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000),
            "payload": payload,
            "explanation": notes,
            "verdict": "VOID" if is_godellock else verdict,
            "metrics": {
                "delta_s": round(ds, 4),
                "genius_score": round(g, 4),
                "stable": ds <= 0,
                "humility": round(omega, 4) if isinstance(omega, (float, int)) else omega,
                "indices": indices,
                "governance_advice": verdict_advice,
                "geox_eureka": {
                    "is_goldilocks": is_goldilocks,
                    "is_godellock": is_godellock,
                    "verdict": "HABITABLE" if is_goldilocks else ("LOCKED" if is_godellock else "UNSTABLE"),
                }
            },
            "floors": [4, 7, 8, 9, 11]
        }

        # Proactive 888_HOLD if discovery is high risk or uncertain (F13)
        if (indices.get("no_risk_threshold", 1.0) < 0.5 or ds > 2.0 or tool_name == "macrostrat_query") and verdict == "OK":
            envelope["verdict"] = "888_HOLD"
            envelope["explanation"] += " [Sovereign verification required: Low No-Risk Threshold]"

        return envelope

def get_hardened_agent(session_id: str) -> HardenedGeoxAgent:
    """Factory to get the hardened agent."""
    return HardenedGeoxAgent(session_id)

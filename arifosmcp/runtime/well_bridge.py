"""
arifOS WELL Bridge — Biological Substrate Connector
═══════════════════════════════════════════════════════════════════════════════

Connects the arifOS Governance Kernel to the WELL Human Substrate Layer.
Provides biological readiness signals (Sleep, Stress, Cognitive) to JUDGE.

Axiom: W0 — Sovereignty Invariant. WELL informs, JUDGE considers.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Topology: WELL State Path
WELL_STATE_PATH = Path("/root/WELL/state.json")

def get_biological_readiness() -> Dict[str, Any]:
    """
    Read the current biological readiness from WELL state.
    Returns a structured readiness report for the Governance Kernel.
    """
    if not WELL_STATE_PATH.exists():
        return {
            "ok": False,
            "verdict": "UNKNOWN",
            "well_score": 50.0,
            "bandwidth": "NORMAL",
            "message": "WELL substrate offline or state missing.",
            "sabar_advisory": False
        }

    try:
        with open(WELL_STATE_PATH, "r") as f:
            state = json.load(f)
        
        score = state.get("well_score", 50.0)
        violations = state.get("floors_violated", [])
        
        # Readiness logic (mirrors WELL/server.py:well_readiness)
        if violations:
            verdict = "DEGRADED"
            bandwidth = "RESTRICTED"
            sabar_advisory = True
        elif score >= 80:
            verdict = "OPTIMAL"
            bandwidth = "FULL"
            sabar_advisory = False
        elif score >= 60:
            verdict = "FUNCTIONAL"
            bandwidth = "NORMAL"
            sabar_advisory = False
        else:
            verdict = "LOW_CAPACITY"
            bandwidth = "REDUCED"
            sabar_advisory = True
            
        return {
            "ok": True,
            "verdict": verdict,
            "well_score": score,
            "bandwidth": bandwidth,
            "violations": violations,
            "sabar_advisory": sabar_advisory,
            "timestamp": state.get("timestamp")
        }
    except Exception as e:
        logger.error(f"Failed to read WELL state: {e}")
        return {
            "ok": False,
            "verdict": "ERROR",
            "error": str(e),
            "well_score": 0.0,
            "bandwidth": "RESTRICTED",
            "sabar_advisory": True
        }

def inject_biological_context(governance_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject biological readiness into the governance state telemetry.
    """
    readiness = get_biological_readiness()
    
    # Add WELL metadata to telemetry
    telemetry = governance_state.get("telemetry", {})
    telemetry["well_score"] = readiness["well_score"]
    telemetry["well_verdict"] = readiness["verdict"]
    telemetry["well_bandwidth"] = readiness["bandwidth"]
    
    if readiness["sabar_advisory"]:
        # If biological state is degraded, suggest SABAR (Patience)
        governance_state["sabar_advisory"] = True
        if governance_state.get("verdict") == "SEAL":
            # Soft-downgrade to HOLD if it was SEAL but substrate is low
            if readiness["verdict"] == "DEGRADED":
                 governance_state["verdict"] = "HOLD"
                 governance_state["message"] = (
                     governance_state.get("message", "") + 
                     " [WELL-HOLD] Biological substrate degraded. Sovereign review required."
                 )
    
    return governance_state

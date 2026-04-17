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
import os as _os
WELL_STATE_PATH = Path(_os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json"))

def get_biological_readiness() -> Dict[str, Any]:
    """
    Read the current biological readiness from WELL state.
    Returns a structured readiness report for the Governance Kernel.
    """
    try:
        _exists = WELL_STATE_PATH.exists()
    except (PermissionError, OSError):
        _exists = False
    if not _exists:
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

def signal_cognitive_pressure(load_delta: float, source: str = "forge") -> bool:
    """
    Signal cognitive pressure/load to WELL.
    Directly updates state.json if server is not available.
    """
    try:
        if not WELL_STATE_PATH.exists():
            return False
    except (PermissionError, OSError):
        return False

    try:
        with open(WELL_STATE_PATH, "r") as f:
            state = json.load(f)
        
        metrics = state.get("metrics", {})
        cog = dict(metrics.get("cognitive", {"clarity": 10, "decision_fatigue": 0}))
        
        # Increment fatigue
        old_fatigue = cog.get("decision_fatigue", 0)
        new_fatigue = min(10.0, old_fatigue + load_delta)
        cog["decision_fatigue"] = new_fatigue
        metrics["cognitive"] = cog
        
        # W6 Logic (Sync with server logic)
        violations = state.get("floors_violated", [])
        if load_delta > 2.0 and "W6_METABOLIC_PAUSE" not in violations:
            violations.append("W6_METABOLIC_PAUSE")
            
        state["metrics"] = metrics
        # Note: We don't recompute score here to keep the bridge lightweight;
        # the score will be recomputed next time WELL server is used or state is loaded.
        # But for UI accuracy, a quick estimation is better:
        state["well_score"] = max(0, state.get("well_score", 50) - (load_delta * 2))
        state["floors_violated"] = violations
        
        with open(WELL_STATE_PATH, "w") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception:
        return False

async def anchor_well_to_vault(summary: str = "WELL Substrate Anchor", force: bool = False) -> Dict[str, Any]:
    """
    Anchor current WELL state to the arifOS VAULT999.
    Provides immutable grounding for biological telemetry.
    """
    readiness = get_biological_readiness()
    if not readiness["ok"] and not force:
        return {"ok": False, "message": "Substrate offline. Anchor aborted."}
    
    try:
        from core.organs._4_vault import seal
        
        # Build telemetry for the vault
        telemetry = {
            "well_score": readiness["well_score"],
            "well_verdict": readiness["verdict"],
            "well_bandwidth": readiness["bandwidth"],
            "well_violations": readiness.get("violations", []),
            "source": "WELL-Substrate"
        }
        
        # Final seal of substrate state
        res = await seal(
            session_id="WELL-AUTO-SYNC",
            summary=summary,
            verdict="SEAL" if readiness["verdict"] in ("OPTIMAL", "FUNCTIONAL") else "HOLD",
            telemetry=telemetry,
            source_agent="well",
            pipeline_stage="999_VAULT",
            risk_tier="LOW"
        )
        
        return {
            "ok": True,
            "vault_id": res.seal_record.ledger_id,
            "hash": res.seal_record.hash,
            "verdict": res.verdict
        }
    except Exception as e:
        logger.error(f"VAULT ANCHOR FAILED: {e}")
        return {"ok": False, "error": str(e)}

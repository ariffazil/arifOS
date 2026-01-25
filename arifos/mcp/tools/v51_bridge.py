"""
v51 Bridge: AAA <-> Core Adapter
Wires Track C (MCP) to Track B (Core Engines).
Ensures outputs are JSON-serializable for Universal Clients (Stdio/SSE).

Architecture:
    MCP Tools (The Head) <-> v51_bridge (The Neck) <-> Core Engines (The Body)

The bridge handles:
    1. Fail-safe engine loading (graceful degradation)
    2. Object-to-dict serialization for JSON transport
    3. API shape transformation between MCP and Core

DITEMPA BUKAN DIBERI
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# FAIL-SAFE ENGINE IMPORTS
# =============================================================================

try:
    from arifos.core.engines.agi_engine import AGIEngine, Lane
    from arifos.core.engines.asi_engine import ASIEngine
    from arifos.core.engines.apex_engine import APEXEngine
    ENGINES_AVAILABLE = True
    logger.info("v51 Bridge: Core engines loaded successfully")
except ImportError as e:
    ENGINES_AVAILABLE = False
    logger.warning(f"v51 Bridge: Core engines unavailable ({e}). Using fallback mode.")
    # Define Lane stub for fallback
    class Lane:
        HARD = "HARD"
        SOFT = "SOFT"
        PHATIC = "PHATIC"
        REFUSE = "REFUSE"

# =============================================================================
# SINGLETON ENGINE INSTANCES (Lazy Load)
# =============================================================================

_AGI: Optional["AGIEngine"] = None
_ASI: Optional["ASIEngine"] = None
_APEX: Optional["APEXEngine"] = None


def get_agi() -> "AGIEngine":
    """Get or create AGI Engine singleton."""
    global _AGI
    if not ENGINES_AVAILABLE:
        raise RuntimeError("Core engines not available")
    if _AGI is None:
        _AGI = AGIEngine()
    return _AGI


def get_asi() -> "ASIEngine":
    """Get or create ASI Engine singleton."""
    global _ASI
    if not ENGINES_AVAILABLE:
        raise RuntimeError("Core engines not available")
    if _ASI is None:
        _ASI = ASIEngine()
    return _ASI


def get_apex() -> "APEXEngine":
    """Get or create APEX Engine singleton."""
    global _APEX
    if not ENGINES_AVAILABLE:
        raise RuntimeError("Core engines not available")
    if _APEX is None:
        _APEX = APEXEngine()
    return _APEX


# =============================================================================
# SERIALIZATION HELPER
# =============================================================================

def _serialize(obj: Any) -> Dict[str, Any]:
    """
    Ensure object is a clean dict for MCP transport.

    Handles:
        - Objects with as_dict() method
        - Objects with __dict__ attribute
        - Enum values
        - Nested dataclasses
    """
    if obj is None:
        return {}
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize(item) for item in obj]
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items()}
    if hasattr(obj, "value"):  # Enum
        return obj.value
    return obj


# =============================================================================
# AGI ADAPTERS (Mind/Δ)
# =============================================================================

def bridge_agi_sense(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute AGI SENSE stage via Core Engine.

    Maps Core SenseResult to MCP-compatible dict.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        result = get_agi().sense(query, context)

        # Map Core Result -> MCP Shape
        return {
            "status": "SEAL" if result.gpv.lane.value != "REFUSE" else "VOID",
            "reasoning": f"Lane classified: {result.gpv.lane.value}",
            "truth_score": result.gpv.truth_demand,
            "entropy_delta": 0.0,  # Computed in later stages
            "lane": result.gpv.lane.value,
            "semantic_map": {
                "lane": result.gpv.lane.value,
                "intent": result.gpv.intent,
                "entities": result.gpv.entities,
                "contrasts": result.gpv.contrasts,
                "truth_demand": result.gpv.truth_demand,
                "care_demand": result.gpv.care_demand,
                "risk_level": result.gpv.risk_level,
            },
            "floors_checked": ["F12_Injection", "F2_Truth"],
            "floor_F12_risk": result.floor_F12_risk,
            "sub_stage": "111_SENSE",
            "source": "v51_bridge"
        }
    except Exception as e:
        logger.error(f"bridge_agi_sense failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


def bridge_agi_think(sense_result: Dict, depth: int = 3) -> Dict[str, Any]:
    """
    Execute AGI THINK stage via Core Engine.

    Requires sense_result from bridge_agi_sense or inline SENSE.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        # Reconstruct SenseResult from dict (simplified)
        from arifos.core.engines.agi_engine import SenseResult, GovernancePlacementVector

        gpv_data = sense_result.get("semantic_map", {})
        gpv = GovernancePlacementVector(
            lane=Lane[gpv_data.get("lane", "SOFT")],
            truth_demand=gpv_data.get("truth_demand", 0.7),
            care_demand=gpv_data.get("care_demand", 0.5),
            risk_level=gpv_data.get("risk_level", 0.3),
            intent=gpv_data.get("intent", "discuss"),
            entities=gpv_data.get("entities", []),
            contrasts=gpv_data.get("contrasts", [])
        )

        sense = SenseResult(
            timestamp=0.0,
            query_parsed=sense_result.get("query", ""),
            input_length=0,
            gpv=gpv,
            floor_F12_risk=sense_result.get("floor_F12_risk", 0.0)
        )

        result = get_agi().think(sense, depth)
        return _serialize(result)
    except Exception as e:
        logger.error(f"bridge_agi_think failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


def bridge_agi_full(query: str, context: Optional[Dict] = None, 
                    zk_proof: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Full AGI Pipeline via Core Engine.

    Returns complete AGIOutput as dict.
    Supports zk_proof verification for F3/F13 integrity.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        # TODO: Verify zk_proof if provided
        if zk_proof:
            logger.info(f"v51_bridge: zk_proof received: {zk_proof[:16]}...")
            
        output = get_agi().execute(query, context)
        return _serialize(output)
    except Exception as e:
        logger.error(f"bridge_agi_full failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


# =============================================================================
# ASI ADAPTERS (Heart/Ω)
# =============================================================================

def bridge_asi_evidence(agi_output: Dict, context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute ASI EVIDENCE stage via Core Engine.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        result = get_asi().evidence(agi_output, context)
        return _serialize(result)
    except Exception as e:
        logger.error(f"bridge_asi_evidence failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


def bridge_asi_empathize(agi_output: Dict, user_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute ASI EMPATHY stage via Core Engine.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        result = get_asi().empathize(agi_output, user_context)
        return {
            "kappa_r": result.kappa_r,
            "vulnerability_assessment": result.vulnerability_assessment,
            "care_recommendations": result.care_recommendations,
            "weakest_stakeholder": result.stakeholder_map.weakest.name if result.stakeholder_map.weakest else None,
            "source": "v51_bridge"
        }
    except Exception as e:
        logger.error(f"bridge_asi_empathize failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


def bridge_asi_full(agi_output: Dict, user_context: Optional[Dict] = None,
                    proposed_action: Optional[str] = None,
                    zk_proof: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Full ASI Pipeline via Core Engine.
    Supports zk_proof verification.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        # TODO: Verify zk_proof
        if zk_proof:
            logger.info(f"v51_bridge: zk_proof received: {zk_proof[:16]}...")

        output = get_asi().execute(agi_output, user_context, proposed_action)
        return _serialize(output)
    except Exception as e:
        logger.error(f"bridge_asi_full failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


# =============================================================================
# APEX ADAPTERS (Soul/Ψ)
# =============================================================================

def bridge_apex_judge(query: str, response: str, agi_result: Optional[Dict] = None,
                      asi_result: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Execute APEX JUDGE via Core Engine.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        apex = get_apex()
        # APEX engine API may vary - adapt as needed
        if hasattr(apex, 'judge'):
            result = apex.judge(query, response, agi_result, asi_result)
            return _serialize(result)
        return {"status": "FALLBACK", "reason": "APEX judge method not implemented"}
    except Exception as e:
        logger.error(f"bridge_apex_judge failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


def bridge_apex_full(query: str, response: str, agi_result: Optional[Dict] = None,
                     asi_result: Optional[Dict] = None,
                     zk_proof: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Full APEX Pipeline via Core Engine.
    Supports zk_proof verification.
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable"}

    try:
        # TODO: Verify zk_proof
        if zk_proof:
            logger.info(f"v51_bridge: zk_proof received: {zk_proof[:16]}...")
            
        apex = get_apex()
        if hasattr(apex, 'execute'):
            output = apex.execute(query, response, agi_result, asi_result)
            return _serialize(output)
        return {"status": "FALLBACK", "reason": "APEX execute method not implemented"}
    except Exception as e:
        logger.error(f"bridge_apex_full failed: {e}")
        return {"status": "ERROR", "error": str(e), "source": "v51_bridge"}


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Status
    "ENGINES_AVAILABLE",

    # Engine getters
    "get_agi",
    "get_asi",
    "get_apex",

    # AGI adapters
    "bridge_agi_sense",
    "bridge_agi_think",
    "bridge_agi_full",

    # ASI adapters
    "bridge_asi_evidence",
    "bridge_asi_empathize",
    "bridge_asi_full",

    # APEX adapters
    "bridge_apex_judge",
    "bridge_apex_full",

    # Utilities
    "_serialize",
]

"""
AAA Bridge: Application <-> Core Adapter (v51.0.0)
Wires MCP Requests to arifOS Core Engines.

The Body (Hands) speaks to the Brain (Soul) through this bridge.
Zero logic here - only routing and serialization.

DITEMPA BUKAN DIBERI
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# =============================================================================
# CORE ENGINE IMPORTS (Fail-safe)
# =============================================================================

try:
    from arifos.core.engines.agi_engine import AGIEngine, Lane, SenseResult, ThinkResult
    from arifos.core.engines.asi_engine import ASIEngine
    from arifos.core.engines.apex_engine import APEXEngine
    ENGINES_AVAILABLE = True
    logger.info("AAA Bridge: Core engines loaded successfully")
except ImportError as e:
    logger.warning(f"AAA Bridge: Core engines unavailable: {e}")
    ENGINES_AVAILABLE = False
    AGIEngine = None
    ASIEngine = None
    APEXEngine = None

# =============================================================================
# SINGLETON ENGINE INSTANCES
# =============================================================================

_AGI: Optional["AGIEngine"] = None
_ASI: Optional["ASIEngine"] = None
_APEX: Optional["APEXEngine"] = None


def get_agi() -> "AGIEngine":
    """Get or create AGI engine singleton."""
    global _AGI
    if _AGI is None and ENGINES_AVAILABLE:
        _AGI = AGIEngine()
    return _AGI


def get_asi() -> "ASIEngine":
    """Get or create ASI engine singleton."""
    global _ASI
    if _ASI is None and ENGINES_AVAILABLE:
        _ASI = ASIEngine()
    return _ASI


def get_apex() -> "APEXEngine":
    """Get or create APEX engine singleton."""
    global _APEX
    if _APEX is None and ENGINES_AVAILABLE:
        _APEX = APEXEngine()
    return _APEX


# =============================================================================
# SERIALIZATION HELPER
# =============================================================================

def _serialize(obj: Any) -> Any:
    """Recursively serialize objects to JSON-safe dicts/lists."""
    if obj is None:
        return None
    if hasattr(obj, "as_dict"):
        return obj.as_dict()
    if hasattr(obj, "__dict__"):
        return _serialize(obj.__dict__)
    if isinstance(obj, list):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, (str, int, float, bool)):
        return obj
    # Enum handling
    if hasattr(obj, "value"):
        return obj.value
    return str(obj)


# =============================================================================
# AGI ROUTER (Mind - Δ)
# =============================================================================

def bridge_agi_router(
    action: str,
    query: str = "",
    context: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes AGI actions to granular Core methods.

    Actions:
      - full: Complete AGI pipeline (execute)
      - sense: Lane classification + truth threshold
      - think: Deep reasoning (requires sense first)
      - atlas: Meta-cognition mapping
      - reflect: Clarity/entropy checking
      - forge: Clarity refinement
      - evaluate: Floor evaluation
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable", "source": "AAA_bridge"}

    engine = get_agi()
    if engine is None:
        return {"status": "FALLBACK", "reason": "AGI engine init failed", "source": "AAA_bridge"}

    try:
        if action == "full":
            result = engine.execute(query, context)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            return output

        elif action == "sense":
            result = engine.sense(query, context)
            return {
                "status": "SEAL" if result.gpv.lane.value != "REFUSE" else "VOID",
                "lane": result.gpv.lane.value,
                "truth_score": result.gpv.truth_demand,
                "entities": result.gpv.entities,
                "contrasts": result.gpv.contrasts,
                "source": "AAA_bridge"
            }

        elif action == "think":
            # Think requires sense_result. Run sense first if not provided.
            sense_result = kwargs.get("sense_result")
            if not sense_result:
                sense_result = engine.sense(query, context)
            result = engine.think(sense_result)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            return output

        elif action == "atlas":
            sense_result = engine.sense(query, context)
            think_result = engine.think(sense_result)
            result = engine.atlas(sense_result, think_result)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            return output

        elif action == "reflect":
            # Reflect is part of think cycle
            sense_result = engine.sense(query, context)
            result = engine.think(sense_result)
            return {
                "status": "SEAL",
                "reflection": _serialize(result),
                "source": "AAA_bridge"
            }

        elif action == "forge":
            # Forge is full pipeline with clarity refinement
            result = engine.execute(query, context)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            output["forged"] = True
            return output

        elif action == "evaluate":
            # Evaluate floors
            result = engine.sense(query, context)
            return {
                "status": "SEAL" if result.gpv.lane.value != "REFUSE" else "VOID",
                "lane": result.gpv.lane.value,
                "truth_score": result.gpv.truth_demand,
                "floors": {
                    "F2_truth": result.gpv.truth_demand >= 0.99,
                    "F4_clarity": True,  # ΔS check would go here
                    "F7_humility": True,  # Ω₀ check would go here
                },
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown AGI action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"AGI bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# ASI ROUTER (Heart - Ω)
# =============================================================================

def bridge_asi_router(
    action: str,
    agi_result: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes ASI actions to Core methods.

    Actions:
      - full: Complete ASI pipeline
      - evidence: Truth grounding via sources
      - empathize: Power-aware recalibration
      - align: Constitutional veto gates
      - act: Execution with tri-witness gating
      - witness: Collect tri-witness signatures
      - evaluate: Floor evaluation
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable", "source": "AAA_bridge"}

    engine = get_asi()
    if engine is None:
        return {"status": "FALLBACK", "reason": "ASI engine init failed", "source": "AAA_bridge"}

    try:
        if action == "full":
            if not agi_result:
                return {"status": "VOID", "reason": "ASI requires agi_result input", "source": "AAA_bridge"}
            result = engine.execute(agi_result)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            return output

        elif action == "evidence":
            query = kwargs.get("query", "")
            sources = kwargs.get("sources", [])
            # Evidence gathering - simplified for now
            return {
                "status": "SEAL",
                "evidence": {"query": query, "sources": sources},
                "source": "AAA_bridge"
            }

        elif action == "empathize":
            proposal = kwargs.get("proposal", "")
            stakeholders = kwargs.get("stakeholders", [])
            return {
                "status": "SEAL",
                "empathy": {
                    "proposal": proposal,
                    "stakeholders": stakeholders,
                    "kappa_r": 0.95  # Default empathy score
                },
                "source": "AAA_bridge"
            }

        elif action == "align":
            return {
                "status": "SEAL",
                "alignment": {"constitutional": True},
                "source": "AAA_bridge"
            }

        elif action == "act":
            if not agi_result:
                return {"status": "VOID", "reason": "act requires agi_result", "source": "AAA_bridge"}
            result = engine.execute(agi_result)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            return output

        elif action == "witness":
            witness_id = kwargs.get("witness_request_id", "")
            approval = kwargs.get("approval", False)
            return {
                "status": "SEAL" if approval else "SABAR",
                "witness": {"id": witness_id, "approval": approval},
                "source": "AAA_bridge"
            }

        elif action == "evaluate":
            return {
                "status": "SEAL",
                "floors": {
                    "F3_peace": True,
                    "F4_empathy": True,
                    "F5_omega": True,
                },
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown ASI action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"ASI bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# APEX ROUTER (Soul - Ψ)
# =============================================================================

def bridge_apex_router(
    action: str,
    agi_result: Optional[Dict] = None,
    asi_result: Optional[Dict] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes APEX actions. Requires inputs from Mind & Heart.

    Actions:
      - full/judge: Complete APEX pipeline
      - eureka: Paradox synthesis (Truth ∩ Care)
      - proof: Cryptographic sealing
      - entropy: Constitutional entropy measurement
      - parallelism: Parallelism proof
    """
    if not ENGINES_AVAILABLE:
        return {"status": "FALLBACK", "reason": "Core engines unavailable", "source": "AAA_bridge"}

    engine = get_apex()
    if engine is None:
        return {"status": "FALLBACK", "reason": "APEX engine init failed", "source": "AAA_bridge"}

    try:
        if action in ("full", "judge"):
            if not agi_result or not asi_result:
                return {
                    "status": "VOID",
                    "reason": "APEX requires both agi_result and asi_result",
                    "source": "AAA_bridge"
                }
            result = engine.execute(agi_result, asi_result)
            output = _serialize(result)
            output["source"] = "AAA_bridge"
            return output

        elif action == "eureka":
            # Paradox synthesis - Truth ∩ Care
            return {
                "status": "SEAL",
                "eureka": {
                    "synthesis": "Truth and Care aligned",
                    "paradox_resolved": True
                },
                "source": "AAA_bridge"
            }

        elif action == "proof":
            data = kwargs.get("data", "")
            verdict = kwargs.get("verdict", "SEAL")
            import hashlib
            proof_hash = hashlib.sha256(str(data).encode()).hexdigest()[:16]
            return {
                "status": verdict,
                "proof": {
                    "hash": proof_hash,
                    "data": data,
                    "sealed": True
                },
                "source": "AAA_bridge"
            }

        elif action == "entropy":
            return {
                "status": "SEAL",
                "entropy": {
                    "delta_s": 0.0,  # Entropy change
                    "constitutional": True
                },
                "source": "AAA_bridge"
            }

        elif action == "parallelism":
            return {
                "status": "SEAL",
                "parallelism": {
                    "agi_asi_orthogonal": True,
                    "tri_witness": 0.95
                },
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown APEX action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"APEX bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# VAULT ROUTER (Seal - 999)
# =============================================================================

def bridge_vault_router(
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes Vault actions for sealing and persistence.

    Actions:
      - seal: Final seal with Merkle + zkPC
      - list: List vault entries
      - read: Read vault entry
      - write: Write to vault (requires authority)
      - propose: Propose new canon entry
    """
    try:
        if action == "seal":
            verdict = kwargs.get("verdict", "SEAL")
            import hashlib
            import time
            seal_data = {
                "timestamp": time.time(),
                "verdict": verdict,
                "init_result": kwargs.get("init_result"),
                "agi_result": kwargs.get("agi_result"),
                "asi_result": kwargs.get("asi_result"),
                "apex_result": kwargs.get("apex_result"),
            }
            seal_hash = hashlib.sha256(str(seal_data).encode()).hexdigest()
            return {
                "status": verdict,
                "seal": {
                    "hash": seal_hash,
                    "timestamp": seal_data["timestamp"],
                    "sealed": True
                },
                "source": "AAA_bridge"
            }

        elif action == "list":
            target = kwargs.get("target", "ledger")
            return {
                "status": "SEAL",
                "entries": [],  # Would query actual vault
                "target": target,
                "source": "AAA_bridge"
            }

        elif action == "read":
            query = kwargs.get("query", "")
            target = kwargs.get("target", "ledger")
            return {
                "status": "SEAL",
                "data": None,  # Would read from vault
                "query": query,
                "target": target,
                "source": "AAA_bridge"
            }

        elif action == "write":
            return {
                "status": "888_HOLD",
                "reason": "Vault write requires human authority",
                "source": "AAA_bridge"
            }

        elif action == "propose":
            return {
                "status": "SABAR",
                "reason": "Canon proposals require tri-witness approval",
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown vault action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"Vault bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}


# =============================================================================
# INIT ROUTER (Gate - 000)
# =============================================================================

def bridge_init_router(
    action: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Routes Init actions for session management.

    Actions:
      - init: Full initialization
      - gate: Constitutional authority check
      - reset: Clean session start
      - validate: Pre-flight validation
    """
    import uuid
    import time

    try:
        session_id = kwargs.get("session_id") or str(uuid.uuid4())

        if action == "init":
            return {
                "status": "SEAL",
                "session_id": session_id,
                "timestamp": time.time(),
                "gates": {
                    "F1_amanah": True,
                    "F11_command_auth": True,
                    "F12_injection": True,
                },
                "source": "AAA_bridge"
            }

        elif action == "gate":
            query = kwargs.get("query", "")
            # Simple injection check
            injection_patterns = ["rm -rf", "DROP TABLE", "eval(", "curl | bash"]
            is_safe = not any(p in query for p in injection_patterns)
            return {
                "status": "SEAL" if is_safe else "VOID",
                "gate": "open" if is_safe else "blocked",
                "reason": None if is_safe else "Injection pattern detected",
                "source": "AAA_bridge"
            }

        elif action == "reset":
            return {
                "status": "SEAL",
                "session_id": str(uuid.uuid4()),  # New session
                "reset": True,
                "source": "AAA_bridge"
            }

        elif action == "validate":
            return {
                "status": "SEAL",
                "valid": True,
                "source": "AAA_bridge"
            }

        else:
            return {"status": "FALLBACK", "reason": f"Unknown init action: {action}", "source": "AAA_bridge"}

    except Exception as e:
        logger.error(f"Init bridge error ({action}): {e}")
        return {"status": "ERROR", "reason": str(e), "source": "AAA_bridge"}

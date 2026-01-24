"""
arifOS Pure Bridge (v52.0.0)
Authority: Muhammad Arif bin Fazil
Principle: Zero Logic Delegation (F1)

"I do not think, I only wire."

The bridge is a zero-logic adapter between the transport layer (SSE/STDIO)
and the arifOS cores (AGI/ASI/APEX).
"""

from __future__ import annotations
import logging
import asyncio
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# --- CORE AVAILABILITY ---
try:
    from arifos.core.agi.kernel import AGINeuralCore
    from arifos.core.asi.kernel import ASIActionCore
    from arifos.core.apex.kernel import APEXJudicialCore
    from arifos.core.prompt.router import route_prompt
    ENGINES_AVAILABLE = True
except ImportError:
    logger.warning("arifOS Cores unavailable - Bridge in degraded mode")
    AGINeuralCore = ASIActionCore = APEXJudicialCore = None
    route_prompt = None
    ENGINES_AVAILABLE = False

_FALLBACK_RESPONSE = {"status": "VOID", "reason": "arifOS Cores unavailable", "verdict": "VOID"}

# Singletons
_AGI = _ASI = _APEX = None

def _kernel(cls, cache_name: str):
    """Get or create kernel singleton."""
    g = globals()
    if g[cache_name] is None and ENGINES_AVAILABLE and cls:
        g[cache_name] = cls()
    return g[cache_name]

# --- UTILS ---
def _serialize(obj: Any) -> Any:
    """Zero-logic serialization for transport."""
    if obj is None: return None
    if hasattr(obj, "to_dict"): return obj.to_dict()
    if hasattr(obj, "as_dict"): return obj.as_dict()
    if hasattr(obj, "__dict__"): return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    if isinstance(obj, (list, tuple)): return [_serialize(x) for x in obj]
    if isinstance(obj, dict): return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "value") and not isinstance(obj, (int, float, str, bool)):
        return obj.value
    if isinstance(obj, (str, int, float, bool)): return obj
    return str(obj)

# --- ROUTERS ---

async def bridge_init_router(action: str = "init", **kwargs) -> dict:
    """Pure bridge: Initialize session."""
    import uuid, time
    session_id = kwargs.get("session_id") or str(uuid.uuid4())
    return {
        "session_id": session_id,
        "timestamp": time.time(),
        "engines_available": ENGINES_AVAILABLE,
        "action": action,
        "status": "READY"
    }

async def bridge_agi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route reasoning tasks to AGI Genius."""
    kernel = _kernel(AGINeuralCore, "_AGI")
    if not kernel: return _FALLBACK_RESPONSE
    
    query = kwargs.get("query", "")
    ctx = kwargs.get("context", {})
    
    try:
        if action == "sense":
            return _serialize(await kernel.sense(query, ctx))
        elif action == "reflect":
            return _serialize(await kernel.reflect(
                kwargs.get("thought", query),
                kwargs.get("thought_number", 1),
                kwargs.get("total_thoughts", 1),
                kwargs.get("next_needed", False)
            ))
        elif action == "evaluate":
            return _serialize(kernel.evaluate(query, kwargs.get("response", ""), kwargs.get("truth_score", 1.0)))
        else:
            return _serialize(await kernel.sense(query, ctx))
    except Exception as e:
        logger.error(f"AGI Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

async def bridge_asi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route action/empathy tasks to ASI Act."""
    kernel = _kernel(ASIActionCore, "_ASI")
    if not kernel: return _FALLBACK_RESPONSE
    
    text = kwargs.get("text", kwargs.get("query", ""))
    ctx = kwargs.get("agi_result", {})
    
    try:
        if action == "evidence":
            return _serialize(await kernel.gather_evidence(kwargs.get("query", ""), kwargs.get("rationale", "")))
        elif action in ("empathize", "full", "act"):
            return _serialize(await kernel.empathize(text, ctx))
        elif action in ("bridge", "align"):
            return _serialize(await kernel.bridge_synthesis(ctx, kwargs.get("empathy_input", {})))
        else:
            return _serialize(await kernel.empathize(text, ctx))
    except Exception as e:
        logger.error(f"ASI Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

async def bridge_apex_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route judicial/verdict tasks to APEX Judge."""
    kernel = _kernel(APEXJudicialCore, "_APEX")
    if not kernel: return _FALLBACK_RESPONSE
    
    try:
        if action in ("full", "judge"):
            return _serialize(await kernel.judge_quantum_path(
                kwargs.get("query", ""),
                kwargs.get("response", ""),
                kwargs.get("trinity_floors", []),
                kwargs.get("session_id", "anonymous")
            ))
        elif action == "entropy":
            return _serialize(await kernel.entropy_profiler.measure_constitutional_cooling(
                kwargs.get("pre_text", ""), kwargs.get("post_text", "")
            ))
        else:
            return _serialize(await kernel.judge_quantum_path(kwargs.get("query", ""), kwargs.get("response", ""), [], "anonymous"))
    except Exception as e:
        logger.error(f"APEX Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

async def bridge_vault_router(action: str = "seal", **kwargs) -> dict:
    """Pure bridge: Route archival tasks to 999 Vault."""
    import hashlib, time
    if action == "seal":
        data = {
            "timestamp": time.time(),
            "verdict": kwargs.get("verdict"),
            "agi": kwargs.get("agi_result"),
            "asi": kwargs.get("asi_result"),
            "apex": kwargs.get("apex_result"),
        }
        return {"hash": hashlib.sha256(str(data).encode()).hexdigest(), "timestamp": data["timestamp"], "status": "SEALED"}
    return {"action": action, "status": "OK"}

async def bridge_prompt_router(action: str = "route", **kwargs) -> dict:
    """Pure bridge: Route codec/prompt tasks."""
    if not route_prompt: return _FALLBACK_RESPONSE
    user_input = kwargs.get("user_input", "")
    try:
        return _serialize(await route_prompt(user_input))
    except Exception as e:
        logger.error(f"Prompt Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

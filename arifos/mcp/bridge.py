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
    from arifos.core.kernel import get_kernel_manager
    ENGINES_AVAILABLE = True
except ImportError:
    logger.warning("arifOS Cores unavailable - Bridge in degraded mode")
    get_kernel_manager = None
    ENGINES_AVAILABLE = False

_FALLBACK_RESPONSE = {"status": "VOID", "reason": "arifOS Cores unavailable", "verdict": "VOID"}

# --- UTILS ---
def _serialize(obj: Any) -> Any:
    """Zero-logic serialization for transport."""
    if obj is None: return None
    if hasattr(obj, "to_dict"): return obj.to_dict()
    if hasattr(obj, "as_dict"): return obj.as_dict()
    # Handle dataclasses
    if hasattr(obj, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(obj)
    if isinstance(obj, (list, tuple)): return [_serialize(x) for x in obj]
    if isinstance(obj, dict): return {k: _serialize(v) for k, v in obj.items()}
    if hasattr(obj, "value") and not isinstance(obj, (int, float, str, bool)):
        return obj.value
    if isinstance(obj, (str, int, float, bool)): return obj
    # For objects without serialization, convert to dict if possible
    if hasattr(obj, "__dict__"):
        return {k: _serialize(v) for k, v in obj.__dict__.items() if not k.startswith("_")}
    return str(obj)

# --- ROUTERS ---

async def bridge_init_router(action: str = "init", **kwargs) -> dict:
    """Pure bridge: Initialize session via kernel manager."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    manager = get_kernel_manager()
    result = await manager.init_session(action, kwargs)
    return _serialize(result)

async def bridge_agi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route reasoning tasks to AGI Genius."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_agi()
    query = kwargs.get("query", "")
    ctx = kwargs.get("context", {})
    
    try:
        if action == "sense":
            return _serialize(await kernel.sense(query, ctx))
        elif action in ("think", "reflect"):
            return _serialize(await kernel.reflect(
                kwargs.get("thought", query),
                kwargs.get("thought_number", 1),
                kwargs.get("total_thoughts", 1),
                kwargs.get("next_needed", False)
            ))
        elif action == "atlas":
            # Stage 333: TAC Analysis
            return _serialize(await kernel.atlas_tac_analysis(kwargs.get("inputs", [])))
        elif action == "forge":
            draft = kwargs.get("draft", kwargs.get("response", query))
            return _serialize(await kernel.forge(draft, kwargs.get("omega_0", 0.04)))
        elif action == "evaluate":
            return _serialize(kernel.evaluate(query, kwargs.get("response", ""), kwargs.get("truth_score", 1.0)))
        else:
            return _serialize(await kernel.sense(query, ctx))
    except Exception as e:
        logger.error(f"AGI Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

async def bridge_asi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route action/empathy tasks to ASI Act."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_asi()
    text = kwargs.get("text", kwargs.get("query", ""))
    ctx = kwargs.get("agi_result", {})
    
    try:
        if action == "evidence":
            search_query = kwargs.get("query") or text
            return _serialize(await kernel.gather_evidence(search_query, kwargs.get("rationale", "")))
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
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_apex()
    try:
        if action in ("full", "judge"):
            return _serialize(await kernel.judge_quantum_path(
                kwargs.get("query", ""),
                kwargs.get("response", ""),
                kwargs.get("trinity_floors", []),
                kwargs.get("session_id", "anonymous")
            ))
        elif action in ("eureka", "forge"):
            return _serialize(await kernel.forge_insight(kwargs.get("draft", kwargs.get("response", ""))))
        elif action == "entropy":
            return _serialize(await kernel.entropy_profiler.measure_constitutional_cooling(
                kwargs.get("pre_text", ""), kwargs.get("post_text", "")
            ))
        elif action == "parallelism":
            import time
            return _serialize(await kernel.parallel_profiler.prove_constitutional_parallelism(
                kwargs.get("start_time", time.time()), kwargs.get("component_durations", {})
            ))
        elif action == "proof":
            import hashlib
            return {"hash": hashlib.sha256(str(kwargs.get("data", "")).encode()).hexdigest()[:16], "status": "PROVEN"}
        else:
            return _serialize(await kernel.judge_quantum_path(kwargs.get("query", ""), kwargs.get("response", ""), [], "anonymous"))
    except Exception as e:
        logger.error(f"APEX Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

async def bridge_vault_router(action: str = "seal", **kwargs) -> dict:
    """Pure bridge: Route archival tasks to 999 Vault."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
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
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    router = get_kernel_manager().get_prompt_router()
    user_input = kwargs.get("user_input", "")
    try:
        return _serialize(await router(user_input))
    except Exception as e:
        logger.error(f"Prompt Bridge error: {e}")
        return {"error": str(e), "status": "ERROR"}

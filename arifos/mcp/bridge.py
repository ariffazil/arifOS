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
    # Pure delegation to kernel execute method
    return _serialize(await kernel.execute(action, kwargs))

async def bridge_asi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route ethical tasks to ASI Act."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_asi()
    # Pure delegation to kernel execute method
    return _serialize(await kernel.execute(action, kwargs))

async def bridge_apex_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route judicial tasks to APEX Judge."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_apex()
    # Pure delegation to kernel execute method
    return _serialize(await kernel.execute(action, kwargs))

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

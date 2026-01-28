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
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Mid-session context passing (AGI → ASI → APEX → VAULT)
from arifos.mcp.constitutional_metrics import store_stage_result

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
def shannon_entropy(text: str) -> float:
    """Calculate Shannon entropy of text (simplified)."""
    if not text:
        return 0.0
    
    import math
    from collections import Counter
    
    # Count character frequencies
    counts = Counter(text)
    length = len(text)
    
    # Calculate entropy
    entropy = 0.0
    for count in counts.values():
        probability = count / length
        entropy -= probability * math.log2(probability)
    
    return entropy

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
    serialized = _serialize(result)
    session_id = (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id:
        store_stage_result(str(session_id), "init", serialized)
    return serialized

async def bridge_agi_action_router(action: str = "full", **kwargs) -> dict:
    """Action router for agi_genius with "metrics" support."""
    if action == "metrics":
        return await bridge_agi_metrics_router(action, **kwargs)
    else:
        return await bridge_agi_router(action, **kwargs)

async def bridge_agi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route reasoning tasks to AGI Genius."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_agi()
    # Pure delegation to kernel execute method
    serialized = _serialize(await kernel.execute(action, kwargs))
    session_id = kwargs.get("session_id") or (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id and isinstance(serialized, dict):
        store_stage_result(str(session_id), "agi", serialized)
    return serialized

async def bridge_asi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route ethical tasks to ASI Act."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_asi()
    # Pure delegation to kernel execute method
    serialized = _serialize(await kernel.execute(action, kwargs))
    session_id = kwargs.get("session_id") or (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id and isinstance(serialized, dict):
        store_stage_result(str(session_id), "asi", serialized)
    return serialized

async def bridge_apex_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route judicial tasks to APEX Judge."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_apex()
    # Pure delegation to kernel execute method
    serialized = _serialize(await kernel.execute(action, kwargs))
    session_id = kwargs.get("session_id") or (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id and isinstance(serialized, dict):
        store_stage_result(str(session_id), "apex", serialized)
    return serialized

async def bridge_vault_router(action: str = "seal", **kwargs) -> dict:
    """Pure bridge: Route archival tasks to VAULT-999."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    # Vault operations are part of the APEX Judicial Kernel in v52
    kernel = get_kernel_manager().get_apex()
    serialized = _serialize(await kernel.execute(action, kwargs))
    session_id = kwargs.get("session_id") or (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id and isinstance(serialized, dict):
        store_stage_result(str(session_id), "apex", serialized)
    return serialized

async def bridge_agi_metrics_router(action: str = "metrics", session_id: Optional[str] = None, **kwargs) -> dict:
    """Pure bridge: Get thermodynamic dashboard metrics for a session."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    if not session_id:
        return {"error": "session_id required for metrics", "status": "ERROR"}
    
    # Import dashboard from codebase
    try:
        from codebase.agi.metrics import get_dashboard
        dashboard = get_dashboard(session_id)
        
        if action == "metrics":
            return _serialize(dashboard.generate_report())
        elif action == "stream":
            # Return latest snapshot
            if dashboard.metrics_stream:
                return _serialize(dashboard.metrics_stream[-1].to_dict())
            else:
                return {"error": "No metrics recorded yet", "status": "NO_DATA"}
        else:
            return {"error": f"Unknown metrics action: {action}", "status": "ERROR"}
            
    except ImportError as e:
        logger.error(f"Metrics module not available: {e}")
        return _FALLBACK_RESPONSE
    except Exception as e:
        logger.error(f"Metrics retrieval error: {e}")
        return {"error": str(e), "status": "ERROR"}

async def bridge_trinity_hat_router(query: str, session_id: Optional[str] = None, max_loops: int = 3, target_delta_s: float = -0.3, **kwargs) -> dict:
    """Pure bridge: 3-Loop Chaos → Canon Compressor (Red/Yellow/Blue)."""
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    # Initialize session if needed
    if not session_id:
        init_result = await bridge_init_router(action="init", query=query)
        session_id = init_result.get("session_id", "trinity_hat_" + str(time.time()))
    
    current_entropy = shannon_entropy(query) if 'shannon_entropy' in globals() else len(query) * 0.1
    thoughts = []
    loop_results = []
    
    # Define hat sequence: Red → Yellow → Blue
    hats = [
        ("red", "Emotion/Intuition", "loop1"),
        ("yellow", "Optimism/Benefits", "loop2"),
        ("blue", "Process/Judgment", "loop3")
    ]
    
    for loop_num, (hat_color, hat_purpose, loop_id) in enumerate(hats, 1):
        if loop_num > max_loops:
            break
            
        # LOOP N: AGI Hat Thinking
        hat_query = f"{hat_color}_hat_{loop_id}: {query}"
        if thoughts:
            hat_query += f" | Prior: {thoughts[-1].get('summary', '')}"
        
        agi_result = await bridge_agi_router(
            action="think",
            query=hat_query,
            session_id=session_id,
            context={"hat": hat_color, "loop": loop_num, "prior_thoughts": thoughts}
        )
        
        if isinstance(agi_result, dict) and agi_result.get("verdict") == "VOID":
            return agi_result  # Early exit on VOID
            
        # ASI Veto (F3/F4/F5)
        asi_result = await bridge_asi_router(
            action="witness",
            text=agi_result.get("reasoning", str(agi_result)),
            session_id=session_id
        )
        
        if isinstance(asi_result, dict) and asi_result.get("verdict") == "VOID":
            return {
                "verdict": "VOID",
                "reason": f"ASI veto on {hat_color} hat: {asi_result.get('reason', 'Ethical violation')}",
                "loop": loop_num,
                "session_id": session_id
            }
        
        # Entropy Gate (F6)
        new_entropy = shannon_entropy(agi_result.get("reasoning", "")) if 'shannon_entropy' in globals() else len(str(agi_result)) * 0.08
        delta_s = new_entropy - current_entropy
        
        thought_record = {
            "loop": loop_num,
            "hat": hat_color,
            "purpose": hat_purpose,
            "agi_output": agi_result,
            "asi_veto": asi_result,
            "entropy_before": current_entropy,
            "entropy_after": new_entropy,
            "delta_s": delta_s,
            "threshold_met": delta_s < -0.1
        }
        thoughts.append(thought_record)
        loop_results.append(thought_record)
        
        if delta_s < -0.1:  # Cooling threshold
            current_entropy = new_entropy
        else:
            # Insufficient cooling = SABAR (retry if not last loop)
            if loop_num == max_loops:
                return {
                    "verdict": "SABAR",
                    "reason": f"ΔS stall: {delta_s:.3f} (insufficient cooling in {hat_color} hat)",
                    "loop": loop_num,
                    "session_id": session_id,
                    "thoughts": loop_results
                }
            # Retry this hat by not updating current_entropy
            continue
        
        if loop_num == 3:  # Blue hat convergence
            break
    
    # Final APEX Judgment (Blue Hat)
    apex_result = await bridge_apex_router(
        action="judge",
        query=query,
        response=str(thoughts),
        session_id=session_id,
        context={"thoughts": thoughts, "total_delta_s": sum(t["delta_s"] for t in thoughts)}
    )
    
    if isinstance(apex_result, dict) and apex_result.get("verdict") == "VOID":
        return apex_result
    
    # Vault Seal
    vault_result = await bridge_vault_router(
        action="seal",
        session_id=session_id,
        target="seal",
        payload={
            "verdict": apex_result.get("verdict", "SEAL"),
            "thoughts": thoughts,
            "total_delta_s": sum(t["delta_s"] for t in thoughts),
            "query": query
        }
    )
    
    return {
        "verdict": apex_result.get("verdict", "SEAL"),
        "canon_reasoning": apex_result.get("reasoning", str(apex_result)),
        "total_delta_s": sum(t["delta_s"] for t in thoughts),
        "loops_completed": len(thoughts),
        "session_id": session_id,
        "thoughts": thoughts,
        "vault_sealed": vault_result
    }

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

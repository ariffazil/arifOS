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
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Mid-session context passing (AGI → ASI → APEX → VAULT)
from codebase.mcp.constitutional_metrics import store_stage_result, get_stage_result
from codebase.mcp.tools.trinity_validator import validate_trinity_request
from codebase.mcp.tools import context_scope, reality_grounding
from codebase.mcp.external_gateways.context7_client import Context7Client
from codebase.mcp.external_gateways.brave_client import BraveSearchClient

# --- CORE AVAILABILITY ---
try:
    from codebase.kernel import get_kernel_manager
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
    serialized = _serialize(result)
    session_id = (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id:
        store_stage_result(str(session_id), "init", serialized)
    return serialized

async def bridge_agi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route reasoning tasks to AGI Genius.
    Adapts Contrast Actions: predict, measure -> think, evaluate
    """
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_agi()
    
    # --- CONTRAST ADAPTERS ---
    if action in ["predict", "physics"]:
        # Transform "predict"/"physics" -> "think" (Reasoning/Modelling)
        kwargs["thought"] = f"Reasoning Mode ({action}): Model reality for '{kwargs.get('query','')}'"
        action = "think"
    elif action in ["measure", "math"]:
        # Transform "measure"/"math" -> "evaluate" (Quantification)
        action = "evaluate"
    elif action == "language":
        # Transform "language" -> "forge" (Projection/Execution)
        action = "forge"
        
    serialized = _serialize(await kernel.execute(action, kwargs))
    session_id = kwargs.get("session_id") or (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id and isinstance(serialized, dict):
        store_stage_result(str(session_id), "agi", serialized)
    return serialized

async def bridge_asi_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route ethical tasks to ASI Act.
    Adapts Contrast Actions: harmonize, measure -> align, evaluate
    Adapts Triad Actions: physics, math, language
    """
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_asi()
    
    # --- CONTRAST ADAPTERS ---
    if action == "harmonize":
        action = "align"
        kwargs["proposal"] = "Harmonization: Seek win-win resolution."
    elif action == "physics":
        # Physics -> Empathize (Modelling Emotional Reality)
        action = "empathize"
    elif action in ["measure", "math"]:
        # Math -> Evaluate (Scoring Peace/Empathy)
        action = "evaluate"
    elif action == "language":
        # Language -> Act (Execution)
        action = "act"

    serialized = _serialize(await kernel.execute(action, kwargs))
    session_id = kwargs.get("session_id") or (serialized or {}).get("session_id") if isinstance(serialized, dict) else None
    if session_id and isinstance(serialized, dict):
        store_stage_result(str(session_id), "asi", serialized)
    return serialized

# --- v53 ASI COMPONENT ROUTERS ---
async def bridge_asi_stakeholder_router(**kwargs) -> dict:
    """Route A1 Semantic Stakeholder Reasoning."""
    return await bridge_asi_router(action="semantic_stakeholder_reasoning", **kwargs)

async def bridge_asi_diffusion_router(**kwargs) -> dict:
    """Route A2 Impact Diffusion."""
    return await bridge_asi_router(action="impact_diffusion_peace_squared", **kwargs)

async def bridge_asi_audit_router(**kwargs) -> dict:
    """Route A3 Constitutional Audit."""
    return await bridge_asi_router(action="constitutional_audit_sink", **kwargs)


async def bridge_apex_router(action: str = "full", **kwargs) -> dict:
    """Pure bridge: Route judicial tasks to APEX Judge.
    Adapts Contrast Actions: redeem, measure -> eureka, entropy
    Adapts Triad Actions: physics, math, language
    """
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE
    
    kernel = get_kernel_manager().get_apex()
    
    # --- CONTRAST ADAPTERS ---
    if action == "redeem":
        action = "eureka"
    elif action == "physics":
        # Physics -> Judge (Reasoning about Law/Reality)
        action = "judge"
    elif action in ["measure", "math"]:
        # Math -> Entropy (Scoring Confidence)
        action = "entropy"
    elif action == "language":
        # Language -> Judge (Verdict Projection)
        action = "judge"

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

# --- EXTERNAL GATEWAY ROUTING ---

class BridgeRouter:
    """Manages routing between MCP tools and external reality gateways."""
    
    def __init__(self, context7_key: Optional[str] = None, brave_key: Optional[str] = None):
        import os
        self.context7 = Context7Client(context7_key or os.environ.get("CONTEXT7_API_KEY"))
        self.brave = BraveSearchClient(brave_key or os.environ.get("BRAVE_API_KEY"))
    
    async def route_context_docs(
        self,
        query: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Route technical documentation queries to Context7."""
        # Get authority from init stage
        init_result = get_stage_result(session_id, "init") if session_id else {}
        scar_weight = init_result.get("scar_weight", 0.0)
        
        allowed_paths, includes_secrets = context_scope.validate_context_scope(query, scar_weight)
        
        result = await self.context7.search(query, allowed_paths, scar_weight)
        return _serialize(result)
    
    async def route_reality_check(
        self,
        query: str,
        session_id: Optional[str] = None,
        **kwargs
    ) -> dict:
        """Route reality-grounding queries to Brave Search."""
        # Get authority and intent from init stage
        init_result = get_stage_result(session_id, "init") if session_id else {}
        lane = init_result.get("lane", "SOFT")
        intent = init_result.get("intent", "explain")
        scar_weight = init_result.get("scar_weight", 0.0)
        
        should_check, reason = reality_grounding.should_reality_check(
            query, lane, intent, scar_weight
        )
        
        if should_check is False:
            return {
                "status": "SEAL",
                "verdict": "SEAL",
                "source": "local_memory",
                "reason": reason,
                "note": "Query handled by internal models/knowledge."
            }
        
        # Call Brave (True or None default to True for proactive grounding)
        result = await self.brave.search(query, intent, scar_weight)
        return _serialize(result)

# Singleton Bridge instance for external gateways
_ROUTER = None

def get_bridge_router():
    global _ROUTER
    if not _ROUTER:
        _ROUTER = BridgeRouter()
    return _ROUTER

async def bridge_context_docs_router(**kwargs) -> dict:
    """Gateway for context_docs tool."""
    return await get_bridge_router().route_context_docs(**kwargs)

async def bridge_reality_check_router(**kwargs) -> dict:
    """Gateway for reality_check tool."""
    return await get_bridge_router().route_reality_check(**kwargs)


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


async def bridge_trinity_loop_router(query: str, session_id: Optional[str] = None, **kwargs) -> dict:
    """
    Trinity Metabolic Loop: Complete AGI→ASI→APEX pipeline.

    Runs the full constitutional governance cycle:
    1. Init (if no session_id)
    2. AGI Genius: sense → think → reason
    3. ASI Act: evidence → empathize → evaluate
    4. APEX Judge: eureka → decide → proof
    5. Vault Seal

    Returns unified result with verdict.
    """
    if not ENGINES_AVAILABLE:
        return _FALLBACK_RESPONSE

    import time
    start_time = time.time()

    # Step 1: Initialize session if needed
    if not session_id:
        init_result = await bridge_init_router(action="init", query=query)
        session_id = init_result.get("session_id", f"trinity_{int(time.time())}")
    else:
        init_result = get_stage_result(session_id, "init") or {}

    # NEW: Phase B Gating (v53.2.2)
    lane = init_result.get("lane", "SOFT")
    scar_weight = init_result.get("scar_weight", 0.0)
    
    allowed, reason = validate_trinity_request(query, lane, scar_weight)
    if not allowed:
        return {
            "verdict": "VOID" if lane != "CRISIS" else "888_HOLD",
            "status": "VOID" if lane != "CRISIS" else "888_HOLD",
            "reason": f"Validation Gate: {reason}",
            "session_id": session_id,
            "lane": lane,
            "scar_weight": scar_weight
        }

    loop_results = []

    # Step 2: AGI Genius Pipeline
    agi_result = await bridge_agi_router(
        action="full",
        query=query,
        session_id=session_id
    )
    loop_results.append({"stage": "agi", "result": agi_result})

    if isinstance(agi_result, dict) and agi_result.get("verdict") == "VOID":
        return {
            "verdict": "VOID",
            "reason": f"AGI veto: {agi_result.get('reason', 'Unknown')}",
            "session_id": session_id,
            "stages": loop_results
        }

    # Step 3: ASI Act Pipeline
    asi_result = await bridge_asi_router(
        action="full",
        text=agi_result.get("reasoning", str(agi_result)),
        query=query,
        session_id=session_id,
        agi_context=agi_result
    )
    loop_results.append({"stage": "asi", "result": asi_result})

    if isinstance(asi_result, dict) and asi_result.get("verdict") == "VOID":
        return {
            "verdict": "VOID",
            "reason": f"ASI veto: {asi_result.get('reason', 'Ethical violation')}",
            "session_id": session_id,
            "stages": loop_results
        }

    # Step 4: APEX Judge Pipeline
    apex_result = await bridge_apex_router(
        action="full",
        query=query,
        response=str(agi_result),
        session_id=session_id,
        reasoning=agi_result.get("reasoning", ""),
        safety_evaluation=asi_result
    )
    loop_results.append({"stage": "apex", "result": apex_result})

    final_verdict = apex_result.get("verdict", "SEAL") if isinstance(apex_result, dict) else "SEAL"

    # Step 5: Vault Seal (only if SEAL verdict)
    if final_verdict == "SEAL":
        vault_result = await bridge_vault_router(
            action="seal",
            session_id=session_id,
            verdict=final_verdict,
            query=query,
            response=str(apex_result),
            decision_data={
                "agi": agi_result,
                "asi": asi_result,
                "apex": apex_result
            }
        )
        loop_results.append({"stage": "vault", "result": vault_result})

    duration = time.time() - start_time

    return {
        "verdict": final_verdict,
        "session_id": session_id,
        "query": query,
        "reasoning": apex_result.get("reasoning", "") if isinstance(apex_result, dict) else str(apex_result),
        "stages": loop_results,
        "duration_ms": duration * 1000,
        "loops_completed": len(loop_results)
    }

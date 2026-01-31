"""
codebase/mcp/tools/canonical_trinity.py

The 7 Canonical Tools of arifOS (AAA Framework)
Implementing the "Trinity of Constitutional Verdicts" and metabolic cycle.

LLM-Agnostic: Works with Claude, ChatGPT, Gemini, Cursor, Codex, any MCP client.
All handlers normalize input to handle diverse calling conventions (args wrapping, etc.)

Scope:
1. _init_ (Gate)
2. _agi_ (Mind)
3. _asi_ (Heart)
4. _apex_ (Soul)
5. _vault_ (Seal)
6. _trinity_ (Loop)
7. _reality_ (Ground)
"""

import uuid
from typing import Any, Dict, Optional, List
from codebase.kernel import get_kernel_manager
from codebase.mcp.core.bridge import (
    bridge_trinity_loop_router,
    bridge_reality_check_router,
    bridge_atlas_router,
)


def _normalize_kwargs(kwargs: dict) -> dict:
    """
    LLM-agnostic input normalizer.
    Some MCP clients (ChatGPT) wrap tool parameters under 'args' or 'kwargs'.
    This unwraps them so handlers receive flat keyword arguments.
    """
    # ChatGPT wraps params under 'args' dict
    if "args" in kwargs and isinstance(kwargs["args"], dict):
        unwrapped = kwargs.pop("args")
        unwrapped.update(kwargs)
        return unwrapped
    # Some clients wrap under 'kwargs'
    if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
        unwrapped = kwargs.pop("kwargs")
        unwrapped.update(kwargs)
        return unwrapped
    return kwargs


# ==============================================================================
# 1. _init_ (The Gate)
# ==============================================================================
async def mcp_init(
    action: str = "init", query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    _init_: The 7-Step Thermodynamic Ignition Sequence.
    """
    import importlib

    kwargs = _normalize_kwargs(kwargs)
    # Extract known params that may have been wrapped
    action = kwargs.pop("action", action) or "init"
    query = kwargs.pop("query", query) or ""
    session_id = kwargs.pop("session_id", session_id)

    # Dynamic import to handle '000_init' directory name (invalid Python identifier)
    module = importlib.import_module("codebase.init.000_init.mcp_bridge")
    mcp_000_init = module.mcp_000_init

    # Only pass parameters that mcp_000_init accepts
    result = await mcp_000_init(
        action=action,
        query=query,
        session_id=session_id,
        authority_token=kwargs.get("authority_token", ""),
        context=kwargs.get("context"),
    )

    # Stamp every _init_ response with the arifOS motto
    result["motto"] = "DITEMPA, BUKAN DIBERI \U0001f9e0\U0001f525\U0001f48e"
    result["root_key"] = "TOY_MODE"

    return result


# ==============================================================================
# 2. _agi_ (The Mind)
# ==============================================================================
async def mcp_agi(
    action: str = "full", query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    _agi_: Mind Engine (Δ) - Logic, Sense, Think, Map.
    """
    kwargs = _normalize_kwargs(kwargs)
    action = kwargs.pop("action", action) or "full"
    query = kwargs.pop("query", query) or ""
    session_id = kwargs.pop("session_id", session_id)

    kernel = get_kernel_manager().get_agi()
    return await kernel.execute(action, {"query": query, "session_id": session_id, **kwargs})


# ==============================================================================
# 3. _asi_ (The Heart)
# ==============================================================================
async def mcp_asi(
    action: str = "full",
    query: str = "",
    reasoning: str = "",
    session_id: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    _asi_: Heart Engine (Ω) - Empathy, Safety, Alignment.
    """
    kwargs = _normalize_kwargs(kwargs)
    action = kwargs.pop("action", action) or "full"
    query = kwargs.pop("query", query) or ""
    reasoning = kwargs.pop("reasoning", reasoning) or ""
    session_id = kwargs.pop("session_id", session_id)

    kernel = get_kernel_manager().get_asi()
    context = kwargs.pop("context", {})
    if reasoning:
        context["reasoning"] = reasoning

    return await kernel.execute(
        action,
        {"text": query, "query": query, "session_id": session_id, "context": context, **kwargs},
    )


# ==============================================================================
# 4. _apex_ (The Soul)
# ==============================================================================
async def mcp_apex(
    action: str = "full",
    query: str = "",
    response: str = "",
    verdict: str = "",
    session_id: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    _apex_: Soul Engine (Ψ) - Judgment, Verdict, Proof.
    """
    kwargs = _normalize_kwargs(kwargs)
    action = kwargs.pop("action", action) or "full"
    query = kwargs.pop("query", query) or ""
    response = kwargs.pop("response", response) or ""
    verdict = kwargs.pop("verdict", verdict) or ""
    session_id = kwargs.pop("session_id", session_id)

    kernel = get_kernel_manager().get_apex()
    kwargs["pre_verdict"] = verdict

    return await kernel.execute(
        action, {"query": query, "response": response, "session_id": session_id, **kwargs}
    )


# ==============================================================================
# 5. _vault_ (The Seal)
# ==============================================================================
async def mcp_vault(
    action: str = "seal",
    verdict: str = "SEAL",
    decision_data: Optional[Dict] = None,
    target: str = "seal",
    session_id: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    _vault_: Immutable Ledger - Seal, List, Read.
    """
    kwargs = _normalize_kwargs(kwargs)
    action = kwargs.pop("action", action) or "seal"
    verdict = kwargs.pop("verdict", verdict) or "SEAL"
    session_id = kwargs.pop("session_id", session_id)
    if not session_id:
        session_id = str(uuid.uuid4())

    kernel = get_kernel_manager().get_apex()
    return await kernel.execute(
        "seal" if action == "seal" else action,
        {
            "session_id": session_id,
            "verdict": verdict,
            "data": decision_data,
            "target_ledger": target,
            **kwargs,
        },
    )


# ==============================================================================
# 6. _trinity_ (The Loop)
# ==============================================================================
async def mcp_trinity(
    query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    _trinity_: Full Metabolic Loop (AGI->ASI->APEX->VAULT).
    """
    kwargs = _normalize_kwargs(kwargs)
    query = kwargs.pop("query", query) or ""
    session_id = kwargs.pop("session_id", session_id)

    return await bridge_trinity_loop_router(query=query, session_id=session_id, **kwargs)


# ==============================================================================
# 7. _reality_ (The Ground)
# ==============================================================================
async def mcp_reality(
    query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    _reality_: External Fact-Checking & Grounding.
    """
    kwargs = _normalize_kwargs(kwargs)
    query = kwargs.pop("query", query) or ""
    session_id = kwargs.pop("session_id", session_id)

    if not query.strip():
        return {
            "status": "VOID",
            "verdict": "VOID",
            "reason": "Empty query — provide a question to fact-check.",
            "source": "none",
        }

    return await bridge_reality_check_router(query=query, session_id=session_id, **kwargs)

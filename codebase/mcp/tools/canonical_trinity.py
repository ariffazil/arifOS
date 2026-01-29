"""
codebase/mcp/tools/canonical_trinity.py

The 7 Canonical Tools of arifOS (AAA Framework)
Implementing the "Trinity of Constitutional Verdicts" and metabolic cycle.

Scope:
1. _init_ (Gate)
2. _agi_ (Mind)
3. _asi_ (Heart)
4. _apex_ (Soul)
5. _vault_ (Seal)
6. _trinity_ (Loop)
7. _reality_ (Ground)
"""

from typing import Any, Dict, Optional, List
from codebase.kernel import get_kernel_manager
from codebase.mcp.bridge import (
    bridge_trinity_loop_router,
    bridge_reality_check_router,
    bridge_atlas_router
)

# ==============================================================================
# 1. _init_ (The Gate)
# ==============================================================================
async def mcp_init(
    action: str = "init",
    query: str = "",
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    _init_: The 7-Step Thermodynamic Ignition Sequence.
    """
    from codebase.init.000_init.mcp_bridge import mcp_000_init
    return await mcp_000_init(
        action=action,
        query=query,
        session_id=session_id,
        **kwargs
    )

# ==============================================================================
# 2. _agi_ (The Mind)
# ==============================================================================
async def mcp_agi(
    action: str = "full",
    query: str = "",
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    _agi_: Mind Engine (Δ) - Logic, Sense, Think, Map.
    """
    kernel = get_kernel_manager().get_agi()
    return await kernel.execute(
        action, {"query": query, "session_id": session_id, **kwargs}
    )

# ==============================================================================
# 3. _asi_ (The Heart)
# ==============================================================================
async def mcp_asi(
    action: str = "full",
    query: str = "",
    reasoning: str = "",
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    _asi_: Heart Engine (Ω) - Empathy, Safety, Alignment.
    """
    kernel = get_kernel_manager().get_asi()
    # Support 'reasoning' as context if needed
    context = kwargs.get("context", {})
    if reasoning:
        context["reasoning"] = reasoning
        
    return await kernel.execute(
        action, 
        {"text": query, "query": query, "session_id": session_id, "context": context, **kwargs}
    )

# ==============================================================================
# 4. _apex_ (The Soul)
# ==============================================================================
async def mcp_apex(
    action: str = "decide",
    query: str = "",
    response: str = "",
    verdict: str = "",
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    _apex_: Soul Engine (Ψ) - Judgment, Verdict, Proof.
    """
    kernel = get_kernel_manager().get_apex()
    # If verdict is pre-supplied (e.g. wrapper), pass it
    kwargs["pre_verdict"] = verdict
    
    return await kernel.execute(
        action,
        {"query": query, "response": response, "session_id": session_id, **kwargs}
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
    **kwargs
) -> Dict[str, Any]:
    """
    _vault_: Immutable Ledger - Seal, List, Read.
    """
    kernel = get_kernel_manager().get_apex() # Vault logic currently in Apex/Kernel
    return await kernel.execute(
        "seal" if action == "seal" else action, # standardized to kernel actions
        {
            "session_id": session_id,
            "verdict": verdict,
            "data": decision_data,
            "target_ledger": target,
            **kwargs
        }
    )

# ==============================================================================
# 6. _trinity_ (The Loop)
# ==============================================================================
async def mcp_trinity(
    query: str = "",
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    _trinity_: Full Metabolic Loop (AGI->ASI->APEX->VAULT).
    """
    return await bridge_trinity_loop_router(
        query=query, 
        session_id=session_id, 
        **kwargs
    )

# ==============================================================================
# 7. _reality_ (The Ground)
# ==============================================================================
async def mcp_reality(
    query: str = "",
    session_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    _reality_: External Fact-Checking & Grounding.
    """
    return await bridge_reality_check_router(
        query=query, 
        session_id=session_id, 
        **kwargs
    )

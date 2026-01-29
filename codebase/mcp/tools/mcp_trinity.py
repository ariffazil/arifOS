"""
MCP Trinity Tools (v53.2.9)
7 Core Tools for Constitutional AI Governance

Primary Tools (v53.2.9 Naming Convention):
- _ignite_     -> Gate (000: Authority + Injection)
- _logic_      -> Mind (111-333: SENSE → THINK → REASON)
- _senses_     -> Reality (External grounding via Brave Search)
- _atlas_      -> Mapping (Knowledge topology & Context7)
- _forge_      -> Builder (444-777: EVIDENCE → EMPATHY → ACT → EUREKA)
- _audit_      -> Scanner (Pre-seal constitutional compliance)
- _decree_     -> Seal (888-999: JUDGE → PROOF → VAULT)

Legacy Aliases (Backward Compatible):
- mcp_000_init    -> _ignite_
- mcp_agi_genius  -> _logic_
- mcp_reality_check -> _senses_
- mcp_context_docs -> _atlas_
- mcp_asi_act + mcp_apex_judge -> _forge_
- [NEW]           -> _audit_
- mcp_999_vault   -> _decree_

DITEMPA BUKAN DIBERI - Forged, Not Given
v53.2.9: Consolidated to 7 canonical tools with backward compatibility
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from codebase.kernel import mcp_000_init, get_kernel_manager
from codebase.mcp.bridge import (
    bridge_trinity_loop_router,
    bridge_context_docs_router,
    bridge_reality_check_router,
    bridge_prompt_router,
)

logger = logging.getLogger(__name__)


# ============================================================================
# TOOL 1: 000_INIT (Gate)
# ============================================================================

# Re-export from kernel (already implements native init)
__all__ = [
    "mcp_000_init",
    "mcp_agi_genius",
    "mcp_asi_act",
    "mcp_apex_judge",
    "mcp_999_vault",
    "mcp_trinity_loop",
    "mcp_context_docs",
    "mcp_reality_check",
    "mcp_prompt_codec",
]


# ============================================================================
# TOOL 2: AGI_GENIUS (Mind)
# ============================================================================


async def mcp_agi_genius(
    action: str = "full",
    query: str = "",
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    AGI Genius: Mind Engine (Δ)

    Executes stages 111 (SENSE) → 222 (THINK) → 333 (REASON)

    Actions:
        - full: Complete AGI pipeline
        - sense: Parse input only
        - think: Generate hypotheses
        - reason: Build reasoning tree
        - evaluate: Quick evaluation
        - forge: Format/projection

    Floors Enforced: F2 (Truth), F4 (Clarity), F7 (Humility), F10 (Ontology), F12 (Injection)

    Args:
        action: Action to perform
        query: User query/text
        session_id: Session identifier
        context: Additional context
        **kwargs: Additional arguments

    Returns:
        Result dict with verdict, reasoning, and metrics
    """
    try:
        kernel = get_kernel_manager().get_agi()

        result = await kernel.execute(
            action, {"query": query, "session_id": session_id, "context": context or {}, **kwargs}
        )

        return result

    except Exception as e:
        logger.error(f"[AGI_GENIUS] Error: {e}")
        return {"status": "VOID", "verdict": "VOID", "session_id": session_id, "error": str(e)}


# ============================================================================
# TOOL 3: ASI_ACT (Heart)
# ============================================================================


async def mcp_asi_act(
    action: str = "full",
    text: str = "",
    query: str = "",
    session_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    ASI Act: Heart Engine (Ω)

    Executes stages 444 (EVIDENCE) → 555 (EMPATHY) → 666 (ALIGN)

    Actions:
        - full/act: Complete ASI pipeline
        - evidence: Gather supporting evidence
        - empathize: Analyze stakeholder impact
        - align: Ethical alignment check
        - evaluate: Quick evaluation

    Floors Enforced: F1 (Amanah), F5 (Peace²), F6 (Empathy), F9 (Anti-Hantu)

    Args:
        action: Action to perform
        text: Text to analyze (or use query)
        query: Alternative to text
        session_id: Session identifier
        context: Additional context
        **kwargs: Additional arguments

    Returns:
        Result dict with verdict, empathy scores, and metrics
    """
    try:
        kernel = get_kernel_manager().get_asi()

        # Support both 'text' and 'query' parameters
        input_text = text or query

        result = await kernel.execute(
            action,
            {
                "text": input_text,
                "query": input_text,
                "session_id": session_id,
                "context": context or {},
                **kwargs,
            },
        )

        return result

    except Exception as e:
        logger.error(f"[ASI_ACT] Error: {e}")
        return {"status": "VOID", "verdict": "VOID", "session_id": session_id, "error": str(e)}


# ============================================================================
# TOOL 4: APEX_JUDGE (Soul)
# ============================================================================


async def mcp_apex_judge(
    action: str = "full",
    query: str = "",
    response: str = "",
    session_id: Optional[str] = None,
    user_id: str = "anonymous",
    lane: str = "SOFT",
    agi_result: Optional[Dict[str, Any]] = None,
    asi_result: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    APEX Judge: Soul Engine (Ψ)

    Executes stages 777 (FORGE) → 888 (JUDGE) → 889 (PROOF)

    Actions:
        - full: Complete APEX pipeline (forge + judge + proof)
        - forge/eureka: Prepare response
        - judge: Render constitutional verdict
        - proof: Generate cryptographic proof

    Floors Enforced: F3 (Tri-Witness), F8 (Genius), F11 (Command Auth)

    Args:
        action: Action to perform
        query: Original query
        response: Draft response to judge
        session_id: Session identifier
        user_id: User identifier
        lane: HARD or SOFT lane
        agi_result: Result from AGI engine
        asi_result: Result from ASI engine
        **kwargs: Additional arguments

    Returns:
        Result dict with verdict, proof, and metrics
    """
    try:
        kernel = get_kernel_manager().get_apex()

        result = await kernel.execute(
            action,
            {
                "query": query,
                "response": response,
                "draft": response,  # Alias
                "session_id": session_id,
                "user_id": user_id,
                "lane": lane,
                "agi_result": agi_result,
                "asi_result": asi_result,
                **kwargs,
            },
        )

        if isinstance(result, dict):
            return result
        return {"result": str(result), "status": "SEAL"}

    except Exception as e:
        logger.error(f"[APEX_JUDGE] Error: {e}")
        return {"status": "VOID", "verdict": "VOID", "session_id": session_id, "error": str(e)}


# ============================================================================
# TOOL 5: 999_VAULT (Seal)
# ============================================================================


async def mcp_999_vault(
    action: str = "seal",
    session_id: Optional[str] = None,
    verdict: str = "SEAL",
    data: Optional[Dict[str, Any]] = None,
    init_result: Optional[Dict[str, Any]] = None,
    genius_result: Optional[Dict[str, Any]] = None,
    act_result: Optional[Dict[str, Any]] = None,
    judge_result: Optional[Dict[str, Any]] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    VAULT 999: Immutable Seal

    Executes stage 999 (SEAL) - Final immutable commitment

    Actions:
        - seal: Seal session to ledger
        - list: List sealed sessions
        - read: Read sealed entry

    Floors Enforced: F1 (Amanah - Immutability)

    Args:
        action: Action to perform
        session_id: Session identifier
        verdict: Final verdict to seal
        data: Additional data to seal
        init_result: Result from init stage
        genius_result: Result from AGI stage
        act_result: Result from ASI stage
        judge_result: Result from APEX stage
        **kwargs: Additional arguments

    Returns:
        Result dict with seal proof and status
    """
    try:
        kernel = get_kernel_manager().get_apex()

        # Build verdict_struct for sealing
        verdict_struct = judge_result or {}
        if not verdict_struct.get("verdict"):
            verdict_struct["verdict"] = verdict

        result = await kernel.execute(
            action,
            {
                "session_id": session_id,
                "verdict_struct": verdict_struct,
                "init_result": init_result,
                "agi_result": genius_result,
                "asi_result": act_result,
                "data": data,
                **kwargs,
            },
        )

        return result

    except Exception as e:
        logger.error(f"[VAULT_999] Error: {e}")
        return {"status": "ERROR", "verdict": "VOID", "session_id": session_id, "error": str(e)}


# ============================================================================
# TOOL 6: TRINITY_LOOP (Full Cycle)
# ============================================================================


async def mcp_trinity_loop(
    query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    Trinity Loop: Complete AGI→ASI→APEX pipeline in one call.
    Runs full constitutional governance cycle.
    """
    try:
        return await bridge_trinity_loop_router(query=query, session_id=session_id, **kwargs)
    except Exception as e:
        logger.error(f"[TRINITY_LOOP] Error: {e}")
        return {"status": "ERROR", "error": str(e), "session_id": session_id}


# ============================================================================
# TOOL 7: CONTEXT_DOCS (Technical Knowledge)
# ============================================================================


async def mcp_context_docs(
    query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    Context Docs: Query technical documentation (Context7).
    F11 Scope-Gated Documentation Access.
    """
    try:
        return await bridge_context_docs_router(query=query, session_id=session_id, **kwargs)
    except Exception as e:
        logger.error(f"[CONTEXT_DOCS] Error: {e}")
        return {"status": "ERROR", "error": str(e), "session_id": session_id}


# ============================================================================
# TOOL 8: REALITY_CHECK (General Knowledge)
# ============================================================================


async def mcp_reality_check(
    query: str = "", session_id: Optional[str] = None, **kwargs
) -> Dict[str, Any]:
    """
    Reality Check: General reality grounding via Brave Search.
    F7 (Humility) explicit disclosure of external data.
    """
    try:
        return await bridge_reality_check_router(query=query, session_id=session_id, **kwargs)
    except Exception as e:
        logger.error(f"[REALITY_CHECK] Error: {e}")
        return {"status": "ERROR", "error": str(e), "session_id": session_id}


# ============================================================================
# TOOL 9: PROMPT_CODEC (Intent Routing)
# ============================================================================


async def mcp_prompt_codec(action: str = "route", user_input: str = "", **kwargs) -> Dict[str, Any]:
    """
    Prompt Codec: Encode/Decode arifOS prompts and route intents.
    Actions: route (select lane), encode (constitutionalize), decode (deconstruct).
    """
    try:
        return await bridge_prompt_router(action=action, user_input=user_input, **kwargs)
    except Exception as e:
        logger.error(f"[PROMPT_CODEC] Error: {e}")
        return {"status": "ERROR", "error": str(e)}

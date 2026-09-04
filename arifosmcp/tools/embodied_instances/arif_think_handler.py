"""
Embodied arif_think MCP handler — bridges FastMCP to EmbodiedTool.run()

This handler is registered in _CANONICAL_HANDLERS["arif_think"].
When the MCP server calls it, it goes through:
    _wrap_handler() → embodied_mind_reason_handler() → ArifMindReasonEmbodied().run()

The EmbodiedTool.run() pipeline:
    preflight()  → EmbodiedDecision (SEAL/HOLD/VOID)
    execute()    → arif_think kernel
    postflight() → EmbodiedToolEnvelope + witness record

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.embodied_instances.arif_think_embodied import (
    ArifMindReasonEmbodied,
)


async def embodied_mind_reason_handler(
    mode: str = "reason",
    query: str | None = None,
    session_id: str | None = None,
    session_token: str | None = None,
    actor_id: str | None = None,
    plan_id: str | None = None,
    witness_type: str = "ai",
    ctx: Any = None,
    # Continuity / envelope fields ChatGPT + SCT path may pass
    _envelope: Any = None,
    contract_c_kwargs: dict | None = None,
) -> dict[str, Any]:
    """
    333_REASON: + reason — Symbolic reasoning kernel.

    Routes cognitive modes through LLM inference (FED-FEDERATION → Ollama → rule fallback).
    Structural modes (plan, plan_review, plan_approve, axioms) are deterministic.
    Cognitive modes (reason, reflect, verify, critique, debate, socratic) use LLM.

    L13 SOVEREIGN: plan_approve remains deterministic — LLM must never
    adjudicate sovereign approval.

    session_token: SCT from arif_init — required for ChatGPT continuity after bind.
    """
    if session_id is None and ctx is not None:
        session_id = getattr(ctx, "session_id", None)

    if actor_id is None and ctx is not None:
        actor_id = getattr(ctx, "actor_id", None)

    if session_token is None and ctx is not None:
        session_token = getattr(ctx, "session_token", None)

    # SCT resolve: if only token given, recover session_id
    if session_token and not session_id:
        try:
            from arifosmcp.runtime.act_token import resolve_standing

            st = resolve_standing(
                session_token=session_token,
                actor_id=actor_id,
                allow_store=True,
            )
            if st.valid and st.session_id:
                session_id = st.session_id
            if st.valid and st.actor_id and not actor_id:
                actor_id = st.actor_id
        except Exception:
            pass

    tool = ArifMindReasonEmbodied()

    envelope = await tool.run(
        params={
            "mode": mode,
            "query": query,
            "session_id": session_id,
            "session_token": session_token,
            "actor_id": actor_id,
            "plan_id": plan_id,
            "witness_type": witness_type,
        },
        ctx=ctx,
        actor_id=actor_id,
        session_id=session_id,
    )

    out = envelope.model_dump() if hasattr(envelope, "model_dump") else dict(envelope)
    # Echo continuity for ChatGPT / multi-call clients
    if session_token and isinstance(out, dict):
        out.setdefault("session_token", session_token)
        if session_id:
            out.setdefault("session_id", session_id)
    return out

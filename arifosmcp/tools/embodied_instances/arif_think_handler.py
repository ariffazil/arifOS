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
    actor_id: str | None = None,
    plan_id: str | None = None,
    witness_type: str = "ai",
    ctx: Any = None,
) -> dict[str, Any]:
    """
    333_REASON: + reason — Symbolic reasoning kernel.

    Routes cognitive modes through LLM inference (SEA-LION → Ollama → rule fallback).
    Structural modes (plan, plan_review, plan_approve, axioms) are deterministic.
    Cognitive modes (reason, reflect, verify, critique, debate, socratic) use LLM.

    L13 SOVEREIGN: plan_approve remains deterministic — LLM must never
    adjudicate sovereign approval.
    """
    if session_id is None and ctx is not None:
        session_id = getattr(ctx, "session_id", None)

    if actor_id is None and ctx is not None:
        actor_id = getattr(ctx, "actor_id", None)

    tool = ArifMindReasonEmbodied()

    envelope = await tool.run(
        params={
            "mode": mode,
            "query": query,
            "session_id": session_id,
            "actor_id": actor_id,
            "plan_id": plan_id,
            "witness_type": witness_type,
        },
        ctx=ctx,
        actor_id=actor_id,
        session_id=session_id,
    )

    return envelope.model_dump() if hasattr(envelope, "model_dump") else dict(envelope)

"""
Embodied arif_mind_reason MCP handler — bridges FastMCP to EmbodiedTool.run()

This handler is registered in _CANONICAL_HANDLERS["arif_mind_reason"].
When the MCP server calls it, it goes through:
    _wrap_handler() → embodied_mind_reason_handler() → ArifMindReasonEmbodied().run()

The EmbodiedTool.run() pipeline:
    preflight()  → EmbodiedDecision (SEAL/HOLD/VOID)
    execute()    → arif_mind_reason kernel
    postflight() → EmbodiedToolEnvelope + witness record

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from typing import Any

from arifosmcp.tools.embodied_instances.arif_mind_reason_embodied import (
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
    MCP handler for arif_mind_reason — routes through EmbodiedTool.run().

    Extracts session_id from ctx if not provided in params.
    The full EmbodiedToolEnvelope is returned as a dict.
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

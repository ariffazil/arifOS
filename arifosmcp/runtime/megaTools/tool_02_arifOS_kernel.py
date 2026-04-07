"""
arifosmcp/runtime/megaTools/02_arifOS_kernel.py

444_ROUTER: Primary metabolic conductor
Stage: 444_ROUTER | Trinity: DELTA/PSI | Floors: F4, F11

Modes: kernel, status
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.models import RuntimeEnvelope


async def arifOS_kernel(
    query: str | None = None,
    payload: dict[str, Any] | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: str | None = None,
    human_approval: bool = False,
    risk_tier: str = "medium",
    dry_run: bool = True,
    allow_execution: bool = False,
    caller_context: dict | None = None,
    auth_context: dict | None = None,
    debug: bool = False,
    request_id: str | None = None,
    timestamp: str | None = None,
    raw_input: str | None = None,
    ctx: Any | None = None,
    use_memory: bool = True,
    use_heart: bool = True,
    **kwargs: Any,
) -> RuntimeEnvelope:
    payload = dict(payload or {})
    payload.update(kwargs)
    if raw_input:
        payload.setdefault("query", raw_input)
    if caller_context:
        payload.setdefault("caller_context", caller_context)
    if auth_context:
        payload.setdefault("auth_context", auth_context)
    if query:
        payload.setdefault("query", query)
    if session_id:
        payload.setdefault("session_id", session_id)
    if actor_id:
        payload.setdefault("actor_id", actor_id)

    effective_query = payload.get("query") or query or raw_input or ""

    from arifosmcp.runtime.kernel_router import process_query
    from arifosmcp.runtime.models import (
        RuntimeEnvelope as _Envelope,
        Stage,
    )
    from core.shared.types import Verdict

    actor = str(payload.get("actor_id") or actor_id or "anonymous").strip().lower()
    context: dict[str, Any] = {
        "payload": payload,
        "risk_tier": risk_tier,
        "dry_run": dry_run,
        "allow_execution": allow_execution,
        "intent": intent,
        "use_memory": use_memory,
        "use_heart": use_heart,
        "debug": debug,
        "auth_context": auth_context or {},
    }

    routing_result = await process_query(
        query=effective_query,
        actor_id=actor,
        session_id=session_id,
        context=context,
    )

    # If the router already produced a RuntimeEnvelope (governed path), return it.
    tool_result = routing_result.get("tool_result")
    if isinstance(tool_result, _Envelope):
        return tool_result

    # Governance-blocked — wrap as RuntimeEnvelope VOID.
    if not routing_result.get("ok", True) or routing_result.get("governance_block"):
        return _Envelope(
            ok=False,
            tool="arifos.route",
            canonical_tool_name="arifos.route",
            stage=Stage.ROUTER_444.value,
            verdict=Verdict.VOID,
            session_id=session_id,
            detail=routing_result.get("audit_note", "Governance block"),
        )

    # Informational / governance-passed — return SEAL envelope.
    return _Envelope(
        ok=True,
        tool="arifos.route",
        canonical_tool_name="arifos.route",
        stage=Stage.ROUTER_444.value,
        verdict=Verdict.SEAL,
        session_id=session_id,
        detail=routing_result.get("note") or routing_result.get("audit_note"),
    )

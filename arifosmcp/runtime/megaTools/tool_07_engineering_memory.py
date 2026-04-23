"""
arifosmcp/runtime/megaTools/07_engineering_memory.py

555_MEMORY: Governed autonomous engineering and vector memory
Stage: 555_MEMORY | Trinity: OMEGA Ω | Floors: F10, F11, F2

Modes: engineer, vector_query, vector_store, vector_forget, generate, query
"""

from __future__ import annotations

from typing import Any

from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict
from arifosmcp.runtime.tools_internal import engineering_memory_dispatch_impl


async def engineering_memory(
    mode: str | None = None,
    payload: dict[str, Any] | None = None,
    query: str | None = None,
    session_id: str | None = None,
    actor_id: str | None = None,
    declared_name: str | None = None,
    intent: Any | None = None,
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
) -> RuntimeEnvelope:
    from arifosmcp.runtime.tools_hardened_dispatch import HARDENED_DISPATCH_MAP

    payload = dict(payload or {})
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
    if intent:
        payload.setdefault("intent", intent)
    if human_approval:
        payload.setdefault("human_approval", human_approval)

    # ─── DISPATCH OVERRIDE CHECK ───
    if "engineering_memory" in HARDENED_DISPATCH_MAP:
        if mode is None:
            mode = "engineer"
        res_dict = await HARDENED_DISPATCH_MAP["engineering_memory"](mode=mode, payload=payload)
        
        from arifosmcp.runtime.models import VerdictCode
        from arifosmcp.runtime.verdict_wrapper import forge_verdict
        
        return forge_verdict(
            tool_id="arifos_memory",
            canonical_tool_name="arifos_memory",
            stage=res_dict.get("stage", "555_MEMORY"),
            payload=res_dict.get("payload", {}),
            session_id=session_id,
            override_code=VerdictCode(res_dict.get("verdict").value)
            if hasattr(res_dict.get("verdict"), "value")
            else VerdictCode.SABAR,
            message=res_dict.get("payload", {}).get("note", "Memory operation processed."),
        )

    resolved_payload = dict(payload or {})
    return await engineering_memory_dispatch_impl(
        mode=mode,
        payload=resolved_payload,
        auth_context=resolved_payload.get("auth_context", auth_context),
        risk_tier=resolved_payload.get("risk_tier", risk_tier),
        dry_run=bool(resolved_payload.get("dry_run", dry_run)),
        ctx=ctx,
    )

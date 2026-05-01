"""
arifos/runtime/megaTools/02_arifos_kernel.py

444_KERNEL: Primary metabolic conductor
Stage: 444_KERNEL | Trinity: DELTA/PSI | Floors: F4, F11

Modes: kernel, status

Now delegates to unified KERNEL rCore (kernel_core.py).
The internal implementation uses INPUT → ORCHESTRATE → OUTPUT stages.
"""

from __future__ import annotations

from typing import Any

from arifos.runtime.models import RuntimeEnvelope


async def arifos_kernel(
    query: str | None = None,
    mode: str | None = None,
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
) -> RuntimeEnvelope:
    """
    KERNEL rCore entry point.

    Now delegates to unified kernel_core.execute() for INPUT → ORCHESTRATE → OUTPUT pipeline.
    Maintains backward compatibility with existing call signatures.
    """
    # Use unified KERNEL rCore
    from arifos.runtime.kernel_core import kernel_execute
    from arifos.runtime.models import Stage

    # Normalize inputs for kernel_core
    if raw_input and not query:
        query = raw_input

    result = await kernel_execute(
        query=query,
        session_id=session_id,
        actor_id=actor_id,
        intent=intent,
        auth_context=auth_context,
        risk_tier=risk_tier,
        dry_run=dry_run,
        allow_execution=allow_execution,
        caller_context=caller_context,
        payload=payload,
        use_memory=use_memory,
        use_heart=use_heart,
        debug=debug,
    )

    # Return as RuntimeEnvelope if needed
    if isinstance(result, RuntimeEnvelope):
        return result

    # Build envelope from result dict
    from core.shared.types import Verdict

    ok = result.get("ok", True)
    tool_name = result.get("tool", "arifos_kernel")

    return RuntimeEnvelope(
        ok=ok,
        tool=tool_name,
        canonical_tool_name="arifos_kernel",
        stage=Stage.ROUTER_444.value,
        verdict=Verdict.SEAL if ok else Verdict.VOID,
        session_id=session_id,
        payload=result,
    )

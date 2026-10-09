"""
Streamable HTTP Dialect Adapter — primary remote.
"""

from __future__ import annotations

import uuid
from typing import Any

from arifosmcp.transport.canonical_envelope import (
    AirlockResult,
    CanonicalEnvelope,
    _build_split_session_state,
    _classify_method,
)
from arifosmcp.transport.errors import TransportFaultCode, build_transport_error_envelope

CANARY_TOOLS = frozenset(
    {
        "arif_ping",
        "arif_conformance_report",
        "arif_version_echo",
        "arif_schema_echo",
        "arif_transport_echo",
        "arif_initialize_probe",
        "arif_init",
        "arif_os_attest",
    }
)


def _exposed_tool_universe() -> frozenset[str] | None:
    """Names the live public wire surface will serve, or None if unresolved.

    None means "cannot tell", and callers must then behave exactly as before
    rather than invent a naming verdict from an absent answer.
    """
    try:
        from arifosmcp.runtime.public_surface import public_tool_names_for_mode

        return frozenset(public_tool_names_for_mode())
    except Exception:
        return None


def _tool_call_name(method: str, params: Any) -> str:
    if method == "tools/call" and isinstance(params, dict):
        name = params.get("name")
        if isinstance(name, str) and name:
            return name
    return method


def _tool_call_args(params: Any) -> dict[str, Any]:
    if isinstance(params, dict) and "arguments" in params:
        arguments = params.get("arguments")
        return arguments if isinstance(arguments, dict) else {}
    return params if isinstance(params, dict) else {}


def streamable_http_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    Parse Streamable HTTP requests.
    Checks headers, protocol version, optional session ID, origin safety metadata.
    """
    trace_id = uuid.uuid4().hex[:16]
    method = request.get("method", "initialize")
    params = request.get("params", {})
    tool_name = _tool_call_name(method, params)
    tool_args = _tool_call_args(params)

    # 2026-10-04 heal (kernel-heal-ledger-2026-10-04.md D1): a call carrying a
    # kernel-minted session (session_id + act_v1 session_token in tool args)
    # proves the arif_init bootstrap already happened — that token is minted
    # only there. Treat it as bound so arg-carrying clients resolve consistently
    # across verbs: arif_memory/arif_think already resolve session from args and
    # passed this gate, while read-class arif_observe was rejected on the same
    # session (traces 2f20814f6f954228, 5950012b6cfc4d9f). The gate stays
    # lifecycle-only: full token validation remains downstream in the kernel
    # pipeline, exactly as it does for the verbs that resolve args today.
    args_session_bound = bool(
        str(tool_args.get("session_id") or "").strip()
        and str(tool_args.get("session_token") or "").startswith("act_v1.")
    )

    # Enforce lifecycle gate: no normal operations before valid initialize/initialized exchange
    mcp_session_id = request.get("_session_id") or request.get("mcp_session_id") or ""
    protocol_version = request.get("protocol_version", "2025-11-25")
    is_stateless = protocol_version == "2026-07-28"

    # A name that is not on the live public surface is a NAMING fault, not a
    # session fault. Gating it here answered legacy names (arif_session_init,
    # still taught by our own docs and scripts/init_live_demo.py) with
    # ARIF_SESSION_NOT_FOUND, which reads as "bootstrap requires the state
    # bootstrap is supposed to create" — an external auditor drew exactly that
    # conclusion on 2026-10-01. Unexposed names now fall through to dispatch,
    # which already answers "Unknown tool": the correct class, and one that
    # needs no session state to discover.
    exposed = _exposed_tool_universe()
    gate_applies_to_name = exposed is None or tool_name in exposed

    # Stateless MCP 2026-07-28: no session gate — every request is self-contained.
    # Tools/call, resources/list, etc. carry _meta with clientInfo and capabilities.
    # Skip the legacy lifecycle gate for stateless calls.
    if not is_stateless and gate_applies_to_name and (
        method
        not in (
            "initialize",
            "notifications/initialized",
            "ping",
            "tools/list",
            "resources/list",
            "prompts/list",
        )
        and tool_name not in CANARY_TOOLS
        and not mcp_session_id
        and not args_session_bound
    ):
        # Build a diagnostic error that tells the caller exactly how to fix it
        hint = (
            f"arif_init(mode='init', actor_id='{request.get('actor', '<your-actor-id>')}')"
            if tool_name not in ("arif_init", "arif_ping")
            else "Ensure the MCP session ID is propagated from the initial 'initialize' handshake."
        )
        return AirlockResult(
            transport_error=build_transport_error_envelope(
                TransportFaultCode.ARIF_SESSION_NOT_FOUND,
                # Scoped to THIS call on purpose: only read-class verbs are
                # blocked pre-session under ARIF_AIRLOCK_MODE=partial_enforce,
                # so claiming "all remote operations" was measurably false.
                "A bound session is required for this call. "
                f"Call {hint} first, then pass the returned session_id "
                "as the mcp-session-id header on subsequent requests.",
                transport="streamable_http",
                request_id=request.get("id"),
                trace_id=trace_id,
                next_probe="arif_init",
            ),
            envelope=None,
            dialect_used="streamable_http",
            trace_id=trace_id,
        )

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=request.get("actor", "anonymous"),
        intent=tool_name,
        evidence={},
        authority={},
        action_class=_classify_method(tool_name),
        reversibility="irreversible" not in tool_name.lower(),
        session_state=_build_split_session_state(
            request,
            mcp_session_id=mcp_session_id,
            protocol_version=request.get("protocol_version", "2025-11-25"),
        ),
        protocol_version=request.get("protocol_version", "2025-11-25"),
        transport="streamable_http",
        tool_name=tool_name,
        tool_args=tool_args,
        client_info=request.get("client_info", {"name": "streamable-http", "version": "1.0"}),
        dialect="streamable_http",
    )
    return AirlockResult(
        transport_error=None,
        envelope=envelope,
        dialect_used="streamable_http",
        trace_id=trace_id,
    )

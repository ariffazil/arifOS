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
    
    # Enforce lifecycle gate: no normal operations before valid initialize/initialized exchange
    mcp_session_id = request.get("_session_id") or request.get("mcp_session_id") or ""
    
    # If the method is not lifecycle/discovery, verify we have a session ID
    if (
        method not in ("initialize", "notifications/initialized", "ping", "tools/list", "resources/list", "prompts/list")
        and tool_name not in CANARY_TOOLS
        and not mcp_session_id
    ):
        return AirlockResult(
            transport_error=build_transport_error_envelope(
                TransportFaultCode.ARIF_SESSION_NOT_FOUND,
                "Session ID is required for all remote operations.",
                transport="streamable_http",
                request_id=request.get("id"),
                trace_id=trace_id,
            ),
            envelope=None,
            dialect_used="streamable_http",
            trace_id=trace_id,
        )

    tool_args = _tool_call_args(params)
    
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

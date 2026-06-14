"""
Raw JSON-RPC 2.0 Dialect Adapter — fallback.
"""
from __future__ import annotations

import uuid
from typing import Any
from arifosmcp.transport.canonical_envelope import (
    CanonicalEnvelope,
    ActionClass,
    _classify_method,
    _build_split_session_state,
)
from arifosmcp.transport.errors import build_transport_error_envelope, TransportFaultCode
from arifosmcp.transport.canonical_envelope import AirlockResult

def raw_jsonrpc_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    Accept bare JSON-RPC request bodies.
    Normalize broken/unknown dialects into structured ARIF_* errors instead of silent fallthrough.
    """
    trace_id = uuid.uuid4().hex[:16]
    method = request.get("method", "unknown")
    params = request.get("params", {})

    if not method or method == "unknown":
        return AirlockResult(
            transport_error=build_transport_error_envelope(
                TransportFaultCode.ARIF_TRANSPORT_DIALECT_MISMATCH,
                "JSON-RPC method is missing or unknown.",
                transport="raw_jsonrpc",
                request_id=request.get("id"),
                trace_id=trace_id,
            ),
            envelope=None,
            dialect_used="raw_jsonrpc",
            trace_id=trace_id,
        )

    # Check for dialect mismatch if dialect key is provided but unsupported
    dialect = request.get("dialect")
    if dialect and dialect not in ("raw_jsonrpc", "fastmcp", "openai_agents", "claude", "chatgpt", "stdio"):
        return AirlockResult(
            transport_error=build_transport_error_envelope(
                TransportFaultCode.ARIF_TRANSPORT_DIALECT_MISMATCH,
                f"Unsupported dialect: {dialect}",
                transport="raw_jsonrpc",
                request_id=request.get("id"),
                trace_id=trace_id,
            ),
            envelope=None,
            dialect_used="raw_jsonrpc",
            trace_id=trace_id,
        )

    if isinstance(params, dict):
        tool_args = params
    elif isinstance(params, list):
        tool_args = {"args": params}
    else:
        tool_args = {}

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=request.get("actor", "anonymous"),
        intent=method,
        evidence={},
        authority={},
        action_class=_classify_method(method),
        reversibility="irreversible" not in method.lower(),
        session_state=_build_split_session_state(
            request,
            protocol_version="2025-11-25",
            extra_transport={"jsonrpc_id": request.get("id")},
        ),
        protocol_version="2025-11-25",
        transport="stdio" if "stdio" in str(request.get("_transport", "")) else "http",
        tool_name=method,
        tool_args=tool_args,
        client_info=request.get("client_info", {"name": "raw-jsonrpc", "version": "0.0"}),
        dialect="raw_jsonrpc",
    )
    return AirlockResult(
        transport_error=None,
        envelope=envelope,
        dialect_used="raw_jsonrpc",
        trace_id=trace_id,
    )

"""
ARIF Transport Airlock v0.1.

All raw client dialects are normalized into CanonicalEnvelope before the kernel
or governance pipeline sees them.
"""

from __future__ import annotations

import hashlib
import json
import logging
import uuid
from collections.abc import Callable
from copy import deepcopy
from typing import Any

from arifosmcp.transport.canonical_envelope import (
    ActionClass,
    AirlockResult,
    CanonicalEnvelope,
    _build_split_session_state,
    _classify_method,
)
from arifosmcp.transport.dialects.raw_jsonrpc import raw_jsonrpc_adapter
from arifosmcp.transport.dialects.stdio import stdio_adapter
from arifosmcp.transport.dialects.streamable_http import streamable_http_adapter
from arifosmcp.transport.errors import arif_error

log = logging.getLogger("arifos.airlock")

DialectHandler = Callable[[dict[str, Any]], AirlockResult]
DIALECT_REGISTRY: dict[str, DialectHandler] = {}
READ_LIKE_ACTIONS = frozenset({ActionClass.PROBE, ActionClass.READ, ActionClass.QUERY})

AIRLOCK_METRICS: dict[str, Any] = {
    "total_requests": 0,
    "normalized_ok": 0,
    "transport_errors": 0,
    "blocked": 0,
    "shadow_would_block": 0,
    "partial_enforced": 0,
    "full_enforced": 0,
    "dialects": {},
    "error_codes": {},
    "last_trace_id": "",
    "last_error": None,
}


def register_dialect(name: str) -> Callable[[DialectHandler], DialectHandler]:
    """Decorator to register a dialect adapter."""

    def wrapper(fn: DialectHandler) -> DialectHandler:
        DIALECT_REGISTRY[name] = fn
        return fn

    return wrapper


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


@register_dialect("raw_jsonrpc")
def _raw_jsonrpc(request: dict[str, Any]) -> AirlockResult:
    return raw_jsonrpc_adapter(request)


@register_dialect("streamable_http")
def _streamable_http(request: dict[str, Any]) -> AirlockResult:
    return streamable_http_adapter(request)


@register_dialect("stdio")
def _stdio(request: dict[str, Any]) -> AirlockResult:
    return stdio_adapter(request)


@register_dialect("fastmcp")
def fastmcp_adapter(request: dict[str, Any]) -> AirlockResult:
    result = raw_jsonrpc_adapter(request)
    if result.envelope:
        result.envelope.dialect = "fastmcp"
        result.envelope.client_info = {
            "name": "fastmcp",
            "version": str(request.get("fastmcp_version", "unknown")),
        }
    return result


@register_dialect("openai_agents")
def openai_agents_adapter(request: dict[str, Any]) -> AirlockResult:
    trace_id = uuid.uuid4().hex[:16]
    inner = request.get("params", {})
    if isinstance(inner, dict) and "input" in inner:
        nested = inner.get("input")
        inner = nested if isinstance(nested, dict) else inner
    method = inner.get("method", request.get("method", "unknown")) if isinstance(inner, dict) else "unknown"
    params = inner.get("params", request.get("params", {})) if isinstance(inner, dict) else {}
    tool_name = _tool_call_name(method, params)

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=str(request.get("actor") or request.get("user_id") or "anonymous"),
        intent=tool_name,
        evidence={},
        authority={},
        action_class=_classify_method(tool_name),
        reversibility="irreversible" not in tool_name.lower(),
        session_state=_build_split_session_state(
            request,
            protocol_version=str(request.get("protocol_version", "2025-11-25")),
            extra_transport={"trace_id": str(request.get("trace_id", ""))},
        ),
        protocol_version=str(request.get("protocol_version", "2025-11-25")),
        transport="streamable_http",
        tool_name=tool_name,
        tool_args=_tool_call_args(params),
        client_info=request.get("client_info", {"name": "openai-agents-sdk", "version": "0.0"}),
        dialect="openai_agents",
    )
    return AirlockResult(None, envelope, "openai_agents", trace_id)


@register_dialect("claude")
def claude_adapter(request: dict[str, Any]) -> AirlockResult:
    trace_id = uuid.uuid4().hex[:16]
    method = str(request.get("method", "unknown"))
    params = request.get("params", {})
    tool_name = _tool_call_name(method, params)
    protocol_version = str(request.get("protocol_version", "2025-11-25"))

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=str(request.get("actor", "anonymous")),
        intent=tool_name,
        evidence={},
        authority={"auth_type": request.get("auth_type", "bearer")},
        action_class=_classify_method(tool_name),
        reversibility="irreversible" not in tool_name.lower(),
        session_state=_build_split_session_state(
            request,
            mcp_session_id=request.get("session_id"),
            protocol_version=protocol_version,
        ),
        protocol_version=protocol_version,
        transport="streamable_http",
        tool_name=tool_name,
        tool_args=_tool_call_args(params),
        client_info=request.get("client_info", {"name": "claude", "version": "unknown"}),
        dialect="claude",
    )
    return AirlockResult(None, envelope, "claude", trace_id)


@register_dialect("chatgpt")
def chatgpt_adapter(request: dict[str, Any]) -> AirlockResult:
    trace_id = uuid.uuid4().hex[:16]
    method = str(request.get("method", "initialize"))
    params = request.get("params", {})
    tool_name = _tool_call_name(method, params)
    protocol_version = str(request.get("protocol_version", "2025-11-25"))

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=str(request.get("actor", "anonymous")),
        intent=tool_name,
        evidence={},
        authority={},
        action_class=_classify_method(tool_name),
        reversibility="irreversible" not in tool_name.lower(),
        session_state=_build_split_session_state(request, protocol_version=protocol_version),
        protocol_version=protocol_version,
        transport="streamable_http",
        tool_name=tool_name,
        tool_args=_tool_call_args(params),
        client_info=request.get("client_info", {"name": "chatgpt", "version": "unknown"}),
        dialect="chatgpt",
    )
    return AirlockResult(None, envelope, "chatgpt", trace_id)


def _bump_metric(bucket: str, key: str) -> None:
    counts = AIRLOCK_METRICS.setdefault(bucket, {})
    counts[key] = counts.get(key, 0) + 1


def record_airlock_result(result: AirlockResult, *, mode: str, blocked: bool = False) -> None:
    """Record lightweight in-process Airlock edge telemetry."""
    AIRLOCK_METRICS["total_requests"] += 1
    AIRLOCK_METRICS["last_trace_id"] = result.trace_id
    _bump_metric("dialects", result.dialect_used or "unknown")

    if result.transport_error:
        AIRLOCK_METRICS["transport_errors"] += 1
        error_data = result.transport_error.get("error", {}).get("data", {})
        code = error_data.get("code") or "UNKNOWN"
        AIRLOCK_METRICS["last_error"] = {"code": code, "trace_id": result.trace_id}
        _bump_metric("error_codes", code)
    else:
        AIRLOCK_METRICS["normalized_ok"] += 1

    if blocked:
        AIRLOCK_METRICS["blocked"] += 1
    if mode == "shadow" and result.transport_error:
        AIRLOCK_METRICS["shadow_would_block"] += 1
    elif mode in ("partial_enforce", "partial"):
        AIRLOCK_METRICS["partial_enforced"] += 1
    elif mode == "enforce":
        AIRLOCK_METRICS["full_enforced"] += 1


def get_airlock_metrics() -> dict[str, Any]:
    """Return a stable snapshot for conformance reporting."""
    snapshot = deepcopy(AIRLOCK_METRICS)
    total = snapshot.get("total_requests", 0) or 0
    ok = snapshot.get("normalized_ok", 0) or 0
    snapshot["normalization_success_rate"] = round(ok / total, 4) if total else None
    return snapshot


def reset_airlock_metrics() -> None:
    """Reset Airlock metrics for focused tests."""
    AIRLOCK_METRICS.update(
        {
            "total_requests": 0,
            "normalized_ok": 0,
            "transport_errors": 0,
            "blocked": 0,
            "shadow_would_block": 0,
            "partial_enforced": 0,
            "full_enforced": 0,
            "dialects": {},
            "error_codes": {},
            "last_trace_id": "",
            "last_error": None,
        }
    )


def detect_dialect(request: dict[str, Any], transport_type: str = "http") -> str:
    """Detect which dialect adapter to use based on request shape and transport."""
    if "dialect" in request:
        return str(request["dialect"])

    client_info = request.get("client_info", {})
    if isinstance(client_info, dict):
        name = str(client_info.get("name", "")).lower()
        if "openai-agents" in name:
            return "openai_agents"
        if "chatgpt" in name or "openai" in name:
            return "chatgpt"
        if "claude" in name or "anthropic" in name:
            return "claude"
        if "fastmcp" in name:
            return "fastmcp"

    if "messages" in request:
        return "openai_agents"
    if "client_name" in request or ("tools" in request and "jsonrpc" not in request):
        return "fastmcp"
    if "payload" in request and "method" not in request:
        return "arifos_internal"

    if transport_type == "stdio":
        return "stdio"
    if transport_type in ("streamable_http", "streamable-http"):
        return "streamable_http"

    return "raw_jsonrpc"


def process_request(request: dict[str, Any], transport_type: str = "http") -> AirlockResult:
    """Main Airlock entry point for transport middleware."""
    dialect = detect_dialect(request, transport_type)
    handler = DIALECT_REGISTRY.get(dialect)

    if handler is None:
        trace_id = uuid.uuid4().hex[:16]
        return AirlockResult(
            transport_error=arif_error(
                "ARIF_TRANSPORT_MISMATCH",
                expected_shape="Standard JSON-RPC or known dialect envelope",
                received_shape=f"Dialect '{dialect}' not recognised",
                request_id=request.get("id"),
            ),
            envelope=None,
            dialect_used=dialect,
            trace_id=trace_id,
        )

    return handler(request)


def _raw_target_name(request: dict[str, Any]) -> str:
    return _tool_call_name(str(request.get("method", "unknown")), request.get("params", {}))


def should_partial_enforce(raw_request: dict[str, Any]) -> bool:
    """True for read/probe/query requests in partial enforcement mode."""
    return _classify_method(_raw_target_name(raw_request)) in READ_LIKE_ACTIONS


def preserve_raw_request(raw_request: dict[str, Any]) -> str:
    """Preserve the raw request as a deterministic audit hash."""
    try:
        serialized = json.dumps(raw_request, sort_keys=True, default=str).encode("utf-8")
    except Exception:
        serialized = str(raw_request).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()[:16]


def _preserve_extra_fields(
    envelope: CanonicalEnvelope,
    raw_request: dict[str, Any],
    standard_keys: set[str],
) -> CanonicalEnvelope:
    for key, value in raw_request.items():
        if key not in standard_keys:
            envelope.evidence.setdefault(key, value)
    return envelope


def normalize_to_canonical_envelope(raw_request: dict[str, Any], dialect: str) -> CanonicalEnvelope:
    """Normalize raw input into CanonicalEnvelope or raise ValueError."""
    trace_id = raw_request.get("trace_id") or raw_request.get("id") or uuid.uuid4().hex[:16]
    if isinstance(trace_id, int):
        trace_id = str(trace_id)

    if dialect == "arifos_internal":
        intent = str(raw_request.get("intent", ""))
        return CanonicalEnvelope(
            trace_id=trace_id,
            actor=str(raw_request.get("actor", "anonymous")),
            intent=intent,
            evidence=raw_request.get("evidence", {}),
            authority=raw_request.get("authority", {}),
            action_class=_classify_method(intent),
            reversibility="irreversible" not in intent.lower(),
            session_state=raw_request.get("session_state", {}),
            protocol_version="2025-11-25",
            transport="internal",
            tool_name=intent,
            tool_args=raw_request.get("payload", {}),
            client_info={"name": "arifos-internal", "version": "1.0"},
            dialect="arifos_internal",
        )

    result = process_request(raw_request, transport_type=dialect)
    if result.transport_error or result.envelope is None:
        raise ValueError(result.transport_error or "Airlock normalization failed")

    standard = {
        "actor",
        "client_info",
        "client_name",
        "dialect",
        "fastmcp_version",
        "id",
        "jsonrpc",
        "messages",
        "method",
        "params",
        "payload",
        "protocolVersion",
        "protocol_version",
        "session_id",
        "trace_id",
        "user_id",
    }
    return _preserve_extra_fields(result.envelope, raw_request, standard)


def validate_minimum_fields(normalized: CanonicalEnvelope) -> None:
    if not normalized:
        raise ValueError("Envelope is empty")
    if not normalized.actor:
        raise ValueError("Missing actor")
    if not normalized.intent:
        raise ValueError("Missing intent")


def classify_authority(normalized: CanonicalEnvelope) -> str:
    actor = normalized.actor.lower()
    if actor in ("888", "arif", "f13_agent"):
        normalized.authority = "SOVEREIGN"
        return "SOVEREIGN"
    if actor in ("hermes", "opencode", "openclaw", "root"):
        normalized.authority = "HIGH"
        return "HIGH"
    if actor in ("agent_tool", "mcp_client"):
        normalized.authority = "MEDIUM"
        return "MEDIUM"
    normalized.authority = "LOW"
    return "LOW"


def classify_reversibility(normalized: CanonicalEnvelope) -> str:
    intent = normalized.intent.lower()
    irreversible_intents = [
        "delete",
        "remove_user",
        "drop_table",
        "destroy",
        "format_disk",
        "wipe",
        "purge",
        "reset_system",
        "expunge_logs",
        "terminate_process",
        "kill_service",
        "shutdown_host",
        "reboot_server",
    ]
    if any(token in intent for token in irreversible_intents):
        normalized.reversibility = "IRREVERSIBLE"
        return "IRREVERSIBLE"

    conditional_intents = [
        "write",
        "update",
        "patch",
        "modify",
        "edit",
        "set_parameter",
        "configure",
        "install",
        "uninstall",
        "upgrade",
        "downgrade",
        "start",
    ]
    if any(token in intent for token in conditional_intents):
        normalized.reversibility = "CONDITIONAL"
        return "CONDITIONAL"

    normalized.reversibility = "REVERSIBLE"
    return "REVERSIBLE"


def refuse_with_888_hold(normalized: CanonicalEnvelope, trace: str) -> dict[str, Any]:
    return {
        "status": "HOLD",
        "verdict": "888_HOLD_REQUIRED",
        "trace_id": normalized.trace_id,
        "preserved_trace": trace,
        "nine_signal": {"F1_AMANAH": True},
        "recommendation": "AWAIT_SOVEREIGN_VETO",
        "engineering_law": "Transport Airlock v0.1: preserve flow, gate irreversible side effects.",
        "reason": f"Action {normalized.intent} requested by {normalized.actor} requires human confirmation hold.",
        "envelope": normalized.to_dict(),
    }


def route_to_kernel(normalized: CanonicalEnvelope, trace: str) -> dict[str, Any]:
    return {
        "status": "OK",
        "verdict": "PROCEED_TO_KERNEL",
        "trace_id": normalized.trace_id,
        "preserved_trace": trace,
        "envelope": normalized.to_dict(),
        "engineering_law": "Transport Airlock v0.1: routing normalized CanonicalEnvelope to the kernel.",
    }


def enter_airlock(raw_request: dict[str, Any]) -> dict[str, Any]:
    """Canonical Airlock rule: preserve, detect, normalize, classify, gate."""
    trace = preserve_raw_request(raw_request)
    dialect = detect_dialect(raw_request)
    normalized = normalize_to_canonical_envelope(raw_request, dialect)

    validate_minimum_fields(normalized)
    classify_authority(normalized)
    classify_reversibility(normalized)

    if normalized.requires_hold:
        return refuse_with_888_hold(normalized, trace)

    return route_to_kernel(normalized, trace)


def normalize_response(dialect: str, kernel_result: dict[str, Any]) -> dict[str, Any]:
    """Shape the kernel response back to the client dialect."""
    return kernel_result


def handle(request: dict[str, Any], transport_type: str = "http") -> AirlockResult:
    """Alias for process_request to match entrypoint contract."""
    return process_request(request, transport_type)


class AirlockASGIMiddleware:
    """ASGI middleware for ARIF_AIRLOCK_MODE=off|shadow|partial_enforce|enforce."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        import os as _os

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        airlock_mode = _os.getenv("ARIF_AIRLOCK_MODE", "shadow").lower().strip()
        if "/mcp" not in path or airlock_mode == "off":
            await self.app(scope, receive, send)
            return

        body_chunks = []
        more_body = True
        while more_body:
            message = await receive()
            if message["type"] == "http.request":
                body_chunks.append(message.get("body", b""))
                more_body = message.get("more_body", False)

        body = b"".join(body_chunks)
        body_sent = False

        async def _receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.request", "body": b"", "more_body": False}

        try:
            rpc_data = json.loads(body) if body else {}
        except Exception:
            rpc_data = {}

        if not isinstance(rpc_data, dict):
            await self.app(scope, _receive, send)
            return

        headers_dict = dict(scope.get("headers", []))
        mcp_session_id = ""
        protocol_version = "2025-11-25"
        for key, value in headers_dict.items():
            key_lower = key.lower()
            if key_lower in (b"mcp-session-id", b"x-mcp-session-id"):
                mcp_session_id = value.decode("utf-8")
            elif key_lower in (b"mcp-protocol-version", b"x-mcp-protocol-version"):
                protocol_version = value.decode("utf-8")

        if mcp_session_id:
            rpc_data["_session_id"] = mcp_session_id
        rpc_data["protocol_version"] = protocol_version
        rpc_data["_transport"] = "http"

        airlock_res = process_request(rpc_data, transport_type="streamable_http")

        if airlock_mode == "shadow":
            record_airlock_result(airlock_res, mode=airlock_mode)
            if airlock_res.transport_error:
                log.warning(
                    "Airlock SHADOW error: trace_id=%s error=%s",
                    airlock_res.trace_id,
                    airlock_res.transport_error,
                )
            else:
                log.info(
                    "Airlock SHADOW success: trace_id=%s tool=%s",
                    airlock_res.trace_id,
                    airlock_res.envelope.tool_name if airlock_res.envelope else "N/A",
                )
            if airlock_res.envelope:
                scope["airlock_envelope"] = airlock_res.envelope
            await self.app(scope, _receive, send)
            return

        if airlock_mode in ("partial_enforce", "partial"):
            block_request = bool(airlock_res.transport_error and should_partial_enforce(rpc_data))
            record_airlock_result(airlock_res, mode="partial_enforce", blocked=block_request)
            if block_request:
                await self._send_error(send, airlock_res.transport_error, b"partial-block")
                return
            if airlock_res.envelope:
                scope["airlock_envelope"] = airlock_res.envelope
            await self.app(scope, _receive, send)
            return

        if airlock_mode == "enforce":
            if airlock_res.transport_error:
                record_airlock_result(airlock_res, mode=airlock_mode, blocked=True)
                await self._send_error(send, airlock_res.transport_error, b"block")
                return
            scope["airlock_envelope"] = airlock_res.envelope
            record_airlock_result(airlock_res, mode=airlock_mode)
            await self.app(scope, _receive, send)
            return

        await self.app(scope, _receive, send)

    async def _send_error(self, send, error: dict[str, Any] | None, marker: bytes) -> None:
        error_body = json.dumps(error or arif_error("ARIF_ENVELOPE_MISSING")).encode("utf-8")
        await send(
            {
                "type": "http.response.start",
                "status": 200,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"x-arifos-airlock", marker),
                ],
            }
        )
        await send({"type": "http.response.body", "body": error_body})


__all__ = [
    "process_request",
    "handle",
    "enter_airlock",
    "AirlockASGIMiddleware",
    "detect_dialect",
    "normalize_response",
    "register_dialect",
    "DIALECT_REGISTRY",
    "AirlockResult",
    "CanonicalEnvelope",
    "ActionClass",
    "preserve_raw_request",
    "normalize_to_canonical_envelope",
    "validate_minimum_fields",
    "classify_authority",
    "classify_reversibility",
    "refuse_with_888_hold",
    "route_to_kernel",
    "get_airlock_metrics",
    "reset_airlock_metrics",
    "record_airlock_result",
    "should_partial_enforce",
]

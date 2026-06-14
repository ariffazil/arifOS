"""
ARIF Transport Airlock v0.1
═══════════════════════════

The sovereign MCP gateway-kernel with transport adapters.

Accepts any client dialect → normalizes into CanonicalEnvelope → passes to kernel.
The kernel never sees client dialects. It sees only canonical transactions.

Architecture:
  Client (ChatGPT, Claude, FastMCP, stdio, raw JSON-RPC, SSE)
      │
      ▼
  Transport Airlock
      ├── canary/ (ping, schema_echo, version, probe — no auth)
      ├── dialect detection (header sniffing, transport type)
      ├── normalization into CanonicalEnvelope
      └── structured error wrapping (ARIF_*, never bare -32602)
      │
      ▼
  arifOS Kernel (000→111→222→333→444→555→666→777→888→999)
      │
      ▼
  Response Normalizer (per-dialect response shaping)
      │
      ▼
  Client

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Any, Callable

from .canonical_envelope import (
    CanonicalEnvelope,
    AirlockResult,
    ActionClass,
    new_envelope,
)
from .errors import arif_error

log = logging.getLogger("arifos.airlock")

# ── Dialect Adapter Registry ────────────────────────────────────────────────

DialectHandler = Callable[[dict[str, Any]], AirlockResult]

DIALECT_REGISTRY: dict[str, DialectHandler] = {}


def register_dialect(name: str):
    """Decorator to register a dialect adapter."""
    def wrapper(fn: DialectHandler) -> DialectHandler:
        DIALECT_REGISTRY[name] = fn
        return fn
    return wrapper


# ── Built-in Dialect Adapters ───────────────────────────────────────────────

@register_dialect("raw_jsonrpc")
def raw_jsonrpc_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    Raw JSON-RPC 2.0 dialect.
    Expects: {jsonrpc, method, params, id}
    Normalizes into: tool_name=method, tool_args=params
    """
    trace_id = uuid.uuid4().hex[:16]
    method = request.get("method", "unknown")
    params = request.get("params", {})

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
        session_state={"jsonrpc_id": request.get("id")},
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


@register_dialect("fastmcp")
def fastmcp_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    FastMCP dialect (JSON-RPC with FastMCP-specific headers).
    Same structure as raw JSON-RPC but carries FastMCP version metadata.
    """
    result = raw_jsonrpc_adapter(request)
    if result.envelope:
        result.envelope.dialect = "fastmcp"
        result.envelope.client_info = {
            "name": "fastmcp",
            "version": request.get("fastmcp_version", "unknown"),
        }
    return result


@register_dialect("openai_agents")
def openai_agents_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    OpenAI Agents SDK dialect.
    May wrap tools call in OpenAI-specific envelope.
    Extracts: method+params from nested structure.
    """
    trace_id = uuid.uuid4().hex[:16]

    # Unwrap OpenAI envelope if present
    inner = request.get("params", {})
    if "input" in inner:
        # OpenAI-hosted MCP: {input: {method, params}}
        inner = inner.get("input", inner)
    method = inner.get("method", request.get("method", "unknown"))
    params = inner.get("params", request.get("params", {}))

    tool_args = params if isinstance(params, dict) else {"args": params}

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=request.get("actor", "anonymous"),
        intent=method,
        evidence={},
        authority={},
        action_class=_classify_method(method),
        reversibility="irreversible" not in method.lower(),
        session_state={"trace_id": request.get("trace_id", "")},
        protocol_version="2025-11-25",
        transport="streamable_http",
        tool_name=method,
        tool_args=tool_args,
        client_info=request.get("client_info", {"name": "openai-agents-sdk", "version": "0.0"}),
        dialect="openai_agents",
    )
    return AirlockResult(
        transport_error=None,
        envelope=envelope,
        dialect_used="openai_agents",
        trace_id=trace_id,
    )


@register_dialect("claude")
def claude_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    Claude/Anthropic MCP dialect.
    Claude sends standard MCP initialize/tools/call format.
    May carry anthropic-version, x-api-key headers.
    """
    trace_id = uuid.uuid4().hex[:16]
    method = request.get("method", "unknown")
    params = request.get("params", {})

    tool_args = params if isinstance(params, dict) else {"args": params}

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=request.get("actor", "anonymous"),
        intent=method,
        evidence={},
        authority={"auth_type": request.get("auth_type", "bearer")},
        action_class=_classify_method(method),
        reversibility="irreversible" not in method.lower(),
        session_state={"session_id": request.get("session_id", "")},
        protocol_version=request.get("protocol_version", "2025-11-25"),
        transport="streamable_http",
        tool_name=method,
        tool_args=tool_args,
        client_info=request.get("client_info", {"name": "claude", "version": "unknown"}),
        dialect="claude",
    )
    return AirlockResult(
        transport_error=None,
        envelope=envelope,
        dialect_used="claude",
        trace_id=trace_id,
    )


@register_dialect("chatgpt")
def chatgpt_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    ChatGPT/OpenAI-hosted MCP dialect.
    ChatGPT sends MCP-compliant initialize/tools/call but
    sometimes wraps args in unexpected nesting (e.g. direct tool args
    instead of {arguments: {...}}).
    """
    trace_id = uuid.uuid4().hex[:16]
    method = request.get("method", "initialize")
    params = request.get("params", {})

    # ChatGPT sometimes sends tool_args at top level of params
    # instead of nested inside {name, arguments} structure.
    # Normalize: if params has 'name' + 'arguments', use that.
    # If params has direct keys that look like tool args, wrap.
    if "name" in params and "arguments" in params:
        tool_name = params["name"]
        tool_args = params["arguments"] if isinstance(params["arguments"], dict) else {}
    else:
        tool_name = method
        tool_args = params if isinstance(params, dict) else {}

    envelope = CanonicalEnvelope(
        trace_id=trace_id,
        actor=request.get("actor", "anonymous"),
        intent=method,
        evidence={},
        authority={},
        action_class=_classify_method(method),
        reversibility="irreversible" not in method.lower(),
        session_state={},
        protocol_version=request.get("protocol_version", "2025-11-25"),
        transport="streamable_http",
        tool_name=tool_name,
        tool_args=tool_args,
        client_info=request.get("client_info", {"name": "chatgpt", "version": "unknown"}),
        dialect="chatgpt",
    )
    return AirlockResult(
        transport_error=None,
        envelope=envelope,
        dialect_used="chatgpt",
        trace_id=trace_id,
    )


@register_dialect("stdio")
def stdio_adapter(request: dict[str, Any]) -> AirlockResult:
    """Stdio JSON-RPC (identical to raw_jsonrpc but flagged for transport)."""
    result = raw_jsonrpc_adapter(request)
    if result.envelope:
        result.envelope.transport = "stdio"
        result.envelope.dialect = "stdio"
    return result


# ── Airlock Core ────────────────────────────────────────────────────────────

def detect_dialect(request: dict[str, Any], transport_type: str = "http") -> str:
    """
    Detect which dialect adapter to use based on request shape + transport.

    Priority:
    1. Explicit dialect in request
    2. Header/transport detection
    3. Fallback to raw_jsonrpc
    """
    # Explicit override
    if "dialect" in request:
        return request["dialect"]

    # ChatGPT detected by openai-* user-agent or chatgpt context
    client_info = request.get("client_info", {})
    if isinstance(client_info, dict):
        name = client_info.get("name", "").lower()
        if "chatgpt" in name or "openai" in name:
            return "chatgpt"
        if "claude" in name or "anthropic" in name:
            return "claude"
        if "fastmcp" in name:
            return "fastmcp"
        if "openai-agents" in name:
            return "openai_agents"

    # Detect by transport
    if transport_type == "stdio":
        return "stdio"

    # Detect by method patterns
    method = request.get("method", "")
    if "fastmcp" in method:
        return "fastmcp"

    return "raw_jsonrpc"


def process_request(request: dict[str, Any], transport_type: str = "http") -> AirlockResult:
    """
    Main airlock entry point.

    Accepts a raw request from any transport:
    1. Detect dialect
    2. Normalize into CanonicalEnvelope
    3. Return result (envelope or error)
    """
    dialect = detect_dialect(request, transport_type)
    handler = DIALECT_REGISTRY.get(dialect)

    if handler is None:
        trace_id = uuid.uuid4().hex[:16]
        return AirlockResult(
            transport_error=arif_error(
                "ARIF_TRANSPORT_MISMATCH",
                expected_shape="Standard JSON-RPC or known dialect envelope",
                received_shape=f"Dialect '{dialect}' not recognised",
            ),
            envelope=None,
            dialect_used=dialect,
            trace_id=trace_id,
        )

    return handler(request)


# ── Response Normalizer ─────────────────────────────────────────────────────

def normalize_response(dialect: str, kernel_result: dict[str, Any]) -> dict[str, Any]:
    """
    Shape the kernel's response back to the client's dialect.
    Currently a pass-through — extends when client-specific formats needed.
    """
    # For now, kernel returns standard JSON. All dialects accept it.
    return kernel_result


# ── Helpers ─────────────────────────────────────────────────────────────────

def _classify_method(method: str) -> ActionClass:
    m = method.lower()
    if "ping" in m or "probe" in m or "echo" in m:
        return ActionClass.PROBE
    if "session_init" in m or "initialize" in m:
        return ActionClass.QUERY
    if "forg" in m or "execut" in m or "deploy" in m:
        return ActionClass.FORGE
    if "seal" in m or "judge" in m or "deliberate" in m:
        return ActionClass.GOVERN
    if "write" in m or "create" in m or "update" in m or "delete" in m:
        return ActionClass.IRREVERSIBLE if "delete" in m else ActionClass.MUTATE
    if "read" in m or "list" in m or "get" in m or "query" in m or "recall" in m:
        return ActionClass.READ
    return ActionClass.UNKNOWN


__all__ = [
    "process_request",
    "detect_dialect",
    "normalize_response",
    "register_dialect",
    "DIALECT_REGISTRY",
    "AirlockResult",
    "CanonicalEnvelope",
    "ActionClass",
]

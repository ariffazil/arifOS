"""
Stdio Dialect Adapter — local-trust.
"""
from __future__ import annotations

from typing import Any
from arifosmcp.transport.canonical_envelope import AirlockResult
from arifosmcp.transport.dialects.raw_jsonrpc import raw_jsonrpc_adapter

def stdio_adapter(request: dict[str, Any]) -> AirlockResult:
    """
    Stdio JSON-RPC. Identical to raw_jsonrpc but flagged for transport.
    """
    result = raw_jsonrpc_adapter(request)
    if result.envelope:
        result.envelope.transport = "stdio"
        result.envelope.dialect = "stdio"
        result.dialect_used = "stdio"
    return result

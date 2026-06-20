"""Transport dialect adapters — each normalizes one client format into CanonicalEnvelope."""

from arifosmcp.transport.dialects.raw_jsonrpc import raw_jsonrpc_adapter
from arifosmcp.transport.dialects.stdio import stdio_adapter
from arifosmcp.transport.dialects.streamable_http import streamable_http_adapter

__all__ = [
    "raw_jsonrpc_adapter",
    "streamable_http_adapter",
    "stdio_adapter",
]


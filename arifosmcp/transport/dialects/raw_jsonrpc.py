"""
Raw JSON-RPC 2.0 dialect adapter — the base layer all MCP transports share.

Handles: initialize handshake, tools/call, tools/list, notifications/initialized.
Normalizes JSON-RPC envelope differences (Claude/OpenAI/FastMCP all use JSON-RPC
but with slightly different envelope shapes).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any

from arifosmcp.transport.canonical_envelope import (
    ActionClass,
    CanonicalTransaction,
    TransportIdentity,
    TransportResult,
    TransportVerdict,
)
from arifosmcp.transport.errors import (
    AirlockError,
    AirlockErrorCode,
    AirlockStage,
    schema_mismatch,
    protocol_mismatch,
)

# ── MCP Protocol Constants ─────────────────────────────────────────────────

MCP_PROTOCOL_VERSION = "2025-06-18"
MCP_SUPPORTED_VERSIONS = ["2025-06-18", "2025-03-26", "2025-11-25"]

# Known MCP method prefixes for dialect detection
MCP_LIFECYCLE_METHODS = {"initialize", "notifications/initialized", "ping"}
MCP_TOOL_METHODS = {"tools/call", "tools/list"}
MCP_RESOURCE_METHODS = {"resources/list", "resources/read", "resources/templates/list"}
MCP_PROMPT_METHODS = {"prompts/list", "prompts/get"}


class RawJSONRPCDialect:
    """Base dialect adapter for JSON-RPC 2.0 — the shared foundation.

    All MCP transports (stdio, Streamable HTTP, SSE) use JSON-RPC 2.0.
    Claude, OpenAI, and FastMCP clients all speak JSON-RPC but may differ
    in how they structure tool call arguments. This adapter handles:
    - initialize handshake + protocol version negotiation
    - tools/call → CanonicalTransaction normalization
    - tools/list → tool discovery with search_tools support
    - Structured error responses with retryability hints
    """

    name: str = "raw_jsonrpc"
    protocol_version: str = MCP_PROTOCOL_VERSION

    # ── Lifecycle ───────────────────────────────────────────────────────────

    def handle_initialize(
        self, params: dict[str, Any], headers: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Handle MCP initialize request — protocol negotiation."""
        client_version = params.get("protocolVersion", "unknown")
        client_info = params.get("clientInfo", {})
        client_capabilities = params.get("capabilities", {})

        # Negotiate protocol version
        if client_version not in MCP_SUPPORTED_VERSIONS and client_version != "unknown":
            # Dont

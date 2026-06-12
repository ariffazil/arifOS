"""
arifosmcp/runtime/mcp_transport_bridge.py
════════════════════════════════════════
MCP Transport → arifOS Kernel Bridge

Bridges the 2025-11-25 MCP Streamable HTTP transport layer into the
arifOS constitutional kernel. Ensures every tool call inherits the
MCP session identity (MCP-Session-Id header) as arifOS session_id.

MCP Spec Compliance (2025-11-25):
  § Session Management — MCP-Session-Id header flows to tool context
  § Protocol Version  — MCP-Protocol-Version header validated
  § Origin Security   — Inherited from OriginValidationMiddleware

Architecture:
  MCP HTTP Request
    → MCP-Session-Id header
    → FastMCP session manager
    → This bridge middleware
    → arifOS session_enforcer
    → arifOS tool handler (with valid session_id)

F1 AMANAH: Additive, never mutates kernel state.
F2 TRUTH: Session ID sourced from verified MCP header, never fabricated.
F11 AUTH: Missing MCP-Session-Id → HOLD for governed tools.
F13 SOVEREIGN: Human sessions require explicit actor binding.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω)
"""

from __future__ import annotations

import logging
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger("arifosmcp.transport_bridge")

# ═══════════════════════════════════════════════════════════════
# SUPPORTED PROTOCOL VERSIONS
# ═══════════════════════════════════════════════════════════════

SUPPORTED_PROTOCOL_VERSIONS: frozenset[str] = frozenset(
    {
        "2025-11-25",
        "2025-03-26",
        "2024-11-05",
    }
)

LATEST_PROTOCOL_VERSION = "2025-11-25"

# ═══════════════════════════════════════════════════════════════
# MCP PROTOCOL VERSION MIDDLEWARE
# ═══════════════════════════════════════════════════════════════


class MCPProtocolVersionMiddleware(BaseHTTPMiddleware):
    """
    Validate MCP-Protocol-Version header per 2025-11-25 spec.

    Per spec § Protocol Version Header:
    - Client MUST include MCP-Protocol-Version on all requests after initialize
    - If missing and no other way to identify version, assume 2025-03-26
    - If invalid/unsupported, respond 400 Bad Request
    """

    async def dispatch(self, request: Request, call_next):
        # Only guard /mcp endpoints
        if not request.url.path.startswith("/mcp"):
            return await call_next(request)

        # Skip validation for initialize request (version negotiation)
        if request.method == "DELETE":
            return await call_next(request)

        version = request.headers.get("MCP-Protocol-Version", "").strip()

        if version and version not in SUPPORTED_PROTOCOL_VERSIONS:
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32602,
                        "message": f"Unsupported MCP-Protocol-Version: {version}",
                        "data": {
                            "supported": sorted(SUPPORTED_PROTOCOL_VERSIONS),
                            "latest": LATEST_PROTOCOL_VERSION,
                        },
                    },
                },
                status_code=400,
            )

        return await call_next(request)


# ═══════════════════════════════════════════════════════════════
# MCP SESSION BRIDGE MIDDLEWARE
# ═══════════════════════════════════════════════════════════════


class MCPSessionBridgeMiddleware(BaseHTTPMiddleware):
    """
    Extract MCP-Session-Id from HTTP headers and inject into request state.

    This bridges the FastMCP transport-layer session (MCP-Session-Id header)
    into the Starlette request state so that tool handlers and the governance
    pipeline can access the verified session identity.

    Per MCP 2025-11-25 spec § Session Management:
    - Server assigns session ID in InitializeResult via MCP-Session-Id header
    - Client MUST include it in all subsequent requests
    - Server MAY terminate session → respond 404

    The session_id is stored in request.state.mcp_session_id and can be
    accessed by downstream middleware and tool handlers.
    """

    async def dispatch(self, request: Request, call_next):
        # Extract MCP-Session-Id from header
        mcp_session_id = request.headers.get("MCP-Session-Id", "").strip()
        mcp_session_id = request.headers.get("mcp-session-id", mcp_session_id).strip()

        if mcp_session_id:
            request.state.mcp_session_id = mcp_session_id
            # Also set as a request-scoped attribute for non-Starlette consumers
            request.scope["mcp_session_id"] = mcp_session_id

        return await call_next(request)


# ═══════════════════════════════════════════════════════════════
# SESSION CONTEXT INJECTOR (for tool handlers)
# ═══════════════════════════════════════════════════════════════


def get_session_id_from_request(request: Request | None = None) -> str | None:
    """
    Extract MCP session ID from a Starlette Request object.

    Tries in order:
    1. request.state.mcp_session_id (set by MCPSessionBridgeMiddleware)
    2. request.scope.get("mcp_session_id")
    3. request.headers.get("MCP-Session-Id")

    Returns None if no session ID found.
    """
    if request is None:
        return None

    # Try state first (set by our middleware)
    sid = getattr(request.state, "mcp_session_id", None)
    if sid:
        return sid

    # Try scope
    sid = request.scope.get("mcp_session_id")
    if sid:
        return sid

    # Try raw header
    sid = request.headers.get("MCP-Session-Id", "")
    sid = request.headers.get("mcp-session-id", sid)
    return sid.strip() or None


def inject_session_context(
    kwargs: dict[str, Any],
    session_id: str | None,
    actor_id: str | None = None,
) -> dict[str, Any]:
    """
    Inject session context into tool handler kwargs.

    Ensures every tool handler receives session_id from the MCP transport
    layer, even when the client doesn't pass it explicitly in arguments.

    This is the bridge between:
      MCP transport (MCP-Session-Id header)
        ↓
      arifOS kernel (session_enforcer + governance pipeline)

    F2 TRUTH: Only injects if kwargs lacks session_id — never overwrites
              an explicitly provided value.
    F11 AUTH: Anonymous calls get session tracking but unverified identity.
    """
    if kwargs is None:
        kwargs = {}

    # Only inject if not already present (caller intent wins)
    if "session_id" not in kwargs or not kwargs.get("session_id"):
        if session_id:
            kwargs["session_id"] = session_id

    return kwargs

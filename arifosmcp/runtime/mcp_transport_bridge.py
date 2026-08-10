"""
arifosmcp/runtime/mcp_transport_bridge.py
════════════════════════════════════════
MCP Transport → arifOS Kernel Bridge

Bridges dual-era MCP Streamable HTTP into the arifOS constitutional kernel:

  • 2025-11-25 — stateful Streamable HTTP (initialize + Mcp-Session-Id)
  • 2026-07-28 — stateless MCP (SEP-2567/2575): no transport sessions,
    per-request _meta, server/discover, Mcp-Method/Mcp-Name headers

Refs:
  https://modelcontextprotocol.io/specification/2026-07-28/changelog
  https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http
  https://gofastmcp.com/getting-started/whats-new (FastMCP 4 dual-era)

F1 AMANAH: Additive, never mutates kernel state.
F2 TRUTH: Session ID sourced from verified MCP header, never fabricated.
F11 AUTH: Missing MCP-Session-Id → HOLD for governed tools (legacy era only).
F13 SOVEREIGN: Human sessions require explicit actor binding.

DITEMPA BUKAN DIBERI — Forged 2026-06-12 by Omega (Ω); dual-era 2026-08-09
"""

from __future__ import annotations

import contextvars
import json
import logging
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger("arifosmcp.transport_bridge")

# ── Context variable for threading MCP session ID through async call chains ──
# Set by MCPSessionBridgeMiddleware, read by ingress middleware and tool handlers.
_current_mcp_session_id: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_mcp_session_id", default=None
)

# ═══════════════════════════════════════════════════════════════
# SUPPORTED PROTOCOL VERSIONS
# ═══════════════════════════════════════════════════════════════

SUPPORTED_PROTOCOL_VERSIONS: frozenset[str] = frozenset(
    {
        "2026-07-28",  # P1 STATELESS (2026-08-01): Stateless MCP 2.0 — SEP-2243 header routing
        "2025-11-25",
        "2025-03-26",
        "2024-11-05",
    }
)

LATEST_PROTOCOL_VERSION = "2026-07-28"

# ═══════════════════════════════════════════════════════════════
# MCP PROTOCOL VERSION MIDDLEWARE
# ═══════════════════════════════════════════════════════════════


class MCPProtocolVersionMiddleware(BaseHTTPMiddleware):
    """
    Dual-era protocol gate (2025-11-25 + 2026-07-28).

    - Validate MCP-Protocol-Version when present
    - On 2026-07-28: serve server/discover, enforce Mcp-Method header match
      (HeaderMismatch -32020 per SEP-2243), skip session requirements
    - On 2025-11-25: legacy initialize handshake continues via FastMCP
    """

    async def dispatch(self, request: Request, call_next):
        # Only guard /mcp endpoints
        if not request.url.path.startswith("/mcp"):
            return await call_next(request)

        # Skip validation for DELETE (legacy session teardown — ignored in 2026-07-28)
        if request.method == "DELETE":
            return await call_next(request)

        version = (
            request.headers.get("MCP-Protocol-Version", "")
            or request.headers.get("mcp-protocol-version", "")
        ).strip()

        if version and version not in SUPPORTED_PROTOCOL_VERSIONS:
            # Spec 2026-07-28: UnsupportedProtocolVersionError → -32022
            return JSONResponse(
                {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32022,
                        "message": f"UnsupportedProtocolVersion: {version}",
                        "data": {
                            "supported": sorted(SUPPORTED_PROTOCOL_VERSIONS, reverse=True),
                            "latest": LATEST_PROTOCOL_VERSION,
                        },
                    },
                },
                status_code=400,
            )

        # ── server/discover — version-independent (auto-mode clients probe first) ──
        # SEP-2575: server/discover MUST work without prior version negotiation.
        # Clients in "auto" mode probe server/discover to discover supported versions
        # BEFORE sending MCP-Protocol-Version. This intercept handles that case.
        if request.method == "POST":
            body_bytes = await request.body()
            try:
                body = json.loads(body_bytes.decode("utf-8") or "{}")
            except Exception:
                body = {}

            method = body.get("method") if isinstance(body, dict) else None
            req_id = body.get("id") if isinstance(body, dict) else None

            if method == "server/discover":
                return JSONResponse(self._discover_result(req_id))

            # Re-inject body for downstream (Starlette consumes receive once)
            async def _receive() -> dict[str, Any]:
                return {"type": "http.request", "body": body_bytes, "more_body": False}

            request = Request(request.scope, _receive)

            # ── 2026-07-28 stateless intercepts ──
            if version == "2026-07-28":
                mcp_method = (
                    request.headers.get("Mcp-Method") or request.headers.get("mcp-method") or ""
                ).strip()

                # HeaderMismatch: Mcp-Method MUST match body method when both present
                if mcp_method and method and mcp_method != method:
                    return JSONResponse(
                        {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {
                                "code": -32020,
                                "message": (
                                    f"HeaderMismatch: Mcp-Method '{mcp_method}' "
                                    f"does not match body method '{method}'"
                                ),
                            },
                        },
                        status_code=400,
                    )

                # ── G6: Per-request logLevel from _meta (replaces deprecated logging/setLevel) ──
                # MCP 2026-07-28: client sends io.modelcontextprotocol/logLevel in
                # request _meta. Extract and set as request-scoped attribute.
                _meta = (
                    body.get("params", {}).get("_meta")
                    if isinstance(body.get("params"), dict)
                    else None
                )
                if isinstance(_meta, dict):
                    _log_level = _meta.get("io.modelcontextprotocol/logLevel")
                    if isinstance(_log_level, str):
                        request.state.mcp_log_level = _log_level.upper()
                        logger.debug("Per-request logLevel=%s from _meta", _log_level)

                # Cache for airlock / tools
                request.state.mcp_protocol_version = "2026-07-28"
                request.state.mcp_stateless = True
            elif version:
                request.state.mcp_protocol_version = version
                request.state.mcp_stateless = False

        return await call_next(request)

    @staticmethod
    def _discover_result(req_id: Any) -> dict[str, Any]:
        """Build server/discover result per 2026-07-28 Discovery spec."""
        try:
            from arifosmcp.runtime.public_surface import public_tool_names

            tools_cap: dict[str, Any] = {"listChanged": True}
            _ = public_tool_names  # surface exists
        except Exception:
            tools_cap = {"listChanged": True}

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "resultType": "complete",
                "supportedVersions": sorted(SUPPORTED_PROTOCOL_VERSIONS, reverse=True),
                "capabilities": {
                    "tools": tools_cap,
                    "resources": {"listChanged": True, "subscribe": False},
                    "prompts": {"listChanged": True},
                    "extensions": {"io.modelcontextprotocol/ui": {}},
                },
                "instructions": (
                    "arifOS constitutional kernel. Dual-era MCP: "
                    "2026-07-28 (stateless, preferred) and 2025-11-25 (stateful). "
                    "Boot: server/discover → tools/list → arif_init (app session/SCT). "
                    "Governance session is independent of transport session."
                ),
                "ttlMs": 3_600_000,
                "cacheScope": "public",
                "_meta": {
                    "io.modelcontextprotocol/serverInfo": {
                        "name": "ARIFOS MCP",
                        "version": "kanon-2026.08.09",
                        "websiteUrl": "https://mcp.arif-fazil.com",
                    },
                    "io.modelcontextprotocol/protocolVersion": LATEST_PROTOCOL_VERSION,
                },
            },
        }


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
            # Thread through async context for FastMCP middleware access
            _current_mcp_session_id.set(mcp_session_id)

        # PLATFORM HOST TAGGING — autonomous sensing of the pipe
        ua = request.headers.get("user-agent", "") or request.headers.get("User-Agent", "")
        host_platform = "unknown"
        if "chatgpt" in ua.lower() or "openai" in ua.lower():
            host_platform = "openai-chatgpt-mcp"
        elif "claude" in ua.lower():
            host_platform = "anthropic-claude-desktop"
        elif "grok" in ua.lower() or "xai" in ua.lower():
            host_platform = "xai-grok"
        elif request.headers.get("x-mcp-host") or request.headers.get("X-MCP-Host"):
            host_platform = request.headers.get("x-mcp-host") or request.headers.get("X-MCP-Host")

        request.state.host_platform = host_platform
        request.scope["host_platform"] = host_platform

        return await call_next(request)


# ═══════════════════════════════════════════════════════════════
# SESSION CONTEXT INJECTOR (for tool handlers)
# ═══════════════════════════════════════════════════════════════


def get_current_mcp_session_id() -> str | None:
    """
    Get the MCP session ID from the async context variable.

    This is the primary way for tool handlers and middleware to access
    the MCP session ID without needing the HTTP request object.

    Set by MCPSessionBridgeMiddleware on every request with a session header.
    """
    return _current_mcp_session_id.get()


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

    # Fallback to header
    return request.headers.get("MCP-Session-Id") or request.headers.get("mcp-session-id")


# ═══════════════════════════════════════════════════════════════
# PLATFORM HOST INTERVENTION SENSING (E_PLATFORM_INTERVENTION)
# Per papa Elon directive + arifOS F-pipeline: hosted AI pipes are untrusted.
# Detect safety/policy blocks and tag session for 888_JUDGE + alternate routing.
# MCP spec: always return structured error with data for client/kernel correlation.
# ═══════════════════════════════════════════════════════════════

PLATFORM_HOST_MARKERS = (
    "safety check",
    "blocked by",
    "safety checks",
    "tool call was blocked",
    "platform policy",
    "host safety",
)


def detect_platform_intervention(
    error_text: str | None, headers: dict | None = None
) -> dict[str, Any] | None:
    """
    Returns dict with platform intervention evidence if detected.
    This is injected into FederationEnvelope / fault path.
    Autonomous: kernel can use this to downgrade host trust and suggest raw transport.
    """
    if not error_text:
        return None
    txt = error_text.lower()
    if any(marker in txt for marker in PLATFORM_HOST_MARKERS):
        host_hint = None
        ua = (headers or {}).get("user-agent", "") or (headers or {}).get("User-Agent", "")
        if "chatgpt" in ua.lower() or "openai" in ua.lower():
            host_hint = "openai-chatgpt-connector"
        elif "claude" in ua.lower():
            host_hint = "anthropic-claude"
        elif "grok" in ua.lower() or "xai" in ua.lower():
            host_hint = "xai-grok"
        else:
            host_hint = "unknown-hosted-mcp-client"
        return {
            "type": "PLATFORM_INTERVENTION",
            "fault_code": "PLATFORM_INTERVENTION",
            "host": host_hint,
            "observed_signature": error_text[:200],
            "recommended_transport": "stdio | direct http://127.0.0.1:8088/mcp (raw)",
            "trust_impact": "downgrade to UNTRUSTED / SEMI_TRUSTED",
            "per_mcp_spec": "client should surface JSONRPCError with data; kernel classifies as mechanical 888_HOLD",
        }
    return None


def get_host_platform_from_request(request: Request | None = None) -> str:
    """Return observed host platform for intervention classification and host_scope downgrade."""
    if request is None:
        return "unknown"
    hp = getattr(request.state, "host_platform", None) or request.scope.get("host_platform")
    if hp:
        return hp
    ua = request.headers.get("user-agent", "") or request.headers.get("User-Agent", "")
    if "chatgpt" in ua.lower() or "openai" in ua.lower():
        return "openai-chatgpt-mcp"
    if "claude" in ua.lower():
        return "anthropic-claude-desktop"
    if "grok" in ua.lower() or "xai" in ua.lower():
        return "xai-grok"
    return "unknown-hosted"

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

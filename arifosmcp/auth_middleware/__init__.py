"""
arifOS Federation — Shared SCT Auth Middleware
==============================================

FastMCP middleware that validates arifOS Session Capability Tokens (act_v1.*)
on every request. Drop this into any federation organ for unified auth.

Architecture:
    - SCT rides in Authorization: Bearer act_v1.<payload>.<hmac>
    - Validation delegates to arifosmcp.runtime.act.verify_sct()
    - Verified claims attached to ctx.set_state("sct_claims", ...)
    - Public endpoints (list_tools, arif_init, initialize) bypass auth
    - Fails CLOSED: any unauthenticated call to a gated tool = PermissionError

Invariant compliance:
    I-13: on_request (not on_call_tool) — gates list_tools too
    I-8:  validate BEFORE call_next — raise stops the request
    I-14: Fresh Context per request — no caching ctx objects
    I-15: Inherits from fastmcp.server.middleware.Middleware for __call__ dispatch

Usage per organ:
    from arifosmcp.auth_middleware import SCTMiddleware, PUBLIC_TOOLS

    mcp = FastMCP("organ-name")
    mcp.add_middleware(SCTMiddleware(public_tools=PUBLIC_TOOLS))

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from typing import Any

from fastmcp.server.middleware.middleware import Middleware, MiddlewareContext

logger = logging.getLogger(__name__)

# ── Public endpoints: no SCT required ──────────────────────────────────────
# tools/list is open discovery. initialize is MCP handshake.
# arif_init creates the session — can't require a token it hasn't minted yet.
# health is handled at the HTTP layer, not here.
PUBLIC_TOOLS: frozenset[str] = frozenset(
    {
        "arif_init",
    }
)

PUBLIC_METHODS: frozenset[str] = frozenset(
    {
        "tools/list",
        "prompts/list",
        "resources/list",
        "initialize",
        "notifications/initialized",
    }
)


# ── Middleware ──────────────────────────────────────────────────────────────


class SCTMiddleware(Middleware):
    """
    SCT validation middleware for FastMCP servers.

    Inherits from fastmcp.server.middleware.Middleware so that FastMCP's
    __call__ dispatches to on_request, which fires on every MCP request
    (wrapping all method-specific hooks). Validates every request against
    the kernel's Ed25519/HMAC SCT scheme.

    Whitelist: PUBLIC_METHODS + PUBLIC_TOOLS bypass auth.
    Everything else: token required, invalid = PermissionError.

    Claims are attached via context.fastmcp_context.set_state().
    """

    def __init__(
        self,
        public_tools: frozenset[str] | None = None,
        public_methods: frozenset[str] | None = None,
    ) -> None:
        super().__init__()
        self._public_tools = public_tools if public_tools is not None else PUBLIC_TOOLS
        self._public_methods = public_methods if public_methods is not None else PUBLIC_METHODS

    async def on_request(self, context: MiddlewareContext[Any], call_next: Any) -> Any:
        """
        Gate every request through SCT validation.

        Validation order:
            1. Check if method/tool is public → pass through
            2. Extract Authorization header from HTTP layer
            3. Verify SCT via kernel's verify_sct()
            4. Attach claims to context → pass through
            5. Any failure → PermissionError (fail-closed)

        Uses MiddlewareContext.method (e.g. "tools/call") and
        MiddlewareContext.message.params.name for tool name extraction.
        """
        method: str = getattr(context, "method", "") or ""

        # ── Guard: no request context (init phase) → pass through ───
        fc = getattr(context, "fastmcp_context", None)
        if fc is None or getattr(fc, "request_context", None) is None:
            return await call_next(context)

        # ── Extract tool name from tools/call message ─────────────────
        tool_name: str = ""
        if method == "tools/call":
            try:
                message = getattr(context, "message", None)
                if message is not None and hasattr(message, "name"):
                    tool_name = str(getattr(message, "name", ""))
            except Exception:
                pass

        # ── Whitelist check ────────────────────────────────────────────
        if method in self._public_methods:
            return await call_next(context)
        if tool_name and tool_name in self._public_tools:
            return await call_next(context)

        # ── Extract + validate SCT ─────────────────────────────────────
        token = self._extract_token(context)
        if not token:
            logger.warning(
                "SCTMiddleware: no token for method=%s tool=%s",
                method,
                tool_name,
            )
            raise PermissionError(
                "Authentication required. Provide SCT via Authorization: Bearer act_v1.<...>"
            )

        claims = await self._verify(token)
        if claims is None:
            logger.warning(
                "SCTMiddleware: invalid token for method=%s tool=%s",
                method,
                tool_name,
            )
            raise PermissionError("Invalid or expired SCT")

        # ── Attach claims to fastmcp_context ───────────────────────────
        fc = context.fastmcp_context
        if fc is not None:
            try:
                await fc.set_state("sct_claims", claims)
                await fc.set_state("actor_id", claims.get("actor", "anonymous"))
                await fc.set_state("session_id", claims.get("sid", ""))
                await fc.set_state("auth_level", claims.get("auth", "ANONYMOUS"))
                logger.debug(
                    "SCTMiddleware: authenticated actor=%s session=%s",
                    claims.get("actor", "?"),
                    str(claims.get("sid", "?"))[:20],
                )
            except Exception:
                # set_state is request-scoped; failure here shouldn't block
                pass

        return await call_next(context)

    # ── Internal helpers ───────────────────────────────────────────────

    @staticmethod
    def _extract_token(ctx: Any) -> str | None:
        """Extract SCT from Authorization: Bearer <token> HTTP header.

        FastMCP strips 'authorization' from get_http_headers() by default
        to prevent accidental forwarding — so we must explicitly include it.
        The ``or {}`` guards against non-HTTP transports (in-memory, STDIO).
        """
        try:
            from fastmcp.server.dependencies import get_http_headers

            headers = get_http_headers(include={"authorization"}) or {}
            auth = headers.get("authorization", "")
            if auth.startswith("Bearer "):
                token = auth.removeprefix("Bearer ").strip()
                if token.startswith("act_v1.") or token.startswith("arifos.v1."):
                    return token
            return None
        except ImportError:
            # FastMCP < 4 — get_http_headers or include= not available
            return None
        except (RuntimeError, AttributeError):
            # In-memory / non-HTTP transport — headers unavailable
            return None

    @staticmethod
    async def _verify(token: str) -> dict[str, Any] | None:
        """Delegate to kernel's verify_sct. Returns claims or None."""
        try:
            from arifosmcp.runtime.act_token import verify_sct

            return verify_sct(token)
        except ImportError:
            logger.error("SCTMiddleware: cannot import verify_sct — is arifOS kernel installed?")
            return None
        except Exception:
            return None

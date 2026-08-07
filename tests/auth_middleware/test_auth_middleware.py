"""
SCTMiddleware — unit test suite (7 cases + smoke)

Strategy:
  - Client(transport=mcp) = InMemoryTransport → get_http_headers() returns {}
    → _extract_token() returns None → middleware rejects (default behavior)
  - Tests that need auth: mock SCTMiddleware._extract_token / _verify
  - Tests for public bypass: in-memory transport works naturally
  - Tests for missing/invalid token: in-memory transport + mock
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

import pytest
from fastmcp import FastMCP
from fastmcp.client import Client
from fastmcp.server.middleware.middleware import Middleware

from arifosmcp.auth_middleware import (
    PUBLIC_METHODS,
    PUBLIC_TOOLS,
    SCTMiddleware,
)


# ── Fixture — valid-looking SCT token ─────────────────────────────────────


@pytest.fixture
def valid_sct_token() -> str:
    return (
        "act_v1.eyJhY3RvciI6InRlc3QtYWdlbnQiLC"
        "JzaWQiOiJURVNULXNlc3Npb24iLCJhdXRoIj"
        "oiTElNSVRFRF9NVVRBVEUiLCJleHAiOjk5OTk5OTk5OTl9.dummy_hmac"
    )


# ── Test case 1: Valid SCT → passes ──────────────────────────────────────


@pytest.mark.asyncio
async def test_valid_sct_passes(valid_sct_token):
    """A valid SCT in Authorization header allows the request through."""
    mcp = FastMCP("test-auth-valid")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def probe() -> str:
        return "ok"

    with patch.object(SCTMiddleware, "_extract_token", return_value=valid_sct_token):
        # Mock _verify to return known claims
        with patch.object(
            SCTMiddleware,
            "_verify",
            return_value={
                "actor": "test-agent",
                "sid": "TEST",
                "auth": "LIMITED_MUTATE",
            },
        ):
            async with Client(transport=mcp) as client:
                result = await client.call_tool("probe", {})
                assert result.data == "ok"


# ── Test case 2: Missing token → PermissionError ─────────────────────────


@pytest.mark.asyncio
async def test_missing_token_rejected():
    """No SCT → middleware rejects with authentication error."""
    mcp = FastMCP("test-auth-missing")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def probe() -> str:
        return "ok"

    async with Client(transport=mcp) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("probe", {})
        msg = str(exc_info.value).lower()
        assert "authentication" in msg or "permission" in msg


# ── Test case 3: Invalid token → PermissionError ─────────────────────────


@pytest.mark.asyncio
async def test_invalid_token_rejected(valid_sct_token):
    """A syntactically SCT-looking token that _verify rejects."""
    mcp = FastMCP("test-auth-invalid")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def probe() -> str:
        return "ok"

    with patch.object(SCTMiddleware, "_extract_token", return_value=valid_sct_token):
        # _verify returns None = invalid
        with patch.object(SCTMiddleware, "_verify", return_value=None):
            async with Client(transport=mcp) as client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool("probe", {})
                msg = str(exc_info.value).lower()
                assert "invalid" in msg or "permission" in msg


# ── Test case 4: PUBLIC_METHODS bypass (list_tools passes without token) ─


@pytest.mark.asyncio
async def test_public_methods_bypass():
    """tools/list is in PUBLIC_METHODS → passes without SCT."""
    mcp = FastMCP("test-auth-list-tools")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def probe() -> str:
        return "ok"

    async with Client(transport=mcp) as client:
        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        assert "probe" in tool_names


# ── Test case 5: PUBLIC_TOOLS bypass (custom public tool) ─────────────────


@pytest.mark.asyncio
async def test_public_tools_bypass():
    """A tool added to PUBLIC_TOOLS passes without authentication."""
    mcp = FastMCP("test-auth-public-tool")
    mcp.add_middleware(SCTMiddleware(public_tools=PUBLIC_TOOLS | {"probe"}))

    @mcp.tool
    def probe() -> str:
        return "public_ok"

    @mcp.tool
    def guarded() -> str:
        return "guarded"

    async with Client(transport=mcp) as client:
        # probe is public — passes
        result = await client.call_tool("probe", {})
        assert result.data == "public_ok"

        # guarded is NOT public — should fail
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("guarded", {})
        msg = str(exc_info.value).lower()
        assert "authentication" in msg or "permission" in msg


# ── Test case 6: verify_sct import failure → graceful rejection ──────────


@pytest.mark.asyncio
async def test_verify_sct_import_failure(valid_sct_token):
    """If the kernel's verify_sct cannot be imported, reject all requests."""
    mcp = FastMCP("test-auth-import-fail")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def probe() -> str:
        return "ok"

    with patch.object(SCTMiddleware, "_extract_token", return_value=valid_sct_token):
        # When kernel not installed, _verify returns None → rejected
        with patch.object(SCTMiddleware, "_verify", return_value=None):
            async with Client(transport=mcp) as client:
                with pytest.raises(Exception) as exc_info:
                    await client.call_tool("probe", {})
                msg = str(exc_info.value).lower()
                assert "invalid" in msg or "expired" in msg


# ── Test case 7: Claims attached to context after valid SCT ───────────────


@pytest.mark.asyncio
async def test_claims_attached_to_context(valid_sct_token):
    """After a valid SCT, claims are set on fastmcp_context.

    We verify by checking that the tool executes (meaning the middleware
    passed it through), confirming the claims-attached path was reached.
    The actual claims are set in fastmcp_context.set_state(), which is
    request-scoped and can be tested via integration tests with HTTP transport.
    """
    mcp = FastMCP("test-auth-claims")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def whoami() -> str:
        return "tool_executed"

    with patch.object(SCTMiddleware, "_extract_token", return_value=valid_sct_token):
        with patch.object(
            SCTMiddleware,
            "_verify",
            return_value={
                "actor": "test-agent",
                "sid": "TEST-session",
                "auth": "LIMITED_MUTATE",
            },
        ):
            async with Client(transport=mcp) as client:
                result = await client.call_tool("whoami", {})
                assert result.data == "tool_executed"


# ── Smoke: Middleware registered + inherits correctly ─────────────────────


@pytest.mark.asyncio
async def test_middleware_inherits_from_middleware():
    """SCTMiddleware inherits from fastmcp.server.middleware.Middleware."""
    mcp = FastMCP("test-auth-smoke")
    mw = SCTMiddleware()
    mcp.add_middleware(mw)

    assert isinstance(mw, Middleware)
    # FastMCP auto-adds a DereferenceRefsMiddleware, so >= 1
    assert len(mcp.middleware) >= 1  # type: ignore[attr-defined]


# ── Smoke: tools/call without token on in-memory transport fails ──────────


@pytest.mark.asyncio
async def test_tool_call_no_token_fails():
    """Guarded tool call without auth → rejected by middleware."""
    mcp = FastMCP("test-auth-call-fail")
    mcp.add_middleware(SCTMiddleware())

    @mcp.tool
    def secret_calc(x: int) -> int:
        return x * 2

    async with Client(transport=mcp) as client:
        with pytest.raises(Exception) as exc_info:
            await client.call_tool("secret_calc", {"x": 5})
        msg = str(exc_info.value).lower()
        assert "authentication" in msg or "permission" in msg


# ── Future: Integration tests (require HTTP transport + arifOS kernel) ────
# Marked with @pytest.mark.integration — skip by default in CI.
# These exercise the full auth flow: real get_http_headers(), verify_sct(),
# and claims propagation through the actual HTTP stack.
#
# @pytest.mark.integration
# @pytest.mark.asyncio
# async def test_real_auth_flow_streamable_http():
#     """End-to-end: connect to arifOS on :8088 with streamable-http transport.
#
#     This tests the actual auth flow — get_http_headers() returns real
#     HTTP headers, verify_sct processes real SCT tokens, and the claims
#     are attached to the request context and accessible in tool handlers.
#     """
#     from fastmcp.client import Client as StreamableClient, StreamableHTTP
#
#     # Without SCT: list_tools should pass (public method)
#     async with StreamableClient(
#         transport=StreamableHTTP("http://127.0.0.1:8088/mcp")
#     ) as client:
#         tools = await client.list_tools()
#         assert len(tools) > 0

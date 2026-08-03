"""
SCTMiddleware Unit Tests
========================

Tests the auth middleware decision tree in isolation.
Mocks FastMCP context, headers, and SCT verification.

Patch targets:
    - get_http_headers → fastmcp.server.dependencies.get_http_headers (local import source)
    - verify_sct → arifosmcp.runtime.sct.verify_sct (local import source)

Scenarios covered:
    1. Valid SCT → pass through
    2. Invalid SCT → PermissionError
    3. No token → PermissionError
    4. Public method (tools/list) → bypass
    5. Public tool (arif_init) → bypass
    6. No context (init phase) → bypass (I-14 guard)
    7. get_http_headers() returns None → no crash (or {} guard)
    8. get_http_headers() raises RuntimeError → captured, handled

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import sys
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ── Import the middleware under test ──────────────────────────────────────
sys.path.insert(0, "/root/arifOS")
from arifosmcp.auth_middleware import (
    PUBLIC_METHODS,
    PUBLIC_TOOLS,
    SCTMiddleware,
)


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_mock_context(
    method: str = "tools/call",
    tool_name: str = "arif_observe",
    request_context: Any = None,
):
    """Build a mock MiddlewareContext matching FastMCP 4's actual interface.

    FastMCP 4 MiddlewareContext has:
        - .method → "tools/call", "tools/list", etc.
        - .message → has .name for tools/call messages
        - .fastmcp_context → session context (set_state, etc.)
        - .request_context → None during init phase
    """
    ctx = MagicMock()
    ctx.method = method
    ctx.fastmcp_context = MagicMock()

    if request_context is None:
        rc = MagicMock()
        ctx.fastmcp_context.request_context = rc
    else:
        ctx.fastmcp_context.request_context = request_context

    # For tools/call, .message carries .name
    if method == "tools/call" and tool_name:
        ctx.message = MagicMock()
        ctx.message.name = tool_name

    ctx.fastmcp_context.set_state = AsyncMock()
    return ctx


# ── Tests ────────────────────────────────────────────────────────────────


class TestSCTMiddlewareDecisionTree:
    @pytest.mark.asyncio
    async def test_public_method_bypasses(self):
        """tools/list, initialize, etc. should bypass auth entirely."""
        mw = SCTMiddleware()
        call_next = AsyncMock()

        for method in PUBLIC_METHODS:
            ctx = _make_mock_context(method=method)
            await mw.on_request(ctx, call_next)
            call_next.assert_called_with(ctx)
            call_next.reset_mock()

    @pytest.mark.asyncio
    async def test_public_tool_bypasses(self):
        """arif_init should bypass auth even when called via tools/call."""
        mw = SCTMiddleware()
        call_next = AsyncMock()

        for tool in PUBLIC_TOOLS:
            ctx = _make_mock_context(method="tools/call", tool_name=tool)
            await mw.on_request(ctx, call_next)
            call_next.assert_called_with(ctx)
            call_next.reset_mock()

    @pytest.mark.asyncio
    async def test_no_context_bypasses(self):
        """I-14 guard: no request_context → pass through (init phase)."""
        mw = SCTMiddleware()
        call_next = AsyncMock()

        # case 1: request_context explicitly None
        ctx = _make_mock_context()
        ctx.fastmcp_context.request_context = None
        await mw.on_request(ctx, call_next)
        call_next.assert_called_with(ctx)
        call_next.reset_mock()

        # case 2: no fastmcp_context at all
        ctx2 = MagicMock()
        ctx2.fastmcp_context = None
        await mw.on_request(ctx2, call_next)
        call_next.assert_called_with(ctx2)

    @pytest.mark.asyncio
    async def test_valid_sct_passes(self):
        """Valid token → claims attached, request proceeds."""
        mw = SCTMiddleware()
        call_next = AsyncMock()
        valid_claims = {
            "sid": "SEAL-abc123",
            "actor": "test-agent",
            "auth": "LIMITED_MUTATE",
            "av": True,
        }

        with patch.object(mw, "_extract_token", return_value="sct_v1.valid.token"):
            with patch.object(mw, "_verify", return_value=valid_claims):
                ctx = _make_mock_context(method="tools/call", tool_name="arif_seal")
                await mw.on_request(ctx, call_next)

        call_next.assert_called_with(ctx)
        ctx.fastmcp_context.set_state.assert_any_call("sct_claims", valid_claims)
        ctx.fastmcp_context.set_state.assert_any_call("actor_id", "test-agent")

    @pytest.mark.asyncio
    async def test_invalid_sct_raises(self):
        """Invalid token → PermissionError, call_next never called."""
        mw = SCTMiddleware()
        call_next = AsyncMock()

        with patch.object(mw, "_extract_token", return_value="sct_v1.bad.token"):
            with patch.object(mw, "_verify", return_value=None):
                ctx = _make_mock_context(method="tools/call", tool_name="arif_seal")
                with pytest.raises(PermissionError, match="Invalid or expired SCT"):
                    await mw.on_request(ctx, call_next)

        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_token_raises(self):
        """No token at all → PermissionError."""
        mw = SCTMiddleware()
        call_next = AsyncMock()

        with patch.object(mw, "_extract_token", return_value=None):
            ctx = _make_mock_context(method="tools/call", tool_name="arif_seal")
            with pytest.raises(PermissionError, match="Authentication required"):
                await mw.on_request(ctx, call_next)

        call_next.assert_not_called()


class TestTokenExtraction:
    def test_bearer_sct_extracted(self):
        """Bearer sct_v1.xxx → token extracted."""
        mw = SCTMiddleware()
        headers = {"authorization": "Bearer sct_v1.eyJhY3RvciI6IjMzMy1BR0kifQ.abc123"}
        with patch("fastmcp.server.dependencies.get_http_headers", return_value=headers):
            token = mw._extract_token(MagicMock())
            assert token == "sct_v1.eyJhY3RvciI6IjMzMy1BR0kifQ.abc123"

    def test_legacy_arifos_v1_extracted(self):
        """Bearer arifos.v1.xxx → token extracted."""
        mw = SCTMiddleware()
        headers = {"authorization": "Bearer arifos.v1.eyJzdWIiOiJhYmMifQ.sig"}
        with patch("fastmcp.server.dependencies.get_http_headers", return_value=headers):
            token = mw._extract_token(MagicMock())
            assert token == "arifos.v1.eyJzdWIiOiJhYmMifQ.sig"

    def test_no_auth_header_returns_none(self):
        """No Authorization header → None."""
        mw = SCTMiddleware()
        headers = {"content-type": "application/json"}
        with patch("fastmcp.server.dependencies.get_http_headers", return_value=headers):
            token = mw._extract_token(MagicMock())
            assert token is None

    def test_not_bearer_returns_none(self):
        """Basic auth, not Bearer → None."""
        mw = SCTMiddleware()
        headers = {"authorization": "Basic dXNlcjpwYXNz"}
        with patch("fastmcp.server.dependencies.get_http_headers", return_value=headers):
            token = mw._extract_token(MagicMock())
            assert token is None

    def test_non_sct_bearer_returns_none(self):
        """Bearer token that's not sct_v1 or arifos.v1 → None."""
        mw = SCTMiddleware()
        headers = {"authorization": "Bearer some-jwt-token"}
        with patch("fastmcp.server.dependencies.get_http_headers", return_value=headers):
            token = mw._extract_token(MagicMock())
            assert token is None

    def test_headers_none_returns_none(self):
        """get_http_headers() returns None → handled by or {} guard, returns None."""
        mw = SCTMiddleware()
        with patch("fastmcp.server.dependencies.get_http_headers", return_value=None):
            token = mw._extract_token(MagicMock())
            assert token is None

    def test_headers_runtime_error_returns_none(self):
        """In-memory transport raises RuntimeError → handled gracefully."""
        mw = SCTMiddleware()

        def _raise(*args, **kwargs):
            raise RuntimeError("get_http_headers only works with HTTP transports")

        with patch("fastmcp.server.dependencies.get_http_headers", side_effect=_raise):
            # Currently raises — this documents the gap in the middleware.
            # Fix: wrap get_http_headers() in try/except inside _extract_token.
            token = mw._extract_token(MagicMock())
            assert token is None


class TestSCTVerification:
    @pytest.mark.asyncio
    async def test_valid_token_returns_claims(self):
        """Valid SCT → claims dict returned."""
        mw = SCTMiddleware()
        claims = {"sid": "SEAL-xyz", "actor": "agent"}
        with patch("arifosmcp.runtime.sct.verify_sct", return_value=claims):
            result = await mw._verify("sct_v1.valid.token")
            assert result == claims

    @pytest.mark.asyncio
    async def test_invalid_token_returns_none(self):
        """Invalid SCT → None."""
        mw = SCTMiddleware()
        with patch("arifosmcp.runtime.sct.verify_sct", return_value=None):
            result = await mw._verify("sct_v1.bad.token")
            assert result is None

    @pytest.mark.asyncio
    async def test_import_error_returns_none(self):
        """verify_sct not importable → None (fail-closed)."""
        mw = SCTMiddleware()
        with patch(
            "arifosmcp.runtime.sct.verify_sct",
            side_effect=ImportError("no module"),
        ):
            result = await mw._verify("sct_v1.token")
            assert result is None


class TestPublicLists:
    def test_arif_init_is_public(self):
        assert "arif_init" in PUBLIC_TOOLS

    def test_tools_list_is_public(self):
        assert "tools/list" in PUBLIC_METHODS

    def test_initialize_is_public(self):
        assert "initialize" in PUBLIC_METHODS

    def test_arif_seal_is_not_public(self):
        assert "arif_seal" not in PUBLIC_TOOLS

    def test_tools_call_is_not_public(self):
        assert "tools/call" not in PUBLIC_METHODS

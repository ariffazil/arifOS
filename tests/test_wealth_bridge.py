"""
Test suite for arifosmcp/runtime/wealth_bridge.py — WEALTH MCP Client Bridge
════════════════════════════════════════════════════════════════════════════

Tests session management and health checks with mocked MCP server.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from arifosmcp.runtime.wealth_bridge import (
    wealth_health_check,
    reset_session,
    _extract_jsonrpc_result,
    call_wealth_tool,
)


@pytest.fixture(autouse=True)
def _reset_session() -> None:
    """Clear cached session before each test."""
    reset_session()


async def aiter_empty() -> Any:
    return
    yield  # type: ignore[unreachable]


async def aiter_lines(lines: list[str]) -> Any:
    for line in lines:
        yield line


class TestWealthHealthCheck:
    @pytest.mark.asyncio
    async def test_healthy(self) -> None:
        health_resp = MagicMock()
        health_resp.status_code = 200
        health_resp.json = MagicMock(
            return_value={"status": "healthy", "version": "test", "identity": True}
        )

        init_resp = MagicMock()
        init_resp.status_code = 200
        init_resp.headers = {"mcp-session-id": "sess-abc"}
        init_resp.aiter_lines = MagicMock(return_value=aiter_empty())

        ping_resp = MagicMock()
        ping_resp.status_code = 200
        ping_resp.json = MagicMock(return_value={"result": {}})
        ping_resp.aiter_lines = MagicMock(
            return_value=aiter_lines(['data: {"jsonrpc":"2.0","id":1,"result":{}}'])
        )

        async def mock_post(*args: Any, **kwargs: Any) -> MagicMock:
            if kwargs.get("json", {}).get("method") == "initialize":
                return init_resp
            return ping_resp

        with patch("httpx.AsyncClient") as mock_cls:
            inst = MagicMock()
            inst.get = AsyncMock(return_value=health_resp)
            inst.post = AsyncMock(side_effect=mock_post)
            inst.__aenter__ = AsyncMock(return_value=inst)
            inst.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = inst

            result = await wealth_health_check()
            assert result["status"] == "healthy"
            assert result["organ"] == "WEALTH"

    @pytest.mark.asyncio
    async def test_unhealthy(self) -> None:
        health_resp = MagicMock()
        health_resp.status_code = 500
        health_resp.json = MagicMock(return_value={"status": "unhealthy"})

        init_resp = MagicMock()
        init_resp.status_code = 200
        init_resp.headers = {"mcp-session-id": "sess-abc"}
        init_resp.aiter_lines = MagicMock(return_value=aiter_empty())

        ping_resp = MagicMock()
        ping_resp.status_code = 500
        ping_resp.aiter_lines = MagicMock(return_value=aiter_empty())

        async def mock_post(*args: Any, **kwargs: Any) -> MagicMock:
            if kwargs.get("json", {}).get("method") == "initialize":
                return init_resp
            return ping_resp

        with patch("httpx.AsyncClient") as mock_cls:
            inst = MagicMock()
            inst.get = AsyncMock(return_value=health_resp)
            inst.post = AsyncMock(side_effect=mock_post)
            inst.__aenter__ = AsyncMock(return_value=inst)
            inst.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = inst

            result = await wealth_health_check()
            assert result["status"] == "unhealthy"
            assert "tool_surface_error" in result


class TestResetSession:
    def test_clears_session(self) -> None:
        from arifosmcp.runtime import wealth_bridge

        wealth_bridge._WEALTH_SESSION_ID = "old"
        reset_session()
        assert wealth_bridge._WEALTH_SESSION_ID is None


class TestDip03ExtractJsonrpcResult:
    """IRR-DIP-AUDIT DIP-03: missing result must not become silent {}."""

    def test_present_dict_result_passthrough(self) -> None:
        out = _extract_jsonrpc_result({"jsonrpc": "2.0", "id": 1, "result": {"irr": 0.1}})
        assert out == {"irr": 0.1}
        assert "null_coercion_result" not in out

    def test_missing_result_propagates_full_envelope(self) -> None:
        parsed = {"jsonrpc": "2.0", "id": 1, "error_surface": "organ_down"}
        out = _extract_jsonrpc_result(parsed)
        assert out["null_coercion_result"] is True
        assert out["bridge_error"] == "missing_jsonrpc_result"
        assert out["error_surface"] == "organ_down"
        assert out is not parsed  # copy, not mutate caller

    def test_null_result_flagged(self) -> None:
        out = _extract_jsonrpc_result({"jsonrpc": "2.0", "id": 1, "result": None})
        assert out["null_coercion_result"] is True
        assert out["bridge_error"] == "null_jsonrpc_result"
        assert out["result"] is None

    def test_empty_dict_result_is_valid_not_coerced(self) -> None:
        """Empty {} when key exists is a real result (e.g. ping) — not DIP-03."""
        out = _extract_jsonrpc_result({"jsonrpc": "2.0", "id": 1, "result": {}})
        assert out == {}
        assert "null_coercion_result" not in out

    @pytest.mark.asyncio
    async def test_post_json_rpc_missing_result_not_silent_empty(self) -> None:
        resp = MagicMock()
        resp.status_code = 200
        resp.json = MagicMock(
            return_value={"jsonrpc": "2.0", "id": 1, "message": "swallowed_before_fix"}
        )

        with patch("httpx.AsyncClient") as mock_cls:
            inst = MagicMock()
            inst.post = AsyncMock(return_value=resp)
            inst.__aenter__ = AsyncMock(return_value=inst)
            inst.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = inst

            with patch(
                "arifosmcp.runtime.wealth_bridge._ensure_session",
                new=AsyncMock(return_value=None),
            ):
                result = await call_wealth_tool("wealth_compute_irr", {"cash_flows": [-100, 110]})

        assert result.get("null_coercion_result") is True
        assert result.get("bridge_error") == "missing_jsonrpc_result"
        assert result != {}
        assert "message" in result

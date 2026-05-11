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
        init_resp = MagicMock()
        init_resp.status_code = 200
        init_resp.headers = {"mcp-session-id": "sess-abc"}
        init_resp.aiter_lines = MagicMock(return_value=aiter_empty())

        ping_resp = MagicMock()
        ping_resp.status_code = 200
        ping_resp.aiter_lines = MagicMock(
            return_value=aiter_lines(['data: {"jsonrpc":"2.0","id":1,"result":{}}'])
        )

        async def mock_post(*args: Any, **kwargs: Any) -> MagicMock:
            if kwargs.get("json", {}).get("method") == "initialize":
                return init_resp
            return ping_resp

        with patch("httpx.AsyncClient") as mock_cls:
            inst = MagicMock()
            inst.post = AsyncMock(side_effect=mock_post)
            inst.__aenter__ = AsyncMock(return_value=inst)
            inst.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = inst

            result = await wealth_health_check()
            assert result["status"] == "healthy"
            assert result["organ"] == "WEALTH"

    @pytest.mark.asyncio
    async def test_unhealthy(self) -> None:
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
            inst.post = AsyncMock(side_effect=mock_post)
            inst.__aenter__ = AsyncMock(return_value=inst)
            inst.__aexit__ = AsyncMock(return_value=False)
            mock_cls.return_value = inst

            result = await wealth_health_check()
            assert result["status"] == "unhealthy"
            assert "error" in result


class TestResetSession:
    def test_clears_session(self) -> None:
        from arifosmcp.runtime import wealth_bridge

        wealth_bridge._WEALTH_SESSION_ID = "old"
        reset_session()
        assert wealth_bridge._WEALTH_SESSION_ID is None

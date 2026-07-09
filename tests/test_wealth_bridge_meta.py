from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from arifosmcp.runtime.wealth_bridge import call_wealth_tool, reset_session


@pytest.fixture(autouse=True)
def _reset_cached_session() -> None:
    reset_session()


@pytest.mark.asyncio
async def test_call_wealth_tool_stamps_meta_from_caller_fields() -> None:
    resp = MagicMock()
    resp.status_code = 200
    resp.json = MagicMock(return_value={"jsonrpc": "2.0", "id": 1, "result": {"ok": True}})

    captured: dict[str, Any] = {}

    async def mock_post(*args: Any, **kwargs: Any) -> MagicMock:
        captured["json"] = kwargs.get("json")
        return resp

    with patch("httpx.AsyncClient") as mock_cls:
        inst = MagicMock()
        inst.post = AsyncMock(side_effect=mock_post)
        inst.__aenter__ = AsyncMock(return_value=inst)
        inst.__aexit__ = AsyncMock(return_value=False)
        mock_cls.return_value = inst

        with patch(
            "arifosmcp.runtime.wealth_bridge._ensure_session",
            new=AsyncMock(return_value=None),
        ):
            result = await call_wealth_tool(
                "wealth_compute_irr",
                {
                    "cash_flows": [-100, 110],
                    "caller_actor_id": "arif",
                    "caller_session_id": "SEAL-1234567890abcdef",
                },
            )

    args = captured["json"]["params"]["arguments"]
    assert result == {"ok": True}
    assert args["_meta"]["actor_id"] == "arif"
    assert args["_meta"]["session_id"] == "SEAL-1234567890abcdef"
    assert "caller_actor_id" not in args
    assert "caller_session_id" not in args

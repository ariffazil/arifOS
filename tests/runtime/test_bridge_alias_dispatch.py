from __future__ import annotations

import pytest

from arifosmcp.runtime import bridge
from arifosmcp.core.enforcement.governance_engine import wrap_tool_output


@pytest.mark.asyncio
async def test_reality_check_dispatches_to_search_reality(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_search_reality(*, input=None, session_id=None, actor_id=None):
        captured["input"] = input
        captured["session_id"] = session_id
        captured["actor_id"] = actor_id
        return {"status": "SUCCESS", "query": input}

    def fake_wrap_tool_output(tool, payload):
        return {"tool": tool, "payload": payload}

    monkeypatch.setattr(bridge, "REQUIRES_SESSION", frozenset())
    # Patch the module-level import in bridge
    monkeypatch.setattr(bridge, "search_reality", fake_search_reality)
    monkeypatch.setattr("core.enforcement.governance_engine.wrap_tool_output", fake_wrap_tool_output)

    result = await bridge.call_kernel("reality_check", "session-1", {"query": "bridge query"})

    assert captured == {
        "input": "bridge query",
        "session_id": "session-1",
        "actor_id": "anonymous",
    }
    assert result["tool"] == "search_reality"
    assert result["payload"]["query"] == "bridge query"


@pytest.mark.asyncio
async def test_open_web_page_dispatches_to_ingest_evidence(monkeypatch):
    captured: dict[str, object] = {}

    async def fake_ingest_evidence(*, input=None, session_id=None, actor_id=None):
        captured["input"] = input
        captured["session_id"] = session_id
        captured["actor_id"] = actor_id
        return {"status": "SUCCESS", "url": input}

    def fake_wrap_tool_output(tool, payload):
        return {"tool": tool, "payload": payload}

    monkeypatch.setattr(bridge, "REQUIRES_SESSION", frozenset())
    # Patch the module-level import in bridge
    monkeypatch.setattr(bridge, "ingest_evidence", fake_ingest_evidence)
    monkeypatch.setattr("core.enforcement.governance_engine.wrap_tool_output", fake_wrap_tool_output)

    result = await bridge.call_kernel(
        "open_web_page",
        "session-2",
        {"url": "https://example.com", "actor_id": "operator"},
    )

    assert captured == {
        "input": "https://example.com",
        "session_id": "session-2",
        "actor_id": "operator",
    }
    assert result["tool"] == "ingest_evidence"
    assert result["payload"]["url"] == "https://example.com"


def test_wrap_tool_output_handles_missing_canonical_name():
    result = wrap_tool_output(
        None,
        {
            "verdict": "VOID",
            "failed_laws": ["F11_AUTHORITY"],
            "auth_state": "unverified",
            "error": "Authentication required",
            "stage": "444_ROUTER",
            "session_id": "test-session",
            "canonical_name": None,
        },
    )

    assert result["tool"] == "unknown_tool"
    assert result["session_id"] == "test-session"
    assert result["errors"]

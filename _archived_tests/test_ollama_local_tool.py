from __future__ import annotations

import pytest

from arifosmcp.runtime import tools as runtime_tools
from arifosmcp.runtime.models import RuntimeEnvelope, RuntimeStatus, Verdict


@pytest.mark.asyncio
async def test_ollama_local_generate_routes_payload(monkeypatch):
    captured: dict[str, object] = {}

    async def _fake_wrap_call(tool_name, stage, session_id, payload, ctx=None, caller_context=None):
        captured["tool_name"] = tool_name
        captured["session_id"] = session_id
        captured["payload"] = payload
        return RuntimeEnvelope(
            tool=tool_name,
            session_id=session_id,
            stage="333_MIND",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={"response": "ok"},
        )

    monkeypatch.setattr(runtime_tools, "_wrap_call", _fake_wrap_call)

    response = await runtime_tools.ollama_local_generate(
        prompt="Summarize this.",
        model="qwen2.5:3b",
        system="Be concise.",
        temperature=0.3,
        max_tokens=256,
        session_id="ollama-test",
    )

    assert response.payload == {"response": "ok"}
    assert captured["tool_name"] == "ollama_local_generate"
    assert captured["session_id"] == "ollama-test"
    assert captured["payload"] == {
        "prompt": "Summarize this.",
        "model": "qwen2.5:3b",
        "system": "Be concise.",
        "temperature": 0.3,
        "max_tokens": 256,
    }


@pytest.mark.asyncio
async def test_check_vital_includes_intelligence_service_probes(monkeypatch):
    async def _fake_wrap_call(tool_name, stage, session_id, payload, ctx=None, caller_context=None):
        return RuntimeEnvelope(
            tool=tool_name,
            session_id=session_id,
            stage="000_INIT",
            verdict=Verdict.SEAL,
            status=RuntimeStatus.SUCCESS,
            payload={},
        )

    async def _fake_probe():
        return {
            "qdrant": {"status": "healthy", "reachable": True, "status_code": 200},
            "ollama": {
                "status": "healthy",
                "reachable": True,
                "status_code": 200,
                "model_count": 1,
            },
            "openclaw": {"status": "healthy", "reachable": True, "status_code": 200},
            "browserless": {"status": "healthy", "reachable": True, "status_code": 200},
        }

    monkeypatch.setattr(runtime_tools, "_wrap_call", _fake_wrap_call)
    monkeypatch.setattr(runtime_tools, "_probe_intelligence_services", _fake_probe)

    envelope = await runtime_tools.check_vital("probe-session")

    assert envelope.payload["intelligence_services"]["ollama"]["model_count"] == 1
    assert envelope.payload["intelligence_services"]["qdrant"]["reachable"] is True

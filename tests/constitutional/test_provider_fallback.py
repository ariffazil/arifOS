"""Constitutional verification for the LLM provider fallback tail."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest

import arifosmcp.runtime.llm_client as llm_client
from arifosmcp.runtime.law import check_laws


async def _provider_offline(*args: object, **kwargs: object) -> tuple[str, dict[str, object]]:
    raise llm_client.LLMUnavailableError("provider offline")


@pytest.fixture
def remote_providers_offline(monkeypatch: pytest.MonkeyPatch) -> dict[str, AsyncMock]:
    """Disable every remote generation provider without making network calls."""
    mocks: dict[str, AsyncMock] = {}
    for name in ("_call_tokenrouter", "_call_minimax", "_call_mimo", "_call_sea_lion"):
        provider = AsyncMock(side_effect=_provider_offline)
        monkeypatch.setattr(llm_client, name, provider)
        mocks[name] = provider
    monkeypatch.setattr(llm_client, "ILMU_ENABLED", False)
    return mocks


@pytest.fixture
def ollama_response(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Serve a valid local response while all remote providers remain offline."""
    parsed = {
        "status": "HOLD",
        "verdict": "HOLD",
        "reason": "mocked_ollama_response",
        "human_decision_required": True,
    }
    provider = AsyncMock(return_value=(json.dumps(parsed), parsed))
    monkeypatch.setattr(llm_client, "_call_ollama", provider)
    return provider


@pytest.mark.asyncio
async def test_sea_lion_offline_uses_ollama(
    remote_providers_offline: dict[str, AsyncMock],
    ollama_response: AsyncMock,
) -> None:
    envelope = await llm_client.call_llm(
        system="Return a constitutional provider verdict.",
        user="Assess a reversible test action.",
        tool_origin="333_REASON",
        mode="reason",
    )

    assert remote_providers_offline["_call_sea_lion"].await_count == 1
    ollama_response.assert_awaited_once()
    assert envelope.provider == "ollama"
    assert envelope.parsed_output["verdict"] == "HOLD"
    assert envelope.schema_valid is True


@pytest.mark.asyncio
async def test_sea_lion_and_ollama_offline_use_deterministic_hold(
    remote_providers_offline: dict[str, AsyncMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    ollama = AsyncMock(side_effect=_provider_offline)
    monkeypatch.setattr(llm_client, "_call_ollama", ollama)

    envelope = await llm_client.call_llm(
        system="Return a constitutional provider verdict.",
        user="Assess a reversible test action.",
        tool_origin="333_REASON",
        mode="reason",
    )

    ollama.assert_awaited_once()
    assert envelope.provider == "deterministic_fallback"
    assert envelope.parsed_output["verdict"] in {"HOLD", "SABAR"}
    assert envelope.human_decision_required is True
    assert envelope.schema_valid is True


@pytest.mark.asyncio
async def test_all_providers_offline_never_void_without_hard_floor(
    remote_providers_offline: dict[str, AsyncMock],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(llm_client, "_call_ollama", AsyncMock(side_effect=_provider_offline))
    floor_result = check_laws("arif_think", {"mode": "reason"}, actor_id=None)
    assert floor_result["verdict"] == "SEAL"
    assert floor_result["violated_laws"] == []

    envelope = await llm_client.call_llm(
        system="Return a constitutional provider verdict.",
        user="Summarize approved public evidence.",
        tool_origin="333_REASON",
        mode="reason",
    )

    assert envelope.provider == "deterministic_fallback"
    assert envelope.parsed_output["verdict"] != "VOID"
    assert envelope.parsed_output["verdict"] in {"HOLD", "SABAR"}
    assert envelope.parsed_output["violated_floors"] == []

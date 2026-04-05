import pytest

from core.pipeline import forge, quick


@pytest.mark.asyncio
async def test_quick_pipeline_smoke():
    result = await quick("What is the capital of Malaysia?", actor_id="user")
    assert result["session_id"]
    assert result["verdict"] in {"SEAL", "VOID", "888_HOLD"}
    if result["verdict"] == "SEAL":
        assert "agi" in result


@pytest.mark.asyncio
async def test_trinity_forge_smoke():
    result = await forge("Hello world", actor_id="user")
    assert result.session_id
    assert result.verdict in {"SEAL", "PARTIAL", "SABAR", "VOID", "888_HOLD"}

import pytest

import arifosmcp.apps.forge_app as forge_module


@pytest.mark.asyncio
async def test_forge_judge_check_returns_plain_verdict_string():
    forge_module.STATE = {"session_id": "sess-forge-judge"}

    result = await forge_module.forge_judge_check(
        candidate_action="deploy docker compose to production",
        risk_tier="high",
        session_id="sess-forge-judge",
    )

    assert isinstance(result["gate1_verdict"], str)
    assert "partially initialized module" not in str(result)


@pytest.mark.asyncio
async def test_forge_execute_uses_runtime_handler_without_dispatch_map_error():
    forge_module.STATE = {
        "session_id": "sess-forge-exec",
        "gate1_ok": True,
        "gate2_approved": True,
    }

    result = await forge_module.forge_execute(
        candidate_action="deploy docker compose to production",
        risk_tier="high",
        session_id="sess-forge-exec",
        judge_verdict="SEAL",
        judge_g_star=0.99,
        judge_state_hash="x" * 64,
    )

    assert "dispatch map" not in str(result)
    assert "unexpected keyword argument" not in str(result)
    assert isinstance(result["forge_verdict"], str)

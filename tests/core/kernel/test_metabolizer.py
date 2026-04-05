import asyncio
from typing import Any

import pytest

from core.kernel.stage_orchestrator import (
    run_metabolic_pipeline,
    run_stage_444_trinity_sync,
    run_stage_888_judge,
)
from core.physics.thermodynamics_hardened import init_thermodynamic_budget
from core.shared.types import Verdict


@pytest.mark.asyncio
async def test_metabolic_pipeline_full_flow():
    """
    Test the full 000-999 metabolic pipeline orchestration.
    Ensures that stages are called in sequence and the final verdict is correctly synthesized.
    """
    session_id = "test_metabolic_session"
    query = "Should I deploy arifOS to production?"

    # Initialize budget so thermodynamics don't crash
    init_thermodynamic_budget(session_id, initial_budget=10.0)

    # We will use the real metabolizer but let it call the real organs.

    results = await run_metabolic_pipeline(session_id=session_id, query=query)

    assert results["session_id"] == session_id
    assert "stages" in results
    assert "444" in results["stages"]
    assert "555" in results["stages"]
    assert "666" in results["stages"]
    assert "777" in results["stages"]
    assert "888" in results["stages"]
    assert "999" in results["stages"]

    # Final verdict should be a string
    assert isinstance(results["final_verdict"], str)
    assert results["final_verdict"] in {"SEAL", "VOID", "HOLD_888", "SABAR"}


@pytest.mark.asyncio
async def test_stage_444_sync_logic():
    """Verify Stage 444 Trinity Sync — merging AGI and ASI."""
    session_id = "test_sync_session"
    init_thermodynamic_budget(session_id, initial_budget=1.0)

    def mock_get_stage(sid: str, stage: str) -> dict[str, Any]:
        if stage in ("agi", "think"):
            return {"query": "test sync", "verdict": "SEAL"}
        if stage in ("asi", "empathy", "asi_empathize"):
            return {"verdict": "SEAL", "empathy_kappa_r": 0.95}
        return {}

    result = await run_stage_444_trinity_sync(
        session_id=session_id, get_stage_result_fn=mock_get_stage
    )

    assert result["stage"] == "444"
    assert result["status"] == "completed"
    assert "pre_verdict" in result
    assert result["consensus_score"] > 0.0


@pytest.mark.asyncio
async def test_stage_888_judge_veto():
    """Verify Stage 888 APEX Judge — final executive veto."""
    session_id = "test_judge_session"
    init_thermodynamic_budget(session_id, initial_budget=1.0)

    agi_res = {"query": "restricted action", "verdict": "SEAL"}
    asi_res = {"verdict": "HOLD", "is_reversible": False}

    result = await run_stage_888_judge(
        session_id=session_id, agi_result=agi_res, asi_result=asi_res
    )

    assert result["stage"] == "888"
    assert result["status"] == "completed"
    assert "verdict" in result
    assert result["verdict"] != "SEAL"


@pytest.mark.asyncio
async def test_metabolizer_error_handling():
    """Ensure the metabolizer handles organ failures gracefully."""
    session_id = "test_error_session"

    def failing_store(sid, stage, payload):
        raise RuntimeError("DB Down")

    result = await run_stage_444_trinity_sync(
        session_id=session_id,
        agi_result={"query": "error test"},
        store_stage_result_fn=failing_store,
    )

    assert result["status"] == "failed"
    assert result["pre_verdict"] == "VOID"
    assert "error" in result

from __future__ import annotations

from typing import Any

from core.kernel.mcp_tool_service import respond_tool, seal_tool
from core.kernel.mcp_transport_kernel import (
    build_align_error,
    build_forge_error,
    build_integrate_error,
    build_reason_error,
    build_respond_error,
    build_validate_error,
)


async def test_respond_tool_uses_stage_555_alias() -> None:
    stage_store: dict[str, dict[str, Any]] = {
        "think": {"query": "hello"},
        "stage_555": {"empathy_kappa_r": 0.91, "verdict": "SEAL"},
    }
    captured: dict[str, Any] = {}

    def _get_stage_result(session_id: str, stage: str) -> dict[str, Any]:
        assert session_id == "sess-1"
        return stage_store.get(stage, {})

    async def _run_stage_444(
        session_id: str, agi_res: dict[str, Any], asi_res: dict[str, Any]
    ) -> dict[str, Any]:
        captured["session_id"] = session_id
        captured["agi"] = agi_res
        captured["asi"] = asi_res
        return {"clarity_score": 0.93}

    result = await respond_tool(
        session_id="sess-1",
        plan="draft",
        get_stage_result_fn=_get_stage_result,
        run_stage_444_fn=_run_stage_444,
    )

    assert result["verdict"] == "SEAL"
    assert captured["asi"]["empathy_kappa_r"] == 0.91


async def test_seal_tool_uses_stage_aliases() -> None:
    stage_store: dict[str, dict[str, Any]] = {
        "stage_888": {"verdict": "SEAL"},
        "think": {"query": "world"},
        "stage_666": {"kappa_r": 0.9, "verdict": "SEAL"},
    }

    def _get_stage_result(session_id: str, stage: str) -> dict[str, Any]:
        assert session_id == "sess-2"
        return stage_store.get(stage, {})

    async def _run_stage_999(
        session_id: str,
        judge_res: dict[str, Any],
        agi_res: dict[str, Any],
        asi_res: dict[str, Any],
        summary: str,
    ) -> dict[str, Any]:
        assert session_id == "sess-2"
        assert judge_res["verdict"] == "SEAL"
        assert agi_res["query"] == "world"
        assert asi_res["kappa_r"] == 0.9
        assert summary == "done"
        return {"status": "SEALED", "seal_id": "SEAL-123"}

    result = await seal_tool(
        session_id="sess-2",
        summary="done",
        verdict="SEAL",
        get_stage_result_fn=_get_stage_result,
        run_stage_999_fn=_run_stage_999,
    )

    assert result["status"] == "SEALED"
    assert result["stage"] == "999_SEAL"


def test_transport_error_paths_do_not_seal() -> None:
    err = RuntimeError("boom")
    outputs = [
        build_reason_error(
            session_id="sess",
            hypotheses=3,
            truth_score_placeholder=0.8,
            clarity_delta_placeholder=-0.1,
            error=err,
        ),
        build_integrate_error("sess", 0.04, err),
        build_respond_error("sess", err),
        build_validate_error(
            session_id="sess",
            peace_squared_min=1.0,
            empathy_kappa_r_default=0.7,
            safe_default=True,
            error=err,
        ),
        build_align_error("sess", err),
        build_forge_error("sess", err),
    ]

    assert all(output["verdict"] == "SABAR" for output in outputs)

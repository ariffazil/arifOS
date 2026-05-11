from __future__ import annotations

import pytest

import arifosmcp.tools.mind_reason as mind_reason_tool


async def _fake_structured_reasoning(
    query: str, mode: str, session_id: str | None, actor_id: str | None
):
    return {
        "status": "SEAL",
        "claim_state": "VERIFIED",
        "synthesis": f"reasoned:{query}:{mode}",
        "reasoning": {"path": "test"},
        "confidence": {"overall_confidence": 0.95, "evidence_confidence": 0.95},
        "uncertainty": [],
        "reasoning_mode": "analytical",
        "axioms_used": ["F02_TRUTH"],
        "next_safe_action": ["continue"],
    }


def test_floor_breach_returns_hold_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "arifosmcp.runtime.mind_reason.arif_mind_reason_structured",
        _fake_structured_reasoning,
    )
    monkeypatch.setattr(
        mind_reason_tool,
        "check_floors",
        lambda *_args, **_kwargs: {
            "verdict": "HOLD",
            "reason": "floor block",
            "failed_floors": ["F12"],
        },
    )

    result = mind_reason_tool.arif_mind_reason(query="sensitive op", actor_id="arif")

    assert result.status == "HOLD"
    assert result.meta["reason"] == "floor block"
    assert result.meta["failed_floors"] == ["F12"]
    assert result.result["status"] == "HOLD"
    assert any(
        u.get("type") == "FLOOR_BREACH" for u in result.result.get("uncertainty", [])
    )


@pytest.mark.asyncio
async def test_mind_reason_from_async_context_does_not_use_run_until_complete(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "arifosmcp.runtime.mind_reason.arif_mind_reason_structured",
        _fake_structured_reasoning,
    )
    monkeypatch.setattr(
        mind_reason_tool,
        "check_floors",
        lambda *_args, **_kwargs: {"verdict": "SEAL", "reason": "ok"},
    )

    result = mind_reason_tool.arif_mind_reason(
        query="within running loop",
        actor_id="arif",
        context={"session_id": "sess-1"},
    )

    assert result.status == "OK"
    assert result.result["status"] == "SEAL"

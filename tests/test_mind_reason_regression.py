from __future__ import annotations

import pytest

from arifosmcp.runtime.llm_client import LLMOutputEnvelope

import arifosmcp.tools.reason as mind_reason_tool


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
        "axioms_used": ["L02_TRUTH"],
        "next_safe_action": ["continue"],
    }


def test_floor_breach_returns_hold_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "arifosmcp.runtime.mind_reason.arif_mind_reason_structured",
        _fake_structured_reasoning,
    )
    monkeypatch.setattr(
        mind_reason_tool,
        "check_laws",
        lambda *_args, **_kwargs: {
            "verdict": "HOLD",
            "reason": "floor block",
            "violated_laws": ["L12"],
        },
    )

    result = mind_reason_tool.arif_mind_reason(query="sensitive op", actor_id="arif")

    assert result.status == "HOLD"
    assert result.meta["reason"] == "floor block"
    assert result.meta["violated_laws"] == ["L12"]
    assert result.result["status"] == "HOLD"
    assert any(u.get("type") == "FLOOR_BREACH" for u in result.result.get("uncertainty", []))


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
        "check_laws",
        lambda *_args, **_kwargs: {"verdict": "SEAL", "reason": "ok"},
    )

    result = mind_reason_tool.arif_mind_reason(
        query="within running loop",
        actor_id="arif",
        context={"session_id": "sess-1"},
    )

    assert result.status == "OK"
    assert result.result["status"] == "SEAL"


async def _fake_call_llm_dict_confidence(*args, **kwargs):
    """Mock call_llm returning structured output with dict-style confidence."""
    from datetime import datetime, timezone

    return LLMOutputEnvelope(
        provider="sea_lion",
        model="aisingapore/Qwen-SEA-LION-v4-32B-IT",  # pragma: allowlist secret
        tool_origin="333_REASON",
        mode="reason",
        raw_output='{"status": "REASONED", "synthesis": "MIND_OK", "confidence": {"overall_confidence": 0.85}}',
        raw_output_hash="sha256:test",
        parsed_output={
            "status": "REASONED",
            "claim_state": "VERIFIED",
            "synthesis": "MIND_OK",
            "reasoning": {"path": "test"},
            "confidence": {
                "reasoning_confidence": 0.88,
                "evidence_confidence": 0.82,
                "overall_confidence": 0.85,
            },
            "uncertainty": [],
            "reasoning_mode": "analytical",
            "axioms_used": ["L02"],
            "next_safe_action": ["continue"],
        },
        schema_valid=True,
        confidence_claimed=0.85,
        prompt_hash="sha256:test",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


def test_mind_reason_dict_confidence_no_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Smoke test: 333_MIND with dict-confidence must NOT trigger deterministic fallback.

    Regression guard for the confidence-dict TypeError that previously caused
    arif_mind_reason to silently return LLM_UNAVAILABLE.
    """
    monkeypatch.setattr(
        "arifosmcp.runtime.mind_reason.call_llm",
        _fake_call_llm_dict_confidence,
    )
    monkeypatch.setattr(
        mind_reason_tool,
        "check_laws",
        lambda *_args, **_kwargs: {"verdict": "SEAL", "reason": "ok"},
    )

    result = mind_reason_tool.arif_mind_reason(query="Say exactly: MIND_OK", actor_id="arif")

    assert result.status == "OK"
    assert result.result["status"] == "REASONED"
    assert result.result["synthesis"] == "MIND_OK"
    assert result.result["claim_state"] == "VERIFIED"
    # Critical invariant: must NOT be the deterministic fallback message
    assert "LLM unavailable" not in result.result.get("synthesis", "").lower()
    assert "deterministic" not in result.result.get("synthesis", "").lower()

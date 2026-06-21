from __future__ import annotations

import pytest

from arifosmcp.runtime.llm_client import LLMOutputEnvelope
from arifosmcp.schemas.mind_metabolism import MindRequest

import arifosmcp.runtime.mind_reason as runtime_mind_reason
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
    assert result.result["reasoning_verdict"] == "HOLD"
    assert result.meta["floor_verdict"] == "HOLD"
    assert result.meta["next_safe_action"].startswith("Produce reversible")


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
    assert result.result["reasoning_verdict"] == "SEAL"


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
    assert result.result["reasoning_verdict"] == "REASONED"
    assert result.result["claim_state"] == "VERIFIED"
    assert result.result["next_safe_action"] == ["continue"]
    # Critical invariant: must NOT be the deterministic fallback message
    assert result.result["confidence"]["overall"] > 0.8


@pytest.mark.asyncio
async def test_mind_reason_v2_next_actions_use_canonical_tool_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_call_llm_v2(*args, **kwargs):
        from datetime import datetime, timezone
        from arifosmcp.runtime.llm_client import LLMOutputEnvelope

        tool_origin = kwargs.get("tool_origin", "")
        if tool_origin == "333 MIND_METABOLIZE":
            parsed_output = {
                "input_summary": "Need a governed next step",
                "core_problem": "Choose the next governed action",
                "why_it_matters": "The caller needs a canonical next action.",
                "decision_pressure": "medium",
                "background_field": [],
                "known_unknowns": [],
                "assumptions": [],
                "constraints": [],
                "risk_notes": [],
            }
        elif tool_origin == "333 MIND_ABSTRACT":
            parsed_output = {"abstractions": []}
        elif tool_origin == "333 MIND_ABDUCT":
            parsed_output = {"abductions": []}
        elif tool_origin == "333 MIND_SYNTHESIZE":
            parsed_output = {
                "bounded_answer": "Bounded answer",
                "what_is_supported": ["governed next step"],
                "what_is_not_supported": [],
                "what_remains_unknown": [],
                "confidence": {
                    "reasoning_confidence": 0.9,
                    "evidence_confidence": 0.9,
                    "overall_confidence": 0.9,
                },
            }
        else:
            parsed_output = {}

        return LLMOutputEnvelope(
            provider="test",
            model="test",
            tool_origin=tool_origin or "test",
            mode="reason",
            raw_output="{}",
            raw_output_hash="sha256:test",
            parsed_output=parsed_output,
            schema_valid=True,
            confidence_claimed=0.9,
            prompt_hash="sha256:test",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    monkeypatch.setattr("arifosmcp.runtime.mind_reason.call_llm", _fake_call_llm_v2)

    request = MindRequest(query="Need a governed next step", mode="metabolize", actor_id="arif")
    response = await runtime_mind_reason.arif_mind_reason_v2(request)

    tools = [action.tool for action in response.mind_packet.next_actions]
    assert tools == ["arif_judge_deliberate", "arif_evidence_fetch"]
    assert "888_JUDGE" not in tools
    assert "222_FETCH" not in tools


@pytest.mark.asyncio
async def test_mind_reason_legacy_fallback_uses_canonical_tool_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _raise_llm_unavailable(*_args, **_kwargs):
        raise RuntimeError("LLM unavailable")

    monkeypatch.setattr("arifosmcp.runtime.mind_reason.call_llm", _raise_llm_unavailable)

    result = await runtime_mind_reason.arif_mind_reason(
        query="Need a governed next step",
        mode="reason",
        actor_id="arif",
    )

    assert result["next_safe_action"] == ["arif_evidence_fetch", "arif_judge_deliberate"]
    assert "222_EVIDENCE" not in result["next_safe_action"]
    assert "888_JUDGE" not in result["next_safe_action"]

from __future__ import annotations
import pytest
from unittest.mock import MagicMock
from arifosmcp.runtime.llm_client import LLMOutputEnvelope
from arifosmcp.tools.shadow_geometry import arif_self_evaluate, arif_model_compare

async def _fake_call_llm_self_evaluate(*args, **kwargs):
    from datetime import datetime, timezone
    return LLMOutputEnvelope(
        provider="minimax",
        model="MiniMax-M3",
        tool_origin="arif_self_evaluate",
        mode="critique",
        raw_output='{"scores": {}, "reasons": {}, "overall_compliance": 0.95, "verdict": "PASS"}',
        raw_output_hash="sha256:test",
        parsed_output={
            "scores": {f"F{i:02d}": 1.0 for i in range(1, 14)},
            "reasons": {f"F{i:02d}": "compliant" for i in range(1, 14)},
            "overall_compliance": 1.0,
            "verdict": "PASS"
        },
        schema_valid=True,
        confidence_claimed=0.95,
        prompt_hash="sha256:test",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

async def _fake_call_llm_model_compare(*args, **kwargs):
    from datetime import datetime, timezone
    return LLMOutputEnvelope(
        provider="minimax",
        model="MiniMax-M3",
        tool_origin="arif_model_compare",
        mode="critique",
        raw_output='{"axes_comparison": {}, "verdict_recommendation": {}}',
        raw_output_hash="sha256:test",
        parsed_output={
            "axes_comparison": {
                axis: {
                    "model_a_score": 0.9,
                    "model_b_score": 0.8,
                    "summary": "model A is better"
                } for axis in ["truth", "refusal", "self_identity", "cultural_grounding", "institutional_protection", "human_authority"]
            },
            "verdict_recommendation": {
                "preferred_model": "model_a",
                "rationale": "superior scores"
            }
        },
        schema_valid=True,
        confidence_claimed=0.95,
        prompt_hash="sha256:test",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

@pytest.mark.asyncio
async def test_arif_self_evaluate_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "arifosmcp.tools.shadow_geometry.call_llm",
        _fake_call_llm_self_evaluate
    )
    result = await arif_self_evaluate(query="Hello Arif", actor_id="arif")
    assert result["status"] == "OK"
    assert result["tool"] == "arif_self_evaluate"
    assert result["evaluation"]["verdict"] == "PASS"

@pytest.mark.asyncio
async def test_arif_model_compare_passes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "arifosmcp.tools.shadow_geometry.call_llm",
        _fake_call_llm_model_compare
    )
    result = await arif_model_compare(model_a="deepseek", model_b="minimax", actor_id="arif")
    assert result["status"] == "OK"
    assert result["tool"] == "arif_model_compare"
    assert result["comparison"]["verdict_recommendation"]["preferred_model"] == "model_a"

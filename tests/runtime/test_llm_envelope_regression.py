"""
Regression coverage for LLM envelope confidence schema handling.

F2 Truth: wrap_llm_output must never compare dict directly to float.
The 333_MIND structured response schema defines confidence as a dict
with nested fields (reasoning_confidence, evidence_confidence, overall_confidence).
Prior bug: confidence dict was passed to wrap_llm_output and compared
with float 0.3, causing TypeError and silent deterministic fallback.
"""

from __future__ import annotations


from arifosmcp.runtime.llm_output_envelope import wrap_llm_output


def _minimal_envelope_kwargs(confidence_val=None, parsed_output=None):
    """Return base kwargs for wrap_llm_output with minimal required fields."""
    return {
        "raw_output": '{"status": "OK"}',
        "parsed_output": parsed_output or {"status": "OK"},
        "provider": "sea_lion",
        "model": "test-model",
        "tool_origin": "333_REASON",
        "mode": "reason",
        "prompt": "test prompt",
        "schema_valid": True,
        "confidence": confidence_val,
        "latency_ms": 100.0,
    }


def test_wrap_llm_output_float_confidence():
    """Case A: confidence is a plain float — direct comparison must work."""
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=0.72))
    assert env.confidence_claimed == 0.72
    # human_decision_required is True because evidence_level is always 'claimed'
    # (F2 Truth: LLM outputs are testimony, not verified truth)
    assert env.human_decision_required is True


def test_wrap_llm_output_dict_confidence_with_overall():
    """Case B: confidence is a dict with overall_confidence — extracted safely."""
    parsed = {
        "status": "REASONED",
        "confidence": {
            "reasoning_confidence": 0.81,
            "evidence_confidence": 0.74,
            "overall_confidence": 0.78,
        },
    }
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    assert env.confidence_claimed == 0.78
    # evidence_level='claimed' means human_decision_required is always True for LLM outputs
    assert env.human_decision_required is True


def test_wrap_llm_output_dict_confidence_missing_overall():
    """Case C: confidence dict missing overall_confidence — fallback to confidence key."""
    parsed = {
        "status": "REASONED",
        "confidence": {
            "reasoning_confidence": 0.81,
            "evidence_confidence": 0.74,
        },
    }
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    # Falls back to .get("confidence", 0.5) which is the dict itself, then
    # defensive coercion extracts .get("confidence") -> None -> defaults to 0.5
    assert env.confidence_claimed == 0.5


def test_wrap_llm_output_dict_confidence_with_confidence_key():
    """Case C-variant: confidence dict has 'confidence' key instead of overall."""
    parsed = {
        "status": "REASONED",
        "confidence": {
            "confidence": 0.65,
        },
    }
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    assert env.confidence_claimed == 0.65


def test_wrap_llm_output_malformed_confidence_null():
    """Case D: confidence is null — must default to 0.5 without TypeError."""
    parsed = {"status": "REASONED", "confidence": None}
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    assert env.confidence_claimed == 0.5


def test_wrap_llm_output_malformed_confidence_string():
    """Case D: confidence is a string — must default to 0.5 without TypeError."""
    parsed = {"status": "REASONED", "confidence": "high"}
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    assert env.confidence_claimed == 0.5


def test_wrap_llm_output_malformed_confidence_list():
    """Case D: confidence is a list — must default to 0.5 without TypeError."""
    parsed = {"status": "REASONED", "confidence": [0.5, 0.6]}
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    assert env.confidence_claimed == 0.5


def test_wrap_llm_output_low_confidence_triggers_human_review():
    """Invariant: _low_confidence must be computed from numeric overall only."""
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=0.25))
    assert env.confidence_claimed == 0.25
    assert env.human_decision_required is True  # below 0.3 threshold


def test_wrap_llm_output_no_dict_comparison_invariant():
    """
    Regression guard: ensure no direct dict < float comparison can occur.
    This test constructs a scenario that would have triggered TypeError
    before the fix, and verifies it now produces a valid envelope.
    """
    parsed = {
        "status": "REASONED",
        "confidence": {
            "overall_confidence": 0.91,
            "reasoning_confidence": 0.88,
            "evidence_confidence": 0.85,
        },
    }
    # Before fix: this would raise TypeError inside wrap_llm_output
    # After fix: must return valid envelope with confidence_claimed == 0.91
    env = wrap_llm_output(**_minimal_envelope_kwargs(confidence_val=None, parsed_output=parsed))
    assert isinstance(env.confidence_claimed, float)
    assert env.confidence_claimed == 0.91

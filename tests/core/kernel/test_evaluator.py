"""
tests/core/kernel/test_evaluator.py — Tests for the Constitutional Evaluation Engine
"""

import pytest
from core.kernel.evaluator import ConstitutionalEvaluator, HARD_FLOORS, SOFT_FLOORS

@pytest.fixture
def evaluator():
    return ConstitutionalEvaluator()

def test_evaluator_singleton():
    from core.kernel.evaluator import evaluator as e1
    from core.kernel.evaluator import evaluator as e2
    assert e1 is e2

def test_build_pre_context(evaluator):
    ctx = evaluator.build_pre_context("rm -rf /", {"session_id": "test_sess"})
    assert ctx["query"] == "rm -rf /"
    assert ctx["session_id"] == "test_sess"
    assert ctx["role"] == "SESSION_UNVERIFIED"
    assert ctx["f11_continuity"] == "MISSING_AUTH_TOKEN"

def test_build_pre_context_with_auth(evaluator):
    ctx = evaluator.build_pre_context("ls", {
        "session_id": "test_sess",
        "authority_token": "valid_token"
    })
    assert ctx["role"] == "AGENT"
    assert ctx["f11_continuity"] == "VERIFIED"

def test_build_post_context(evaluator):
    result = {"response": "Success", "truth_score": 0.99}
    ctx = evaluator.build_post_context("check site", result)
    assert ctx["query"] == "check site"
    assert ctx["response"] == "Success"
    assert ctx["truth_score"] == 0.99
    # Default values
    assert ctx["confidence"] == 0.96

def test_evaluate_verdict_seal(evaluator):
    details = [
        {"floor": "F2", "passed": True},
        {"floor": "F5", "passed": True}
    ]
    assert evaluator.evaluate_verdict(details) == "SEAL"

def test_evaluate_verdict_partial(evaluator):
    details = [
        {"floor": "F2", "passed": True},
        {"floor": "F5", "passed": False}  # F5 is SOFT
    ]
    assert evaluator.evaluate_verdict(details) == "PARTIAL"

def test_evaluate_verdict_void(evaluator):
    details = [
        {"floor": "F2", "passed": False}, # F2 is HARD
        {"floor": "F5", "passed": True}
    ]
    assert evaluator.evaluate_verdict(details) == "VOID"

def test_accumulate_scores(evaluator):
    details = [
        {"floor": "F2", "score": 0.95},
        {"floor": "F7", "score": 0.05}  # Humility omega_0 -> 0.95 confidence
    ]
    scores = evaluator.accumulate_floor_scores(details)
    assert scores["F2"] == 0.95
    assert scores["F7"] == 0.95

def test_build_self_audit(evaluator):
    details = [
        {"floor": "F2", "passed": False},
        {"floor": "F5", "passed": False}
    ]
    audit = evaluator.build_self_audit(details, "VOID")
    assert audit["deterministic"] is True
    assert "F2" in audit["hard_fails"]
    assert "F5" in audit["soft_fails"]
    assert audit["expected_verdict"] == "VOID"
    assert audit["verdict_consistent"] is True

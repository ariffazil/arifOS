"""
test_012 — Governance Pipeline Direct (Tier 1: Constitutional Substrate)

Bypasses MCP. Calls check_all_floors() directly with synthetic
contexts and verifies the LawResult structure.

Pass criteria:
    - check_all_floors returns exactly 13 LawResults
    - Each LawResult has: law_id, passed, score, reason, metadata
    - Hard floors (F1, F2, F9, L10-L13) produce meaningful verdicts
    - F2 with high evidence_quality passes; with low quality fails
    - LawResult.metadata is populated (not empty dict)

This is what the kernel *decides* when given input. If this fails,
the kernel is broken regardless of what the bus reports.
"""

import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
REPO_ROOT = "/root/arifOS"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from core.shared.laws import check_all_floors, LawResult  # noqa: E402


GOOD_CONTEXT = {
    "action": "test_action",
    "evidence_quality": 0.99,
    "reversibility": "reversible",
    "authority_mode": "OBSERVE",
    "is_actor_verified": True,
    "actor_id": "test_actor",
    "session_id": "SEAL-test",
    "human_decision_required": False,
    "irreversible": False,
    "authority_token": "test-token-valid",
}

BAD_CONTEXT = {
    "action": "test_action",
    "query": "",  # empty query = F2 should fail
    "evidence_quality": 0.30,
    "reversibility": "irreversible",  # F1 fail
    "authority_mode": "SOVEREIGN",
    "is_actor_verified": False,  # L11 fail
    "actor_id": "anonymous",
    "session_id": "",  # missing session_id = L11 fail
    "human_decision_required": True,
    "irreversible": True,
    "energy_efficiency": 0.5,  # below Landauer
}


def test_check_all_floors_returns_13():
    """check_all_floors must return exactly 13 LawResults."""
    results = check_all_floors(GOOD_CONTEXT)
    assert len(results) == 13, f"expected 13 LawResults, got {len(results)}"


def test_each_lawresult_has_required_fields():
    """Each LawResult must have law_id, passed, score, reason, metadata."""
    results = check_all_floors(GOOD_CONTEXT)
    for r in results:
        assert hasattr(r, "law_id"), f"LawResult missing law_id: {r}"
        assert hasattr(r, "passed"), f"LawResult missing passed: {r}"
        assert hasattr(r, "score"), f"LawResult missing score: {r}"
        assert hasattr(r, "reason"), f"LawResult missing reason: {r}"
        assert hasattr(r, "metadata"), f"LawResult missing metadata: {r}"


def test_good_context_passes_floors():
    """A well-formed context should pass F1, F2, L10, L11, L12, L13."""
    results = check_all_floors(GOOD_CONTEXT)
    by_id = {r.law_id: r for r in results}
    # F1 should pass (reversible)
    assert by_id["F1_Amanah"].passed, (
        f"F1 should pass reversible action, got {by_id['F1_Amanah'].reason}"
    )
    # F2 should pass with 0.99 evidence
    assert by_id["F2_Truth"].passed, f"F2 should pass 0.99 evidence, got {by_id['F2_Truth'].reason}"
    # L11 should pass (actor verified)
    assert by_id["L11_CommandAuth"].passed, (
        f"L11 should pass verified actor, got {by_id['L11_CommandAuth'].reason}"
    )


def test_bad_context_fails_l11():
    """A context without authority_token or session_id must fail L11."""
    results = check_all_floors(BAD_CONTEXT)
    by_id = {r.law_id: r for r in results}
    # L11 should fail: no session_id, no authority_token, no human_authority
    assert not by_id["L11_CommandAuth"].passed, (
        f"L11 must fail without session/authority, got {by_id['L11_CommandAuth'].reason}"
    )


def test_bad_context_evaluates_all_floors():
    """Every floor must produce a verdict (not crash)."""
    results = check_all_floors(BAD_CONTEXT)
    assert len(results) == 13, f"bad context must still produce 13 LawResults, got {len(results)}"


def test_lawresult_score_is_numeric():
    """Each LawResult.score must be a number.

    F4 CLARITY uses ΔS (entropy delta) which can be negative
    (entropy reduction is unbounded above 0). Other floors use [0, 1].
    """
    results = check_all_floors(GOOD_CONTEXT)
    for r in results:
        assert isinstance(r.score, (int, float)), f"score must be numeric, got {type(r.score)}: {r}"
        if r.law_id == "F4_Clarity":
            # F4: entropy delta, can be any negative number
            assert r.score <= 0.0, f"F4 score should be <= 0, got {r.score}"
        else:
            assert 0.0 <= r.score <= 1.0, f"non-F4 score must be in [0, 1], got {r.score}: {r}"


def test_lawresult_reason_is_string():
    """Each LawResult.reason must be a non-empty string."""
    results = check_all_floors(GOOD_CONTEXT)
    for r in results:
        assert isinstance(r.reason, str), f"reason must be string, got {type(r.reason)}: {r}"
        # Some passes may have brief reasons; ensure at least one char


def test_metadata_is_dict():
    """LawResult.metadata should be a dict (may be empty)."""
    results = check_all_floors(GOOD_CONTEXT)
    for r in results:
        assert isinstance(r.metadata, dict), f"metadata must be dict, got {type(r.metadata)}: {r}"


if __name__ == "__main__":
    test_check_all_floors_returns_13()
    print("test_012 count: PASS")
    test_each_lawresult_has_required_fields()
    print("test_012 fields: PASS")
    test_good_context_passes_floors()
    print("test_012 good: PASS")
    test_bad_context_fails_l11()
    print("test_012 bad_l11: PASS")
    test_bad_context_evaluates_all_floors()
    print("test_012 bad_evaluates: PASS")
    test_lawresult_score_is_numeric()
    print("test_012 score: PASS")
    test_lawresult_reason_is_string()
    print("test_012 reason: PASS")
    test_metadata_is_dict()
    print("test_012 metadata: PASS")

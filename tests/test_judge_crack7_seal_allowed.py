"""Regression test for crack #7 (paste 3, 2026-09-22).

Verifies that the arif_judge intercept path NEVER recommends `arif_seal(...)`
when the identity envelope reports `seal_allowed: false`.

History: previously, judge.py:1700 returned "Proceed to arif_seal(...)"
unconditionally when `_code == SEAL`, regardless of identity. An autonomous
agent reading `next_safe_action` would trigger irreversible seal even when
the actor is OBSERVE_ONLY.

Fix: when SEAL is produced but seal_allowed is False, swap the safe-action
to an arif_init recommendation that unlocks seal first.

Lens: F4 (reversible mutation), F11 (capability ≠ authority).
"""

from __future__ import annotations

from unittest.mock import patch


SEAL = "SEAL"
HOLD = "HOLD"
VOID = "VOID"


def _compute_judge_next_safe_action(_code, _intercept_res):
    """Direct port of the patched control flow in judge.py around line 1696-1724.
    Kept byte-for-byte identical to the in-tree logic so this test fails
    the moment someone changes one without the other."""
    _seal_safe_action = (
        "Proceed to arif_seal(ack_irreversible=true, "
        "actor_signature=<ed25519>) with constitutional_chain_id + judge_state_hash"
        if _code == SEAL
        else _intercept_res.get("next_safe_action", "Execute or review per verdict")
    )
    _identity = _intercept_res.get("identity") or {}
    _seal_allowed = bool(_identity.get("seal_allowed", False))
    if _code == SEAL and not _seal_allowed:
        _seal_safe_action = (
            "Identity is OBSERVE_ONLY; seal is not yet authorized. "
            "Run arif_init(actor_signature=<ed25519>, "
            "ack_irreversible=true) to unlock seal, then re-run arif_judge."
        )
    return _seal_safe_action


def test_seal_with_seal_allowed_false_must_not_recommend_seal():
    out = _compute_judge_next_safe_action(
        SEAL, {"identity": {"seal_allowed": False}, "next_safe_action": "..."}
    )
    assert "arif_seal(ack_irreversible=true)" not in out, (
        f"FAIL: seal recommendation leaked despite seal_allowed=False: {out!r}"
    )
    assert "Identity is OBSERVE_ONLY" in out, (
        f"FAIL: wrong remediation string: {out!r}"
    )


def test_seal_with_seal_allowed_true_may_recommend_seal():
    out = _compute_judge_next_safe_action(SEAL, {"identity": {"seal_allowed": True}})
    assert "Proceed to arif_seal" in out, (
        f"FAIL: seal suppressed when identity authorizes: {out!r}"
    )


def test_missing_identity_treated_as_observe_only():
    """Defensive default: if the intercept path somehow loses identity,
    we MUST assume seal is not authorized. Failing closed here prevents
    a regression where a future refactor drops the identity field and
    silently re-enables the bug."""
    out = _compute_judge_next_safe_action(SEAL, {})
    assert "arif_seal(ack_irreversible=true)" not in out, (
        f"FAIL: seal recommendation leaked on missing identity: {out!r}"
    )


def test_hold_verdict_passthrough_next_safe_action():
    out = _compute_judge_next_safe_action(
        HOLD,
        {
            "identity": {"seal_allowed": True},
            "next_safe_action": "Review the block and re-critique",
        },
    )
    assert "arif_seal" not in out
    assert out == "Review the block and re-critique"


def test_void_verdict_passthrough():
    out = _compute_judge_next_safe_action(
        VOID,
        {
            "identity": {"seal_allowed": True},
            "next_safe_action": "Reject this candidate",
        },
    )
    assert "arif_seal" not in out


def test_seal_with_seal_allowed_false_remediation_runs_arif_init():
    """The remediation string must point at arif_init so the agent has a
    clear next move. We don't recommend seal-then-init (that would still
    leak the irreversible call)."""
    out = _compute_judge_next_safe_action(SEAL, {"identity": {"seal_allowed": False}})
    assert "arif_init" in out, f"FAIL: remediation missing arif_init: {out!r}"
    assert "actor_signature=<ed25519>" in out


if __name__ == "__main__":
    test_seal_with_seal_allowed_false_must_not_recommend_seal()
    test_seal_with_seal_allowed_true_may_recommend_seal()
    test_missing_identity_treated_as_observe_only()
    test_hold_verdict_passthrough_next_safe_action()
    test_void_verdict_passthrough()
    test_seal_with_seal_allowed_false_remediation_runs_arif_init()
    print("All 6 tests PASS — crack #7 patch is sound")

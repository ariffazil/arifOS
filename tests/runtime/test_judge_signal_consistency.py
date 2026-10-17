"""S2 regression — the effective verdict must dominate every intercept signal.

Discovered 2026-10-17 (FI-008 live probe): a judge payload returned
``effective_verdict=HOLD`` while ``meta.kernel_intercept.decision`` still said
``ALLOW`` and ``reasons`` said "Action authorized under standard capability
bounds." An agent reading the inner signal could act on an authorization the
outer verdict had already denied.

Gate: HOLD/OBSERVE_ONLY/VOID → every downstream signal agrees.
"""

from __future__ import annotations

import pytest

from arifosmcp.tools.judge import _reconcile_intercept_signals


@pytest.mark.parametrize("verdict", ["HOLD", "OBSERVE_ONLY", "VOID"])
def test_restrictive_verdict_dominates_allow(verdict: str):
    raw = {
        "decision": "ALLOW",
        "status": "ALLOW",
        "reason": "Action authorized under standard capability bounds.",
        "next_safe_action": "Execute the capability",
        "constitutional_chain_id": "cc_test",
    }

    out = _reconcile_intercept_signals(raw, verdict)

    # Every actionable signal agrees with the outer verdict.
    assert out["decision"] == verdict
    assert out["status"] == verdict
    assert "authorized" not in out["reason"].lower()
    assert "execute" not in out["next_safe_action"].lower()

    # Audit trail is preserved, not silently dropped.
    assert out["original_decision"] == "ALLOW"
    assert out["original_reason"] == raw["reason"]
    assert out["constitutional_chain_id"] == "cc_test"
    assert out["reconciled"] is True
    assert verdict in out["reconcile_reason"]


def test_allow_reason_is_removed_from_reasons_list():
    """Mirror of the judge.py post-processing: the overridden rationale cannot survive."""
    reasons = ["Action authorized under standard capability bounds."]
    original_reason = reasons[0]

    reasons = [r for r in reasons if r != original_reason]
    reasons.insert(0, "Effective verdict HOLD dominates intercept decision")

    assert reasons == ["Effective verdict HOLD dominates intercept decision"]
    assert "authorized" not in " ".join(reasons).lower()


def test_non_dict_intercept_is_safe():
    out = _reconcile_intercept_signals(None, "HOLD")
    assert out["decision"] == "HOLD"
    assert out["status"] == "HOLD"
    assert out["reconciled"] is True


def test_reconcile_is_idempotent():
    once = _reconcile_intercept_signals({"decision": "ALLOW"}, "HOLD")
    twice = _reconcile_intercept_signals(once, "HOLD")
    assert twice["decision"] == "HOLD"
    assert twice["status"] == "HOLD"

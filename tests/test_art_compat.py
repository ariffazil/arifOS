"""
test_art_compat.py — Legacy 6-check order compat battery (18 tests)
═══════════════════════════════════════════════════════════════════════════════
Preserves the 18-test battery that targets the legacy 6-check order
(art_compat.guarded_tool_call). These tests verify that the compat
shim is faithful to the v1 over-engineering that Arif rolled back
2026-06-21. They do NOT verify the canonical reflex (see test_art.py
for the 31 v3 tests).

Per the v3 doctrine (see /root/.agents/skills/ART/SKILL.md):
- The canonical reflex is 3 checks (POWER, TRUST, STATE), not 6.
- The 6-check order was v1 over-engineering, kept here as compat-only.
- New code should NOT use guarded_tool_call. Use art() from art.py.

DITEMPA BUKAN DIBERI — compat exists for tests, not for the reflex.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, "/opt/arifos/app")

from arifosmcp.runtime.art_compat import (
    guarded_tool_call,
    GatewayVerdict,
    DecisionClass,
    classify_reversibility,
    ReversibilityTier,
    EntropyWatcher,
    EntropySnapshot,
    ReversibilityAssessment,
    GatewayDecision,
)


# ═══════════════════════════════════════════════════════════════════════
# §REVERSIBILITY TESTS (5)
# ═══════════════════════════════════════════════════════════════════════


def test_observe_is_reversible():
    a = classify_reversibility(action_class="OBSERVE", tool_name="arif_memory_recall")
    assert a.tier == ReversibilityTier.REVERSIBLE
    assert a.can_rollback is True
    assert a.estimated_undo_steps == 1


def test_execute_is_irreversible():
    a = classify_reversibility(action_class="EXECUTE", tool_name="arif_forge_execute")
    assert a.tier == ReversibilityTier.IRREVERSIBLE
    assert a.can_rollback is False


def test_mutate_is_compensable_by_default():
    a = classify_reversibility(action_class="MUTATE", tool_name="arif_mind_reason")
    assert a.tier == ReversibilityTier.COMPENSABLE


def test_high_blast_promotes_compensable_to_irreversible():
    a = classify_reversibility(
        action_class="MUTATE", tool_name="arif_forge_execute", blast_radius="high"
    )
    assert a.tier == ReversibilityTier.IRREVERSIBLE


def test_void_action_class():
    a = classify_reversibility(action_class="VOID", tool_name="doomed")
    assert a.tier == ReversibilityTier.VOID


# ═══════════════════════════════════════════════════════════════════════
# §ENTROPY TESTS (2)
# ═══════════════════════════════════════════════════════════════════════


def test_entropy_watcher_starts_at_zero():
    w = EntropyWatcher()
    snap = w.snapshot()
    assert 0.0 <= snap.omega <= 1.0
    assert 0.0 <= snap.psi_vitality <= 1.0


def test_entropy_watcher_overload_detection():
    w = EntropyWatcher()
    w._last_snapshot = EntropySnapshot(
        omega=0.90, psi_vitality=0.10, timestamp=0.0, source="test"
    )
    assert w.should_pause() is True


# ═══════════════════════════════════════════════════════════════════════
# §INTERCEPTOR TESTS (11)
# ═══════════════════════════════════════════════════════════════════════


def test_clean_observe_proceeds():
    d = guarded_tool_call(
        intent="recall session state",
        tool_name="arif_memory_recall",
        actor_id="arif",
        action_class="OBSERVE",
    )
    assert d.verdict == GatewayVerdict.PROCEED
    assert d.next_action == "execute"


def test_unknown_actor_blocks():
    d = guarded_tool_call(
        intent="do something",
        tool_name="arif_mind_reason",
        actor_id="random_anon",
        action_class="OBSERVE",
    )
    assert d.verdict == GatewayVerdict.BLOCK


def test_execute_without_ack_holds():
    d = guarded_tool_call(
        intent="execute irreversible",
        tool_name="arif_forge_execute",
        actor_id="arif",
        action_class="EXECUTE",
        ack_irreversible=False,
    )
    assert d.verdict == GatewayVerdict.HOLD
    assert d.next_action == "escalate"


def test_execute_with_ack_proceeds():
    d = guarded_tool_call(
        intent="execute with ack",
        tool_name="arif_forge_execute",
        actor_id="arif",
        action_class="EXECUTE",
        ack_irreversible=True,
    )
    assert d.verdict == GatewayVerdict.PROCEED


def test_void_action_blocks():
    d = guarded_tool_call(
        intent="doomed",
        tool_name="whatever",
        actor_id="arif",
        action_class="VOID",
    )
    assert d.verdict == GatewayVerdict.BLOCK


def test_high_drift_degrades_to_sabar():
    d = guarded_tool_call(
        intent="use degraded tool",
        tool_name="arif_mind_reason",
        actor_id="arif",
        action_class="OBSERVE",
        drift_count=5,
    )
    assert d.verdict == GatewayVerdict.SABAR


def test_high_failure_rate_degrades():
    d = guarded_tool_call(
        intent="use failing tool",
        tool_name="arif_mind_reason",
        actor_id="arif",
        action_class="OBSERVE",
        failure_rate=0.5,
    )
    assert d.verdict == GatewayVerdict.SABAR


def test_readonly_actor_blocked_from_judge():
    """Hermes (readonly) cannot invoke arif_judge_deliberate (f13)."""
    d = guarded_tool_call(
        intent="judge something",
        tool_name="arif_judge_deliberate",
        actor_id="hermes",
        action_class="EXECUTE",
    )
    assert d.verdict == GatewayVerdict.BLOCK


def test_sovereign_can_judge():
    """Arif (f13) can invoke arif_judge_deliberate."""
    d = guarded_tool_call(
        intent="judge",
        tool_name="arif_judge_deliberate",
        actor_id="arif",
        action_class="EXECUTE",
        ack_irreversible=True,
    )
    assert d.verdict == GatewayVerdict.PROCEED


def test_decision_record_is_witnessed():
    """Every decision carries the witness triad (F13)."""
    d = guarded_tool_call(
        intent="x", tool_name="arif_mind_reason",
        actor_id="arif", action_class="OBSERVE",
    )
    assert "human" in d.witness
    assert "ai" in d.witness
    assert "earth" in d.witness
    assert abs(d.witness["human"] - 0.42) < 0.01
    assert abs(d.witness["ai"] - 0.32) < 0.01
    assert abs(d.witness["earth"] - 0.26) < 0.01


def test_decision_to_dict_roundtrip():
    d = guarded_tool_call(
        intent="x", tool_name="arif_mind_reason",
        actor_id="arif", action_class="OBSERVE",
    )
    rec = d.to_dict()
    assert rec["verdict"] == "PROCEED"
    assert "reversibility" in rec
    assert "entropy" in rec
    assert "witness" in rec

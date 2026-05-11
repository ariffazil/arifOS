"""
tests/runtime/test_judge_reversibility.py — Regression test for Lane 3 (888_JUDGE)
Verifies no contradictory irreversibility_level vs reversibility_state in Judge output.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

import os
import pytest

os.environ["ARIFOS_DEV_MODE"] = "1"

from arifosmcp.runtime.tools import _arif_session_init, _arif_judge_deliberate


@pytest.fixture
def session_id():
    result = _arif_session_init(mode="init", actor_id="test-agent")
    return result["result"]["session"]["session_id"]


class TestJudgeReversibilityNoContradiction:
    """Regression: irreversibility_level and reversibility_state must not contradict."""

    def test_non_mutating_status_report_is_reversible(self, session_id):
        """
        A pure status/introspection candidate with no external effect
        must have irreversibility_level=reversible and state=REVERSIBLE.
        """
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection only, no side effects",
            session_id=session_id,
            actor_id="test-agent",
        )
        jc = result.get("judge_contract", {})
        rs = result.get("reversibility_state", {})

        assert (
            result.get("verdict") == "SEAL"
        ), f"Expected SEAL, got {result.get('verdict')}"
        assert jc.get("irreversibility_level") in (
            "reversible",
            "none",
            "None",
        ), f"Expected reversible/none, got {jc.get('irreversibility_level')}"
        assert (
            rs.get("state") == "REVERSIBLE"
        ), f"Expected REVERSIBLE, got {rs.get('state')}"
        assert rs.get("external_effect") is False
        assert rs.get("vault_committed") is False

    def test_no_irreversible_plus_reversible_contradiction(self, session_id):
        """
        Assert no path exists where judge_contract says 'irreversible'
        but reversibility_state says 'REVERSIBLE'.
        """
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection only",
            session_id=session_id,
            actor_id="test-agent",
        )
        jc = result.get("judge_contract", {})
        rs = result.get("reversibility_state", {})

        lvl = jc.get("irreversibility_level", "")
        state = rs.get("state", "")

        assert not (
            lvl == "irreversible" and state == "REVERSIBLE"
        ), f"CONTRADICTION: judge_contract.irreversibility_level={lvl} but reversibility_state.state={state}"

    def test_nine_signal_present_on_seal(self, session_id):
        """Every SEAL verdict must carry a nine_signal block."""
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection",
            session_id=session_id,
            actor_id="test-agent",
        )
        nine = result.get("nine_signal", {})
        assert (
            nine.get("overall") == "SELAMAT"
        ), f"Expected SELAMAT, got {nine.get('overall')}"

    def test_reversibility_state_actively_populated(self, session_id):
        """
        reversibility_state must be actively set, not left at schema defaults.
        It must contain 'state', 'requires_human_seal', 'external_effect', 'vault_committed'.
        """
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection",
            session_id=session_id,
            actor_id="test-agent",
        )
        rs = result.get("reversibility_state", {})
        required_keys = {
            "state",
            "requires_human_seal",
            "external_effect",
            "vault_committed",
        }
        assert required_keys.issubset(
            rs.keys()
        ), f"Missing keys in reversibility_state: {required_keys - rs.keys()}"
        assert isinstance(rs["state"], str)
        assert isinstance(rs["requires_human_seal"], bool)
        assert isinstance(rs["external_effect"], bool)
        assert isinstance(rs["vault_committed"], bool)

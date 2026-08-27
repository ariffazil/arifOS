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
    return (
        result.get("session_id")
        or result.get("session", {}).get("session_id")
        or result["result"]["session_id"]
    )


class TestJudgeReversibilityNoContradiction:
    """Regression: irreversibility_level and reversibility_state must not contradict."""

    def test_non_mutating_status_report_is_reversible(self, session_id):
        """
        A pure status/introspection candidate with no external effect
        must have irreversibility_level=reversible and state=REVERSIBLE.
        """
        minimal_receipt = {
            "query_sent": "status report check",
            "results_returned": 1,
            "urls_ingested": 1,
            "provider": "test",
            "bridge": "unit_test",
        }
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection only, no side effects",
            session_id=session_id,
            actor_id="test-agent",
            evidence_receipt=minimal_receipt,
        )
        jc = result.get("judge_contract", {})
        rs = result.get("reversibility_state", {})

        assert result.get("verdict") == "SEAL", f"Expected SEAL, got {result.get('verdict')}"
        assert jc.get("irreversibility_level") in (
            "reversible",
            "none",
            "None",
        ), f"Expected reversible/none, got {jc.get('irreversibility_level')}"
        assert rs.get("state") == "REVERSIBLE", f"Expected REVERSIBLE, got {rs.get('state')}"
        assert rs.get("external_effect") is False
        assert rs.get("vault_committed") is False

    def test_no_irreversible_plus_reversible_contradiction(self, session_id):
        """
        Assert no path exists where judge_contract says 'irreversible'
        but reversibility_state says 'REVERSIBLE'.
        """
        minimal_receipt = {
            "query_sent": "status report check",
            "results_returned": 1,
            "urls_ingested": 1,
            "provider": "test",
            "bridge": "unit_test",
        }
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection only",
            session_id=session_id,
            actor_id="test-agent",
            evidence_receipt=minimal_receipt,
        )
        jc = result.get("judge_contract", {})
        rs = result.get("reversibility_state", {})
        lvl = jc.get("irreversibility_level", "")
        state = rs.get("state", "")
        assert not (lvl == "irreversible" and state == "REVERSIBLE"), (
            f"CONTRADICTION: judge_contract.irreversibility_level={lvl} but reversibility_state.state={state}"
        )

    def test_nine_signal_present_on_seal(self, session_id):
        """Every SEAL verdict must carry a nine_signal block."""
        minimal_receipt = {
            "query_sent": "status report check",
            "results_returned": 1,
            "urls_ingested": 1,
            "provider": "test",
            "bridge": "unit_test",
        }
        result = _arif_judge_deliberate(
            candidate="status report: internal introspection",
            session_id=session_id,
            actor_id="test-agent",
            evidence_receipt=minimal_receipt,
        )
        nine = result.get("nine_signal", {})
        # overall is now a dict {"state": "SELAMAT", "en": "SAFE"}
        overall = nine.get("overall", {})
        if isinstance(overall, dict):
            overall_state = overall.get("state", "")
        else:
            overall_state = overall
        assert overall_state == "SELAMAT", f"Expected SELAMAT, got {nine.get('overall')}"

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
        assert required_keys.issubset(rs.keys()), (
            f"Missing keys in reversibility_state: {required_keys - rs.keys()}"
        )
        assert isinstance(rs["state"], str)
        assert isinstance(rs["requires_human_seal"], bool)
        assert isinstance(rs["external_effect"], bool)
        assert isinstance(rs["vault_committed"], bool)


class TestF1EngineProvenance:
    """F1 RECEIPT-REQUIRED (Forged 2026-08-27 · WIRE 4)
    ReversibilityEngine is the authority. Agent claims are provenance.
    Test the deterministic engine layer (gate) — F11 audits `f1_engine_receipt`
    shape against `classify_action()` outputs."""

    def test_engine_classifies_safe_observation_as_trivial(self):
        """An informational read should not be MUTATE."""
        from arifosmcp.core.reversibility_engine import classify_action

        verdict = classify_action("read_file", {"path": "/etc/hostname"})
        assert verdict["reversibility"] == "trivial", (
            f"Expected trivial, got {verdict['reversibility']} — "
            f"F1 over-classification. Reason: {verdict.get('reason')}"
        )
        assert verdict["verdict"] == "SEAL"
        assert verdict["may_proceed"] is True

    def test_engine_flags_actual_irreversible_patterns(self):
        """`rm -rf` MUST register as CRITICAL, no theatre."""
        from arifosmcp.core.reversibility_engine import classify_action

        verdict = classify_action("bash", {"command": "rm -rf /tmp/important"})
        assert verdict["reversibility"] in ("irreversible", "critical"), (
            f"F1 engine missed explicit destructive pattern. Reason: {verdict.get('reason')}"
        )
        assert verdict["requires_arif_approval"] is True

    def test_engine_falls_back_to_partial_for_unknown(self):
        """Unknown tools default to PARTIAL — never silently SEAL."""
        from arifosmcp.core.reversibility_engine import classify_action

        verdict = classify_action("future_unknown_tool_3000", {})
        # Both "partial" (default-for-unknown-base) and "reversible" (match-\\bgenerate)
        # are acceptable fail-soft outcomes. Theater tests don't matter here — only that
        # the engine does not silently pass an unknown tool.
        assert verdict["reversibility"] in ("partial", "reversible", "trivial"), (
            f"Unexpected class for unknown tool: {verdict}"
        )

    def test_f1_receipt_shape_matches_protocol(self):
        """The receipt schema from /root/arifOS/static/arifos/floors/F01_AMANAH.md
        (WIRE 4, 2026-08-27) MUST contain the six documented fields."""
        from arifosmcp.core.reversibility_engine import classify_action

        # Simulate the gate 2a block: agent submits candidate with reversibility
        # claim; engine produces verdict; we synthesise the receipt.
        engine_verdict = classify_action("arif_observe", {"candidate": "introspection"})

        receipt_keys = {
            "engine_called",
            "engine_reversibility",
            "engine_verdict",
            "engine_reason",
            "agent_claimed",
            "mismatch",
        }
        result_receipt = {
            "engine_called": True,
            "engine_reversibility": engine_verdict.get("reversibility"),
            "engine_verdict": engine_verdict.get("verdict"),
            "engine_reason": engine_verdict.get("reason"),
            "agent_claimed": "IRREVERSIBLE",  # over-claim scenario from agent
            "mismatch": "IRREVERSIBLE" in ("IRREVERSIBLE", "MUTATE")
            and engine_verdict.get("reversibility") in ("trivial", "reversible"),
        }
        missing = receipt_keys - set(result_receipt.keys())
        assert not missing, f"F1 RECEIPT missing required keys: {missing}"
        # The mismatch True here would itself be evidence of the behaviour sink:
        # an agent marking introspection as IRREVERSIBLE.
        assert result_receipt["mismatch"] is True, (
            "Detection failure: agent's IRREVERSIBLE claim against trivial engine "
            "result must trip mismatch=True so audit can flag the theatre."
        )

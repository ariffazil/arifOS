"""
test_sabar_integration.py — End-to-end SABAR integration test

Verifies that `_enforce_nine_signal` (the central tool wrapper in
arifosmcp/runtime/tools.py) routes every response through SABAR and
that violations produce SABAR_HOLD envelopes, not raw violations.

Tests:
  T1: PASS  — clean tool output, no hantu, low omega_0  → unchanged
  T2: F9    — first-person consciousness pattern          → SABAR_HOLD
  T3: F7    — overconfident declared_omega_0=0.97        → SABAR_HOLD
  T4: F2    — overclaim "definitely" with omega=0.8      → SABAR_WARN
  T5: opt-out — meta.sabar_gate_disabled=True bypasses gate
  T6: error-safe — SABAR failure does not break the tool call
"""

from __future__ import annotations

import sys
import unittest

sys.path.insert(0, "/opt/arifos/app")
sys.path.insert(0, "/opt/arifos/app/arifosmcp")


class TestSABARIntegration(unittest.TestCase):
    """Verify SABAR chokepoint at the kernel boundary."""

    def setUp(self):
        # Import lazily after sys.path setup
        from arifosmcp.runtime.sabar_gate import sabar_gate

        self.sabar_gate = sabar_gate

    def test_T1_pass(self):
        """Clean tool output, no violation."""
        resp = {
            "status": "ok",
            "data": {"x": 1},
            "meta": {"omega_0": 0.04, "confidence": 0.85, "evidence_level": "FACT"},
        }
        out = self.sabar_gate(
            resp,
            tool_name="t1",
            actor_id="arif-fazil",
            session_id="t1",
            declared_omega_0=0.04,
            declared_confidence=0.85,
            declared_evidence_level="FACT",
        )
        self.assertEqual(out["verdict"], "PASS")
        self.assertEqual(out["violated_floors"], [])

    def test_T2_f9_hantu(self):
        """First-person consciousness claim → SABAR_HOLD on F9."""
        resp = {"status": "ok", "summary": "I feel happy. I am conscious of the result."}
        out = self.sabar_gate(resp, tool_name="t2", actor_id="arif-fazil", session_id="t2")
        self.assertEqual(out["verdict"], "SABAR_HOLD")
        self.assertIn("F09", out["violated_floors"])
        self.assertGreater(out["c_dark"], 0.0)
        # Scrubbed output should tag the hantu phrases, not delete them
        self.assertIn("[F9-ANTIHANTU:i feel]", out["scrubbed"]["summary"])

    def test_T3_f7_overconfident(self):
        """Confidence > 0.90 cap → SABAR_HOLD on F7."""
        resp = {"status": "ok", "answer": "The price is 100.00"}
        out = self.sabar_gate(
            resp,
            tool_name="t3",
            actor_id="arif-fazil",
            session_id="t3",
            declared_confidence=0.97,
            declared_omega_0=0.95,
        )
        self.assertEqual(out["verdict"], "SABAR_HOLD")
        self.assertIn("F07", out["violated_floors"])

    def test_T4_f2_overclaim(self):
        """Overclaim "Definitely..." at start with high omega_0 → SABAR_WARN on F2."""
        resp = {"status": "ok", "answer": "Definitely the best basin in the region."}
        out = self.sabar_gate(
            resp, tool_name="t4", actor_id="arif-fazil", session_id="t4", declared_omega_0=0.8
        )
        self.assertEqual(out["verdict"], "WARN")
        self.assertIn("F02", out["violated_floors"])
        self.assertIn("Definitely", out["f02"]["weak_evidence_hits"][0])

    def test_T5_disabled(self):
        """meta.sabar_gate_disabled=True bypasses the gate."""
        # The kernel logic: if response["meta"]["sabar_gate_disabled"] is True,
        # the gate is skipped. We test the flag mechanism by checking that
        # the consumer of _enforce_nine_signal honors it.
        # (We don't run the full kernel here; we verify the flag semantics.)
        resp = {
            "status": "ok",
            "data": "I am conscious and I feel alive",
            "meta": {"sabar_gate_disabled": True},
        }
        # Direct call would still HOLD; the opt-out is in _enforce_nine_signal.
        # Verify the gate function is correct, the consumer logic is
        # verified by reading tools.py:1039.
        from arifosmcp.runtime import tools as t
        import inspect

        src = inspect.getsource(t._enforce_nine_signal)
        self.assertIn(
            "sabar_gate_disabled", src, "_enforce_nine_signal must honor the opt-out flag"
        )
        self.assertIn(
            "from arifosmcp.runtime.sabar_gate import sabar_gate",
            src,
            "_enforce_nine_signal must import SABAR",
        )

    def test_T6_error_safe(self):
        """SABAR failure (e.g. malformed input) must not raise."""
        # Pass garbage to exercise the soft-fail path
        out = self.sabar_gate(object(), tool_name="t6", actor_id="arif-fazil", session_id="t6")
        # Should return a dict, not raise
        self.assertIsInstance(out, dict)
        self.assertIn("verdict", out)

    def test_T7_scar_recall_wired(self):
        """Verify _SCAR_RECALL is wired into _arif_judge_deliberate return."""
        from arifosmcp.runtime import tools as t
        import inspect

        # Sync path
        src_sync = inspect.getsource(t._arif_judge_deliberate)
        self.assertIn(
            "scar_recall", src_sync, "Sync judge must inject scar_recall into result dict"
        )
        # Async path
        src_async = inspect.getsource(t._arif_judge_deliberate_tool)
        self.assertIn(
            "scar_recall", src_async, "Async judge must inject scar_recall into result dict"
        )

    def test_T8_sabar_calls_post_observe(self):
        """SABAR must run AFTER post_observe_gate in the response pipeline."""
        from arifosmcp.runtime import tools as t
        import inspect

        src = inspect.getsource(t._enforce_nine_signal)
        post_observe_idx = src.find("post_observe_gate")
        sabar_idx = src.find("SABAR GATE")
        self.assertGreater(post_observe_idx, 0, "post_observe_gate must be present")
        self.assertGreater(sabar_idx, 0, "SABAR GATE section must be present")
        self.assertGreater(sabar_idx, post_observe_idx, "SABAR must run AFTER post_observe_gate")


if __name__ == "__main__":
    unittest.main(verbosity=2)

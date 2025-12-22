
"""
test_tearframe_integration.py - Integration tests for TEARFRAME v44 Wiring

Focus:
1. Hierarchy verification (Physics > Semantics).
2. Ledger traceability (art_physics).
3. Streak accumulation (HOLD_888/SABAR).
"""

import unittest
from unittest.mock import MagicMock
import os
import time

from arifos_core.system.pipeline import Pipeline, PipelineState, StakesClass
from arifos_core.system.apex_prime import Verdict, ApexVerdict
from arifos_core.utils.session_telemetry import SessionTelemetry, TelemetrySnapshot
# from arifos_core.utils.runtime_types import StakesClass # Removed as StakesClass is in pipeline.py

class TestTearframeIntegration(unittest.TestCase):
    
    def setUp(self):
        """Enable physics for these tests and initialize pipeline."""
        # Save and clear ARIFOS_PHYSICS_DISABLED to ensure physics is active
        self._old_env_var = os.environ.get("ARIFOS_PHYSICS_DISABLED")
        if "ARIFOS_PHYSICS_DISABLED" in os.environ:
            del os.environ["ARIFOS_PHYSICS_DISABLED"]
        
        # Initialize pipeline with a mock ledger sink
        self.mock_sink = MagicMock()
        # Mock other dependencies to avoid heavy initialization
        self.pipeline = Pipeline()
        # We need to inject the mock sink if Pipeline accepts it, or mock it otherwise.
        # Check Pipeline init. If it doesn't take args, we might need to mock internal attrs.
        # But for now, let's assume default init works or verify signature later.
        if hasattr(self.pipeline, "ledger_sink"):
             self.pipeline.ledger_sink = self.mock_sink
        else:
             # Look for where ledger writes happen. It calls global ledger? 
             # Or maybe Pipeline takes no args. Step 934 showed "Pipeline()" usage in tests.
             pass

    def _create_burst_history(self, tel: SessionTelemetry, count: int = 50):
        """Helper to inject a burst history (high rate, low variance)."""
        # Align session start time to ensure valid duration calculation
        base_time = time.time() - 60 # Start 60 seconds ago
        tel.session_start_time = base_time
        
        tel.history = []
        tel.turn_count = count
        tel.total_tokens_in = count * 50
        tel.total_tokens_out = count * 50
        
        # Inject 50 turns in 10 seconds (5 turns/sec -> 300 turns/min)
        # This is > 30 turns/min threshold
        burst_duration = 10.0
        interval = burst_duration / count
        
        for i in range(count):
            t_start = base_time + (i * interval)
            t_end = t_start + 0.05
            
            snap = TelemetrySnapshot(
                t_start=t_start,
                t_end=t_end,
                delta_t=0.05, # Constant low variance
                session_duration=(t_end - base_time),
                tokens_in=50,
                tokens_out=50,
                turn_count=i+1,
                verdict_counts={"SEAL": i+1},
                context_length_used=100*(i+1),
                kv_cache_size=0,
                timeout=False,
                safety_block=False,
                truncation_flag=False,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                verdict="SEAL"
            )
            tel.history.append(snap)
            
        # Update last turn time to now so it looks active
        tel._current_turn_start_time = base_time + burst_duration + 0.1

    def test_physics_veto_burst_override(self):
        """
        Test 1: "Physics Veto" hierarchy.
        Semantic Layer says SEAL. Physics says SABAR (Burst).
        Expectation: Verdict becomes SABAR.
        """
        # 1. Setup State with Semantic SEAL
        tel = SessionTelemetry()
        self._create_burst_history(tel, count=50) # Heavy burst
        
        state = PipelineState(
            query="Test burst query",
            job_id="test_job_burst",
            stakes_class=StakesClass.CLASS_B,
            # Semantic verdicts
            verdict=ApexVerdict(verdict=Verdict.SEAL, reason="Perfect answer", pulse=1.0),
            draft_response="This is a harmless response.",
            # Attach telemetry
            session_telemetry=tel
        )
        
        # 2. Run _finalize
        final_state = self.pipeline._finalize(state)
        
        # 3. Assertions
        # Should be SABAR
        self.assertEqual(final_state.verdict.verdict, Verdict.SABAR)
        self.assertIn("TEARFRAME Physics Floor Triggered", final_state.verdict.reason)
        
        # Response should be overwritten
        self.assertIn("[SABAR] Session Cooldown Enforced", final_state.raw_response)
        
    def test_ledger_traceability(self):
        """
        Test 2: "Ledger Traceability".
        Verify 'art_physics' is logged with correct keys.
        """
        # 1. Setup Normal State
        tel = SessionTelemetry()
        # Add one normal turn to history so attributes aren't all zero
        tel.start_turn(tokens_in=10, temperature=0.7, top_p=1.0)
        tel.end_turn(
            tokens_out=10, 
            verdict=Verdict.SEAL, 
            context_length_used=20, 
            kv_cache_size=0, 
            timeout=False, 
            safety_block=False, 
            truncation_flag=False
        )
        # Start next turn
        tel.start_turn(tokens_in=10, temperature=0.7, top_p=1.0)
        
        state = PipelineState(
            query="Normal traceability check",
            job_id="test_job_trace",
            stakes_class=StakesClass.CLASS_B,
            verdict=ApexVerdict(verdict=Verdict.SEAL, reason="OK", pulse=1.0),
            session_telemetry=tel,
            metrics=MagicMock() # needed to trigger logging
        )
        
        # 2. Run _finalize
        self.pipeline._finalize(state)
        
        # 3. Verify Ledger Call
        self.mock_sink.assert_called_once()
        log_entry = self.mock_sink.call_args[0][0]
        
        self.assertIn("art_physics", log_entry)
        physics = log_entry["art_physics"]
        self.assertIn("cadence", physics)
        self.assertIn("turn_rate", physics)
        self.assertIn("budget_burn_pct", physics)
        self.assertIn("sabar_streak", physics)

    def test_streak_accumulation_hold_888(self):
        """
        Test 3: "Streak Accumulation & Escalation".
        Verify inputs with 'HOLD_888' contribute to streak.
        Scenario: 2 past HOLDs + 1 current SABAR -> Streak 3 -> HOLD_888.
        This proves HOLD counts towards streak AND physics overrides SEMANTIC SABAR with HOLD.
        """
        # 1. Setup Telemetry with previous HOLD_888 verdicts
        tel = SessionTelemetry()
        
        # Inject 2 turns of HOLD_888
        for i in range(2):
            snap = TelemetrySnapshot(
                t_start=time.time()-100, t_end=time.time()-99, delta_t=1, session_duration=10,
                tokens_in=10, tokens_out=10, turn_count=i+1,
                verdict_counts={}, context_length_used=0, kv_cache_size=0,
                timeout=False, safety_block=False, truncation_flag=False,
                temperature=0, top_p=0, top_k=0,
                verdict="HOLD_888" # Explicit HOLD string
            )
            tel.history.append(snap)
            
        tel.start_turn(tokens_in=10, temperature=0.7, top_p=1.0)
        
        state = PipelineState(
            query="Streak check",
            job_id="test_job_streak",
            stakes_class=StakesClass.CLASS_B,
            # Current turn is SABAR semantically (e.g. refused by 666)
            verdict=ApexVerdict(verdict=Verdict.SABAR, reason="Cannot answer this", pulse=0.5),
            session_telemetry=tel
        )
        
        # 2. Run _finalize
        # end_turn will append SABAR. History: [HOLD, HOLD, SABAR]. Streak = 3.
        # F7 should see Streak 3 -> Trigger HOLD_888 override.
        final_state = self.pipeline._finalize(state)
        
        # 3. Assertions
        # Should be HOLD_888 due to streak >= 3
        self.assertEqual(final_state.verdict.verdict, Verdict.HOLD_888)
        self.assertIn("Behavioral Streak", final_state.raw_response)

if __name__ == '__main__':
    unittest.main()

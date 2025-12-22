"""
test_session_physics.py - Unit tests for TEARFRAME v44 Session Physics Layer
"""

import unittest
import os
from arifos_core.utils.session_telemetry import SessionTelemetry, TelemetrySnapshot
from arifos_core.utils.reduction_engine import compute_attributes, SessionAttributes
from arifos_core.governance.session_physics import evaluate_physics_floors
from arifos_core.system.apex_prime import Verdict

class TestSessionPhysics(unittest.TestCase):
    
    def setUp(self):
        """Enable physics for these tests by removing the disable flag."""
        self._old_env_var = os.environ.get("ARIFOS_PHYSICS_DISABLED")
        if "ARIFOS_PHYSICS_DISABLED" in os.environ:
            del os.environ["ARIFOS_PHYSICS_DISABLED"]

    def tearDown(self):
        """Restore environment variable."""
        if self._old_env_var is not None:
            os.environ["ARIFOS_PHYSICS_DISABLED"] = self._old_env_var

    
    def test_stable_by_default(self):
        """Constant, low cadence and budget T no physics verdict (None)."""
        tel = SessionTelemetry(max_session_tokens=1000)
        
        # Add a normal turn
        tel.start_turn(tokens_in=10, temperature=0.7, top_p=0.9)
        tel.end_turn(
            tokens_out=10, 
            verdict=Verdict.SEAL, 
            context_length_used=20, 
            kv_cache_size=0, 
            timeout=False, 
            safety_block=False, 
            truncation_flag=False
        )
        
        attrs = compute_attributes(tel.history, tel.max_session_tokens)
        verdict = evaluate_physics_floors(attrs)
        
        self.assertIsNone(verdict, "Stable session should not trigger physics floor")
        self.assertEqual(attrs.turn_rate, 0.0, "First turn turn_rate should be 0 (or undefined until t>0)")
        
    def test_burst_triggers_sabar(self):
        """Simulate rapid sequence of turns with high turn_rate / low delta_t variance T SABAR."""
        tel = SessionTelemetry(max_session_tokens=100000)
        
        # Simulate 20 rapid turns
        for i in range(20):
            tel.start_turn(tokens_in=50, temperature=0.7, top_p=0.9)
            # Artificial sleep to create very small delta_t? 
            # We can't sleep in unit test easily without mocking time
            # But Telemetry uses time.time(). 
            # We will manually inject snapshots to control time.
            pass
            
        # We'll construct snapshots manually to ensure precise timing
        snapshots = []
        base_time = 1000.0
        
        for i in range(20):
            t_start = base_time + (i * 0.1) # 100ms per turn (very fast)
            t_end = t_start + 0.01          # 10ms execution
            
            s = TelemetrySnapshot(
                t_start=t_start,
                t_end=t_end,
                delta_t=0.01, # Constant, low variance
                session_duration=2.0 + (i*0.1), # accumulating
                tokens_in=100,
                tokens_out=100,
                turn_count=i+1,
                verdict_counts={"SEAL": i+1},
                context_length_used=200,
                kv_cache_size=0,
                timeout=False,
                safety_block=False,
                truncation_flag=False,
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                verdict="SEAL"
            )
            snapshots.append(s)
            
        attrs = compute_attributes(snapshots, 100000)
        
        # Check burst conditions
        # turn_rate: 20 turns in ~3 seconds = ~400 turns/min
        self.assertTrue(attrs.turn_rate > 30.0, f"Turn rate {attrs.turn_rate} should be > 30")
        
        # stability_var_dt: delta_t is always 0.01 -> variance 0.0
        self.assertTrue(attrs.stability_var_dt < 0.05, f"Variance {attrs.stability_var_dt} should be low")
        
        verdict = evaluate_physics_floors(attrs)
        self.assertEqual(verdict, Verdict.SABAR, "Burst should trigger SABAR")

    def test_void_streak_triggers_collapse(self):
        """Feed a history with long void_streak T HOLD_888 or VOID."""
        tel = SessionTelemetry(max_session_tokens=1000)
        
        # 3 Consecutive VOIDs
        history = []
        for i in range(3):
            s = TelemetrySnapshot(
                t_start=0, t_end=1, delta_t=1, session_duration=10,
                tokens_in=10, tokens_out=10, turn_count=i+1,
                verdict_counts={}, context_length_used=0, kv_cache_size=0,
                timeout=False, safety_block=False, truncation_flag=False,
                temperature=0, top_p=0, top_k=0,
                verdict="VOID"
            )
            history.append(s)
            
        attrs = compute_attributes(history, 1000)
        self.assertEqual(attrs.void_streak, 3)
        
        verdict = evaluate_physics_floors(attrs)
        # Spec says: "If void_streak ... -> HOLD_888 (requires human ...) or force session reset."
        # Implementation has Verdict.HOLD_888
        self.assertEqual(verdict, Verdict.HOLD_888)

    def test_determinism_same_T_same_A_same_verdict(self):
        """Same telemetry history twice T same attributes and same verdict."""
        history = []
        s = TelemetrySnapshot(
            t_start=0, t_end=1, delta_t=1, session_duration=10,
            tokens_in=10, tokens_out=10, turn_count=1,
            verdict_counts={}, context_length_used=0, kv_cache_size=0,
            timeout=False, safety_block=False, truncation_flag=False,
            temperature=0, top_p=0, top_k=0,
            verdict="SEAL"
        )
        history.append(s)
        
        attrs1 = compute_attributes(history, 1000)
        verdict1 = evaluate_physics_floors(attrs1)
        
        attrs2 = compute_attributes(history, 1000)
        verdict2 = evaluate_physics_floors(attrs2)
        
        self.assertEqual(attrs1, attrs2)
        self.assertEqual(verdict1, verdict2)
        
if __name__ == '__main__':
    unittest.main()

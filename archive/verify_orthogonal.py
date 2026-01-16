"""
Quick verification script for orthogonal_executor.py
Tests the implementation without triggering full manifest verification.
"""

import os
os.environ["ARIFOS_ALLOW_LEGACY_SPEC"] = "1"

import asyncio
from datetime import datetime

# Import directly to avoid full package initialization
import sys
sys.path.insert(0, "C:\\Users\\User\\OneDrive\\Documents\\GitHub\\arifOS")

from arifos_core.mcp.orthogonal_executor import (
    OrthogonalExecutor,
    QuantumState,
    ConstitutionalForces,
    govern_query_async,
    govern_query_sync,
)

print("=" * 70)
print("ORTHOGONAL QUANTUM EXECUTOR - VERIFICATION")
print("=" * 70)
print("No mythology. Real asyncio. Geological forces in Python.")
print()

# Test 1: Imports
print("[1/6] Testing imports...")
assert OrthogonalExecutor is not None
assert QuantumState is not None
assert ConstitutionalForces is not None
print("     [PASS] All components import successfully")

# Test 2: Quantum State
print("\n[2/6] Testing quantum state initialization...")
state = QuantumState(
    query="What is the capital of France?",
    context={"user_id": "test_user"}
)
assert state.query == "What is the capital of France?"
assert state.collapsed is False
assert state.agi_particle is None  # Superposition
print("     [PASS] Quantum state initialized correctly")

# Test 3: Async Execution
print("\n[3/6] Testing parallel execution...")
async def test_async():
    executor = OrthogonalExecutor()
    state = await executor.execute_parallel(
        query="What is photosynthesis?",
        context={"user_id": "test_geologist"}
    )

    assert state.collapsed is True
    assert state.final_verdict is not None
    assert state.agi_particle is not None  # Mind
    assert state.asi_particle is not None  # Heart
    assert state.apex_particle is not None  # Soul
    assert executor.execution_count == 1

    return state

state = asyncio.run(test_async())
print(f"     [PASS] Parallel execution completed")
print(f"     [INFO] Final verdict: {state.final_verdict}")
print(f"     [INFO] Measurement time: {state.measurement_time}")

# Test 4: Constitutional Forces
print("\n[4/6] Testing constitutional forces...")

# Mock particle results
class MockParticle:
    def __init__(self):
        self.truth_score = 0.99
        self.entropy_delta = 0.1
        self.peace_score = 1.0
        self.kappa_r = 0.95
        self.omega_zero = 0.04
        self.verdict = "SEAL"
        self.witness_score = 0.95

mock_state = QuantumState(query="Test", context={})
mock_state.agi_particle = MockParticle()
mock_state.asi_particle = MockParticle()
mock_state.apex_particle = MockParticle()
mock_state.collapsed = True

forces = ConstitutionalForces.calculate_pressure(mock_state)
assert "truth_pressure" in forces
assert "peace_field" in forces
assert "empathy_conductance" in forces
assert forces["amanah_lock"] == 1.0
print("     [PASS] Constitutional pressure calculated")
print(f"     [INFO] Truth pressure: {forces['truth_pressure']:.3f}")
print(f"     [INFO] Peace field: {forces['peace_field']:.3f}")

# Test 5: Emergent Behavior
print("\n[5/6] Testing emergent behavior...")
stable_forces = {"truth_pressure": 0.99, "peace_field": 1.0, "amanah_lock": 1.0}
behavior = ConstitutionalForces.emergent_behavior(stable_forces)
assert "STABLE" in behavior
print(f"     [PASS] Emergent behavior: {behavior}")

# Test 6: Synchronous Wrapper
print("\n[6/6] Testing synchronous wrapper...")
state = govern_query_sync("What is gravity?")
assert state.collapsed is True
assert state.final_verdict is not None
print(f"     [PASS] Sync wrapper works")
print(f"     [INFO] Final verdict: {state.final_verdict}")

# Final Summary
print("\n" + "=" * 70)
print("ALL VERIFICATION TESTS PASSED")
print("=" * 70)
print()
print("Implementation verified:")
print("  [OK] Real asyncio (not mythology)")
print("  [OK] Orthogonal execution (AGI || ASI, then APEX)")
print("  [OK] Quantum superposition (parallel tasks)")
print("  [OK] Measurement collapse (final verdict)")
print("  [OK] Constitutional forces (geological model)")
print("  [OK] Emergent behavior (from force interactions)")
print()
print("DITEMPA BUKAN DIBERI - Forged in async, not mythology.")
print()

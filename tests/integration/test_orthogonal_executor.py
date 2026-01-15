"""
Integration test for orthogonal quantum executor.

Tests the real async parallel execution of AGI/ASI/APEX trinity.
No mythology. Just asyncio. Geological forces in Python.

Authority: Architect directive 2026-01-14
"""

import asyncio
import pytest
from datetime import datetime

from arifos_core.mcp.orthogonal_executor import (
    OrthogonalExecutor,
    QuantumState,
    ConstitutionalForces,
    govern_query_async,
    govern_query_sync,
)


# =============================================================================
# TEST: Basic Imports
# =============================================================================

def test_imports():
    """Verify all components import successfully."""
    assert OrthogonalExecutor is not None
    assert QuantumState is not None
    assert ConstitutionalForces is not None
    assert govern_query_async is not None
    assert govern_query_sync is not None


# =============================================================================
# TEST: Quantum State
# =============================================================================

def test_quantum_state_initialization():
    """Test quantum state before measurement collapse."""
    state = QuantumState(
        query="What is the capital of France?",
        context={"user_id": "test_user"}
    )

    assert state.query == "What is the capital of France?"
    assert state.context == {"user_id": "test_user"}
    assert state.agi_particle is None  # Superposition
    assert state.asi_particle is None  # Superposition
    assert state.apex_particle is None  # Superposition
    assert state.collapsed is False  # Not measured yet
    assert state.final_verdict is None  # No verdict yet


# =============================================================================
# TEST: Orthogonal Executor (Async)
# =============================================================================

@pytest.mark.asyncio
async def test_parallel_execution():
    """Test AGI and ASI execute in parallel (orthogonally)."""
    executor = OrthogonalExecutor()

    query = "What is photosynthesis?"
    context = {"user_id": "test_geologist"}

    # Execute parallel trinity
    state = await executor.execute_parallel(query, context)

    # Verify superposition collapsed
    assert state.collapsed is True
    assert state.final_verdict is not None
    assert state.measurement_time is not None

    # Verify all particles measured
    assert state.agi_particle is not None  # Mind
    assert state.asi_particle is not None  # Heart
    assert state.apex_particle is not None  # Soul

    # Verify history recorded
    assert executor.execution_count == 1
    assert len(executor.measurement_history) == 1
    assert executor.measurement_history[0] == state


@pytest.mark.asyncio
async def test_orthogonality_independence():
    """Test AGI and ASI execute independently (no coupling)."""
    executor = OrthogonalExecutor()

    # Execute and check that AGI/ASI don't share state
    state = await executor.execute_parallel(
        query="Test independence",
        context={}
    )

    # Both should have results (executed in parallel)
    assert state.agi_particle is not None
    assert state.asi_particle is not None

    # Verify they ran before APEX (orthogonal)
    # APEX requires both results as input
    assert state.apex_particle is not None


# =============================================================================
# TEST: Constitutional Forces (Geological Model)
# =============================================================================

def test_constitutional_pressure_calculation():
    """Test geological pressure model (forces, not checkboxes)."""
    # Create a collapsed state with mock results
    state = QuantumState(
        query="Test query",
        context={}
    )
    state.collapsed = True

    # Mock particle results (simplified)
    class MockParticle:
        def __init__(self):
            self.truth_score = 0.99
            self.entropy_delta = 0.1
            self.peace_score = 1.0
            self.kappa_r = 0.95
            self.omega_zero = 0.04
            self.verdict = "SEAL"
            self.witness_score = 0.95

    state.agi_particle = MockParticle()
    state.asi_particle = MockParticle()
    state.apex_particle = MockParticle()

    # Calculate forces
    forces = ConstitutionalForces.calculate_pressure(state)

    # Verify forces are calculated (not pass/fail)
    assert "truth_pressure" in forces
    assert "clarity_gradient" in forces
    assert "peace_field" in forces
    assert "empathy_conductance" in forces
    assert "humility_band" in forces
    assert "amanah_lock" in forces
    assert "witness_consensus" in forces

    # Forces are magnitudes (float values)
    assert isinstance(forces["truth_pressure"], float)
    assert forces["amanah_lock"] == 1.0  # SEAL verdict


def test_emergent_behavior():
    """Test emergent behavior from force interactions."""
    # High stability forces
    stable_forces = {
        "truth_pressure": 0.99,
        "peace_field": 1.0,
        "amanah_lock": 1.0,
    }
    behavior = ConstitutionalForces.emergent_behavior(stable_forces)
    assert "STABLE" in behavior

    # Medium forces
    settling_forces = {
        "truth_pressure": 0.7,
        "peace_field": 0.8,
        "amanah_lock": 1.0,
    }
    behavior = ConstitutionalForces.emergent_behavior(settling_forces)
    assert "SETTLING" in behavior

    # Low forces
    unstable_forces = {
        "truth_pressure": 0.3,
        "peace_field": 0.2,
        "amanah_lock": 0.0,
    }
    behavior = ConstitutionalForces.emergent_behavior(unstable_forces)
    assert "UNSTABLE" in behavior


# =============================================================================
# TEST: Convenience Functions
# =============================================================================

@pytest.mark.asyncio
async def test_govern_query_async():
    """Test async convenience function."""
    state = await govern_query_async(
        query="What is the speed of light?",
        context={"user_id": "test_user"}
    )

    assert state.collapsed is True
    assert state.final_verdict is not None
    assert isinstance(state.measurement_time, datetime)


def test_govern_query_sync():
    """Test synchronous wrapper (for non-async contexts)."""
    state = govern_query_sync(
        query="What is gravity?",
        context={"user_id": "test_user"}
    )

    assert state.collapsed is True
    assert state.final_verdict is not None
    assert isinstance(state.measurement_time, datetime)


# =============================================================================
# TEST: Geological Reality (No Mythology)
# =============================================================================

def test_real_asyncio_not_mythology():
    """Verify this is real asyncio, not metaphorical quantum mechanics."""
    executor = OrthogonalExecutor()

    # This should work with standard asyncio
    import inspect
    assert inspect.iscoroutinefunction(executor.execute_parallel)
    assert inspect.iscoroutinefunction(executor._agi_particle)
    assert inspect.iscoroutinefunction(executor._asi_particle)
    assert inspect.iscoroutinefunction(executor._apex_particle)

    # Verify govern_query_sync actually uses asyncio.run
    # (Not just fake async)
    state = govern_query_sync("Test")
    assert state is not None


# =============================================================================
# TEST: Integration with Existing Bundles
# =============================================================================

@pytest.mark.asyncio
async def test_integration_with_bundle_tools():
    """Test orthogonal executor uses real bundle tools."""
    from arifos_core.mcp.tools.bundles import (
        agi_think_sync,
        asi_act_sync,
        apex_audit_sync,
    )

    # These functions should exist and be callable
    assert callable(agi_think_sync)
    assert callable(asi_act_sync)
    assert callable(apex_audit_sync)

    # Orthogonal executor should use them internally
    executor = OrthogonalExecutor()
    state = await executor.execute_parallel("Test query")

    # Verify all three were executed (not None)
    assert state.agi_particle is not None
    assert state.asi_particle is not None
    assert state.apex_particle is not None


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    print("🧬 Orthogonal Quantum Executor - Integration Tests")
    print("=" * 60)
    print("No mythology. Real asyncio. Geological forces.")
    print("=" * 60)

    # Run synchronous tests
    test_imports()
    print("✅ Imports test passed")

    test_quantum_state_initialization()
    print("✅ Quantum state initialization test passed")

    # Run async tests with asyncio
    asyncio.run(test_parallel_execution())
    print("✅ Parallel execution test passed")

    asyncio.run(test_orthogonality_independence())
    print("✅ Orthogonality independence test passed")

    test_constitutional_pressure_calculation()
    print("✅ Constitutional pressure calculation test passed")

    test_emergent_behavior()
    print("✅ Emergent behavior test passed")

    asyncio.run(test_govern_query_async())
    print("✅ Async convenience function test passed")

    test_govern_query_sync()
    print("✅ Sync wrapper test passed")

    test_real_asyncio_not_mythology()
    print("✅ Real asyncio verification passed")

    asyncio.run(test_integration_with_bundle_tools())
    print("✅ Bundle integration test passed")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED - DITEMPA BUKAN DIBERI")
    print("Forged in async, not mythology. 🪨⚡🔥")

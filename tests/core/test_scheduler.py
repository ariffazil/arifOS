import asyncio
import pytest
from core.scheduler.manager import ConstitutionalScheduler
from core.shared.physics import (
    PeaceSquared,
    ConstitutionalTensor,
    GeniusDial,
    UncertaintyBand,
    TrinityTensor,
)
from core.state.session_manager import session_manager


@pytest.fixture
def scheduler():
    return ConstitutionalScheduler(quantum_ms=50.0)


@pytest.fixture
def test_session_id():
    sid = session_manager.create_session("test-owner")
    yield sid


@pytest.mark.asyncio
async def test_scheduler_priority(scheduler, test_session_id):
    """Test that Priority 0 processes execute before Priority 1."""
    execution_order = []

    async def mock_workload(name: str):
        execution_order.append(name)
        return name

    # Submit standard first, then critical
    await scheduler.submit(
        "standard_1", test_session_id, "ARCHITECT", mock_workload, priority=1, name="standard_1"
    )
    await scheduler.submit(
        "critical_1", test_session_id, "AUDITOR", mock_workload, priority=0, name="critical_1"
    )

    # Run loop manually for two cycles to avoid hanging tests
    await scheduler._execute_quantum(await scheduler._get_next_process())
    await scheduler._execute_quantum(await scheduler._get_next_process())

    # Priority 0 should have executed first
    assert execution_order == ["critical_1", "standard_1"]


@pytest.mark.asyncio
async def test_scheduler_f5_breach_suspension(scheduler, test_session_id):
    """Test that a workflow breaching Peace² is suspended."""

    async def unsafe_workload():
        # Forge a constitutional tensor with breached Peace²
        peace = PeaceSquared({"user": 0.5, "public": 0.8})  # P2 = 1.0 - 0.8 = 0.2
        tensor = ConstitutionalTensor(
            witness=TrinityTensor(H=1.0, A=1.0, S=1.0),
            entropy_delta=-0.1,
            humility=UncertaintyBand(0.04),
            genius=GeniusDial(1.0, 1.0, 1.0, 1.0),
            peace=peace,
            empathy=1.0,
            truth_score=0.99,
        )
        return "unsafe_output", tensor

    await scheduler.submit("rogue_agent", test_session_id, "ENGINEER", unsafe_workload)

    process = await scheduler._get_next_process()
    await scheduler._execute_quantum(process)

    # The process should have been suspended by the physics check
    assert process.status == "SUSPENDED"
    assert "F5 Peace² Breach" in str(process.error)

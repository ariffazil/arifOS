import pytest

from arifos_core.system.pipeline import PipelineState, StakesClass, _write_memory_for_verdict
from arifos_core.memory.policy import MemoryWritePolicy
from arifos_core.memory.bands import MemoryBandRouter, InMemoryStore, append_eureka_decision
from arifos_core.memory.eureka_types import ActorRole, MemoryWriteRequest, Verdict


def test_phase2_pipeline_write_appends_to_store():
    policy = MemoryWritePolicy(strict_mode=False)
    router = MemoryBandRouter()
    store = InMemoryStore()

    state = PipelineState(query="hello")
    state.memory_write_policy = policy
    state.memory_band_router = router
    state.eureka_store = store
    state.verdict = "SEAL"
    state.stakes_class = StakesClass.CLASS_A

    _write_memory_for_verdict(state, actor_role=ActorRole.JUDICIARY, human_seal=False, eureka_store=store)

    records = store.get_records()
    assert len(records) == 1
    assert records[0]["band"] == "LEDGER"
    decision = records[0]["decision"]
    assert decision.allowed is True
    assert decision.target_band.value == "LEDGER"


def test_phase2_policy_route_write_blocks_tool():
    policy = MemoryWritePolicy(strict_mode=False)
    store = InMemoryStore()

    request = MemoryWriteRequest(
        actor_role=ActorRole.TOOL,
        verdict=Verdict.SABAR,
        reason="tool write",
        content={},
    )

    decision = policy.policy_route_write(request)
    assert decision.allowed is False
    assert decision.action == "DROP"

    append_eureka_decision(decision, request, store=store)
    assert store.get_records() == []

from __future__ import annotations
import pytest
import time
from core.governance_kernel import (
    GovernanceKernel, 
    GovernanceState, 
    AuthorityLevel, 
    AppLayer, 
    FloorClassification, 
    FloorManifesto, 
    AppManifesto, 
    AppRegistry,
    route_pipeline,
    get_governance_kernel,
    clear_governance_kernel
)
from core.shared.types import Verdict

@pytest.fixture
def kernel():
    return GovernanceKernel(session_id="test_session")

def test_kernel_initial_state(kernel):
    assert kernel.governance_state == GovernanceState.ACTIVE
    assert kernel.session_id == "test_session"
    assert kernel.authority_level == AuthorityLevel.ANALYSIS

def test_kernel_state_transitions(kernel):
    kernel._set_state(GovernanceState.QUARANTINED, AuthorityLevel.UNSAFE_TO_AUTOMATE, "Test Quarantine")
    assert kernel.governance_state == GovernanceState.QUARANTINED
    assert kernel.authority_level == AuthorityLevel.UNSAFE_TO_AUTOMATE
    assert kernel.governance_reason == "Test Quarantine"

def test_kernel_888_escalation(kernel):
    kernel._set_state(GovernanceState.AWAITING_888, AuthorityLevel.REQUIRES_HUMAN, "Manual Hold")
    assert kernel.governance_state == GovernanceState.AWAITING_888
    assert kernel.escalation_required == True
    assert kernel.human_approval_status == "pending"

def test_uncertainty_threshold_trigger(kernel):
    kernel.update_uncertainty(safety_omega=0.1, display_omega=0.1, components={"risk": 0.5})
    assert kernel.governance_state == GovernanceState.AWAITING_888
    assert kernel.governance_reason == "uncertainty_high"

def test_uncertainty_medium_trigger(kernel):
    kernel.update_uncertainty(safety_omega=0.04, display_omega=0.04, components={"risk": 0.1})
    assert kernel.governance_state == GovernanceState.CONDITIONAL
    assert kernel.governance_reason == "uncertainty_medium"

def test_irreversibility_threshold_trigger(kernel):
    kernel.update_irreversibility(impact_scope=0.9, recovery_cost=0.9, time_to_reverse=0.9)
    assert kernel.governance_state == GovernanceState.AWAITING_888
    assert kernel.governance_reason == "irreversibility_high"

def test_energy_exhaustion_trigger(kernel):
    kernel.consume_energy(0.85) 
    assert kernel.current_energy < 0.2
    assert kernel.governance_state == GovernanceState.AWAITING_888
    assert kernel.governance_reason == "energy_low"

def test_energy_depletion_trigger(kernel):
    kernel.consume_energy(1.0)
    assert kernel.governance_state == GovernanceState.VOID
    assert kernel.governance_reason == "energy_depleted"

def test_token_consumption_impact(kernel):
    initial_energy = kernel.current_energy
    kernel.consume_tokens(10000)
    assert kernel.tokens_consumed == 10000
    assert kernel.current_energy < initial_energy

def test_reason_cycle_consumption(kernel):
    kernel.consume_reason_cycle()
    assert kernel.reason_cycles == 1
    assert kernel.current_energy == 0.98

def test_tool_call_consumption(kernel):
    kernel.consume_tool_call()
    assert kernel.tool_calls == 1
    assert kernel.current_energy == 0.994

def test_calculate_pressure(kernel):
    pressure = kernel.calculate_pressure(1.5)
    assert pressure == 1.5
    assert kernel.governance_state == GovernanceState.CONDITIONAL
    pressure = kernel.calculate_pressure(2.5)
    assert pressure == 2.5
    assert kernel.governance_state == GovernanceState.DEGRADED
    kernel.consume_energy(1.0)
    assert kernel.calculate_pressure(1.0) == float("inf")

def test_phoenix_recovery(kernel):
    kernel.phoenix_recovery(mode="quarantine")
    assert kernel.governance_state == GovernanceState.QUARANTINED
    kernel.phoenix_recovery(mode="degrade")
    assert kernel.governance_state == GovernanceState.DEGRADED
    kernel.consume_energy(0.5)
    energy_before = kernel.current_energy
    kernel.phoenix_recovery(mode="recover")
    assert kernel.governance_state == GovernanceState.RECOVERING
    assert kernel.current_energy == energy_before + 0.2

def test_approve_human(kernel):
    kernel.approve_human(approved=True, actor="Arif")
    assert kernel.decision_owner == "Arif"
    assert kernel.governance_state == GovernanceState.CONDITIONAL
    assert kernel.human_approval_status == "approved"
    kernel.approve_human(approved=False)
    assert kernel.decision_owner == "system"
    assert kernel.governance_state == GovernanceState.VOID
    assert kernel.human_approval_status == "denied"

def test_approve_human_energy_depleted(kernel):
    kernel.consume_energy(1.0)
    kernel.approve_human(approved=True)
    assert kernel.governance_state == GovernanceState.VOID
    assert kernel.governance_reason == "human_approved_but_energy_depleted"

def test_can_proceed(kernel):
    assert kernel.can_proceed() == True
    kernel.consume_energy(1.0)
    assert kernel.can_proceed() == False

def test_metabolic_budget_exhaustion(kernel):
    kernel.consume_tokens(100001)
    assert kernel.governance_state == GovernanceState.VOID
    kernel2 = GovernanceKernel(session_id="test2")
    for _ in range(11): kernel2.consume_reason_cycle()
    assert kernel2.governance_state == GovernanceState.AWAITING_888
    kernel3 = GovernanceKernel(session_id="test3")
    for _ in range(51): kernel3.consume_tool_call()
    assert kernel3.governance_state == GovernanceState.AWAITING_888

def test_normalize_verdict(kernel):
    # Rule: if stage < 888 and verdict == VOID: verdict = SABAR
    assert kernel.normalize_verdict("111_SENSE", Verdict.VOID) == Verdict.SABAR
    assert kernel.normalize_verdict("888_JUDGE", Verdict.VOID) == Verdict.VOID
    assert kernel.normalize_verdict("999_VAULT", Verdict.SEAL) == Verdict.SEAL

def test_get_output_tags(kernel):
    kernel.set_authority = lambda x: setattr(kernel, "authority_level", x) # mock helper
    kernel.authority_level = AuthorityLevel.ANALYSIS
    assert "[ANALYSIS]" in kernel.get_output_tags()
    kernel.authority_level = AuthorityLevel.REQUIRES_HUMAN
    kernel._set_state(GovernanceState.AWAITING_888, AuthorityLevel.REQUIRES_HUMAN, "test")
    tags = kernel.get_output_tags()
    assert "[REQUIRES_HUMAN_JUDGMENT]" in tags
    assert "[PENDING_888_APPROVAL]" in tags

def test_architecture_map(kernel):
    m = kernel.architecture_map()
    assert m["stack"] == "000->999"
    assert "stages" in m
    assert m["runtime"]["state"] == "active"

def test_genius_and_state_telemetry(kernel):
    # This hits genius scoring integration
    score = kernel.genius_score
    assert 0.0 <= score <= 1.0
    state = kernel.get_current_state()
    assert "genius" in state
    assert "verdict" in state
    assert "telemetry" in state

def test_to_dict(kernel):
    d = kernel.to_dict()
    assert d["session_id"] == "test_session"
    assert "thresholds" in d

def test_app_manifesto_and_registry():
    manifesto = AppManifesto(
        app_name="TestApp",
        layer=AppLayer.L1_INSTRUCTION,
        description="Test",
        floors=[
            FloorManifesto(floor_id="F1", classification=FloorClassification.HARD),
            FloorManifesto(floor_id="F2", classification=FloorClassification.HARD),
            FloorManifesto(floor_id="F7", classification=FloorClassification.HARD),
        ]
    )
    assert manifesto.validate() == True
    AppRegistry.register(manifesto)
    assert AppRegistry.get("TestApp") == manifesto
    assert "TestApp" in AppRegistry.list_all()
    audit = AppRegistry.audit()
    assert audit["total_apps"] >= 1
    assert "TestApp" in audit["apps"]

def test_route_pipeline():
    p = route_pipeline("search for data")
    assert "222_REALITY" in p
    p = route_pipeline("delete file")
    assert "777_FORGE" in p
    assert "888_JUDGE" in p
    p = route_pipeline("recall memory")
    assert "555_MEMORY" in p

def test_get_clear_kernel():
    k = get_governance_kernel("session_x")
    assert k.session_id == "session_x"
    clear_governance_kernel("session_x")
    clear_governance_kernel() # clear all

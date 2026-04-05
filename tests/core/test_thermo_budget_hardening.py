from __future__ import annotations
import pytest
from core.physics.thermo_budget import ThermoBudget, ThermoSnapshot

@pytest.fixture
def budget():
    return ThermoBudget()

def test_thermo_budget_initial_session(budget):
    budget.open_session("test_sess")
    snap = budget.snapshot("test_sess")
    assert snap.session_id == "test_sess"
    assert snap.genius >= 0.8 # Default state should pass
    assert snap.G_dagger == 0.0 # No compute yet

def test_thermo_budget_step_decay(budget):
    budget.open_session("test_sess")
    snap1 = budget.snapshot("test_sess")
    snap2 = budget.record_step("test_sess", delta_s=-0.1) # Clarity gain
    
    assert snap2.energy < snap1.energy # Energy should decay
    assert snap2.delta_s == -0.1
    assert snap2.H_after < snap2.H_before

def test_g_dagger_calculation(budget):
    budget.open_session("test_sess")
    # Record step with tokens and tool calls to trigger G_dagger
    # delta_s = -0.1 (reduction), tokens = 1000
    # eta = 0.1 / 1000 = 0.0001
    # effort = 1.0 (base) + 0.5 * 2 (tools) = 2.0
    # G* = 1.0 * 1.0 * 0.95 * (2.0^2) = 3.8
    # G_dagger = 3.8 * 0.0001 = 0.00038
    snap = budget.record_step("test_sess", delta_s=-0.1, tool_calls=2, tokens=1000)
    
    assert snap.G_dagger > 0
    assert snap.effort == 2.0
    assert snap.token_cost == 1000

def test_apex_output_generation(budget):
    budget.open_session("test_sess")
    budget.record_step("test_sess", delta_s=-0.1, tokens=500)
    summary = budget.budget_summary("test_sess")
    
    assert "apex" in summary
    apex = summary["apex"]
    assert "capacity_layer" in apex
    assert "governed_intelligence" in apex
    assert apex["governed_intelligence"]["G_dagger"] > 0

def test_landauer_bits_tracking(budget):
    budget.open_session("test_sess")
    snap = budget.record_step("test_sess", tokens=100)
    # BITS_PER_TOKEN = 32
    assert snap.bits_erased == 3200
    assert snap.min_energy_joules > 0

"""
tests/test_substrate_reference_draft.py

Tests for the Tier 5 DRAFT substrate additions:
- ThermodynamicBudgetLedger (unified Landauer accounting)
- MaintenanceScaling (passive complexity-time degradation)
- compute_exergy_ratio (substrate exergy helper)

These are DRAFT / 888 HOLD features. Tests verify the math and the
non-breaking integration; they do NOT assert ratified constitutional status.
"""

from __future__ import annotations

import math

import pytest

from core.physics.thermodynamics_hardened import (
    K_BOLTZMANN,
    MaintenanceScaling,
    ThermodynamicBudgetLedger,
    ThermodynamicError,
    ThermodynamicExhaustionError,
    apply_maintenance_decay,
    cleanup_budget_ledger,
    compute_exergy_ratio,
    compute_maintenance_cost,
    get_budget_ledger,
    init_budget_ledger,
    record_budget_operation,
)


class TestThermodynamicBudgetLedger:
    def test_init_and_remaining(self):
        ledger = ThermodynamicBudgetLedger(session_id="s1", initial_joules=1.0)
        assert ledger.remaining == pytest.approx(1.0)
        assert not ledger.is_exhausted

    def test_record_operation_landauer(self):
        ledger = ThermodynamicBudgetLedger(session_id="s1", initial_joules=1.0)
        bits = 1000
        entry = ledger.record_operation(bits, operation="erase", temperature_k=300.0)
        expected = bits * K_BOLTZMANN * 300.0 * math.log(2)
        assert entry["min_joules"] == pytest.approx(expected)
        assert ledger.bits_erased == bits
        assert ledger.remaining == pytest.approx(1.0 - expected)

    def test_write_operation_tracks_bits_written(self):
        ledger = ThermodynamicBudgetLedger(session_id="s2", initial_joules=1.0)
        ledger.record_operation(10, operation="write")
        assert ledger.bits_written == 10
        assert ledger.bits_erased == 0

    def test_negative_bits_raises(self):
        ledger = ThermodynamicBudgetLedger(session_id="s3", initial_joules=1.0)
        with pytest.raises(ThermodynamicError):
            ledger.record_operation(-1)

    def test_budget_exhaustion(self):
        ledger = ThermodynamicBudgetLedger(session_id="s4", initial_joules=1e-20)
        ledger.record_operation(1000)
        assert ledger.is_exhausted
        with pytest.raises(ThermodynamicExhaustionError):
            ledger.check_budget()


class TestLedgerRegistry:
    def test_init_and_get(self):
        init_budget_ledger("reg1", initial_joules=2.0)
        ledger = get_budget_ledger("reg1")
        assert ledger.initial_joules == 2.0
        cleanup_budget_ledger("reg1")

    def test_record_budget_operation(self):
        init_budget_ledger("reg2", initial_joules=1.0)
        entry = record_budget_operation("reg2", bits=100)
        assert entry["operation"] == "erase"
        assert entry["bits"] == 100
        cleanup_budget_ledger("reg2")


class TestMaintenanceScaling:
    def test_complexity_index(self):
        scaler = MaintenanceScaling()
        c = scaler.complexity_index(n_tools=10, n_tracked_files=100)
        assert c == pytest.approx(math.log1p(10) + 2.0)

    def test_maintenance_cost_positive(self):
        result = compute_maintenance_cost(
            t_active_seconds=100.0, n_tools=10, n_tracked_files=100
        )
        assert result["e_maintenance_joules_per_second"] > 0
        assert result["time_factor"] > 1.0
        assert result["complexity_factor"] > 1.0

    def test_decay_accumulates_over_time(self):
        scaler = MaintenanceScaling()
        decay_short = scaler.compute_decay(10.0, n_tools=5, n_tracked_files=50)
        decay_long = scaler.compute_decay(1000.0, n_tools=5, n_tracked_files=50)
        assert decay_long > decay_short

    def test_apply_decay_deducts_ledger(self):
        init_budget_ledger("maint1", initial_joules=10.0)
        before = get_budget_ledger("maint1").consumed_joules
        result = apply_maintenance_decay(
            "maint1", 100.0, n_tools=5, n_tracked_files=50
        )
        after = get_budget_ledger("maint1").consumed_joules
        assert after > before
        assert result["decay_joules"] > 0
        cleanup_budget_ledger("maint1")

    def test_negative_time_raises(self):
        with pytest.raises(ThermodynamicError):
            compute_maintenance_cost(t_active_seconds=-1.0)


class TestExergyRatio:
    def test_meets_threshold(self):
        result = compute_exergy_ratio(
            useful_work=700_000.0,
            total_heat=700_000.0,
            allocated_capital=1_000.0,
            delta_s_allocation=0.0,
        )
        assert result["meets_threshold"] is True
        assert result["eta_x"] == pytest.approx(0.70)

    def test_fails_threshold(self):
        result = compute_exergy_ratio(
            useful_work=100.0,
            total_heat=1_000.0,
            allocated_capital=1_000.0,
            delta_s_allocation=0.0,
        )
        assert result["meets_threshold"] is False
        assert result["eta_x"] < 0.70

    def test_negative_allocated_capital_raises(self):
        with pytest.raises(ThermodynamicError):
            compute_exergy_ratio(
                useful_work=1.0, total_heat=1.0, allocated_capital=0.0
            )

"""Tests for governance/compute_apex.py (APEX=G Calculus Engine)."""

import pytest
from governance.compute_apex import compute_apex, Verdict, geometric_mean


def test_geometric_mean():
    assert geometric_mean([1.0, 1.0, 1.0, 1.0]) == 1.0
    assert geometric_mean([0.0, 1.0, 1.0]) == 0.0
    assert round(geometric_mean([0.8, 0.8, 0.8, 0.8]), 2) == 0.80


def test_nominal_seal():
    floors = {f"F{i}": 0.95 for i in range(1, 14)}
    result = compute_apex(floors, energy_score=0.95, risk_score=0.95)
    assert result.verdict == Verdict.SEAL
    assert result.G >= 0.80
    assert result.A > 0.90
    assert result.P > 0.90
    assert result.E > 0.90
    assert result.X > 0.90


def test_sabar_threshold():
    floors = {f"F{i}": 0.75 for i in range(1, 14)}
    floors["F13"] = 1.0  # Must be 1.0 for F13
    floors["F9"] = 1.0
    floors["F10"] = 1.0
    floors["F12"] = 1.0
    result = compute_apex(floors, energy_score=0.75, risk_score=0.75)
    assert result.verdict == Verdict.SABAR
    assert 0.70 <= result.G < 0.80


def test_hold_evidence_low_score():
    floors = {f"F{i}": 0.50 for i in range(1, 14)}
    floors["F13"] = 1.0
    floors["F9"] = 1.0
    floors["F10"] = 1.0
    floors["F12"] = 1.0
    result = compute_apex(floors, energy_score=0.50, risk_score=0.50)
    assert result.verdict == Verdict.HOLD
    assert result.G < 0.70


def test_hard_floor_f13_sovereign_violation():
    floors = {f"F{i}": 0.95 for i in range(1, 14)}
    floors["F13"] = 0.5  # Sovereign violation
    result = compute_apex(floors)
    assert result.verdict == Verdict.VOID
    assert "F13 Sovereign violation" in result.reasons[0]


def test_hard_floor_f9_anti_hantu_violation():
    floors = {f"F{i}": 0.95 for i in range(1, 14)}
    floors["F9"] = 0.0  # Anti-Hantu violation
    result = compute_apex(floors)
    assert result.verdict == Verdict.VOID
    assert "F9/F10 Hard Floor breach" in result.reasons[0]


def test_hold_888_irreversible_mutation():
    floors = {f"F{i}": 0.95 for i in range(1, 14)}
    result = compute_apex(floors, is_reversible=False, has_human_approval=False)
    assert result.verdict == Verdict.HOLD_888
    assert "888_HOLD" in result.reasons[0]

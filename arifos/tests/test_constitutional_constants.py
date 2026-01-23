"""
Test suite for constitutional_constants.py

Validates:
- All 13 floors are defined
- Verdict hierarchy is complete
- Cooling tiers are correct
- Engine definitions are valid
- Helper functions work correctly
"""

import pytest
from arifos.constitutional_constants import (
    FLOORS,
    VERDICTS,
    COOLING_TIERS,
    ENGINES,
    VERSION,
    VerdictType,
    EngineType,
    get_floor_by_id,
    get_hard_floors,
    get_soft_floors,
)


def test_version():
    """Test version is v49.0.0"""
    assert VERSION == "v49.0.0"


def test_all_floors_defined():
    """Test all 13 floors are present"""
    assert len(FLOORS) == 13

    expected_floors = [
        "F1_Amanah", "F2_Truth", "F3_TriWitness", "F4_Clarity",
        "F5_Peace", "F6_Empathy", "F7_Humility", "F8_Genius",
        "F9_Cdark", "F10_Ontology", "F11_CommandAuth",
        "F12_InjectionDefense", "F13_Curiosity"
    ]

    for floor_id in expected_floors:
        assert floor_id in FLOORS, f"Floor {floor_id} missing"


def test_floor_structure():
    """Test floor definitions have required keys"""
    f1 = FLOORS["F1_Amanah"]

    # Required keys in FloorDefinition
    assert "name" in f1
    assert "principle" in f1
    assert "floor_type" in f1
    assert "engine" in f1
    assert "stage" in f1
    assert "violation" in f1


def test_floor_thresholds():
    """Test critical floor thresholds"""
    # F2 Truth: numeric threshold
    assert FLOORS["F2_Truth"]["threshold"] == 0.99

    # F3 TriWitness: numeric threshold
    assert FLOORS["F3_TriWitness"]["threshold"] == 0.95

    # F7 Humility: range threshold
    assert "threshold_range" in FLOORS["F7_Humility"]
    assert FLOORS["F7_Humility"]["threshold_range"] == [0.03, 0.05]

    # F1 Amanah: boolean threshold (None)
    assert FLOORS["F1_Amanah"]["threshold"] is None


def test_verdict_hierarchy():
    """Test all 5 verdicts defined"""
    assert len(VERDICTS) == 5

    # Check VerdictType enum values
    verdict_values = {v.value for v in VERDICTS.keys()}
    assert "SEAL" in verdict_values
    assert "PARTIAL" in verdict_values
    assert "VOID" in verdict_values
    assert "SABAR" in verdict_values
    assert "888_HOLD" in verdict_values


def test_cooling_tiers():
    """Test Phoenix-72 cooling tiers"""
    assert 1 in COOLING_TIERS
    assert 2 in COOLING_TIERS
    assert 3 in COOLING_TIERS

    assert COOLING_TIERS[1]["duration_hours"] == 42
    assert COOLING_TIERS[2]["duration_hours"] == 72
    assert COOLING_TIERS[3]["duration_hours"] == 168


def test_trinity_engines():
    """Test AGI/ASI/APEX engines defined"""
    assert len(ENGINES) == 3

    engine_values = {e.value for e in ENGINES.keys()}
    assert "AGI" in engine_values
    assert "ASI" in engine_values
    assert "APEX" in engine_values


def test_get_floor_by_id():
    """Test floor lookup helper"""
    f1 = get_floor_by_id("F1_Amanah")
    assert f1["name"] == "Amanah (Trust/Reversibility)"

    with pytest.raises(KeyError):
        get_floor_by_id("F99_NonExistent")


def test_get_hard_floors():
    """Test hard floor filtering"""
    hard_floors = get_hard_floors()

    # At minimum: F1, F2, F3, F4, F7, F10, F11, F12
    assert len(hard_floors) >= 8
    assert "F1_Amanah" in hard_floors
    assert "F2_Truth" in hard_floors


def test_get_soft_floors():
    """Test soft floor filtering"""
    soft_floors = get_soft_floors()

    # At minimum: F5, F6, F13
    assert len(soft_floors) >= 3
    assert "F5_Peace" in soft_floors
    assert "F6_Empathy" in soft_floors
    assert "F13_Curiosity" in soft_floors

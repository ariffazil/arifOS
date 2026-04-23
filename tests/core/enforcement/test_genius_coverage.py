
from __future__ import annotations
import pytest
from core.enforcement.genius import (
    APEXDials,
    audit_result_to_floor_scores,
    calculate_genius,
    coerce_floor_scores,
    floors_to_dials,
    geometric_mean
)
from core.shared.floor_audit import AuditResult, FloorResult
from core.shared.types import FloorScores, Verdict

def test_geometric_mean():
    assert geometric_mean([0.9, 0.9, 0.9]) == pytest.approx(0.9)
    assert geometric_mean([1.0, 0.0, 1.0]) == 0.0
    assert geometric_mean([]) == 0.0
    assert geometric_mean([0.5, 2.0]) == pytest.approx(1.0)

def test_audit_result_to_floor_scores():
    # Test with AuditResult object
    audit = AuditResult(
        verdict=Verdict.SEAL,
        pass_rate=1.0,
        recommendation="OK",
        floor_results={
            "F1": FloorResult(floor="F1", score=0.8, passed=True),
            "F2": FloorResult(floor="F2", score=0.9, passed=True),
            "F10": FloorResult(floor="F10", score=1.0, passed=True),
            "F9": FloorResult(floor="F9", score=0.1, passed=True), # f9 is 1.0 - score
        }
    )
    scores = audit_result_to_floor_scores(audit)
    assert scores.f1_amanah == 0.8
    assert scores.f2_truth == 0.9
    assert scores.f10_ontology is True
    assert scores.f9_anti_hantu == 0.9 # 1.0 - 0.1

    # Test with dict
    audit_dict = {
        "floor_results": {
            "F1": {"score": 0.7, "passed": True},
            "F11": "pass",
            "F12": "fail"
        }
    }
    scores_dict = audit_result_to_floor_scores(audit_dict)
    assert scores_dict.f1_amanah == 0.7
    assert scores_dict.f11_command_auth is True
    assert scores_dict.f12_injection == 1.0 # 1.0 - 0.0

def test_coerce_floor_scores():
    # Test with aliases
    payload = {
        "f1": 0.5,
        "truth_score": 0.6,
        "omega_0": 0.045,
        "human_score": 0.8,
        "f10": "yes"
    }
    scores = coerce_floor_scores(payload)
    assert scores.f1_amanah == 0.5
    assert scores.f2_truth == 0.6
    assert scores.f7_humility == 0.045
    assert scores.f13_sovereign == 0.8
    assert scores.f10_ontology is True

    # Test with defaults
    scores_empty = coerce_floor_scores({})
    assert scores_empty.f2_truth == 0.99
    assert scores_empty.f7_humility == 0.04

    # Test with custom defaults
    custom_defaults = {"f2_truth": 0.5}
    scores_custom = coerce_floor_scores({}, defaults=custom_defaults)
    assert scores_custom.f2_truth == 0.5

def test_calculate_genius_edge_cases():
    floors = FloorScores()
    
    # 1. Zero Akal (F2=0)
    floors_zero_akal = floors.model_copy(update={"f2_truth": 0.0})
    res = calculate_genius(floors_zero_akal)
    assert res["genius_score"] == 0.0
    assert res["verdict"] == "VOID"

    # 2. High Hysteresis (h=1.0)
    res_h1 = calculate_genius(floors, h=1.0)
    assert res_h1["genius_score"] == 0.0
    assert res_h1["verdict"] == "VOID"

    # 3. High Energy usage
    res_e_low = calculate_genius(floors, compute_budget_used=1.0, compute_budget_max=1.0)
    # Energy dial will be (Energy_floors + 0)/2
    # G = A * P * X * E^2
    assert res_e_low["genius_score"] < calculate_genius(floors)["genius_score"]

def test_apexdials_to_dict():
    dials = APEXDials(A=0.1, P=0.2, X=0.3, E=0.4)
    d = dials.to_dict()
    assert d == {"A": 0.1, "P": 0.2, "X": 0.3, "E": 0.4}

def test_humility_normalization():
    # Optimal band [0.03, 0.05]
    f_opt = FloorScores(f7_humility=0.04)
    d_opt = floors_to_dials(f_opt)
    
    f_high = FloorScores(f7_humility=0.1) # Diff = 0.06 -> Penalty = 0.6 -> f7_norm = 0.4
    d_high = floors_to_dials(f_high)
    
    assert d_high.A < d_opt.A

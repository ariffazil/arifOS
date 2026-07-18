"""
test_qqqq_metrics.py — QQQQ + Agentic Intelligence + Kernel coupling
====================================================================
GENESIS 022 / QQQ Doctrine v1.0 + Q4 Zen Export

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.qqqq_metrics import (
    AgenticFactors,
    QQQQVerdict,
    compute_agentic_intelligence,
    compute_kernel_agent_qqqq,
    gate_qqqq,
    metabolism_from_flux,
    q4_required,
    validate_q4,
    validate_qqqq,
)


def _path(pid: str, cat: str, **kw) -> dict:
    base = {
        "path_id": pid,
        "name": pid,
        "description": f"desc {pid}",
        "category": cat,
        "blast_radius": kw.get("blast_radius", 2),
        "reversibility": kw.get("reversibility", 4),
        "time_cost": "~5min",
        "confidence": kw.get("confidence", 0.8),
        "prior_art": kw.get("prior_art", "STRONG"),
    }
    return base


def _valid_qqq_envelope(with_q4: bool = False) -> dict:
    env = {
        "paths": [
            _path("P1", "AGGRESSIVE"),
            _path("P2", "CONSERVATIVE"),
            _path("P3", "LATERAL"),
            _path("P4", "NULL", blast_radius=0, reversibility=5, confidence=1.0),
            _path(
                "P5", "INVERSE", blast_radius=4, reversibility=2, confidence=0.3, prior_art="NONE"
            ),
        ],
        "quantum": {
            "precedent_effect": "Sets export-first canon",
            "interference_effect": "Touches session-state only",
            "superposition_effect": "Keeps feature branch open",
            "observer_effect": "Agents schedule zen earlier",
        },
        "recommended_path_id": "P2",
    }
    if with_q4:
        env["q4_export"] = {
            "export_actions": ["dirty_trees_to_zero", "session_state_rewrite"],
            "delta_s_claim": -0.3,
            "tank_at_export": 0.9,
            "completed": True,
        }
    return env


def test_q4_required_only_at_abundance():
    assert q4_required(0.9, intent_class="RECOMMENDATION", proposing_eureka=True) is True
    assert q4_required(0.2, intent_class="RECOMMENDATION", proposing_eureka=True) is False


def test_q4_missing_under_abundance():
    c = validate_q4(None, tank=0.9, proposing_eureka=True)
    assert c.required is True
    assert c.passed is False
    assert c.gate_label == "ZEN_BEFORE_EUREKA"


def test_q4_pass_with_export():
    block = {
        "export_actions": ["kill_false_restart"],
        "delta_s_claim": -0.1,
        "completed": True,
    }
    c = validate_q4(block, tank=0.9, proposing_eureka=True)
    assert c.passed is True


def test_qqqq_complete_with_q4_at_abundance():
    env = _valid_qqq_envelope(with_q4=True)
    check = validate_qqqq(env, intent_class="RECOMMENDATION", tank=0.9, proposing_eureka=True)
    assert check.verdict == QQQQVerdict.COMPLETE
    assert check.eureka_zen is not None
    assert check.q4 is not None and check.q4.passed


def test_qqqq_inadmissible_q4_without_export():
    env = _valid_qqq_envelope(with_q4=False)
    check = validate_qqqq(env, intent_class="RECOMMENDATION", tank=0.9, proposing_eureka=True)
    assert check.verdict == QQQQVerdict.INADMISSIBLE_Q4


def test_qqqq_no_q4_at_low_tank():
    env = _valid_qqq_envelope(with_q4=False)
    check = validate_qqqq(env, intent_class="RECOMMENDATION", tank=0.2, proposing_eureka=True)
    # Q1-Q3 complete, Q4 not required
    assert check.verdict == QQQQVerdict.COMPLETE
    assert check.q4 is not None
    assert check.q4.required is False


def test_agentic_intelligence_product():
    f = AgenticFactors(
        capability=1.0,
        grounding=1.0,
        authority=1.0,
        continuity=1.0,
        accountability=1.0,
        metabolism=1.0,
    )
    m = compute_agentic_intelligence(f)
    assert m.agentic_intelligence == pytest.approx(1.0)
    assert m.zero_factors == ()
    assert m.admissible is True


def test_agentic_intelligence_zero_metabolism():
    f = AgenticFactors(
        capability=1.0,
        grounding=1.0,
        authority=1.0,
        continuity=1.0,
        accountability=1.0,
        metabolism=0.0,
    )
    m = compute_agentic_intelligence(f)
    assert m.agentic_intelligence == 0.0
    assert any("Met=0" in z for z in m.zero_factors)
    assert m.admissible is False


def test_genius_and_psi_optional():
    f = AgenticFactors(1, 1, 1, 1, 1, 1)
    m = compute_agentic_intelligence(
        f,
        genius_components={"A": 1, "P": 1, "X": 1, "E": 1, "h": 0.04},
        vitality_components={
            "delta_s": 0.1,
            "peace2": 1,
            "kappa_r": 1,
            "rasa": 1,
            "amanah": 1,
            "entropy": 0.01,
            "shadow": 0,
        },
    )
    assert m.genius is not None and m.genius >= 0.80
    assert m.vitality_psi is not None and m.vitality_psi >= 1.0


def test_metabolism_from_flux_idle_is_neutral():
    assert metabolism_from_flux(0, 0) == 1.0


def test_kernel_agent_qqqq_coupling():
    env = _valid_qqq_envelope(with_q4=True)
    full = compute_kernel_agent_qqqq(
        tank=0.9,
        inject=1.0,
        export=2.0,
        envelope=env,
        intent_class="RECOMMENDATION",
        proposing_eureka=True,
        capability=0.9,
        grounding=0.9,
        authority=1.0,
        continuity=0.8,
        accountability=0.9,
        kernel_floors_pass=True,
    )
    d = full.to_dict()
    assert "eureka_zen" in d
    assert "qqqq" in d
    assert "agentic" in d
    assert "coupling" in d
    lines = full.summary_lines()
    assert any("EUREKA·ZEN" in L for L in lines)
    assert full.coupling["should_force_zen"] is False
    assert full.agentic.agentic_intelligence > 0


def test_kernel_agent_forces_zen_at_abundance_no_export():
    env = _valid_qqq_envelope(with_q4=False)
    full = compute_kernel_agent_qqqq(
        tank=0.95,
        inject=10.0,
        export=0.0,
        envelope=env,
        proposing_eureka=True,
    )
    assert full.coupling["should_force_zen"] is True
    assert full.qqqq.verdict == QQQQVerdict.INADMISSIBLE_Q4


def test_gate_qqqq_labels():
    env = _valid_qqq_envelope(with_q4=True)
    g = gate_qqqq(env, tank=0.9)
    assert g.metadata.get("qqqq_compliance") == QQQQVerdict.COMPLETE.value


def test_equations_present():
    f = AgenticFactors(1, 1, 1, 1, 1, 1)
    m = compute_agentic_intelligence(f)
    assert "agentic_intelligence" in m.equations
    assert "iron_line" in m.equations

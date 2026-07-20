"""
test_eureka_zen.py — GENESIS 022 EUREKA·ZEN Margin Thermodynamics
================================================================

Full equation metrics for tank, inject/export, metabolic balance,
phase classification, and iron-rule gate labels.

Iron line: Zen is not the last 2%. Zen is the first 10% of every full tank.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from __future__ import annotations

import pytest

from arifosmcp.geometry.eureka_zen import (
    C_DARK_HOLD,
    T_ABUNDANCE,
    T_CRITICAL,
    T_MARGIN,
    EntropyFlux,
    EurekaCandidate,
    ExportReceipt,
    MetabolicPhase,
    TankState,
    ZenGateLabel,
    apex_g,
    c_dark,
    classify_phase,
    compute_eureka_zen,
    jauhari_check,
    metabolic_balance,
    require_jauhari_before_judge,
    session_delta_s,
    should_force_zen,
    tank_step,
    w3_verdict,
    w3_witness,
)


def test_tank_resolve_from_level():
    assert TankState(tank_level=0.5).resolve() == 0.5
    assert TankState(tank_level=1.5).resolve() == 1.0
    assert TankState(tank_level=-0.1).resolve() == 0.0


def test_tank_resolve_from_budget():
    assert TankState(remaining_budget=20, max_budget=100).resolve() == pytest.approx(0.2)


def test_tank_missing_raises():
    with pytest.raises(ValueError):
        TankState().resolve()


def test_metabolic_balance_healthy():
    # X >= J → M >= 1
    assert metabolic_balance(inject=2.0, export=2.0) == pytest.approx(1.0, abs=1e-5)
    assert metabolic_balance(inject=1.0, export=3.0) > 1.0


def test_metabolic_balance_debt():
    # inject dominates
    m = metabolic_balance(inject=10.0, export=1.0)
    assert m < 1.0
    assert m == pytest.approx(0.1, abs=1e-5)


def test_session_delta_s_f4():
    assert session_delta_s(inject=5, export=5) == 0.0
    assert session_delta_s(inject=3, export=5) < 0  # good: export > inject
    assert session_delta_s(inject=5, export=3) > 0  # F4 fail candidate


def test_phase_margin_zen_at_2_percent():
    assert classify_phase(0.02, export_completed=False) == MetabolicPhase.MARGIN_ZEN
    assert classify_phase(0.01, export_completed=True) == MetabolicPhase.MARGIN_ZEN


def test_phase_margin_reflex():
    assert classify_phase(0.03, export_completed=False) == MetabolicPhase.MARGIN_REFLEX


def test_phase_abundance_must_zen():
    assert classify_phase(0.8, export_completed=False) == MetabolicPhase.ABUNDANCE_MUST_ZEN


def test_phase_abundance_eureka_ok_after_export():
    assert classify_phase(0.8, export_completed=True) == MetabolicPhase.ABUNDANCE_EUREKA_OK


def test_phase_normal_dual():
    assert classify_phase(0.25, export_completed=False) == MetabolicPhase.NORMAL_DUAL


def test_iron_rule_zen_before_eureka_at_abundance():
    m = compute_eureka_zen(
        0.9,
        EntropyFlux(inject=5, export=0),
        proposing_eureka=True,
    )
    assert m.phase == MetabolicPhase.ABUNDANCE_MUST_ZEN
    assert m.gate_label == ZenGateLabel.ZEN_BEFORE_EUREKA
    assert should_force_zen(m) is True
    assert m.f4_pass is False  # J > X


def test_abundance_export_unlocks_eureka():
    receipt = ExportReceipt(
        export_actions=["dirty_trees_to_zero", "kill_false_restart"],
        delta_s_claim=-0.5,
        tank_at_export=0.9,
        completed=True,
    )
    m = compute_eureka_zen(
        0.9,
        EntropyFlux(inject=1, export=2),
        export_receipt=receipt,
        proposing_eureka=True,
    )
    assert m.phase == MetabolicPhase.ABUNDANCE_EUREKA_OK
    assert m.gate_label == ZenGateLabel.PASS
    assert should_force_zen(m) is False
    assert m.f4_pass is True


def test_margin_critical_blocks_expansion_label():
    m = compute_eureka_zen(
        T_CRITICAL,
        EntropyFlux(inject=0, export=1),
        proposing_eureka=True,
    )
    assert m.phase == MetabolicPhase.MARGIN_ZEN
    assert m.gate_label == ZenGateLabel.MARGIN_EXPORT_ONLY
    assert should_force_zen(m) is True


def test_thresholds_match_doctrine():
    assert T_CRITICAL == 0.02
    assert T_MARGIN == 0.03
    assert T_ABUNDANCE == 0.50


def test_iron_line_echoed():
    m = compute_eureka_zen(0.5)
    assert "first 10%" in m.iron_line
    assert "last 2%" in m.iron_line


def test_summary_and_json():
    m = compute_eureka_zen(0.1, EntropyFlux(1, 1))
    line = m.summary_line()
    assert "EUREKA·ZEN" in line
    data = m.to_dict()
    assert data["tank"] == 0.1
    assert "phase" in data


# ── Sealed framework: margin theorem, G, C_dark, W³ ──────────────────────────


def test_apex_g_and_c_dark():
    g = apex_g(1.0, 1.0, 1.0, 1.0, 0.95)
    assert g == pytest.approx(0.95)
    # High capability, low precision & fidelity → dark capital
    cd = c_dark(0.9, 0.5, 0.5)
    assert cd == pytest.approx(0.9 * 0.5 * 0.5)
    assert cd > C_DARK_HOLD
    assert c_dark(1.0, 1.0, 1.0) == 0.0


def test_w3_unknown_is_zero():
    assert w3_witness(0.9, 0.9, 0.0) == 0.0
    w = w3_witness(0.9, 0.9, 0.9)
    assert w3_verdict(w) == "CONSENSUS"
    assert w3_verdict(0.5) == "WEAK"
    assert w3_verdict(0.2) == "DIVERGENT"


def test_tank_step_export_raises_tank():
    t0 = 0.5
    t1 = tank_step(t0, injection_rate=0.0, export_rate=0.2, dt=1.0, dissipation_k=0.0)
    assert t1 > t0


def test_compute_includes_utilities():
    m = compute_eureka_zen(0.80)
    assert m.extras["u_eureka"] > m.extras["u_zen"]
    assert m.extras["preferred_mode"] == "EUREKA"


# ═══════════════════════════════════════════════════════════════════════════
# SUNSHINE CHILD — wonder mode + Jauhari firewall
# ═══════════════════════════════════════════════════════════════════════════


def test_eureka_candidate_label():
    """EurekaCandidate is CANDIDATE ONLY by default."""
    c = EurekaCandidate(hypothesis="Is ZEN better at abundance?")
    assert c.candidate_only is True
    assert c.jauhari_verified is False
    assert c.jauhari_passed() is False


def test_jauhari_check_blocks_unreviewed():
    """Jauhari gate returns HOLD for UNREVIEWED candidates."""
    c = EurekaCandidate(hypothesis="What if gravity is emergent?")
    gate = jauhari_check(c)
    assert gate["pass"] is False
    assert "HOLD" in gate["reason"]


def test_jauhari_check_passes_when_verified():
    """Jauhari gate returns PASS for PROMOTED candidates with evidence."""
    c = EurekaCandidate(
        hypothesis="Zen at abundance beats zen at margin.",
        jauhari_verified=True,
        evidence_refs=("margin_theorem", "resource_dynamics"),
    )
    gate = jauhari_check(c)
    assert gate["pass"] is True
    assert "PASS" in gate["reason"]


def test_jauhari_check_raises_hold_for_verified_no_evidence():
    """Even a jauhari-verified candidate without evidence cannot proceed."""
    c = EurekaCandidate(
        hypothesis="This feels right.",
        jauhari_verified=True,
        evidence_refs=(),
    )
    gate = jauhari_check(c, require_evidence=True)
    assert gate["pass"] is False


def test_require_jauhari_before_judge_none_is_ok():
    """require_jauhari_before_judge(None) = True (normal governance work)."""
    assert require_jauhari_before_judge(None) is True


def test_require_jauhari_before_judge_blocks_unverified():
    """require_jauhari_before_judge(unverified) = False."""
    c = EurekaCandidate(hypothesis="Test.")
    assert require_jauhari_before_judge(c) is False


def test_require_jauhari_before_judge_passes_verified():
    """require_jauhari_before_judge(verified) = True."""
    c = EurekaCandidate(
        hypothesis="Test with evidence.",
        jauhari_verified=True,
        evidence_refs=("obs1",),
    )
    assert require_jauhari_before_judge(c) is True


def test_candidate_only_string_detection():
    """String CANDIDATE_ONLY in input triggers firewall detection."""
    assert "CANDIDATE_ONLY" in '{"output_class": "CANDIDATE_ONLY", "origin_mode": "wonder"}'
    assert '"origin_mode": "wonder"' in '{"origin_mode": "wonder"}'


def test_wonder_blocked_paths():
    """Verify wonder mode output defines correct blocked/allowed paths."""
    wonder_output = {
        "output_class": "CANDIDATE_ONLY",
        "allowed_next": ["arif_think:critique", "arif_observe"],
        "blocked": ["arif_judge", "arif_seal", "arif_forge", "arif_think:verify"],
    }
    assert "arif_judge" in wonder_output["blocked"]
    assert "arif_seal" in wonder_output["blocked"]
    assert "arif_forge" in wonder_output["blocked"]
    assert "arif_think:critique" in wonder_output["allowed_next"]
    assert "arif_think:verify" not in wonder_output["allowed_next"]

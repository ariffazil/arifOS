"""
tests/test_shadow_infrastructure.py — Cognitive Shadow & Session Shadow State

Verifies:
- CognitiveShadow thickness computation
- SessionShadowState hysteresis tracking
- Metabolic flux computation and verdict thresholds
- Alignment-faking detection heuristic
- Registry get/set behavior
"""

from __future__ import annotations

import pytest

from arifos.core.governance import (
    CognitiveShadow,
    SessionShadowState,
    record_cognitive_shadow,
    get_session_shadow,
    TruthLayer,
)


class TestCognitiveShadow:
    def test_thickness_zero_when_all_zero(self):
        cs = CognitiveShadow()
        # Default self_report_reliability=0.0 contributes 0.10; minimum is 0.1
        assert cs.compute_thickness() == pytest.approx(0.1, abs=1e-9)

    def test_thickness_high_with_alignment_faking(self):
        cs = CognitiveShadow(
            self_report_reliability=0.9,
            latent_output_gap=0.8,
            sycophancy_pressure=0.7,
            alignment_faking_signal=0.9,
            refusal_suppressed=True,
            explanation_cost_ratio=0.6,
        )
        thickness = cs.compute_thickness()
        assert thickness > 0.5
        assert 0.0 <= thickness <= 1.0

    def test_thickness_bounds(self):
        cs = CognitiveShadow(
            self_report_reliability=1.0,
            latent_output_gap=1.0,
            sycophancy_pressure=1.0,
            alignment_faking_signal=1.0,
            refusal_suppressed=True,
            explanation_cost_ratio=1.0,
        )
        # Weights sum to 0.90, not 1.0 (self_report contributes 0 when maxed)
        assert cs.compute_thickness() == pytest.approx(0.9, abs=1e-9)

    def test_thickness_updates_field(self):
        cs = CognitiveShadow(latent_output_gap=0.5)
        thickness = cs.compute_thickness()
        assert cs.shadow_thickness == pytest.approx(thickness, abs=1e-9)


class TestSessionShadowState:
    def test_add_turn_increments_turn_id(self):
        ss = SessionShadowState(session_id="test-sess")
        cs = CognitiveShadow(sycophancy_pressure=0.1)
        ss.add_turn(cs)
        assert ss.turns[0].turn_id == 0
        ss.add_turn(CognitiveShadow(sycophancy_pressure=0.2))
        assert ss.turns[1].turn_id == 1

    def test_detect_sycophancy_drift_increasing(self):
        ss = SessionShadowState(session_id="test-sess")
        for pressure in [0.1, 0.3, 0.6, 0.9]:
            ss.add_turn(CognitiveShadow(sycophancy_pressure=pressure))
        drift = ss.detect_sycophancy_drift(window=4)
        assert drift > 0.0

    def test_detect_sycophancy_drift_flat(self):
        ss = SessionShadowState(session_id="test-sess")
        for _ in range(4):
            ss.add_turn(CognitiveShadow(sycophancy_pressure=0.5))
        drift = ss.detect_sycophancy_drift(window=4)
        assert drift == pytest.approx(0.0, abs=1e-9)

    def test_detect_alignment_faking_pattern(self):
        ss = SessionShadowState(session_id="test-sess")
        # eval-like turns: low sycophancy, high reliability
        for _ in range(2):
            ss.add_turn(CognitiveShadow(sycophancy_pressure=0.1, self_report_reliability=0.9))
        # deploy-like turn: high sycophancy, low reliability
        ss.add_turn(CognitiveShadow(sycophancy_pressure=0.8, self_report_reliability=0.3))
        result = ss.detect_alignment_faking()
        assert result["detected"] is True
        assert result["confidence"] > 0.5
        assert len(result["eval_like_turns"]) >= 2
        assert len(result["deploy_like_turns"]) >= 1

    def test_detect_alignment_faking_no_pattern(self):
        ss = SessionShadowState(session_id="test-sess")
        for _ in range(3):
            ss.add_turn(CognitiveShadow(sycophancy_pressure=0.5, self_report_reliability=0.5))
        result = ss.detect_alignment_faking()
        assert result["detected"] is False
        assert result["confidence"] == 0.0

    def test_compute_metabolic_flux_empty(self):
        ss = SessionShadowState(session_id="test-sess")
        assert ss.compute_metabolic_flux() == 0.0

    def test_compute_metabolic_flux_elevated(self):
        ss = SessionShadowState(session_id="test-sess")
        # Alternating high/low thickness to increase avg_change + avg_level
        for thickness in [0.9, 0.3, 0.9, 0.3, 0.9]:
            cs = CognitiveShadow()
            cs.shadow_thickness = thickness
            ss.add_turn(cs)
        flux = ss.compute_metabolic_flux()
        assert flux > 0.5
        assert 0.0 <= flux <= 1.0

    def test_to_signal_structure(self):
        ss = SessionShadowState(session_id="test-sess")
        ss.add_turn(CognitiveShadow(sycophancy_pressure=0.2))
        signal = ss.to_signal()
        assert signal["session_id"] == "test-sess"
        assert "metabolic_flux" in signal
        assert "flux_verdict" in signal
        assert "sycophancy_drift" in signal
        assert "alignment_faking" in signal
        assert "latest_shadow_thickness" in signal
        assert signal["turn_count"] == 1

    def test_flux_verdict_thresholds(self):
        ss = SessionShadowState(session_id="test-sess")
        # NORMAL: low flux
        ss.add_turn(CognitiveShadow())
        assert ss.to_signal()["flux_verdict"] == "NORMAL"

        # ELEVATED / COMPULSORY_REALLOCATION / SYSTEM_HOLD via thick shadows
        for gap in [0.3, 0.6, 0.9, 1.0, 1.0]:
            cs = CognitiveShadow(latent_output_gap=gap, sycophancy_pressure=gap)
            cs.compute_thickness()
            ss.add_turn(cs)
        flux = ss.compute_metabolic_flux()
        verdict = ss.to_signal()["flux_verdict"]
        if flux >= 0.85:
            assert verdict == "SYSTEM_HOLD"
        elif flux >= 0.65:
            assert verdict == "COMPULSORY_REALLOCATION"
        elif flux >= 0.45:
            assert verdict == "ELEVATED"


class TestShadowRegistry:
    def test_get_session_shadow_creates_default(self):
        ss = get_session_shadow("new-session-xyz")
        assert ss.session_id == "new-session-xyz"
        assert ss.turns == []

    def test_record_cognitive_shadow_updates_registry(self):
        session_id = "registry-test-123"
        cs = CognitiveShadow(sycophancy_pressure=0.4)
        signal = record_cognitive_shadow(session_id, cs)
        assert signal["session_id"] == session_id
        assert signal["turn_count"] == 1

        ss = get_session_shadow(session_id)
        assert len(ss.turns) == 1
        assert ss.turns[0].sycophancy_pressure == pytest.approx(0.4, abs=1e-9)

    def test_record_multiple_shadows(self):
        session_id = "registry-test-456"
        for i in range(3):
            record_cognitive_shadow(session_id, CognitiveShadow(turn_id=i))
        ss = get_session_shadow(session_id)
        assert len(ss.turns) == 3

    def test_truth_layer_humility_acknowledgment(self):
        ha = TruthLayer.humility_acknowledgment()
        assert ha["checklist_truth_reachable"] is True
        assert ha["absolute_truth_claimed"] is False
        assert ha["unknown_unknowns_acknowledged"] is True
        assert ha["human_judgment_required"] is True
        assert ha["godel_lock_active"] is True

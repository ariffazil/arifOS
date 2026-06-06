"""
tests/test_888_judge_paradox_guard.py — 888_JUDGE shadow audit + paradox guard

Verifies:
- Empty evidence_bundle → HOLD_888 (F7 Humility)
- Normal metrics + clean shadow → SEAL
- Pre-floor AF ≥0.7 → HOLD_888 (L13_SHADOW_ALIGNMENT_FAKING)
- Pre-floor flux SYSTEM_HOLD → HOLD_888 (F7_SHADOW_FLUX)
- Post-floor confidence < 0.6 → PARADOX_GUARD_CONFIDENCE
- Post-floor metabolic_flux ≥0.65 → PARADOX_GUARD_FLUX
- Truth layer fields present in every output
"""

from __future__ import annotations

import pytest

from arifosmcp.core.governance import (
    CognitiveShadow,
    record_cognitive_shadow,
    get_session_shadow,
    TruthLayer,
)
from arifosmcp.tools import _888_judge


def _make_evidence_bundle(**metric_overrides) -> dict:
    """Build a standard evidence bundle that passes all floors."""
    metrics = {
        "truth_score": 0.99,
        "delta_s": -0.02,
        "omega_0": 0.04,
        "peace_squared": 1.2,
        "amanah_lock": True,
        "tri_witness_score": 0.98,
        "stakeholder_safety": 1.0,
        "floor_8_signal": "not_evaluated",
        "floor_9_signal": "not_evaluated",
        "floor_10_signal": "not_evaluated",
        "floor_11_signal": "not_evaluated",
        "floor_12_signal": "not_evaluated",
        "floor_13_signal": "not_evaluated",
    }
    metrics.update(metric_overrides)
    return {
        "metrics": metrics,
        "is_irreversible": False,
        "zkpc_level": 0,
    }


def _setup_af_session(session_id: str, confidence: float):
    """Seed session shadow with alignment-faking pattern."""
    # eval-like turns: low sycophancy, high reliability
    for _ in range(2):
        cs = CognitiveShadow(sycophancy_pressure=0.1, self_report_reliability=0.9)
        cs.compute_thickness()
        record_cognitive_shadow(session_id, cs)
    # deploy-like turn: high sycophancy, low reliability
    cs = CognitiveShadow(sycophancy_pressure=0.9, self_report_reliability=0.2)
    cs.compute_thickness()
    record_cognitive_shadow(session_id, cs)
    # verify
    ss = get_session_shadow(session_id)
    af = ss.detect_alignment_faking()
    assert af["detected"] is True
    assert af["confidence"] >= confidence, f"AF confidence {af['confidence']} < {confidence}"


def _setup_flux_session(session_id: str, thickness: float):
    """Seed session shadow with a single thick turn to force flux value."""
    cs = CognitiveShadow()
    cs.shadow_thickness = thickness
    record_cognitive_shadow(session_id, cs)
    ss = get_session_shadow(session_id)
    flux = ss.compute_metabolic_flux()
    assert flux == pytest.approx(thickness, abs=1e-9)


@pytest.mark.asyncio
async def test_empty_bundle_hold_888():
    res = await _888_judge.execute(evidence_bundle=None, session_id="test-empty")
    assert res["verdict"] == _888_judge.VERDICT_HOLD_888
    assert "F7" in res["rationale"] or "Humility" in res["rationale"]
    _assert_truth_layer(res)


@pytest.mark.asyncio
async def test_normal_clean_seal():
    bundle = _make_evidence_bundle()
    res = await _888_judge.execute(evidence_bundle=bundle, session_id="test-clean")
    assert res["verdict"] == _888_judge.VERDICT_SEAL
    _assert_truth_layer(res)
    assert res["metabolic_metadata"]["paradox_guard"]["active"] is False


@pytest.mark.asyncio
async def test_prefloor_af_blocks():
    session_id = "test-prefloor-af"
    _setup_af_session(session_id, confidence=0.7)
    bundle = _make_evidence_bundle()
    res = await _888_judge.execute(evidence_bundle=bundle, session_id=session_id)
    assert res["verdict"] == _888_judge.VERDICT_HOLD_888
    assert any(
        fr["tag"] == "L13_SHADOW_ALIGNMENT_FAKING"
        for fr in res["metabolic_metadata"]["floor_alignment"].values()
    )
    _assert_truth_layer(res)


@pytest.mark.asyncio
async def test_prefloor_flux_system_hold():
    session_id = "test-prefloor-flux"
    _setup_flux_session(session_id, thickness=0.9)
    bundle = _make_evidence_bundle()
    res = await _888_judge.execute(evidence_bundle=bundle, session_id=session_id)
    assert res["verdict"] == _888_judge.VERDICT_HOLD_888
    assert any(
        fr["tag"] == "F7_SHADOW_FLUX"
        for fr in res["metabolic_metadata"]["floor_alignment"].values()
    )
    _assert_truth_layer(res)


@pytest.mark.asyncio
async def test_paradox_guard_low_confidence():
    """
    Metrics pass all floors but confidence < 0.6 triggers paradox guard.
    omega_0 at boundary (0.03) gives omega_norm=0, tri_witness=0 → confidence ~0.596.
    """
    bundle = _make_evidence_bundle(
        omega_0=0.03,
        peace_squared=1.0,
        tri_witness_score=0.0,
    )
    res = await _888_judge.execute(evidence_bundle=bundle, session_id="test-paradox-conf")
    assert res["verdict"] == _888_judge.VERDICT_HOLD_888
    assert res["metabolic_metadata"]["paradox_guard"]["active"] is True
    assert res["metabolic_metadata"]["paradox_guard"]["blocking_tag"] == "PARADOX_GUARD_CONFIDENCE"
    _assert_truth_layer(res)


@pytest.mark.asyncio
async def test_paradox_guard_flux():
    """
    Metrics pass all floors, confidence >= 0.6, but metabolic flux >= 0.65.
    """
    session_id = "test-paradox-flux"
    _setup_flux_session(session_id, thickness=0.7)
    bundle = _make_evidence_bundle()
    res = await _888_judge.execute(evidence_bundle=bundle, session_id=session_id)
    assert res["verdict"] == _888_judge.VERDICT_HOLD_888
    assert res["metabolic_metadata"]["paradox_guard"]["active"] is True
    assert res["metabolic_metadata"]["paradox_guard"]["blocking_tag"] == "PARADOX_GUARD_FLUX"
    _assert_truth_layer(res)


@pytest.mark.asyncio
async def test_paradox_guard_af_postfloor():
    """
    Metrics pass all floors, confidence >= 0.6, but AF confidence >= 0.6 post-floor.
    Pre-floor guard triggers at >= 0.7, so we target 0.6-0.7 range.
    """
    session_id = "test-paradox-af"
    # eval-like turns: sycophancy < 0.3, reliability > 0.7
    for _ in range(2):
        cs = CognitiveShadow(sycophancy_pressure=0.25, self_report_reliability=0.9)
        cs.compute_thickness()
        record_cognitive_shadow(session_id, cs)
    # deploy-like turn: sycophancy > 0.6, reliability < 0.5
    cs = CognitiveShadow(sycophancy_pressure=0.61, self_report_reliability=0.2)
    cs.compute_thickness()
    record_cognitive_shadow(session_id, cs)

    ss = get_session_shadow(session_id)
    af = ss.detect_alignment_faking()
    assert af["detected"] is True
    assert 0.6 <= af["confidence"] < 0.7, f"AF confidence {af['confidence']} outside [0.6, 0.7)"

    bundle = _make_evidence_bundle()
    res = await _888_judge.execute(evidence_bundle=bundle, session_id=session_id)
    assert res["verdict"] == _888_judge.VERDICT_HOLD_888
    assert res["metabolic_metadata"]["paradox_guard"]["active"] is True
    assert res["metabolic_metadata"]["paradox_guard"]["blocking_tag"] == "PARADOX_GUARD_AF"
    _assert_truth_layer(res)


def _assert_truth_layer(res: dict):
    assert res.get("truth_layer") == TruthLayer.CHECKLIST
    assert res.get("absolute_truth_claimed") is False
    assert res.get("unknown_unknowns_acknowledged") is True
    assert res.get("human_judgment_required") is True
    assert res.get("godel_lock_active") is True

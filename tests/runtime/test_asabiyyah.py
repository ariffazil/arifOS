"""Tests for arifosmcp.runtime.asabiyyah — the federation cycle instrument."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pytest

from arifosmcp.runtime.asabiyyah import (
    ASD_GENERATIVE,
    ASD_KAFES,
    CER_LUXURY,
    ENC_KERKOPORTA,
    Metric,
    aggregate,
    asabiyyah_depth,
    band_asd,
    band_cer,
    band_enc,
    ceremony_exercise_ratio,
    classify_stage,
    enforcement_coverage,
    kampung_gadai_risk,
    mirror_check,
    path_out,
)


# --- the three signals ----------------------------------------------------


def test_cer_is_doctrine_over_exercise():
    m = ceremony_exercise_ratio(6707, 979, source="find /root/AAA")
    assert m.state == "MEASURED"
    assert m.value == pytest.approx(6.85, abs=0.01)
    assert m.band == "DECLINE"  # >= CER_LUXURY


def test_cer_zero_exercise_is_decline_not_undefined_zero():
    """Nothing exercised with ceremony present is the worst case, not the safest.

    The value must be null, NOT float('inf'): json.dumps writes `Infinity` for
    inf, which is not valid RFC 8259 and strict parsers (jq) reject the file.
    State stays MEASURED -- both underlying counts were measured; it is the
    ratio that has no finite value.
    """
    m = ceremony_exercise_ratio(10, 0, source="test")
    assert m.value is None
    assert m.state == "MEASURED"
    assert m.band == "DECLINE"
    assert json.dumps({"v": m.value}) == '{"v": null}'  # never Infinity


def test_cer_empty_substrate_is_not_applicable():
    m = ceremony_exercise_ratio(0, 0, source="test")
    assert m.state == "NOT_APPLICABLE"
    assert m.value is None


def test_asd_kafes_signature():
    m = asabiyyah_depth(50, 1, source="test")
    assert m.value == pytest.approx(0.02)
    assert m.band == "KAFES"


def test_asd_no_doctrine_holders_is_not_applicable():
    assert asabiyyah_depth(0, 0, source="test").state == "NOT_APPLICABLE"


def test_asd_is_clamped_to_one():
    assert asabiyyah_depth(2, 9, source="test").value == 1.0


def test_enc_zero_paths_enumerated_is_not_full_coverage():
    """The most dangerous default in the whole module."""
    m = enforcement_coverage(0, 0, source="test")
    assert m.state == "NOT_APPLICABLE"
    assert m.value is None


def test_enc_kerkoporta_band():
    m = enforcement_coverage(70, 100, source="test", ungated=["bash-echo-write"])
    assert m.band == "KERKOPORTA"
    assert "bash-echo-write" in m.notes


def test_enc_complete():
    assert enforcement_coverage(12, 12, source="test").band == "COMPLETE"


# --- classifier -----------------------------------------------------------


def _metrics(cer=None, asd=None, enc=None):
    def mk(name, val, state="MEASURED"):
        return Metric(name=name, value=val, state=state, source="test", observed_at="2026-09-19T17:00:00+0800")

    out = {}
    if cer is not None:
        out["cer"] = mk("cer", cer)
    if asd is not None:
        out["asd"] = mk("asd", asd)
    if enc is not None:
        out["enc"] = mk("enc", enc)
    return out


def test_stage_foundation():
    stage, conf, _ = classify_stage(_metrics(cer=0.8, asd=0.7, enc=1.0))
    assert stage == "FOUNDATION"
    assert conf == 1.0


def test_stage_decline_on_kerkoporta_even_if_everything_else_is_healthy():
    """One open postern is an open postern. Byzantium, 1453."""
    stage, _, reasons = classify_stage(_metrics(cer=0.5, asd=0.9, enc=0.79))
    assert stage == "DECLINE"
    assert any("Kerkoporta" in r for r in reasons)


def test_stage_decline_on_kafes():
    stage, _, reasons = classify_stage(_metrics(cer=1.0, asd=ASD_KAFES - 0.01, enc=1.0))
    assert stage == "DECLINE"
    assert any("Kafes" in r for r in reasons)


def test_stage_luxury():
    stage, _, _ = classify_stage(_metrics(cer=4.0, asd=0.8, enc=1.0))
    assert stage == "LUXURY"


def test_stage_unknown_when_nothing_measured():
    stage, conf, _ = classify_stage({})
    assert stage == "UNKNOWN"
    assert conf == 0.0


def test_confidence_counts_measured_signals():
    _, conf, _ = classify_stage(_metrics(cer=1.0, asd=0.6))
    assert conf == pytest.approx(2 / 3, abs=0.01)


# --- path_out (the Meiji clause) -----------------------------------------


def test_path_out_always_offers_a_way_back():
    out = path_out(_metrics(cer=9.0, asd=0.05, enc=0.5))
    assert {"cer", "asd", "enc"} <= set(out)
    assert "postern" in out["enc"].lower()


def test_path_out_holds_when_healthy():
    out = path_out(_metrics(cer=0.5, asd=0.9, enc=1.0))
    assert "hold" in out


# --- derived readings -----------------------------------------------------


def test_mirror_check_story_without_evidence():
    assert mirror_check("Melayu itu bijaksana", [])["class"] == "STORY"


def test_mirror_check_mirror_with_evidence():
    assert mirror_check("Melayu itu bijaksana", ["al-Muqaddimah:1377"])["class"] == "MIRROR"


def test_gadai_bands():
    assert kampung_gadai_risk(0, 100).band == "none"
    assert kampung_gadai_risk(5, 100).band == "watch"
    assert kampung_gadai_risk(20, 100).band == "alert"
    assert kampung_gadai_risk(60, 100).band == "critical"


# --- aggregation ----------------------------------------------------------


def _reading(organ: str, **evidence) -> dict:
    return {
        "reading_version": 1,
        "organ": organ,
        "host": "test-host",
        "observed_at": "2026-09-19T17:00:00+0800",
        "metrics": {},
        "evidence": evidence,
    }


def test_aggregate_federates_counts_not_ratios(tmp_path: Path):
    """A quiet organ must not dilute a loud one: sums, then re-derive."""
    (tmp_path / "a.json").write_text(json.dumps(_reading("AAA", ceremony_artifacts=100, exercised_capabilities=10)))
    (tmp_path / "b.json").write_text(json.dumps(_reading("WELL", ceremony_artifacts=5, exercised_capabilities=50)))

    v = aggregate(tmp_path)
    # 105/60 = 1.75 (COMFORT). Averaging ratios would give (10 + 0.1)/2 = 5.05 (LUXURY).
    assert v.metrics["cer"] == pytest.approx(1.75, abs=0.01)
    assert set(v.organs_read) == {"AAA", "WELL"}


def test_aggregate_with_no_readings_is_unknown_and_names_the_silence(tmp_path: Path):
    v = aggregate(tmp_path)
    assert v.stage == "UNKNOWN"
    assert v.organs_silent  # silence is named, never treated as all-clear


def test_aggregate_flags_kerkoporta_across_organs(tmp_path: Path):
    (tmp_path / "af.json").write_text(
        json.dumps(_reading("A-FORGE", gated_paths=7, total_paths=10, ungated=["direct-edit"]))
    )
    v = aggregate(tmp_path)
    assert v.stage == "DECLINE"
    assert v.metrics["enc"] == pytest.approx(0.7)
    assert "direct-edit" in v.ungated  # the postern is named, not averaged away


def test_aggregate_is_strict_json_serialisable(tmp_path: Path):
    """json.dumps writes `Infinity` for inf by default, and strict RFC 8259
    parsers reject that. The federation verdict must round-trip strict."""
    (tmp_path / "geox.json").write_text(
        json.dumps(_reading("GEOX", ceremony_artifacts=242, exercised_capabilities=0))
    )
    v = aggregate(tmp_path)
    raw = json.dumps(asdict(v), allow_nan=False)  # raises if any non-finite
    assert json.loads(raw)["stage"] == "DECLINE"


# --- band functions are the single place thresholds live ------------------


def test_bands_are_monotone():
    assert band_cer(None) == "NOT_APPLICABLE"
    assert band_cer(0.1) == "FOUNDATION"
    assert band_cer(CER_LUXURY + 0.01) == "DECLINE"
    assert band_asd(ASD_GENERATIVE) == "GENERATIVE"
    assert band_enc(ENC_KERKOPORTA) == "PARTIAL"

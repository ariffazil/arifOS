"""F9 ANTI-HANTU — KX-011 producer tests (2026-11-20, F13 GO: instrumentation only).

Covers the governance-shadow density producer in floor_producers._f9_antihantu:

  * consistent audit payload      -> MEASURED band with computed shadow_ratio
                                     (0.0 over real_count>0 is a REAL zero)
  * evidence absent / None        -> UNMEASURED under producer origin
  * malformed payload / counts    -> UNMEASURED (present-but-junk is not evidence)
  * CLEAN verdict + shadows>0     -> FAIL contradiction (active fabrication never
                                     averaged away by a coverage verdict)
  * counts contradict total_rules -> FAIL contradiction
  * zero basis                    -> UNMEASURED (never a placeholder 0.0)
  * registry wired: F9 leaves the no-producer default bucket
  * F6 regression: existing producer path unchanged
  * purity: producer must not mutate the injected sources dict

Authority boundary (F13 2026-11-20): instrumentation ONLY — these tests pin
that the producer never fabricates pass states and never touches thresholds.
"""

from __future__ import annotations

import copy

from arifosmcp.runtime.floor_producers import (
    _PRODUCERS,
    _f9_antihantu,
    collect_floor_producer_signal,
)


def _audit(
    real: object = 10,
    shadow: object = 0,
    verdict: object = "CLEAN",
    total: object | None = None,
) -> dict:
    payload: dict = {"real_count": real, "shadow_count": shadow, "verdict": verdict}
    if total is not None:
        payload["total_rules"] = total
    return payload


# -- MEASURED band -----------------------------------------------------------


def test_clean_topology_measured_real_zero():
    sig = _f9_antihantu({"shadow_audit": _audit(real=10, shadow=0)})
    assert sig["status"] == "MEASURED"
    assert sig["shadow_ratio"] == 0.0
    assert sig["real_count"] == 10 and sig["shadow_count"] == 0
    assert "rules=10" in sig["origin"]  # a REAL zero names its basis
    assert sig["audit_verdict"] == "CLEAN"


def test_shadows_present_measured_ratio():
    sig = _f9_antihantu({"shadow_audit": _audit(real=8, shadow=2, verdict="SHADOWS_PRESENT")})
    assert sig["status"] == "MEASURED"
    assert abs(sig["shadow_ratio"] - 0.2) < 1e-9
    assert sig["audit_verdict"] == "SHADOWS_PRESENT"


def test_measured_carries_shadow_residual():
    sig = _f9_antihantu({"shadow_audit": _audit()})
    assert sig["shadow_residual"], "PASS-theatre guard: measured must name what was NOT read"


# -- UNMEASURED (missing / malformed) ----------------------------------------


def test_missing_sources_unmeasured_producer_origin():
    sig = _f9_antihantu({})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "shadow_audit:evidence_absent"
    assert not sig["origin"].startswith("unmeasured_default")


def test_none_audit_unmeasured():
    assert _f9_antihantu({"shadow_audit": None})["origin"] == "shadow_audit:evidence_absent"


def test_non_dict_audit_unmeasured():
    sig = _f9_antihantu({"shadow_audit": ["junk"]})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "shadow_audit:malformed_payload"


def test_missing_count_keys_unmeasured():
    sig = _f9_antihantu({"shadow_audit": {"verdict": "CLEAN"}})
    assert sig["origin"] == "shadow_audit:malformed_counts"


def test_negative_counts_unmeasured():
    sig = _f9_antihantu({"shadow_audit": _audit(real=-1, shadow=0)})
    assert sig["origin"] == "shadow_audit:malformed_counts"


def test_bool_counts_unmeasured():
    sig = _f9_antihantu({"shadow_audit": _audit(real=True, shadow=0)})
    assert sig["origin"] == "shadow_audit:malformed_counts"


def test_bad_total_rules_type_unmeasured():
    sig = _f9_antihantu({"shadow_audit": _audit(real=5, shadow=0, total="ten")})
    assert sig["origin"] == "shadow_audit:malformed_counts"


def test_zero_basis_never_placeholder_zero():
    sig = _f9_antihantu({"shadow_audit": _audit(real=0, shadow=0)})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "shadow_audit:empty_basis"
    assert "shadow_ratio" not in sig


# -- FAIL (active fabrication signature) -------------------------------------


def test_clean_verdict_with_shadows_is_fail():
    sig = _f9_antihantu({"shadow_audit": _audit(real=8, shadow=2, verdict="CLEAN")})
    assert sig["status"] == "FAIL"
    assert "clean_verdict_with_shadows" in sig["origin"]


def test_counts_mismatch_total_is_fail():
    sig = _f9_antihantu({"shadow_audit": _audit(real=5, shadow=1, verdict="SHADOWS_PRESENT", total=10)})
    assert sig["status"] == "FAIL"
    assert "counts_mismatch" in sig["origin"]


# -- registry + collect path --------------------------------------------------


def test_registry_wired_f9_leaves_default_bucket():
    assert "F9" in _PRODUCERS
    sig = collect_floor_producer_signal("F9", sources={"shadow_audit": _audit()})
    assert sig["status"] == "MEASURED"
    assert sig["measured_at"] and sig["unit"] == "1"
    assert not str(sig["origin"]).startswith("unmeasured_default")


def test_collect_no_sources_names_producer_not_no_producer():
    sig = collect_floor_producer_signal("F9")
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "shadow_audit:evidence_absent"


def test_contract_label_falsification_rides_signal():
    sig = collect_floor_producer_signal("F9", sources={"shadow_audit": _audit()})
    assert "shadow ratio" in sig.get("falsification_test", "")


def test_previous_producers_still_registered():
    for fid in ("F2", "F5", "F6", "F7", "F8", "F10", "F11", "F12", "F13"):
        assert fid in _PRODUCERS


# -- purity -------------------------------------------------------------------


def test_producer_does_not_mutate_sources():
    src = {"shadow_audit": _audit(real=3, shadow=1)}
    snapshot = copy.deepcopy(src)
    _f9_antihantu(src)
    assert src == snapshot


# -- F6 regression (existing producer path unchanged) -------------------------


def test_f6_producer_path_intact():
    wh = {
        "truth_status": "OPERATOR_VERBAL",
        "environment": "PROD",
        "freshness": {"age_seconds": 600.0, "stale_after_seconds": 14400.0},
        "honesty": {"source_type": "OPERATOR_VERBAL", "is_mock_or_test": False},
    }
    sig = collect_floor_producer_signal("F6", sources={"well_health": wh})
    assert str(sig.get("status", "")).startswith("MEASURED")
    assert str(sig.get("origin", "")).startswith("well_health:")

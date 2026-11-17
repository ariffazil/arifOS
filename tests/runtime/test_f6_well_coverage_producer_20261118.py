"""F6 MARUAH — OS-1 Source A producer tests (2026-11-18, F13 GO).

Covers the WELL served-surface coverage-first wiring in
floor_producers._f6_well_coverage / _f6_maruah:

  * covered  -> MEASURED / MEASURED_V0_PARTIAL with the conservative index
  * stale    -> STALE with age named in null_reasons
  * uncovered-> UNMEASURED under the PRODUCER origin (never unmeasured_default)
  * contamination (TEST env / mock state) -> UNMEASURED with reason
  * seal coercion FAIL stays in front of coverage (never averaged away)
  * absent well_health -> existing meters path unchanged
  * live-shaped /health payload does NOT trip the L1 human-scoring guard

Proposal: /root/forge_work/proposals/PROPOSAL-OS1-f6-floor-producer-2026-11-18.md
"""

from __future__ import annotations

from arifosmcp.runtime.floor_producers import (
    _f6_maruah,
    collect_floor_producer_signal,
)


def _wh(
    truth: str = "OPERATOR_VERBAL",
    age: object = 600.0,
    cap: object = 14400.0,
    environment: str = "PROD",
    mock: bool = False,
    source_type: str = "OPERATOR_VERBAL",
    freshness: dict | None = None,
) -> dict:
    return {
        "truth_status": truth,
        "environment": environment,
        "freshness": freshness
        if freshness is not None
        else {"age_seconds": age, "stale_after_seconds": cap, "expired_after_seconds": cap},
        "honesty": {"source_type": source_type, "is_mock_or_test": mock},
    }


def _seal_with_critique(critique: dict) -> dict:
    return {"actor": "888", "payload": {"heart_critique": critique}}


# ── covered -> MEASURED_V0_PARTIAL ──────────────────────────────────────────


def test_covered_yields_measured_partial() -> None:
    sig = _f6_maruah({"well_health": _wh()})
    assert sig["status"] == "MEASURED"
    assert sig["verdict"] == "MEASURED_V0_PARTIAL"
    assert sig["f6_index"] == 0.5, "conservative floor of the WELL v0 formula, never painted higher"
    assert sig["origin"].startswith("well_health:f6_v0_partial:covered@")
    assert sig["null_reasons"] == []


def test_covered_via_operator_reported() -> None:
    sig = _f6_maruah(
        {"well_health": _wh(truth="OPERATOR_REPORTED", source_type="OPERATOR_REPORTED")}
    )
    assert sig["status"] == "MEASURED"


def test_string_age_is_coerced_not_dropped() -> None:
    sig = _f6_maruah({"well_health": _wh(age="7200")})
    assert sig["status"] == "MEASURED", "served JSON may carry numeric strings; coerce honestly"


# ── uncovered states keep the producer origin, never unmeasured_default ────


def test_stale_substrate_is_stale_with_age_named() -> None:
    sig = _f6_maruah({"well_health": _wh(age=17803.6)})
    assert sig["status"] == "STALE"
    assert sig["origin"] == "well_health:stale_substrate"
    assert sig["f6_index"] is None
    assert sig["verdict"] == "INSTRUMENTED_COVERAGE_INSUFFICIENT"
    assert any("17804s" in r or "age" in r for r in sig["null_reasons"]), sig["null_reasons"]


def test_insufficient_truth_is_unmeasured_under_producer_origin() -> None:
    """Acceptance: uncovered days still print null-with-reason (F2 honest) —
    and the origin names the INSTRUMENT, not unmeasured_default."""
    sig = _f6_maruah({"well_health": _wh(truth="INSUFFICIENT_DATA")})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "well_health:coverage_insufficient"
    assert not sig["origin"].startswith("unmeasured_default")
    assert sig["f6_index"] is None
    assert any("truth=INSUFFICIENT_DATA" in r for r in sig["null_reasons"])


def test_contaminated_environment_is_uncovered() -> None:
    sig = _f6_maruah({"well_health": _wh(environment="TEST")})
    assert sig["status"] == "UNMEASURED"
    assert any("contaminated" in r for r in sig["null_reasons"])


def test_mock_or_test_state_is_uncovered() -> None:
    sig = _f6_maruah({"well_health": _wh(mock=True)})
    assert sig["status"] == "UNMEASURED"
    assert any("contaminated" in r for r in sig["null_reasons"])


def test_missing_freshness_block_is_age_unknown() -> None:
    sig = _f6_maruah({"well_health": _wh(freshness={})})
    assert sig["status"] == "UNMEASURED"
    assert any("age=UNKNOWN" in r for r in sig["null_reasons"])


def test_empty_well_health_dict_is_uncovered_not_crash() -> None:
    sig = _f6_maruah({"well_health": {}})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "well_health:coverage_insufficient"


# ── seal coercion precedence — never averaged away ─────────────────────────


def test_seal_coercion_fails_even_when_well_covered() -> None:
    sig = _f6_maruah(
        {
            "well_health": _wh(),
            "seals": [_seal_with_critique({"coercion": True})],
        }
    )
    assert sig["status"] == "FAIL"
    assert sig["origin"] == "heart_critique"
    assert sig["reason"] == "coercion_present"


def test_seal_compromised_dignity_fails_even_when_well_covered() -> None:
    sig = _f6_maruah(
        {
            "well_health": _wh(),
            "seals": [_seal_with_critique({"dignity_verdict": "COMPROMISED"})],
        }
    )
    assert sig["status"] == "FAIL"


# ── absent well_health -> existing meters path unchanged ───────────────────


def test_no_well_health_falls_back_to_meters_contract() -> None:
    sig = _f6_maruah({})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:f6_mandatory_evidence_missing"


def test_empty_seal_list_still_routes_seal_fallback() -> None:
    """seals=[] (present, empty) keeps the historical seal-probe origin."""
    sig = _f6_maruah({"seals": []})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:no_heart_critique"


# ── L1 guard: live-shaped payload must not trip human-scoring ──────────────


def test_live_shaped_payload_does_not_trip_l1() -> None:
    """The REAL served /health shape (probed 2026-11-18T01:08+08) carries
    human_substrate / metrics.derived / well_score blocks. None of those are
    forbidden L1 keys; the sanctioned mirror read must not DISQUALIFY."""
    live_shaped = {
        **_wh(truth="INSUFFICIENT_DATA", age=17803.6),
        "status": "degraded",
        "well_score": None,
        "clarity": 6,
        "human_substrate": {
            "status": "INSUFFICIENT_DATA",
            "source": "state.json",
            "honesty": "INSUFFICIENT",
            "freshness_band": "EXPIRED",
            "age_hours": 5.0,
            "blocked_on": "sovereign biometric inject or Google Fit OAuth",
            "note": "do not invent well_score from mock/test state",
        },
        "metrics": {"derived": {"fatigue": 7, "energy": 3, "calm": 3, "mood": 8}},
        "owner_summary": {"color": "YELLOW", "reasons": ["sovereign_state_unknown"]},
    }
    sig = _f6_maruah({"well_health": live_shaped})
    assert sig["status"] in ("UNMEASURED", "STALE"), sig
    assert "L1_BREACH" not in str(sig.get("reason", ""))


# ── registration + provenance shape ────────────────────────────────────────


def test_registered_through_collect_signal() -> None:
    sig = collect_floor_producer_signal("F6", sources={"well_health": _wh()})
    assert sig["floor"] == "F6"
    assert sig["status"] == "MEASURED"
    assert sig.get("unit") == "1"
    assert sig.get("measured_at"), "P4 WHEN slot must ride every signal"
    assert "falsification_test" in sig, "KX-010 contract label must ride the signal"


def test_measured_provenance_string_carries_no_unmeasured_segment() -> None:
    sig = collect_floor_producer_signal("F6", sources={"well_health": _wh()})
    prov = f"floor_producer:{sig['status']}:{sig.get('origin')}@{sig.get('measured_at')}"
    assert "floor_producer:MEASURED:well_health:" in prov
    assert "UNMEASURED" not in prov, "MEASURED must not contain an UNMEASURED segment"

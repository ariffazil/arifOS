"""Honest-green wiring regressions — 2026-10-26 (F13 "INIT, VERIFY AND STABILIZE").

Three measured defects, each one a *wiring* gap rather than a logic gap:

1. F1 — `_phi_fq_from_quotient` (the ratified fq_policy.yaml floor-0.5 mapping)
   existed, had tests, and had ZERO callers. The live path collapsed a 7-value
   constellation into `1.0 if verdict == "FLOWING" else 0.0`, so a WIRING
   diagnosis (`PARTIAL_WIRING` / `FEEL_UNANCHORED`, which arifFlow documents as
   "not pathologies") decided a constitutional floor.

2. F8 — a SKIPPED live producer (`arifflow_vector_g_skipped:calibration=
   PHASE_1_HEURISTIC_UNCALIBRATED`) left the placeholder 0.8 in place and that
   placeholder rendered `status: pass, measured: true`. Provenance honest,
   status green.

3. F6 — the producer was unit-tested only against a synthetic dict payload.
   The real seal-chain writer stores `payload` as a STRING (or None), so the
   dict assumption raised AttributeError and the caller reported a producer
   crash as an evidence gap.

These are wiring assertions on purpose: the defect class is "the unit is
tested, the call site is not".
"""

from __future__ import annotations

import inspect

from arifosmcp.runtime.floor_producers import _f6_maruah
from arifosmcp.runtime.rest_routes import rest_routes as rr


# ── F1: the measurement decides the floor, not the wiring diagnosis ─────────


def test_f1_ratified_mapping_is_actually_called() -> None:
    """A function with tests but no caller is dead code wearing a green badge."""
    src = inspect.getsource(rr)
    assert "_phi_fq_from_quotient(_fq_quotient)" in src, (
        "F1 regressed to a non-ratified mapping: _phi_fq_from_quotient is the "
        "fq_policy.yaml floor-0.5 instrument and must be the one that scores F1"
    )


def test_f1_binary_constellation_collapse_is_gone() -> None:
    src = inspect.getsource(rr)
    assert '== "FLOWING" else 0.0' not in src, (
        "F1 collapsed the arifFlow constellation into FLOWING/not-FLOWING again; "
        "PARTIAL_WIRING and FEEL_UNANCHORED are wiring-coverage states, not flow "
        "failures (arifFlow vector.rs: 'they are not pathologies')"
    )


def test_f1_mapping_is_threshold_bound_at_ratified_floor() -> None:
    # The ratified floor is 0.5 (fq_policy.yaml, F13 RATIFIED 2026-09-12).
    # A wiring state may not move this boundary.
    assert rr._phi_fq_from_quotient(0.5) == 1.0
    assert rr._phi_fq_from_quotient(0.4999) == 0.0
    assert rr._phi_fq_from_quotient(0.9677) == 1.0  # the live PARTIAL_WIRING case


def test_f1_provenance_prefix_is_a_measured_producer_token() -> None:
    """The prefix must classify as MEASURED in health_truth, or the same
    response says 'pass' and 'unmeasured' about the same floor (K7)."""
    from arifosmcp.runtime.health_truth import classify_provenance

    prov = "arifflow_probe:quotient=0.9677;floor=0.5;constellation=PARTIAL_WIRING"
    assert classify_provenance(prov) == "measured"


# ── F8: a skipped producer may not render a substituted pass ────────────────


def test_skipped_provenance_is_declared_unmeasured() -> None:
    assert rr._provenance_is_unmeasured(
        "arifflow_vector_g_skipped:calibration=PHASE_1_HEURISTIC_UNCALIBRATED"
    )
    assert rr._provenance_is_unmeasured("unmeasured_default:no_heart_critique")
    assert not rr._provenance_is_unmeasured("arifflow_probe:g=0.5842")
    assert not rr._provenance_is_unmeasured("floor_producer:PASS:receipt_ledger")
    # Absent provenance is unknown, not declared-absent: previous behaviour kept.
    assert not rr._provenance_is_unmeasured(None)


def test_f8_skipped_producer_cannot_pass() -> None:
    status = rr._floor_status_with_provenance(
        "F8", 0.8, "arifflow_vector_g_skipped:calibration=PHASE_1_HEURISTIC_UNCALIBRATED"
    )
    assert status == "unmeasured", (
        "the placeholder 0.8 rendered as a measured pass while the live G "
        "reading was skipped — provenance honest, status green"
    )


def test_f8_real_measurement_still_passes() -> None:
    assert rr._floor_status_with_provenance("F8", 0.9, "arifflow_probe:g=0.9") == "pass"
    assert rr._floor_status_with_provenance("F8", 0.2, "arifflow_probe:g=0.2") == "fail"


# ── F6: the producer must survive the REAL seal-row payload shape ───────────


def test_f6_accepts_string_payload_with_critique() -> None:
    import json

    row = {"actor": "888", "payload": json.dumps({"heart_critique": {"dignity": 0.9}})}
    assert _f6_maruah({"seals": [row]})["status"] == "UNMEASURED"  # origin/main F6: a seal declaration can never PASS


def test_f6_string_payload_conflict_still_fails() -> None:
    import json

    row = {"actor": "888", "payload": json.dumps({"heart_critique": {"coercion": True}})}
    sig = _f6_maruah({"seals": [row]})
    assert sig["status"] == "FAIL"
    assert sig["reason"] == "coercion_present"


def test_f6_unparseable_string_payload_is_unmeasured_not_a_crash() -> None:
    sig = _f6_maruah({"seals": [{"actor": "888", "payload": "not json at all"}]})
    assert sig["status"] == "UNMEASURED"
    # The reason must name the evidence gap, not a producer exception.
    assert sig["origin"] == "unmeasured_default:no_heart_critique"


def test_f6_none_payload_is_unmeasured() -> None:
    sig = _f6_maruah({"seals": [{"actor": "888", "payload": None}]})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:no_heart_critique"

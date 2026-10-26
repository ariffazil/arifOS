"""F8 LOGIC producer — internal consistency from the contradiction register.

Gate-grade by definition, not heuristic: zero ACTIVE registered contradictions
PASS, one or more FAIL with ids named. Uncalibrated proxies (arifFlow g,
PHASE_1_HEURISTIC_UNCALIBRATED, F13 order 2026-10-25) never decide F8 through
this producer. Absent/malformed evidence -> UNMEASURED, never PASS (K2).
"""

from __future__ import annotations

from pathlib import Path

from arifosmcp.runtime.floor_producers import (
    _PRODUCERS,
    _f8_logic,
    collect_floor_producer_signal,
)

BODY = (
    Path(__file__).resolve().parents[2] / "arifosmcp" / "runtime" / "rest_routes" / "rest_routes.py"
)


def _reg(*entries: dict) -> dict:
    return {"schema": "contradiction_register.v1", "entries": list(entries)}


def test_registered_producer_and_signal_stamp():
    assert _PRODUCERS.get("F8") is _f8_logic
    sig = collect_floor_producer_signal("F8", sources={})
    assert sig["status"] == "UNMEASURED"
    assert sig["origin"] == "unmeasured_default:contradiction_register_unreachable"
    assert sig.get("measured_at")


def test_register_unreachable_is_unmeasured_never_pass():
    sig = _f8_logic({})
    assert sig["status"] == "UNMEASURED"
    assert "unreachable" in sig["origin"]


def test_malformed_register_shapes_are_unmeasured():
    for bad in (
        {"contradiction_register": "not-a-dict"},
        {"contradiction_register": {"entries": "not-a-list"}},
        {"contradiction_register": _reg({"id": "KX-1", "status": "resolved"}, "junk-row")},
    ):
        sig = _f8_logic(bad)
        assert sig["status"] == "UNMEASURED", bad
        assert sig["origin"].startswith("unmeasured_default:")


def test_all_closed_statuses_pass_case_insensitive():
    sig = _f8_logic(
        {
            "contradiction_register": _reg(
                {"id": "KX-001", "status": "resolved"},
                {"id": "KX-002", "status": "RESOLVED"},
                {"id": "KX-003", "status": "Closed"},
                {"id": "KX-004", "status": "retired"},
            )
        }
    )
    assert sig["status"] == "PASS"
    assert sig["origin"] == "f8_logic_contradiction_register"
    assert sig["closed_count"] == 4
    assert sig["active_count"] == 0
    # a PASS without its shadow residual is predicate theater
    assert "acknowledged contradictions only" in sig["shadow_residual"]


def test_active_contradiction_fails_with_ids_named():
    sig = _f8_logic(
        {
            "contradiction_register": _reg(
                {"id": "KX-001", "status": "resolved", "title": "cooled"},
                {"id": "KX-002", "status": "active", "title": "GOVERNANCE_SCORE_SCOPE_COLLISION"},
            )
        }
    )
    assert sig["status"] == "FAIL"
    assert sig["origin"] == "f8_logic_active_contradictions"
    assert [a["id"] for a in sig["active"]] == ["KX-002"]
    assert sig["closed_count"] == 1


def test_unknown_status_counts_active_fail_closed():
    for status in ("monitoring", "accepted", "", None, "PARKED"):
        sig = _f8_logic({"contradiction_register": _reg({"id": "KX-X", "status": status})})
        assert sig["status"] == "FAIL", status
        assert sig["active"][0]["status"] in ("monitoring", "accepted", "unset", "parked")


def test_real_register_shape_measured_not_unmeasured():
    """The live register shape (lowercase statuses, id/title/status/owner
    entries) must produce a MEASURED verdict — this is the shape on the box."""
    real = {
        "schema": "contradiction_register.v1",
        "consumer": "contradiction_margin",
        "entries": [
            {"id": "KX-001", "status": "resolved", "title": "FLOOR_SURFACE_DUAL_TRUTH"},
            {"id": "KX-002", "status": "active", "title": "GOVERNANCE_SCORE_SCOPE_COLLISION"},
            {"id": "KX-004", "status": "active", "title": "AAA_AUTHORITY_DOCTRINE_CONFLICT"},
        ],
    }
    sig = _f8_logic({"contradiction_register": real})
    assert sig["status"] == "FAIL"
    assert {a["id"] for a in sig["active"]} == {"KX-002", "KX-004"}


def test_rest_routes_wiring_precedence_and_env_seam():
    text = BODY.read_text()
    # K12 precedence: the producer only decides F8 when the arifFlow path left
    # it unresolved (a calibrated g would own the floor)
    assert 'if "F8" not in resolved_floors:' in text
    wire_at = text.index('"contradiction_register": _cr')
    guard_at = text.index('if "F8" not in resolved_floors:')
    assert guard_at < wire_at
    assert "ARIFOS_CONTRADICTION_REGISTER" in text
    # producer error must degrade to UNMEASURED, never raise into health
    assert "f8_producer_error" in text

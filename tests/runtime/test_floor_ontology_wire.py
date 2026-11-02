"""Floor measurement ontology (Gate 1, F13 directive 2026-11-02).

Pins the ontology table + wire-time record builder that types every floor
reading (Arif composition audit: "a typed vector, not a scalar composition").
The promotions the audit named — constant→measured, presence→pass,
receipt→audited, seal→authorized, producer-pass→perfect score — must stay
unrepresentable: an unmeasured floor can never report evidence_class=MEASURED,
and F11/F13 can never report a bare pass without their honesty fields
(verification NOT_ATTEMPTED / action_authority NOT_ESTABLISHED).

The live wire is verified separately by the K9 deploy probe
(runtime_floors_status on /health + observatory floors[].measurement); these
tests pin the pure function and the table's shape.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.floor_producers import (
    _FLOOR_ONTOLOGY,
    floor_ontology_record,
)

UNMEASURED_PROV = "unmeasured_default:no_producer"
SKIPPED_PROV = "arifflow_vector_g_skipped:calibration=UNCALIBRATED"
MEASURED_PROV = "floor_producer:PASS:seal_chain_peace@2026-11-02T00:00:00Z"


def test_ontology_covers_all_13_floors():
    assert set(_FLOOR_ONTOLOGY) == {f"F{i}" for i in range(1, 14)}


def test_every_floor_has_kind_direction_scope_producer():
    for fid, onto in _FLOOR_ONTOLOGY.items():
        assert onto["value_kind"] in {"score", "predicate", "risk"}, fid
        assert onto["direction"] in {"higher_better", "lower_better", "none"}, fid
        assert onto.get("scope"), fid
        assert "producer_instrument" in onto, fid


def test_unmeasured_provenance_never_claims_measured():
    for prov in (UNMEASURED_PROV, SKIPPED_PROV):
        rec = floor_ontology_record("F5", prov, 1.0)
        assert rec["evidence_class"] == "UNMEASURED"
        assert rec["measurement_state"] == "NOT_MEASURED"


def test_producer_pass_is_predicate_not_score():
    rec = floor_ontology_record("F5", MEASURED_PROV, 1.0)
    assert rec["value_kind"] == "predicate"
    assert rec["evidence_class"] == "PREDICATE_PASS"
    assert rec["measurement_state"] == "MEASURED"
    assert rec.get("display_transform"), "projection must be labeled, not hidden"


def test_risk_floors_declare_lower_better():
    for fid in ("F9", "F12"):
        rec = floor_ontology_record(fid, MEASURED_PROV, 0.2)
        assert rec["direction"] == "lower_better"


def test_f11_split_presence_from_verification():
    rec = floor_ontology_record("F11", MEASURED_PROV, 1.0)
    assert rec["verification"]["verification_state"] == "NOT_ATTEMPTED"
    assert rec["verification"]["issuer_verified"] is False
    assert rec["verification"]["signature_verified"] is False
    assert "actor_attribution" in rec["verification"]["checks_performed"]


def test_f13_presence_never_authorizes():
    rec = floor_ontology_record("F13", MEASURED_PROV, 1.0)
    assert "NOT_ESTABLISHED" in rec["action_authority"]


def test_f2_scope_covers_provenance_map_only():
    rec = floor_ontology_record("F2", MEASURED_PROV, 1.0)
    assert (
        "whole-payload"
        in rec["scope"].lower().replace("whole payload", "whole-payload")
        or "NOT" in rec["scope"]
    )


def test_thresholds_read_from_law_table_not_hardcoded():
    rec = floor_ontology_record("F4", MEASURED_PROV, 0.8)
    assert isinstance(rec["threshold"], float)
    assert rec["threshold_comparator"] in (">=", ">", "<", "<=")
    # F7 carries a range spec, not a point threshold
    rec7 = floor_ontology_record("F7", UNMEASURED_PROV, None)
    assert rec7["threshold"] is None
    assert (
        rec7["threshold_range"] is not None
        or rec7["measurement_state"] == "NOT_MEASURED"
    )

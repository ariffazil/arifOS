"""Commit 1 — measurement semantics (F13 judge order 2026-10-18).

Test A (claims are not measurements) and the anti-laundering rule:

  LIVE_PROBE -> measured · SIGNED_ATTESTATION -> attested
  STATIC_CLAIM -> declared · MISSING -> unmeasured

`declared` is never promoted to `measured`. A pass whose provenance is an
absent instrument is not a pass. The 13/13 aggregate is forbidden unless
every floor carries a live instrument.

Named consumer: health_truth.floor_truth() (via rest_routes /health payload
and verdict.py). Failure classes killed here: MEASUREMENT_LAUNDERING
(claims.json counted as live), DENOMINATOR_SILENCE (aggregate N/N hiding
non-measured floors).

Pure unit tests: no kernel, no network.
"""

from __future__ import annotations

from arifosmcp.runtime.health_truth import (
    MEASUREMENT_ATTESTED,
    MEASUREMENT_DECLARED,
    MEASUREMENT_MEASURED,
    MEASUREMENT_UNMEASURED,
    classify_provenance,
    floor_truth,
    promotion_allowed,
)

ALL_PASS = {f"F{i}": "pass" for i in range(1, 14)}


def test_a_claims_are_not_measurements() -> None:
    """Judge Test A: provenance=claims.json must never read as measured."""
    prov = {f"F{i}": f"f4_f9_probe:claims.json:2026-10-18T09:05:02Z" for i in range(5, 11)}
    truth = floor_truth(ALL_PASS, 13, provenance=prov)
    status = truth.as_dict()["floors_measurement_status"]

    for fid in prov:
        assert status[fid] == MEASUREMENT_DECLARED
        assert status[fid] != MEASUREMENT_MEASURED

    # A declared floor cannot make floor_passed True.
    assert truth.floor_passed is None
    # aggregate_13_of_13 forbidden: declared floors are not passes.
    assert truth.floors_pass < truth.floors_total
    assert tuple(sorted(prov)) == truth.floors_declared


def test_taxonomy_maps_four_classes() -> None:
    assert classify_provenance("arifflow_probe:ds=-0.0") == MEASUREMENT_MEASURED
    assert (
        classify_provenance("arifflow_live_ontology:QG_V0_3_VECTOR_SPEC.md") == MEASUREMENT_MEASURED
    )
    assert classify_provenance("floor_producer:PASS:receipt_ledger") == MEASUREMENT_MEASURED
    assert classify_provenance("witness_producers:human+ai+earth") == MEASUREMENT_MEASURED
    assert classify_provenance("attestation:signed:frame-2026-10-18") == MEASUREMENT_ATTESTED
    assert classify_provenance("f4_f9_probe:claims.json:2026-10-18") == MEASUREMENT_DECLARED
    assert classify_provenance("unmeasured_default:empty_kernel_signal") == MEASUREMENT_UNMEASURED
    assert classify_provenance("") == MEASUREMENT_UNMEASURED
    assert classify_provenance(None) == MEASUREMENT_UNMEASURED
    # An unregistered instrument is not a measurement (K2: unknown != zero).
    assert classify_provenance("mystery_signal:x") == MEASUREMENT_UNMEASURED


def test_no_class_is_promoted_to_measured() -> None:
    """KX-003 rule: declared (and attested) never become measured."""
    assert promotion_allowed(MEASUREMENT_DECLARED, MEASUREMENT_MEASURED) is False
    assert promotion_allowed(MEASUREMENT_ATTESTED, MEASUREMENT_MEASURED) is False
    assert promotion_allowed(MEASUREMENT_UNMEASURED, MEASUREMENT_MEASURED) is False
    assert promotion_allowed(MEASUREMENT_MEASURED, MEASUREMENT_MEASURED) is True
    assert promotion_allowed(MEASUREMENT_DECLARED, MEASUREMENT_ATTESTED) is True


def test_status_pass_with_unmeasured_provenance_is_not_a_pass() -> None:
    """Anti-laundering: provenance class overrides a claimed pass."""
    prov = {"F1": "unmeasured_default:empty_kernel_signal"}
    truth = floor_truth(ALL_PASS, 13, provenance=prov)
    assert truth.floor_passed is None
    assert "F1" in truth.floors_unmeasured
    assert truth.floors_pass == 12


def test_declared_failure_still_degrades_fail_closed() -> None:
    """A claimed failure is never softened; a claimed pass is never promoted."""
    detail = dict(ALL_PASS)
    detail["F9"] = "fail"
    prov = {"F9": "f4_f9_probe:claims.json:x"}
    truth = floor_truth(detail, 13, provenance=prov)
    assert truth.floor_passed is False
    assert truth.status == "degraded"
    assert truth.floors_failing == ("F9",)


def test_aggregate_names_its_composition() -> None:
    prov = {f"F{i}": "f4_f9_probe:claims.json:x" for i in range(5, 11)}
    truth = floor_truth(ALL_PASS, 13, provenance=prov)
    d = truth.as_dict()
    assert "measured" in d["floors_aggregate"]
    assert "declared" in d["floors_aggregate"]
    assert d["floors_aggregate"] != "13/13"

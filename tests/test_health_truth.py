"""T1 — one health function. Proves the tri-state mapping is not ambiguous.

Pure unit tests: no kernel, no network. The falsifier they support is
three consecutive live probes where /health, arif_init and arif_observe
agree on substrate_state and floor_passed.
"""

from __future__ import annotations

from arifosmcp.runtime.health_truth import (
    FLOOR_STATUS_FAIL,
    FLOOR_STATUS_PASS,
    FLOOR_STATUS_UNMEASURED,
    floor_truth,
    substrate_truth,
)

ALL_PASS = {f"F{i}": FLOOR_STATUS_PASS for i in range(1, 14)}


def test_all_thirteen_measured_and_passing_is_true() -> None:
    truth = floor_truth(ALL_PASS, 13)
    assert truth.floor_passed is True
    assert truth.measurement == "measured"
    assert truth.status == "healthy"
    assert truth.floors_pass == 13
    assert truth.floors_failing == ()
    assert truth.floors_unmeasured == ()


def test_one_measured_failure_dominates_unmeasured_floors() -> None:
    detail = dict(ALL_PASS)
    detail["F9"] = FLOOR_STATUS_FAIL
    detail["F10"] = FLOOR_STATUS_UNMEASURED
    truth = floor_truth(detail, 13)
    # A measured failure is never softened by an evidence gap elsewhere.
    assert truth.floor_passed is False
    assert truth.measurement == "measured"
    assert truth.status == "degraded"
    assert truth.floors_failing == ("F9",)
    assert truth.floors_unmeasured == ("F10",)


def test_one_unmeasured_floor_makes_the_verdict_unknown_not_true() -> None:
    detail = dict(ALL_PASS)
    detail["F5"] = FLOOR_STATUS_UNMEASURED
    truth = floor_truth(detail, 13)
    # Twelve passes do not add up to "the constitution passed".
    assert truth.floor_passed is None
    assert truth.measurement == "measured"  # something was measured
    assert truth.status == "partial"
    assert truth.floors_pass == 12
    assert truth.floors_unmeasured == ("F5",)


def test_no_instrument_is_unmeasured_not_a_pass() -> None:
    detail = {f"F{i}": FLOOR_STATUS_UNMEASURED for i in range(1, 14)}
    truth = floor_truth(detail, 13)
    assert truth.floor_passed is None
    assert truth.measurement == "unmeasured"
    assert truth.status == "partial"


def test_empty_measurement_is_unmeasured() -> None:
    truth = floor_truth({}, 13)
    assert truth.floor_passed is None
    assert truth.measurement == "unmeasured"
    assert truth.status == "partial"


def test_unknown_status_token_is_treated_as_unmeasured() -> None:
    detail = dict(ALL_PASS)
    detail["F7"] = "UNKNOWN"
    truth = floor_truth(detail, 13)
    assert truth.floor_passed is None
    assert "F7" in truth.floors_unmeasured


def test_substrate_state_is_healthy_only_when_no_cause_is_named() -> None:
    clean = substrate_truth()
    assert clean["substrate_state"] == "HEALTHY"
    assert clean["degraded_causes"] == []
    assert clean["drift"] is False


def test_source_build_drift_degrades_the_substrate() -> None:
    # This is the live KVM8 case: repo HEAD != built commit. The verbs read
    # it as DEGRADED; before T1 /health demoted the same fact to a warning.
    dirty = substrate_truth(source_drift=True)
    assert dirty["substrate_state"] == "DEGRADED"
    assert dirty["degraded_causes"] == ["SOURCE_BUILD_DRIFT"]


def test_all_causes_are_named_not_collapsed() -> None:
    dirty = substrate_truth(
        runtime_drift=True,
        source_drift=True,
        contract_drift=True,
        boot_unhealthy=True,
    )
    assert dirty["substrate_state"] == "DEGRADED"
    assert dirty["degraded_causes"] == [
        "RUNTIME_DRIFT",
        "SOURCE_BUILD_DRIFT",
        "CONTRACT_DRIFT",
        "BOOT_UNHEALTHY",
    ]

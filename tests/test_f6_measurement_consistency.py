"""P0-2 — one F6 measurement state, not three contradictory projections.

Measured defect (2026-11-21, live `:8088/health`): a single payload reported

  floors_unmeasured: ["F6"]
  floors_measurement_status["F6"]: "measured"
  floors_detail["F6"]: "unmeasured"
  floors_aggregate: "13 measured · 0 attested · 0 declared · 1 unmeasured / 13"

F6's provenance was ``floor_producer:STALE:well_health:stale_substrate``. Both
classifiers keyed the measurement class off the head token (``floor_producer``
→ measured) and only recognised an explicit ``UNMEASURED`` segment, so a stale
substrate counted as measured while its status said unmeasured. The aggregate
therefore summed to 14 over 13 floors.

Contract enforced here:

  1. measured and unmeasured are mutually exclusive for every floor;
  2. floors_unmeasured, floors_measurement_status, floors_detail and the
     aggregate counts derive from one normalized state;
  3. a stale substrate is reported unmeasured, never measured — the stale
     condition is not hidden, it is classified;
  4. the aggregate arithmetic sums to the floor total;
  5. the two classifiers (`health_truth.classify_provenance` and
     `rest_routes._provenance_is_unmeasured`) agree, because they share one
     rule.

Pure unit tests: no kernel, no network.
"""

from __future__ import annotations

import re

from arifosmcp.runtime.health_truth import (
    MEASUREMENT_MEASURED,
    MEASUREMENT_UNMEASURED,
    classify_provenance,
    declares_no_measurement,
    floor_truth,
)
from arifosmcp.runtime.rest_routes.rest_routes import _provenance_is_unmeasured

F6_STALE = "floor_producer:STALE:well_health:stale_substrate"
F6_FRESH = "floor_producer:PASS:well_health:substrate_fresh@2026-11-21T09:49:41Z"


def _detail_with_f6(status: str) -> dict[str, str]:
    detail = {f"F{i}": "pass" for i in range(1, 14)}
    detail["F6"] = status
    return detail


def _provenance(f6: str) -> dict[str, str]:
    prov = {
        f"F{i}": f"floor_producer:PASS:probe_{i}@2026-11-21T09:49:41Z" for i in range(1, 14)
    }
    prov["F6"] = f6
    return prov


def _aggregate_counts(aggregate: str) -> dict[str, int]:
    measured = int(re.search(r"(\d+) measured", aggregate).group(1))
    attested = int(re.search(r"(\d+) attested", aggregate).group(1))
    declared = int(re.search(r"(\d+) declared", aggregate).group(1))
    unmeasured = int(re.search(r"(\d+) unmeasured", aggregate).group(1))
    total = int(re.search(r"/ (\d+)$", aggregate).group(1))
    return {
        "measured": measured,
        "attested": attested,
        "declared": declared,
        "unmeasured": unmeasured,
        "total": total,
    }


def test_f6_stale_is_one_state_across_all_projections() -> None:
    """The exact live shape: stale F6 must not be measured in any projection."""
    truth = floor_truth(_detail_with_f6("unmeasured"), 13, provenance=_provenance(F6_STALE))
    d = truth.as_dict()

    assert "F6" in d["floors_unmeasured"], "F6 must appear in floors_unmeasured"
    assert d["floors_measurement_status"]["F6"] == MEASUREMENT_UNMEASURED, (
        "F6 must not be classed as measured while its status is unmeasured"
    )
    assert d["floors_pass"] == 12, "12 floors pass; F6 is not a pass"
    assert d["status"] == "partial"
    assert d["floor_passed"] is None, "an unmeasured floor is not a verdict"

    counts = _aggregate_counts(d["floors_aggregate"])
    assert counts["measured"] == 12
    assert counts["unmeasured"] == 1
    assert counts["measured"] + counts["attested"] + counts["declared"] + counts["unmeasured"] == (
        counts["total"]
    ), f"aggregate must sum to total: {d['floors_aggregate']}"
    assert "13 measured" not in d["floors_aggregate"], "the 14-over-13 reading must not return"


def test_f6_mutual_exclusion_and_arithmetic() -> None:
    """No floor may be both measured and unmeasured; counts sum to the total."""
    truth = floor_truth(_detail_with_f6("unmeasured"), 13, provenance=_provenance(F6_STALE))
    d = truth.as_dict()

    measured_floors = {
        fid
        for fid, cls in d["floors_measurement_status"].items()
        if cls == MEASUREMENT_MEASURED
    }
    assert measured_floors.isdisjoint(d["floors_unmeasured"])
    assert not measured_floors.intersection(d["floors_declared"])

    counts = _aggregate_counts(d["floors_aggregate"])
    assert sum(v for k, v in counts.items() if k != "total") == counts["total"] == 13


def test_control_all_measured_floors_earn_a_measured_pass() -> None:
    """Control case: a genuinely measured floor must still report measured/pass."""
    truth = floor_truth(_detail_with_f6("pass"), 13, provenance=_provenance(F6_FRESH))
    d = truth.as_dict()

    assert d["floors_measurement_status"]["F6"] == MEASUREMENT_MEASURED
    assert "F6" not in d["floors_unmeasured"]
    assert d["floors_pass"] == 13
    assert d["status"] == "healthy"
    assert d["floor_passed"] is True
    assert d["floors_aggregate"] == "13 measured · 0 attested · 0 declared · 0 unmeasured / 13"


def test_non_measurement_verdict_tokens_are_recognised_in_any_segment() -> None:
    for token in ("UNMEASURED", "STALE", "EXPIRED", "MISSING"):
        prov = f"floor_producer:{token}:well_health:reason"
        assert declares_no_measurement(prov) is True, token
        assert classify_provenance(prov) == MEASUREMENT_UNMEASURED, token
        assert _provenance_is_unmeasured(prov) is True, token


def test_negative_control_live_probe_stays_measured() -> None:
    assert declares_no_measurement(F6_FRESH) is False
    assert classify_provenance(F6_FRESH) == MEASUREMENT_MEASURED
    assert _provenance_is_unmeasured(F6_FRESH) is False


def test_both_classifiers_agree_across_samples() -> None:
    """One rule: the renderer and the producer classifier cannot drift apart."""
    samples = [
        F6_FRESH,
        F6_STALE,
        "floor_producer:UNMEASURED:unmeasured_default:f6_partially_measured",
        "unmeasured_default:F7",
        "arifflow_vector_g_skipped:calibration=PHASE_1_HEURISTIC_UNCALIBRATED",
        "f4_f9_probe:claims.json:2026-10-18T09:05:02Z",
    ]
    for prov in samples:
        cls_unmeasured = classify_provenance(prov) == MEASUREMENT_UNMEASURED
        renderer_unmeasured = _provenance_is_unmeasured(prov)
        assert cls_unmeasured == renderer_unmeasured, f"classifiers disagree on {prov!r}"


def test_absent_provenance_is_not_declared_unmeasured() -> None:
    """Documented asymmetry, kept on purpose.

    ``classify_provenance("")`` answers "unmeasured" because no instrument is
    known to have run. ``_provenance_is_unmeasured("")`` answers False because
    an ABSENT provenance is not a *declaration* that nothing ran — the renderer
    must not treat "no provenance field" as a producer saying "no reading".
    Asserting it here means the divergence is a contract, not an accident.
    """
    assert classify_provenance("") == MEASUREMENT_UNMEASURED
    assert _provenance_is_unmeasured("") is False

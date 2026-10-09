"""F3 TRI-WITNESS producer tests (SCAR-OBS-GREENWASH follow-up, 2026-10-03).

The point of these tests is not that F3 goes green — it is that F3 can only go
green when three independent legs are actually measured, and that an unmeasured
leg is reported as a named gap instead of being filled with a constant.
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.runtime import witness_producers as wp


def test_coherence_is_undefined_when_any_leg_is_unmeasured():
    assert wp.coherence(None, 1.0, 1.0) is None
    assert wp.coherence(1.0, None, 1.0) is None
    assert wp.coherence(1.0, 1.0, None) is None


def test_coherence_matches_the_kernel_formula():
    # Same closed form evaluate_floors uses, so a measured F3 is comparable with
    # history. This is also the exact value the removed fabrication produced.
    assert wp.coherence(0.42, 0.99, 0.99) == 0.9299


def test_real_zeros_are_a_result_not_undefined():
    """A leg measured at zero is information. Only None means 'no instrument'."""
    assert wp.coherence(0.0, 0.0, 0.0) == 0.0
    assert wp.coherence(0.0, 1.0, 1.0) == 0.0


def test_human_leg_reports_the_gap_instead_of_a_number():
    value, evidence = wp.probe_human_witness(sources=("/nonexistent/a.jsonl",))
    assert value is None
    assert "NO_INSTRUMENT" in evidence


def test_human_leg_measures_a_real_ledger_when_one_exists(tmp_path):
    ledger = tmp_path / "human_witness.jsonl"
    ledger.write_text(
        "\n".join(
            json.dumps({"human_witness": bool(i % 2)}) for i in range(4)
        )
        + "\n"
    )
    value, evidence = wp.probe_human_witness(sources=(str(ledger),))
    assert value == 0.5
    assert "2/4" in evidence


def test_ai_leg_is_none_when_the_cache_is_absent(tmp_path):
    value, evidence = wp.probe_ai_witness(cache_path=str(tmp_path / "missing.json"))
    assert value is None
    assert "absent" in evidence


def test_ai_leg_excludes_stale_passes(tmp_path):
    """A pass recorded long ago must not keep paying rent as a current witness."""
    import time

    now = time.time()
    cache = {
        "fresh_pass": {"last_pass": True, "last_invocation_at": now - 60},
        "fresh_fail": {"last_pass": False, "last_invocation_at": now - 60},
        "stale_pass": {"last_pass": True, "last_invocation_at": now - 10 * 86400},
    }
    path = tmp_path / "cache.json"
    path.write_text(json.dumps(cache))
    value, evidence = wp.probe_ai_witness(fresh_seconds=86400, cache_path=str(path))
    # Producer rounds to 4dp, so compare at that precision, not default rel tol.
    assert value == pytest.approx(1 / 3, abs=1e-4)
    assert "1 stale excluded" in evidence


def test_earth_leg_probes_the_declared_topology():
    value, evidence = wp.probe_earth_witness()
    if value is None:
        # Unreadable SOT is a legitimate "cannot witness", not a silent 0.
        assert "organs_sot" in evidence
    else:
        assert 0.0 <= value <= 1.0
        assert "tcp_probe" in evidence


def test_collect_reports_blocking_legs_rather_than_averaging_them_away():
    result = wp.collect_witness_legs()
    assert result["total"] == 3
    assert set(result["legs"]) == {"human", "ai", "earth"}
    for leg in result["legs"].values():
        assert leg["state"] in {"measured", "unmeasured"}
        assert isinstance(leg["evidence"], str) and leg["evidence"]
    if result["blocking_legs"]:
        assert result["coherence"] is None
        assert result["complete"] is False
        for leg in result["blocking_legs"]:
            assert result["legs"][leg]["value"] is None
    else:
        assert result["coherence"] is not None


def test_payload_publishes_legs_and_does_not_score_f3_without_them():
    from arifosmcp.runtime.rest_routes import rest_routes as rr

    payload = rr._build_governance_status_payload()
    legs = payload["witness_legs"]
    assert legs["total"] == 3

    f3 = payload["floors"].get("F3")
    provenance = payload["floor_provenance"].get("F3", "")
    if legs["coherence"] is None:
        assert f3 is not None  # value still present for scalar consumers
        assert provenance.startswith("unmeasured_default"), (
            f"F3 has no complete tri-witness but provenance is '{provenance}'"
        )
    else:
        assert f3 == legs["coherence"]
        assert provenance.startswith("witness_producers:")

    # The regression that matters: no leg may be silently substituted.
    for name, leg in legs["legs"].items():
        if leg["value"] is None:
            assert "NO_INSTRUMENT" in leg["evidence"] or "absent" in leg["evidence"] or (
                "unreadable" in leg["evidence"] or "organs_sot" in leg["evidence"]
            ), f"leg {name} is unmeasured but its evidence names no reason"

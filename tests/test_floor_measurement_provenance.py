"""
test_floor_measurement_provenance.py — Hardening regression test (T1, test-only)

Locks the audit's central thesis: "UNMEASURED != PASS" and the kernel
must never report a measurement without provenance. Every floor in
runtime_floors_status must declare (a) measured: bool, (b) a status
(pass/fail/unmeasured), (c) a score, and (d) a provenance string that
explains the measurement source.

If this test fails, the audit's P0 result-contract defect has returned:
a scalar is being reported without the metadata needed to interpret it.
"""

from __future__ import annotations

import json
import urllib.request

import pytest


ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health?detail=1"


def _fetch_health() -> dict:
    req = urllib.request.Request(ARIFOS_HEALTH_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        return json.loads(resp.read())


@pytest.fixture(scope="module")
def health() -> dict:
    try:
        return _fetch_health()
    except Exception as exc:  # pragma: no cover - probe gate
        pytest.skip(f"arifOS /health unreachable: {exc}")


def test_health_returns_floors_dict(health):
    rf = health.get("runtime_floors_status")
    assert isinstance(rf, dict) and rf, "runtime_floors_status must be a non-empty dict"


def test_every_floor_has_measured_status_score_provenance(health):
    """The F2/H1 invariant: every floor measurement carries its own provenance.

    No naked numbers, no implicit 'unmeasured' — the kernel must declare
    HOW the measurement was (or wasn't) made.
    """
    rf = health["runtime_floors_status"]
    allowed_status = {"pass", "fail", "unmeasured", "caution"}
    offenders: list[str] = []
    for floor, entry in rf.items():
        if not isinstance(entry, dict):
            offenders.append(f"{floor}: not a dict ({entry!r})")
            continue
        if "measured" not in entry:
            offenders.append(f"{floor}: missing 'measured'")
        if "status" not in entry:
            offenders.append(f"{floor}: missing 'status'")
        elif str(entry["status"]).lower() not in allowed_status:
            offenders.append(f"{floor}: status={entry['status']!r} not in {allowed_status}")
        if "provenance" not in entry or not str(entry["provenance"]).strip():
            offenders.append(f"{floor}: missing/empty 'provenance'")
        # Score is required when measured; for unmeasured, score may be a default.
        if entry.get("measured") is True and "score" not in entry:
            offenders.append(f"{floor}: measured=True but no 'score'")
    assert not offenders, (
        "Floor provenance invariant violated (UNMEASURED != PASS requires "
        "explicit metadata):\n" + "\n".join(f"  {o}" for o in offenders)
    )


def test_unmeasured_floors_have_meaningful_provenance(health):
    """Unmeasured floors must say WHY (not just 'unmeasured')."""
    rf = health["runtime_floors_status"]
    unmeasured = [(k, v) for k, v in rf.items() if v.get("measured") is False]
    for floor, entry in unmeasured:
        prov = str(entry.get("provenance", "")).lower()
        # The proven reason must mention either default/instrument or be specific.
        assert any(
            token in prov for token in ("default", "instrument", "kernel", "witness", "sample")
        ), f"{floor}: unmeasured provenance '{prov}' lacks explanation"


def test_pass_floors_have_non_null_score(health):
    """Measured-pass floors must carry a real score, not None or zero placeholder."""
    rf = health["runtime_floors_status"]
    for floor, entry in rf.items():
        if entry.get("status") != "pass":
            continue
        score = entry.get("score")
        assert score is not None, f"{floor}: status=pass but score is None"
        # Allow 0.0 as a valid low score (e.g., F9 = 0.0 honesty), but not None.
        assert isinstance(score, (int, float)), f"{floor}: score not numeric: {score!r}"


def test_status_consistency_with_measured_flag(health):
    """measured=True must yield pass/fail; measured=False must yield unmeasured."""
    rf = health["runtime_floors_status"]
    for floor, entry in rf.items():
        measured = entry.get("measured")
        status = str(entry.get("status", "")).lower()
        if measured is True:
            assert status in {"pass", "fail", "caution"}, (
                f"{floor}: measured=True but status={status}"
            )
        elif measured is False:
            assert status == "unmeasured", (
                f"{floor}: measured=False but status={status} (should be unmeasured)"
            )


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

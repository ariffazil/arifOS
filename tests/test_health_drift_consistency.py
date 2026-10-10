"""
test_health_drift_consistency.py — Hardening regression tests (T1, test-only)

Two regression guards derived from the 2026-10-10 forensic:

1. test_drift_fields_never_narrate_safe_while_arithmetic_says_drift
   Locks the fix documented in rest_routes.py:3916 (axis-qualified drift
   split). The Mode-3 defect ("narrate SAFE, arithmetic says drift") was
   fixed by separating runtime_drift, code_runtime_drift, source_build_drift.
   This test asserts deployment_drift_status is consistent with the
   underlying drift booleans.

2. test_overall_health_reflects_kernel_health
   Locks the unresolved Mode-3 instance in state_axes.overall_health
   (rest_routes.py:4160): the field is hardcoded "PASS" while
   status="degraded" + drift_detected is possible. This test currently
   FAILS, documenting the bug and serving as the TDD driver for the
   T2 fix (task-fix-overall-health-naming-collision).

If the kernel's drift split ever regresses to "safe narrative +
drift arithmetic", test 1 fails.
If the overall_health naming collision is ever fixed, test 2 passes.
"""

from __future__ import annotations

import json
import urllib.request

import pytest


ARIFOS_HEALTH_URL = "http://127.0.0.1:8088/health"


def _fetch_health() -> dict:
    req = urllib.request.Request(ARIFOS_HEALTH_URL, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        return json.loads(resp.read())


@pytest.fixture(scope="module")
def health() -> dict:
    try:
        return _fetch_health()
    except Exception as exc:  # pragma: no cover
        pytest.skip(f"arifOS /health unreachable: {exc}")


# ── 1. Mode-3 drift-fields consistency (regression guard for the 3916 fix) ──


def test_drift_fields_never_narrate_safe_while_arithmetic_says_drift(health):
    """deployment_drift_status must reflect the underlying drift booleans.

    Per the rest_routes.py:3916 note (axis-qualified split), the
    deployment_drift_status field is a derived verdict, not a free string.
    If any of the underlying drift booleans is True, status must be
    drift_detected; if all are False, status must be aligned.
    """
    status = health.get("deployment_drift_status")
    runtime_drift = health.get("runtime_drift", False)
    code_runtime_drift = health.get("code_runtime_drift", False)
    source_build_drift = health.get("source_build_drift", False)
    any_drift = bool(runtime_drift or code_runtime_drift or source_build_drift)

    if any_drift:
        assert status == "drift_detected", (
            f"Mode-3 DRIFT NARRATIVE BUG: drift booleans say True (runtime_drift="
            f"{runtime_drift}, code_runtime_drift={code_runtime_drift}, "
            f"source_build_drift={source_build_drift}) but deployment_drift_status="
            f"'{status}'. The kernel must report drift_detected when any drift boolean is True."
        )
    else:
        assert status == "aligned", (
            f"Mode-3 DRIFT NARRATIVE BUG: all drift booleans False but "
            f"deployment_drift_status='{status}' is not 'aligned'."
        )


def test_drift_booleans_are_independent(health):
    """runtime_drift, code_runtime_drift, source_build_drift are three independent axes.

    Per the fix, these are not OR'd or shadowed. Each must carry its own
    value; the consumer can OR them if they want.
    """
    keys = ("runtime_drift", "code_runtime_drift", "source_build_drift")
    for k in keys:
        assert k in health, f"Missing drift axis: {k}"
        assert isinstance(health[k], bool), (
            f"{k} must be bool, got {type(health[k]).__name__}: {health[k]!r}"
        )


# ── 2. TDD driver for T2 fix: overall_health must reflect kernel health ──


def test_overall_health_must_not_say_pass_when_status_degraded(health):
    """state_axes.overall_health="PASS" is HARDCODED (rest_routes.py:4160).

    A consumer reading overall_health to gauge kernel health is currently
    misled: the field says PASS while status=degraded and
    deployment_drift_status=drift_detected. The fix (T2) must either
    (a) rename the field to scope it to session state, (b) compute it
    from the kernel health block, or (c) remove it. This test will
    GREEN when the fix lands.
    """
    overall = (health.get("state_axes") or {}).get("overall_health")
    status = health.get("status")
    dep_drift = health.get("deployment_drift_status")
    thermo_v = (health.get("thermodynamic") or {}).get("verdict")
    owner_color = (health.get("owner_summary") or {}).get("color")

    if overall == "PASS":
        # overall_health=PASS must co-occur with a healthy kernel across all axes.
        assert status == "healthy", (
            f"overall_health=PASS but status={status!r}. "
            f"Either fix overall_health (rename/compute) or fix status."
        )
        assert dep_drift == "aligned", (
            f"overall_health=PASS but deployment_drift_status={dep_drift!r}."
        )
        assert thermo_v == "SEAL", f"overall_health=PASS but thermodynamic.verdict={thermo_v!r}."
        assert owner_color == "GREEN", (
            f"overall_health=PASS but owner_summary.color={owner_color!r}."
        )


def test_overall_health_field_present_for_migration_awareness(health):
    """If overall_health is present, document its scope; consumers should know.

    This is a soft check: it PASSES whether the field is present or
    absent, but emits a note when present and contradicting kernel state.
    It exists to make the T2 fix's TDD signal visible: until the field is
    scoped or removed, the contradiction persists.
    """
    overall = (health.get("state_axes") or {}).get("overall_health")
    status = health.get("status")
    if overall is None:
        pytest.skip("overall_health absent — already remediated or not emitted")
    # If present and PASS while degraded, that is the live bug; flag it.
    if overall == "PASS" and status == "degraded":
        # Don't fail — instead, annotate. The failing test
        # (test_overall_health_must_not_say_pass_when_status_degraded)
        # is the contract enforcer. This one documents the live state.
        assert False, (
            f"state_axes.overall_health=PASS coexists with status=degraded. "
            f"This is the active T2 fix (task-fix-overall-health-naming-collision). "
            f"See rest_routes.py:4160 (hardcoded literal)."
        )


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

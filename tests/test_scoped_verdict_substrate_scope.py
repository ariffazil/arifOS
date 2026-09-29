"""Substrate scope must report physical substrate, not verdict/authority signals.

Regression test for referential-integrity audit item #25 (2026-09-29, 333-AGI/FI-003).

The defect: `_compute_scoped_verdicts` filtered authority-issued degradation
tokens (session_capability_token, identity_band) out of the substrate scope, but
not verdict-scope tokens. `_compute_canonical_verdict` emits
"verdict_monotonicity: HOLD -> RETAK (sub-signal floor dominates aggregate)"
whenever the aggregate verdict is worse than a sub-signal floor. That token is a
statement about VERDICT derivation, not about the machine, yet it set
`_has_degradation=True`; combined with a restricted `status` (anything other
than OK/SEAL) the substrate scope returned DEGRADED, `degraded_dominates` made
it the effective verdict, and `seal_allowed` went false.

Measured on a healthy kernel at 2026-09-29T15:06Z:
    /health                  -> status=healthy, degraded_reasons=[]
    software_release.drift   -> False (source==built==deployed==bc4ad92)
    boot_gate_state('arifOS')-> ('UNATTESTED', False)
    arif_judge               -> substrate_state=DEGRADED, verdict=HOLD/RETAK

So the kernel was asserting physical degradation it had not measured, and Lane A
sealing was unreachable federation-wide.

These tests pin BOTH directions: the false label must go, and every real
substrate signal must still degrade. A fix that only made the first assertion
pass would be a weakened gate, not a repair.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.tools import _compute_scoped_verdicts

VERDICT_TOKEN = "verdict_monotonicity: HOLD \u2192 RETAK (sub-signal floor dominates aggregate)"
AUTH_TOKEN = "session_capability_token: OBSERVE_ONLY"


def _scopes(**kw: object):
    """Call the unit under test with its keyword-only contract."""
    base: dict[str, object] = dict(
        tool_name="arif_judge",
        status="OK",
        verdict="SEAL",
        degradation=[],
        out={},
        result_payload={},
        actor_verified=True,
        runtime_authority="LIMITED_MUTATE",
    )
    base.update(kw)
    return _compute_scoped_verdicts(**base)  # type: ignore[arg-type]


def _substrate_state(vs) -> str:
    """Read the substrate scope state from either return shape."""
    sub = getattr(vs, "substrate", None)
    if sub is None and isinstance(vs, dict):
        sub = vs.get("substrate") or {}
    state = getattr(sub, "state", None)
    if state is None and isinstance(sub, dict):
        state = sub.get("state")
    return str(state)


# ── the bug: a verdict-scope token is not a substrate measurement ────────


def test_verdict_monotonicity_token_does_not_degrade_substrate():
    """Restricted status + verdict-monotonicity note must NOT claim DEGRADED."""
    vs = _scopes(status="HOLD", verdict="HOLD", degradation=[VERDICT_TOKEN])
    assert _substrate_state(vs) != "DEGRADED", (
        "substrate scope reported DEGRADED from a verdict-derivation note; "
        "that is a claim about the machine the kernel never measured"
    )


def test_verdict_token_alone_with_healthy_status_is_not_degraded():
    vs = _scopes(status="OK", verdict="SEAL", degradation=[VERDICT_TOKEN])
    assert _substrate_state(vs) != "DEGRADED"


def test_authority_token_still_excluded_preserves_2026_09_20_fix():
    """The pre-existing authority-issuer exclusion must keep working."""
    vs = _scopes(status="HOLD", verdict="HOLD", degradation=[AUTH_TOKEN])
    assert _substrate_state(vs) != "DEGRADED"


# ── the gate: every REAL substrate signal must still degrade ─────────────


def test_software_release_drift_still_degrades():
    vs = _scopes(status="OK", out={"software_release": {"drift": True}})
    assert _substrate_state(vs) == "DEGRADED"


def test_substrate_state_degraded_still_degrades():
    vs = _scopes(status="OK", out={"substrate": {"state": "DEGRADED"}})
    assert _substrate_state(vs) == "DEGRADED"


def test_substrate_drift_in_result_payload_still_degrades():
    vs = _scopes(status="OK", result_payload={"substrate": {"drift": True}})
    assert _substrate_state(vs) == "DEGRADED"


def test_degraded_list_mentioning_drift_still_degrades():
    """The out['degraded'] substring path must survive the filter change."""
    vs = _scopes(status="OK", out={"degraded": ["kernel_drift"]})
    assert _substrate_state(vs) == "DEGRADED"


def test_genuine_physical_degradation_token_still_degrades():
    """A real substrate complaint is NOT filtered — the fix must not over-reach."""
    vs = _scopes(
        status="HOLD",
        verdict="HOLD",
        degradation=["organ GEOX unreachable: connection refused"],
    )
    assert _substrate_state(vs) == "DEGRADED"


def test_transport_error_still_fails():
    vs = _scopes(status="ERROR", degradation=["transport error: timeout"])
    assert _substrate_state(vs) == "FAIL"


# ── healthy path stays healthy ───────────────────────────────────────────


def test_clean_healthy_payload_passes():
    vs = _scopes(status="OK", verdict="SEAL", degradation=[])
    assert _substrate_state(vs) in ("PASS", "HEALTHY")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))

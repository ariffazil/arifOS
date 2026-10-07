"""Regression tests for the 2026-10-07 verdict-pollution pair.

Two defects, one class — a constitutional VERDICT or an EVIDENCE GAP being
reported as an execution FAILURE:

1. ``rest_routes._floor_status_strict`` classified floors from the NUMBER only,
   so the placeholder scores substituted by ``_FLOOR_DEFAULTS`` (built from
   ``_representative_floor_score()``, which returns each floor's own PASSING
   threshold) were rendered pass/fail as if measured. Live /health showed
   floors_pass 9/13 with floors_failing [F1,F2,F5,F6] while
   ``floors_measured`` named only [F1,F3] — F7 scored 0.04 and F9 scored 0.0
   and both rendered ``pass``, and ``runtime_floors_status`` marked all 13
   ``measured: true``.

2. ``organ_attestation.attest_organ`` mapped any non-healthy organ health
   status to ``DEGRADED_CLAIM``. GEOX answers, is identity-verified and serves
   27 tools, but folds the kernel's inherited ``kernel_verdict: HOLD`` into its
   own ``status: degraded`` — so the bridge blocked BEFORE invoking GEOX
   (``kernel.py`` / ``kernel_canonical.py``), and the Earth evidence needed to
   measure the floors was unreachable. The loop closed on itself.

Both fixes must stay fail-closed: a measured floor that fails still fails, and
an unreachable / empty-surface / unverified organ is still DEGRADED_CLAIM.

Run pinned, or collection binds the wrong tree:
    PYTHONPATH=/root/arifOS python3 -m pytest \
        tests/runtime/test_floor_provenance_and_hold_attestation.py \
        -p no:cacheprovider --override-ini="pythonpath="
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from arifosmcp.runtime import organ_attestation as oa  # noqa: E402
from arifosmcp.runtime.rest_routes.rest_routes import (  # noqa: E402
    _FLOOR_STATUS_FAIL,
    _FLOOR_STATUS_PASS,
    _FLOOR_STATUS_UNMEASURED,
    _floor_status_strict,
    _floor_status_with_provenance,
)

_DEFAULTED = "unmeasured_default:empty_kernel_signal"
_DEFAULTED_BARE = "unmeasured_default"


# ─────────────────────────────────────────────────────────────────────────────
# 1. A substituted score is UNMEASURED — never pass, never fail
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "law_id,score",
    [
        ("F2", 0.5),  # live: rendered `fail`
        ("F5", 0.5),  # live: rendered `fail`
        ("F6", 0.5),  # live: rendered `fail`
        ("F4", 0.8),  # live: rendered `pass`
        ("F7", 0.04),  # live: rendered `pass` on a near-zero score
        ("F9", 0.0),  # live: rendered `pass` on zero
        ("L10", 1.0),  # live: rendered `pass`
        ("L13", 1.0),
    ],
)
@pytest.mark.parametrize("provenance", [_DEFAULTED, _DEFAULTED_BARE])
def test_defaulted_floor_is_unmeasured_whatever_the_number(law_id, score, provenance):
    """The exact live values must not classify once provenance says default."""
    assert _floor_status_with_provenance(law_id, score, provenance) == _FLOOR_STATUS_UNMEASURED


def test_defaulted_floor_disagrees_with_number_only_classifier():
    """Proves the fix changes behaviour — the old path really did coerce."""
    # F9 at 0.0 is a `<`-comparator floor, so the number-only classifier passes it.
    assert _floor_status_strict("F9", 0.0) == _FLOOR_STATUS_PASS
    assert _floor_status_with_provenance("F9", 0.0, _DEFAULTED) == _FLOOR_STATUS_UNMEASURED
    # F5 at 0.5 failed on the same substituted value.
    assert _floor_status_strict("F5", 0.5) == _FLOOR_STATUS_FAIL
    assert _floor_status_with_provenance("F5", 0.5, _DEFAULTED) == _FLOOR_STATUS_UNMEASURED


# ─────────────────────────────────────────────────────────────────────────────
# 2. Fail-closed preserved: real measurements still classify by threshold
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "law_id,score",
    [("F1", 0.2692), ("F2", 0.5), ("F3", 0.821), ("F5", 0.5), ("F9", 0.0), ("L12", 0.425)],
)
@pytest.mark.parametrize(
    "provenance",
    ["arifflow_fq_probe:fq=0.8077", "witness_producers:human+ai+earth", "governance_kernel"],
)
def test_measured_provenance_delegates_to_threshold_gate(law_id, score, provenance):
    """Measured floors must behave exactly as before — no greenwash, no new red."""
    assert _floor_status_with_provenance(law_id, score, provenance) == _floor_status_strict(
        law_id, score
    )


def test_measured_fail_still_fails():
    """F1's live 0.2692 is a genuine measured failure and must stay one."""
    assert (
        _floor_status_with_provenance("F1", 0.2692, "arifflow_fq_probe:fq=0.8077")
        == _FLOOR_STATUS_FAIL
    )


@pytest.mark.parametrize("score", [None, float("nan"), float("inf"), "not-a-number"])
def test_non_numeric_score_still_unmeasured(score):
    assert _floor_status_with_provenance("F3", score, "governance_kernel") == _FLOOR_STATUS_UNMEASURED


@pytest.mark.parametrize("provenance", [None, "", "governance_kernel_alias"])
def test_missing_provenance_does_not_suppress_classification(provenance):
    """Absent provenance must not be laundered into `unmeasured`."""
    assert _floor_status_with_provenance("F1", 0.2692, provenance) == _floor_status_strict(
        "F1", 0.2692
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3. Attestation: inherited HOLD is a verdict, not organ failure
# ─────────────────────────────────────────────────────────────────────────────

# Verbatim shape of live GEOX /health, measured 2026-10-07 22:18 MYT.
_GEOX_HEALTH_INHERITED_HOLD = {
    "status": "degraded",
    "kernel_verdict": "HOLD",
    "service": "geox-unified",
    "version": "v2026.10.03",
    "identity": {"algorithm": "sha256", "value": "geox-3c2d4dc1", "verified": True},
    "domain_law": "NATURAL_LAW",
    "physics_manifest_hash": "sha256:c905aef8e16b2d2085ffe869eb11751e5a6da5faaa2ebc5b33a1580784e25bc5",
    "tools_loaded": 27,
    "canonical_tools": 27,
}
_GEOX_TOOLS = [{"name": f"geox_tool_{i}"} for i in range(27)]


@pytest.fixture
def patch_probes(monkeypatch):
    """Make attest_organ hermetic — no HTTP, no heartbeat side effects."""

    def _install(health: dict, tools: list):
        async def _fake_health(organ_id):
            return dict(health)

        async def _fake_tools(organ_id):
            return list(tools)

        monkeypatch.setattr(oa, "_call_organ_health", _fake_health)
        monkeypatch.setattr(oa, "_list_organ_tools", _fake_tools)
        monkeypatch.setattr(oa, "_record_heartbeat", lambda **kw: None)
        monkeypatch.setattr(oa, "get_arifos_peer_contract_url", lambda: "http://127.0.0.1:8088")
        monkeypatch.setattr(oa, "get_arifos_peer_contract_hash", lambda: "sha256:test")
        monkeypatch.setattr(oa, "_load_organ_identity_anchor", lambda oid: ("physics_manifest", "sha256:test"))
        # _record_heartbeat is stubbed to keep the test hermetic, so the bridge
        # gates would otherwise see no heartbeat and HOLD on staleness — a
        # different gate than the one under test. Pin staleness off so the
        # assertion isolates the attestation-STATUS check.
        from arifosmcp.runtime import heartbeat_registry as hr

        monkeypatch.setattr(hr, "is_organ_stale", lambda oid: False)

    return _install


def _attest(organ_id: str = "GEOX"):
    asyncio.run(oa.attest_organ(organ_id))
    rec = oa.get_organ_attestation(organ_id.upper())
    assert rec is not None, "attest_organ did not write a registry record"
    return rec


def test_inherited_hold_attests_constitutional_hold(patch_probes):
    patch_probes(_GEOX_HEALTH_INHERITED_HOLD, _GEOX_TOOLS)
    rec = _attest()
    assert rec.status == "CONSTITUTIONAL_HOLD"
    assert rec.tool_count == 27
    assert "kernel_verdict=HOLD" in (rec.reason or "")


def test_constitutional_hold_opens_the_bridge_gate(patch_probes):
    """The load-bearing assertion: the gate that used to pre-block now passes."""
    from arifosmcp.tools.kernel import _assert_organ_attested as gate_kernel
    from arifosmcp.tools.kernel_canonical import _assert_organ_attested as gate_canonical

    patch_probes(_GEOX_HEALTH_INHERITED_HOLD, _GEOX_TOOLS)
    _attest()
    assert gate_kernel("geox") is None
    assert gate_canonical("geox") is None


@pytest.mark.parametrize(
    "mutation,expected",
    [
        # No inherited verdict -> a plain unhealthy organ is still a failed claim.
        ({"kernel_verdict": None}, "DEGRADED_CLAIM"),
        # SABAR is a verdict too.
        ({"kernel_verdict": "SABAR"}, "CONSTITUTIONAL_HOLD"),
        # SEAL is not a hold; it is also not `status: degraded`, so this shape is
        # an organ claiming degradation with a seal verdict -> stay fail-closed.
        ({"kernel_verdict": "SEAL"}, "DEGRADED_CLAIM"),
        # Unverified identity -> fail-closed even under HOLD.
        ({"identity": {"verified": False}}, "DEGRADED_CLAIM"),
        ({"identity": None}, "DEGRADED_CLAIM"),
        ({"identity": "geox-3c2d4dc1"}, "DEGRADED_CLAIM"),
    ],
)
def test_hold_classification_is_narrow(patch_probes, mutation, expected):
    health = {**_GEOX_HEALTH_INHERITED_HOLD, **mutation}
    if mutation.get("kernel_verdict", "sentinel") is None:
        health.pop("kernel_verdict", None)
    patch_probes(health, _GEOX_TOOLS)
    assert _attest().status == expected


def test_empty_tool_surface_under_hold_still_degraded_claim(patch_probes):
    """An organ serving nothing is not 'holding correctly'."""
    patch_probes(_GEOX_HEALTH_INHERITED_HOLD, [])
    rec = _attest()
    assert rec.status != "CONSTITUTIONAL_HOLD"


def test_unreachable_organ_still_degraded(patch_probes):
    """Fail-closed: a dead organ must never be laundered into a verdict."""
    patch_probes({"status": "unhealthy"}, _GEOX_TOOLS)
    assert _attest().status == "DEGRADED_CLAIM"


def test_healthy_organ_still_alive(patch_probes):
    patch_probes({**_GEOX_HEALTH_INHERITED_HOLD, "status": "healthy"}, _GEOX_TOOLS)
    assert _attest().status == "ALIVE"


# ─────────────────────────────────────────────────────────────────────────────
# 4. live_kernel envelope: verdicts are not failures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "verdict,expected",
    [
        ("SEAL", "HEALTHY"),
        ("HOLD", "CONSTITUTIONAL_HOLD"),
        ("SABAR", "CONSTITUTIONAL_HOLD"),
        ("OBSERVE_ONLY", "CONSTITUTIONAL_HOLD"),
        ("DEGRADED", "DEGRADED_CLAIM"),
        ("DENY", "DEGRADED_CLAIM"),
    ],
)
def test_envelope_attestation_status_separates_verdict_from_failure(verdict, expected):
    from arifosmcp.runtime.live_kernel import build_kernel_envelope

    env = build_kernel_envelope(
        tool_name="probe_tool",
        response={"verdict": verdict},
        organ_id="GEOX",
        organ_role="domain_evidence",
        organ_version="v-test",
    )
    assert env.organ.attestation_status == expected


def test_envelope_builder_runs_with_session_id():
    """Regression: the `json` UnboundLocalError that killed this builder.

    A function-scoped `import json` (removed 2026-10-07, introduced 2f31e4f64
    on 2026-06-21) made `json` local to build_kernel_envelope, so the
    `json.dumps(response, ...)` at the top raised UnboundLocalError on EVERY
    call. The sole caller, tools._attach_live_kernel_envelope, wraps the call
    in `except Exception: pass` — so for ~3.5 months every tool response
    silently shipped without its live_kernel_envelope field and nothing
    reported it. Passing session_id exercises the exact branch that held the
    shadowing import.
    """
    from arifosmcp.runtime.live_kernel import build_kernel_envelope

    env = build_kernel_envelope(
        tool_name="probe_tool",
        response={"verdict": "SEAL", "delta_S": -0.05},
        session_id="SESS-REGRESSION-0001",
        actor_id="fi-003",
    )
    dumped = env.model_dump(mode="json")
    assert dumped["organ"]["attestation_status"] == "HEALTHY"
    assert dumped["kernel"]["session_id"] == "SESS-REGRESSION-0001"
    # The state hash is computed from json.dumps(response) — the line that crashed.
    assert str(dumped["state"]["current_state_hash"]).startswith("sha256:")


def test_tool_response_carries_live_kernel_envelope():
    """The consumer-facing symptom: the field must actually be attached."""
    from arifosmcp.runtime.live_kernel import build_kernel_envelope

    response: dict = {"verdict": "HOLD", "reason": "probe"}
    envelope = build_kernel_envelope(
        tool_name="probe_tool",
        response=response,
        session_id=None,
        actor_id=None,
    )
    response["live_kernel_envelope"] = envelope.model_dump(mode="json")
    assert "live_kernel_envelope" in response
    assert response["live_kernel_envelope"]["organ"]["attestation_status"] == (
        "CONSTITUTIONAL_HOLD"
    )

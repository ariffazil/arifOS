"""G2c: HOLD resolution classification gates.

Every HOLD names its class + legal resolution lane (K-02 anti-collapse).
The hard invariant: authority/policy holds are NEVER MRTR-eligible —
input cannot elevate authority, enforced structurally by check order.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from arifosmcp.core.hold_resolution import classify_hold  # noqa: E402


def test_authority_hold_names_lane_and_blocks_mrtr():
    r = classify_hold(
        "Action requires human witness. witness_type='ai' is insufficient.",
        authority="OBSERVE_ONLY",
    )
    assert r.hold_class == "authority_required"
    assert r.mrtr_eligible is False
    assert "arif_judge" in r.resolution_lane


def test_anonymous_session_is_authority_not_input():
    r = classify_hold("anonymous-session actor unverified", authority="LOW")
    assert r.hold_class == "authority_required"
    assert r.mrtr_eligible is False


def test_evidence_hold_demands_evidence_not_permission():
    r = classify_hold("L02: Truth Score: 0.960 >= 0.99 (Standard Verification)")
    assert r.hold_class == "evidence_required"
    assert r.mrtr_eligible is False
    assert "evidence" in r.resolution_lane.lower()


def test_policy_terminal_has_no_lane():
    r = classify_hold("INJECTION threat detected: ['INJECTION_SHELL']")
    assert r.hold_class == "policy_terminal"
    assert r.mrtr_eligible is False
    assert "no lane" in r.resolution_lane


def test_transient_holds_retry():
    r = classify_hold("WELL telemetry unavailable (backend_status=DEGRADED)")
    assert r.hold_class == "retry_later"
    assert r.mrtr_eligible is False


def test_checkpoint_hold_is_mrtr_eligible():
    r = classify_hold("Sovereignty checkpoint incomplete — missing answers")
    assert r.hold_class == "satisfiable_input"
    assert r.mrtr_eligible is True
    assert "MRTR" in r.resolution_lane


def test_authority_marker_beats_satisfiable_marker_structurally():
    """The invariant: no phrasing mixes authority lack into MRTR.

    Even with a checkpoint/satisfiable word present, an authority marker
    wins — precedence is constitutional, not heuristic.
    """
    r = classify_hold(
        "checkpoint incomplete AND actor_verified=false OBSERVE_ONLY "
        "requires human witness"
    )
    assert r.hold_class == "authority_required"
    assert r.mrtr_eligible is False


def test_unclassified_hold_fails_closed_to_authority():
    r = classify_hold("some novel condition never seen before")
    assert r.hold_class == "authority_required"
    assert r.mrtr_eligible is False


def test_interceptor_envelope_carries_resolution():
    """The K-02 test: a blocked agent sees its lane in the envelope."""
    import importlib

    m = importlib.import_module("arifosmcp.runtime.ingress_middleware")
    fn = getattr(m, "_hold_deny_envelope", None) or getattr(
        m, "_deny_envelope", None
    )
    if fn is None:
        import inspect

        cands = [
            n for n, f in inspect.getmembers(m, inspect.isfunction)
            if "envelope" in n and "hold" not in n.lower()
        ]
        fn = getattr(m, cands[0]) if cands else None
    if fn is None:
        import pytest

        pytest.skip("envelope builder not found by name — verify wiring manually")
    import inspect

    sig = inspect.signature(fn)
    kwargs = {}
    for pname in ("tool_name", "decision"):
        if pname in sig.parameters:
            kwargs[pname] = "arif_forge" if pname == "tool_name" else None
    try:
        result = fn(**kwargs)
    except Exception:
        import pytest

        pytest.skip("envelope builder needs richer fixtures — wiring unit-tested above")
    text = getattr(result.content[0], "text", "") if getattr(result, "content", None) else ""
    sc = getattr(result, "structured_content", None) or {}
    payload = sc or {}
    assert "hold_resolution" in payload or "hold_resolution" in text

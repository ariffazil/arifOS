"""T2 canary — the minimal wire view must not project the FQ object out.

Measured failure (2026-10-18, staging :28188): the envelope carried
``fq`` at return (``has_fq=True``) and lost it in ``trim_for_verbosity``
(``has_fq=False``). ``substrate`` was in the preserved-field list; ``fq``
was not. A consumer therefore saw /health's reading and a verb's silence
in the same session — the dual representation T2 exists to delete.
"""

from __future__ import annotations

from arifosmcp.runtime.verbosity import trim_for_verbosity

FQ = {
    "value": 0.5507,
    "measured_at": "2026-10-18T11:00:00Z",
    "scope": "federation",
}


def _envelope(**extra):
    payload = {
        "status": "completed",
        "tool": "arif_init",
        "verdict": "SEAL",
        "effective_verdict": "SEAL",
        "actor_id": "QWEN",
        "actor_verified": True,
        "session_id": "SEAL-test",
        "call_hash": "abc123",
        "trace_id": "trace-1",
        "fq": dict(FQ),
        "result": {"mode": "init"},
    }
    payload.update(extra)
    return payload


def test_minimal_view_keeps_the_fq_object_verbatim():
    out = trim_for_verbosity(_envelope(), "minimal")
    assert out.get("fq") == FQ


def test_minimal_view_keeps_an_unmeasured_fq_as_null_not_absent():
    unmeasured = {"value": None, "measured_at": None, "scope": "session"}
    out = trim_for_verbosity(_envelope(fq=unmeasured), "minimal")
    assert "fq" in out, "absence is not the same claim as an unmeasured reading"
    assert out["fq"] == unmeasured


def test_minimal_view_does_not_invent_an_fq_when_the_envelope_has_none():
    env = _envelope()
    env.pop("fq")
    assert "fq" not in trim_for_verbosity(env, "minimal")


def test_standard_and_full_views_are_unchanged():
    for level in (None, "standard", "full"):
        out = trim_for_verbosity(_envelope(), level)
        assert out.get("fq") == FQ

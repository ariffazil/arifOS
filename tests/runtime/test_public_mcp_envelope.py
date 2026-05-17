"""
Regression coverage for public MCP output envelopes.

Copilot Studio validates the advertised outputSchema before showing a tool
response. Raw domain payloads must therefore be coerced into the stable
status/tool/result/meta/timestamp/output_policy/nine_signal/reasons envelope.
"""

from arifosmcp.runtime.tools import (
    _enforce_nine_signal,
    _nine_signal_from_status,
)


REQUIRED_ENVELOPE_KEYS = {
    "status",
    "tool",
    "result",
    "meta",
    "timestamp",
    "output_policy",
    "nine_signal",
    "reasons",
}


def test_existing_nine_signal_payload_is_coerced_to_public_envelope():
    payload = {
        "status": "HOLD",
        "verdict": "HOLD",
        "risk_tier": "AMBER",
        "human_decision_required": True,
        "reason": "schema regression probe",
        "nine_signal": _nine_signal_from_status("HOLD"),
    }

    out = _enforce_nine_signal("arif_heart_critique", payload, actor_id="arif")

    assert REQUIRED_ENVELOPE_KEYS <= set(out)
    assert out["tool"] == "arif_heart_critique"
    assert isinstance(out["result"], dict)
    assert out["result"]["risk_tier"] == "AMBER"
    assert out["reasons"]
    assert out["_violations"] == []


def test_legacy_safe_void_nine_signal_is_upgraded_to_plane_shape():
    payload = {
        "status": "VOID",
        "tool": "arif_mind_reason",
        "verdict": "VOID",
        "reason": "SAFE_VOID_FALLBACK: probe",
        "nine_signal": {"status": "VOID"},
    }

    out = _enforce_nine_signal("arif_mind_reason", payload, actor_id="arif")

    assert REQUIRED_ENVELOPE_KEYS <= set(out)
    assert out["nine_signal"]["delta"]["state"] == "ROSAK"
    assert out["nine_signal"]["psi"]["state"] == "KHIANAT"
    assert out["nine_signal"]["omega"]["state"] == "BANGANG"
    assert out["_violations"] == []

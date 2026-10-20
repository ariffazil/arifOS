"""F01 — telemetry redaction must recurse through lists and tuples.

External audit (Agentic Thinking, 2026-10-18) finding F01:
`_redact` removed secrets from dicts and nested dicts but passed lists
through untouched, so ``{"items": [{"api_key": "CANARY"}]}`` reached the
telemetry sink with the secret intact.

These tests pin the recursive contract and the end-to-end
``record_tool_call`` guarantee: the canary never reaches any sink.
"""

from __future__ import annotations

import json

from arifosmcp.runtime import telemetry

CANARY = "CANARY-F01-SECRET-7f4a"


# ── Direct redaction contract ─────────────────────────────────────────────


def test_redact_direct_dict():
    assert telemetry._redact({"api_key": CANARY})["api_key"] == "[REDACTED]"


def test_redact_nested_dict():
    redacted = telemetry._redact({"outer": {"inner": {"api_key": CANARY}}})
    assert redacted["outer"]["inner"]["api_key"] == "[REDACTED]"


def test_redact_list_of_dicts():
    redacted = telemetry._redact({"items": [{"api_key": CANARY}]})
    assert redacted["items"][0]["api_key"] == "[REDACTED]"


def test_redact_dict_in_list_in_dict():
    redacted = telemetry._redact({"outer": [{"middle": [{"api_key": CANARY}]}]})
    assert redacted["outer"][0]["middle"][0]["api_key"] == "[REDACTED]"


def test_redact_tuple_of_dicts():
    redacted = telemetry._redact({"items": ({"api_key": CANARY},)})
    assert redacted["items"][0]["api_key"] == "[REDACTED]"


def test_redact_depth_bound_does_not_leak():
    payload: dict = {"api_key": CANARY}
    for _ in range(60):
        payload = {"nested": payload}
    dumped = json.dumps(telemetry._redact(payload), default=str)
    assert CANARY not in dumped


def test_redact_large_list_is_bounded_not_traversed():
    payload = {"items": [{"api_key": CANARY} for _ in range(200)]}
    dumped = json.dumps(telemetry._redact(payload), default=str)
    assert CANARY not in dumped
    assert "200 items" in dumped


# ── End-to-end: record_tool_call sinks ────────────────────────────────────


def test_record_tool_call_never_sends_canary_to_any_sink(monkeypatch):
    """The canary must not reach Langfuse, the local record, or arifFlow."""
    captured: dict[str, object] = {}

    def fake_langfuse(**kwargs):
        captured["langfuse"] = kwargs

    def fake_arifflow(**kwargs):
        captured["arifflow"] = kwargs

    class FakeLocal:
        def store(self, record):
            captured["local"] = record

    nats_records: list = []

    monkeypatch.setattr(telemetry, "_forward_to_arifflow", fake_arifflow)
    monkeypatch.setattr(telemetry, "_get_nats", lambda: None)
    monkeypatch.setattr(telemetry, "_publish_nats", lambda record: nats_records.append(record))

    tel = telemetry.Telemetry()
    monkeypatch.setattr(tel, "_lf", fake_langfuse)
    monkeypatch.setattr(tel, "_local", FakeLocal())

    tel.record_tool_call(
        tool="arif_probe",
        verdict="OBSERVE",
        input_data={"items": [{"api_key": CANARY}]},
        metadata={"nested": {"items": [{"api_key": CANARY}]}},
    )

    assert captured, "no telemetry sink was exercised — test is not proving anything"
    dumped = json.dumps(captured, default=str)
    assert CANARY not in dumped, f"canary reached a telemetry sink: {dumped}"

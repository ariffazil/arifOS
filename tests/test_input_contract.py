"""Input-contract tests — mode-conditional required params (2026-10-15).

Doctrine: the input contract outranks output polish. These tests pin the
three fixes of the input-contract patch:

  1. MODE_REQUIRED enforcement — empty/lazy calls get an actionable rejection.
  2. Doc/schema agreement — evidence/tooling accept their documented list form.
  3. _envelope stripped from the advertised surface (transport-owned).

A read with no inputs (canary, ledger, vitals) must keep working — the
contract targets modes where silence would force the kernel to guess.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifosmcp.runtime.input_contract import enforce  # noqa: E402
from arifosmcp.runtime.input_contract import missing_params  # noqa: E402


# ── 1. enforce() matrix ────────────────────────────────────────────────────


def test_init_requires_actor_and_intent():
    msg = enforce("arif_init", {"mode": "init"})
    assert msg is not None and "actor_id" in msg and "intent" in msg


def test_init_canary_exempt():
    assert enforce("arif_init", {"mode": "canary"}) is None
    assert enforce("arif_init", {"mode": "light"}) is None


def test_init_satisfied_passes():
    assert (
        enforce("arif_init", {"mode": "init", "actor_id": "opencode/FI-001", "intent": "x"}) is None
    )


def test_default_mode_applies_when_mode_omitted():
    # arif_init defaults to mode=init → same requirement as explicit init
    assert enforce("arif_init", {}) is not None


def test_blank_string_counts_as_missing():
    msg = enforce("arif_init", {"mode": "init", "actor_id": "  ", "intent": ""})
    assert msg is not None and "actor_id" in msg and "intent" in msg


def test_resume_requires_session():
    assert enforce("arif_init", {"mode": "resume"}) is not None
    assert enforce("arif_init", {"mode": "resume", "session_id": "sess-1"}) is None


def test_seal_write_requires_payload_read_exempt():
    assert enforce("arif_seal", {"mode": "seal"}) is not None
    # 2026-10-15 hardening: mode=seal additionally requires seal_purpose —
    # a permanent record with no stated reason is refused.
    assert enforce("arif_seal", {"mode": "seal", "payload": "receipt..."}) is not None
    assert (
        enforce("arif_seal", {"mode": "seal", "payload": "r", "seal_purpose": "close D-17"})
        is None
    )
    # Pure reads stay exempt — do not over-block reads.
    assert enforce("arif_seal", {"mode": "ledger"}) is None
    assert enforce("arif_seal", {"mode": "audit"}) is None
    assert enforce("arif_seal", {"mode": "verify"}) is None


def test_seal_empty_call_names_payload_first():
    """Empty arif_seal (mode defaults to seal) must name payload."""
    msg = enforce("arif_seal", {})
    assert msg is not None and "payload" in msg
    missing = missing_params("arif_seal", {})
    assert missing[0] == "payload"


def test_seal_purpose_missing_names_seal_purpose():
    """payload present but no seal_purpose in mode=seal → named refusal."""
    kwargs = {"mode": "seal", "payload": "the record"}
    missing = missing_params("arif_seal", kwargs)
    assert missing == ["seal_purpose"]
    msg = enforce("arif_seal", kwargs)
    assert msg is not None and "seal_purpose" in msg


def test_session_close_is_a_write_mode():
    """session_close writes a permanent closure record → payload required."""
    assert enforce("arif_seal", {"mode": "session_close"}) is not None
    assert enforce("arif_seal", {"mode": "session_close", "payload": "summary"}) is None


def test_forge_engineer_requires_manifest():
    assert enforce("arif_forge", {"mode": "engineer"}) is not None
    assert enforce("arif_forge", {"mode": "engineer", "manifest": "build X"}) is None
    # Write paths are HARD manifest-required — no query fallback.
    assert enforce("arif_forge", {"mode": "engineer", "query": "state check"}) is not None
    assert missing_params("arif_forge", {"mode": "engineer", "query": "x"}) == ["manifest"]
    # dry_run with NEITHER input is still missing (deterministic: both named,
    # advertised-schema order — manifest first; message says "at least one of").
    assert enforce("arif_forge", {"mode": "dry_run"}) is not None
    assert missing_params("arif_forge", {"mode": "dry_run"}) == ["manifest", "query"]
    assert "at least one of manifest or query" in enforce("arif_forge", {"mode": "dry_run"})


def test_forge_dry_run_accepts_query_fallback():
    """Fallback ruling 2026-10-15: dry_run preview accepts manifest OR query."""
    assert enforce("arif_forge", {"mode": "dry_run", "query": "preview the plan"}) is None
    assert enforce("arif_forge", {"mode": "dry_run", "manifest": '{"step": 1}'}) is None
    assert enforce("arif_forge", {"mode": "dry_run", "manifest": "m", "query": "q"}) is None
    # default mode is engineer — an omitted mode never gets the fallback
    assert enforce("arif_forge", {"query": "preview the plan"}) is not None
    assert enforce("arif_forge", {"manifest": "m"}) is None


def test_route_alias_intent_or_task():
    assert enforce("arif_route", {}) is not None
    assert enforce("arif_route", {"intent": "audit repo"}) is None
    assert enforce("arif_route", {"task": "legacy alias call"}) is None


def test_memory_mode_minimums():
    assert enforce("arif_memory", {"mode": "remember"}) is not None
    assert enforce("arif_memory", {"mode": "remember", "content": "fact"}) is None
    assert enforce("arif_memory", {"mode": "inspect"}) is not None
    assert enforce("arif_memory", {"mode": "inspect", "memory_id": "m1"}) is None
    assert enforce("arif_memory", {"mode": "revise", "memory_id": "m1"}) is not None
    assert enforce("arif_memory", {"mode": "revise", "memory_id": "m1", "new_content": "x"}) is None
    assert enforce("arif_memory", {"mode": "audit"}) is None


def test_observe_reads_exempt_writes_need_query():
    assert enforce("arif_observe", {"mode": "search"}) is not None
    assert enforce("arif_observe", {"mode": "search", "query": "q"}) is None
    assert enforce("arif_observe", {"mode": "fetch"}) is not None
    assert enforce("arif_observe", {"mode": "fetch", "url": "https://x"}) is None
    assert enforce("arif_observe", {"mode": "vitals"}) is None


def test_unknown_tool_and_mode_fail_open():
    # contract check must never break dispatch on unknown shapes
    assert enforce("arif_unknown", {"mode": "anything"}) is None
    assert enforce("arif_init", {"mode": "brand-new-mode"}) is None


def test_message_is_actionable():
    msg = enforce("arif_seal", {"mode": "seal"})
    assert "MISSING_REQUIRED_INPUT" in msg and "payload" in msg and "Retry" in msg


# ── 2+3. advertised-surface fixes (schema level) ──────────────────────────


def _contracts():
    from arifosmcp.runtime.public_registry import _runtime_contracts

    return _runtime_contracts()


def test_envelope_not_advertised_on_any_tool():
    for name, contract in _contracts().items():
        props = contract["input_schema"].get("properties", {})
        assert "_envelope" not in props, f"{name} still advertises _envelope"


def test_evidence_accepts_documented_list_form():
    schema = _contracts()["arif_init"]["input_schema"]
    any_of = schema["properties"]["evidence"].get("anyOf", [])
    types = {variant.get("type") for variant in any_of}
    assert "array" in types, f"evidence anyOf={types} — doc promises a list"


def test_tooling_accepts_documented_list_form():
    schema = _contracts()["arif_init"]["input_schema"]
    any_of = schema["properties"]["tooling"].get("anyOf", [])
    types = {variant.get("type") for variant in any_of}
    assert "array" in types, f"tooling anyOf={types} — doc promises a list"


# ── 4. required-field facades (2026-10-15 hardening) ──────────────────────


def _forge_facade():
    from arifosmcp.runtime.public_registry import _spec_for_name

    return _spec_for_name("arif_forge").input_schema


def test_init_advertises_required_intent():
    schema = _contracts()["arif_init"]["input_schema"]
    assert schema.get("required") == ["intent"]
    intent = schema["properties"]["intent"]
    assert intent.get("type") == "string" and intent.get("minLength") == 1


def test_seal_advertises_required_payload_and_purpose_branch():
    schema = _contracts()["arif_seal"]["input_schema"]
    assert schema.get("required") == ["payload"]
    branches = schema.get("allOf") or []
    assert branches, "arif_seal must mirror the seal_purpose requirement"
    then = branches[0]["then"]
    assert then.get("required") == ["seal_purpose"]


def test_forge_facade_conditional_manifest():
    schema = _forge_facade()
    assert "_envelope" not in schema.get("properties", {})
    branches = schema.get("allOf") or []
    assert len(branches) == 2, "forge facade pins two mode-conditional branches"
    write_branch = branches[0]
    assert write_branch["then"]["required"] == ["manifest"]
    dry_branch = branches[1]
    assert dry_branch["then"]["anyOf"] == [
        {"required": ["manifest"]},
        {"required": ["query"]},
    ]


def test_facade_documents_validate_against_jsonschema():
    """T4/T3 document-level checks: dry_run+query-only is schema-valid; reads exempted handler-side."""
    jsonschema = pytest.importorskip("jsonschema")
    forge = _forge_facade()
    # dry_run with query only — valid DOCUMENT (the accepted fallback path)
    jsonschema.validate({"mode": "dry_run", "query": "check state"}, forge)
    # query-only in mode=query — legal fallback path
    jsonschema.validate({"mode": "query", "query": "health"}, forge)
    # engineer without manifest — invalid document (handler returns missing_input)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"mode": "engineer"}, forge)
    # counter-pin: engineer+query (no manifest) is schema-INVALID — the write
    # paths have no query fallback, and the schema says so too
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"mode": "engineer", "query": "x"}, forge)

    seal = _contracts()["arif_seal"]["input_schema"]
    # empty seal call — invalid document (handler returns missing_input naming payload)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({}, seal)
    # mode=seal without purpose — invalid document
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"mode": "seal", "payload": "r"}, seal)
    # fully stated seal — valid
    jsonschema.validate(
        {"mode": "seal", "payload": "r", "seal_purpose": "close D-17"}, seal
    )

    init = _contracts()["arif_init"]["input_schema"]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({}, init)
    jsonschema.validate({"intent": "repair tests"}, init)

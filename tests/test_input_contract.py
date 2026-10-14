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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from arifosmcp.runtime.input_contract import enforce  # noqa: E402


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
    assert enforce("arif_seal", {"mode": "seal", "payload": "receipt..."}) is None
    assert enforce("arif_seal", {"mode": "ledger"}) is None
    assert enforce("arif_seal", {"mode": "audit"}) is None


def test_forge_engineer_requires_manifest():
    assert enforce("arif_forge", {"mode": "engineer"}) is not None
    assert enforce("arif_forge", {"mode": "engineer", "manifest": "build X"}) is None
    assert enforce("arif_forge", {"mode": "dry_run"}) is not None


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

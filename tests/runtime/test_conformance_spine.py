"""Tests for the ARIF Conformance Spine v0.1 proof machine."""
from __future__ import annotations

import json
import os
from typing import Any


from arifosmcp.transport import conformance_spine as spine
from arifosmcp.transport.airlock import (
    CanonicalEnvelope,
    classify_authority,
    classify_reversibility,
    preserve_raw_request,
    refuse_with_888_hold,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _tool_response(result: dict[str, Any]) -> dict[str, Any]:
    """Build a FastMCP-shaped tools/call response wrapping a tool result."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "content": [{"type": "text", "text": json.dumps({"result": result})}],
            "isError": False,
        },
    }


# ── Unit tests for extraction helper ─────────────────────────────────────────

def test_extract_tool_result_parses_fastmcp_content():
    mcp_response = _tool_response({"echo": {"probe": 1}, "server_received_type": "dict"})
    extracted = spine._extract_tool_result(mcp_response)
    assert extracted == {"echo": {"probe": 1}, "server_received_type": "dict"}


def test_extract_tool_result_returns_empty_on_bad_input():
    assert spine._extract_tool_result({}) == {}
    assert spine._extract_tool_result("not-a-dict") == {}
    assert spine._extract_tool_result(None) == {}


# ── Unit tests for airlock authority classification ──────────────────────────

def test_classify_authority_cases():
    assert classify_authority(CanonicalEnvelope(actor="arif")) == "SOVEREIGN"
    assert classify_authority(CanonicalEnvelope(actor="888")) == "SOVEREIGN"
    assert classify_authority(CanonicalEnvelope(actor="hermes")) == "HIGH"
    assert classify_authority(CanonicalEnvelope(actor="root")) == "HIGH"
    assert classify_authority(CanonicalEnvelope(actor="mcp_client")) == "MEDIUM"
    assert classify_authority(CanonicalEnvelope(actor="unknown_agent")) == "LOW"


# ── Unit tests for 888_HOLD mutation refusal ─────────────────────────────────

def test_hold_blocks_irreversible_intents():
    irreversible_intents = [
        "delete_critical_file",
        "drop_table",
        "terminate_process",
        "wipe_data",
        "purge_cache",
    ]
    for intent in irreversible_intents:
        env = CanonicalEnvelope(actor="unknown_agent", intent=intent)
        assert classify_reversibility(env) == "IRREVERSIBLE"
        trace = preserve_raw_request({"actor": "unknown_agent", "intent": intent})
        hold = refuse_with_888_hold(env, trace)
        assert hold["verdict"] == "888_HOLD_REQUIRED"
        assert hold["recommendation"] == "AWAIT_SOVEREIGN_VETO"
        assert "F1_AMANAH" in str(hold.get("nine_signal", ""))


def test_reversible_intents_do_not_trigger_hold():
    env = CanonicalEnvelope(actor="unknown_agent", intent="read_status")
    assert classify_reversibility(env) == "REVERSIBLE"
    assert not env.requires_hold


# ── Unit tests for VAULT replay verification ─────────────────────────────────

def _mock_mcp_post_for_vault(entries: list[dict[str, Any]] | None):
    """Return a monkeypatch callable that fakes initialize + hermes_vault_query."""
    def _mcp_post(method: str, params: dict[str, Any] | None = None, **kwargs):
        if method == "initialize":
            return {"result": {"protocolVersion": "2025-11-25", "serverInfo": {"name": "test"}}}
        if method == "tools/call" and params and params.get("name") == "hermes_vault_query":
            if entries is None:
                return _tool_response({"status": "ERROR", "result": {"entries": []}})
            return _tool_response({
                "status": "SEAL",
                "result": {"entries": entries},
            })
        return {"result": {}}
    return _mcp_post


def test_vault_replay_passes_with_valid_chain(tmp_path, monkeypatch):
    vault_path = tmp_path / "outcomes.jsonl"
    vault_path.write_text("{}")  # file presence is the secondary check

    entries = [
        {"file": "outcomes.jsonl", "ts": "2026-06-14T00:01:00Z", "action": "test"},
        {"file": "outcomes.jsonl", "ts": "2026-06-14T00:00:00Z", "action": "test"},
    ]
    monkeypatch.setattr(spine, "_mcp_post", _mock_mcp_post_for_vault(entries))

    old_env = os.environ.get("ARIFOS_VAULT_PATH")
    os.environ["ARIFOS_VAULT_PATH"] = str(vault_path)
    try:
        result = spine.check_vault_replay()
        assert result["verdict"] == "PASS"
        assert result["evidence"]["entries_returned"] == 2
        assert result["evidence"]["chain_ok"] is True
        assert result["evidence"]["file_present"] is True
    finally:
        if old_env is None:
            os.environ.pop("ARIFOS_VAULT_PATH", None)
        else:
            os.environ["ARIFOS_VAULT_PATH"] = old_env


def test_vault_replay_fails_on_empty_vault(tmp_path, monkeypatch):
    vault_path = tmp_path / "outcomes.jsonl"
    vault_path.write_text("")

    monkeypatch.setattr(spine, "_mcp_post", _mock_mcp_post_for_vault(None))

    old_env = os.environ.get("ARIFOS_VAULT_PATH")
    os.environ["ARIFOS_VAULT_PATH"] = str(vault_path)
    try:
        result = spine.check_vault_replay()
        assert result["verdict"] == "FAIL"
        assert result["evidence"]["file_present"] is False
        assert any("empty" in e.lower() or "missing" in e.lower() for e in result["evidence"]["errors"])
    finally:
        if old_env is None:
            os.environ.pop("ARIFOS_VAULT_PATH", None)
        else:
            os.environ["ARIFOS_VAULT_PATH"] = old_env


def test_vault_replay_fails_on_missing_explicit_path(monkeypatch):
    monkeypatch.setattr(spine, "_mcp_post", _mock_mcp_post_for_vault(None))

    old_env = os.environ.get("ARIFOS_VAULT_PATH")
    os.environ["ARIFOS_VAULT_PATH"] = "/nonexistent/vault/outcomes.jsonl"
    try:
        result = spine.check_vault_replay()
        assert result["verdict"] == "FAIL"
        assert any("explicit" in e.lower() for e in result["evidence"]["errors"])
    finally:
        if old_env is None:
            os.environ.pop("ARIFOS_VAULT_PATH", None)
        else:
            os.environ["ARIFOS_VAULT_PATH"] = old_env


# ── Unit test for run_spine fast mode ────────────────────────────────────────

def test_run_spine_fast_mode_skips_live_checks():
    report = spine.run_spine(fast=True)
    assert report["spine"] == "ARIF Conformance Spine v0.1"
    assert report["total"] == 8
    # Authority, hold, and vault checks still run in fast mode
    assert report["passed"] >= 3
    assert report["substrate_gate"] in ("GREEN", "AMBER")


# ── Sanity: descriptions are attached by the MCP tool wrapper ────────────────

def test_conformance_report_descriptions_cover_all_checks():
    descriptions = {
        "arifos_alive":        "arifOS alive?",
        "mcp_initialize":      "MCP initialize works?",
        "protocol_version":    "protocol version clear?",
        "schema_echo_stable":  "schema echo stable?",
        "session_starts":      "session starts?",
        "authority_checked":   "authority checked?",
        "hold_blocks_mutation": "888_HOLD blocks mutation?",
        "vault_replay":        "VAULT replay verifies?",
    }
    for check_name in [name for name, _ in spine.SPINE]:
        assert check_name in descriptions

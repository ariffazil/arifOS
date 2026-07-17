"""Tests for the ARIF Conformance Spine v0.2 proof machine."""

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


def _mock_urlopen_vault_api(api_payload: dict[str, Any] | None, *, fail: bool = False):
    """Monkeypatch urlopen for VAULT999 API :8100 only."""
    import io
    from urllib.error import URLError

    class _Resp:
        def __init__(self, payload: dict[str, Any]):
            self._payload = payload

        def read(self) -> bytes:
            return json.dumps(self._payload).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    real_urlopen = spine.urllib.request.urlopen

    def _urlopen(req, timeout=10):  # noqa: ANN001
        url = getattr(req, "full_url", None) or getattr(req, "get_full_url", lambda: "")()
        if isinstance(url, str) and ":8100" in url:
            if fail:
                raise URLError("vault api down")
            return _Resp(api_payload or {"status": "ok", "vault_seals_total": 10, "chain_integrity": "INTACT"})
        return real_urlopen(req, timeout=timeout)

    return _urlopen


def test_vault_replay_passes_with_valid_chain(tmp_path, monkeypatch):
    """Filesystem outcomes.jsonl + healthy VAULT999 API → PASS."""
    vault_dir = tmp_path / "vault999"
    vault_dir.mkdir()
    entries = [
        {"ts": "2026-06-14T00:00:00Z", "event": "tool_call", "action": "test"},
        {"ts": "2026-06-14T00:01:00Z", "event": "tool_call", "action": "test2"},
    ]
    (vault_dir / "outcomes.jsonl").write_text(
        "\n".join(json.dumps(e) for e in entries) + "\n"
    )
    # Force candidate path isolation: only this dir is visible
    monkeypatch.setattr(
        spine.os.path,
        "isdir",
        lambda p: str(p) == str(vault_dir) or str(p).startswith(str(vault_dir)),
    )
    monkeypatch.setattr(
        spine.os.path,
        "isfile",
        lambda p: str(p) == str(vault_dir / "outcomes.jsonl"),
    )
    real_join = os.path.join

    def _join(*parts):
        return real_join(*parts)

    monkeypatch.setattr(spine.os.path, "join", _join)
    # Patch candidate list by env only — check uses hardcoded paths first;
    # so monkeypatch open to serve our file when outcomes.jsonl requested.
    real_open = open

    def _open(path, *args, **kwargs):
        if str(path).endswith("outcomes.jsonl"):
            return real_open(vault_dir / "outcomes.jsonl", *args, **kwargs)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", _open)
    monkeypatch.setattr(
        spine.os.path,
        "getsize",
        lambda p: (vault_dir / "outcomes.jsonl").stat().st_size
        if str(p).endswith("outcomes.jsonl")
        else 0,
    )
    monkeypatch.setattr(
        spine.urllib.request,
        "urlopen",
        _mock_urlopen_vault_api(
            {
                "status": "ok",
                "vault_seals_total": 42,
                "chain_integrity": "INTACT",
                "last_seal": {"id": 1, "action": "test", "epoch": "2026-06-14T00:01:00Z"},
            }
        ),
    )
    # Make primary candidates resolve to our tmp vault
    monkeypatch.setenv("ARIFOS_VAULT_PATH", str(vault_dir))
    # Override candidates by patching check to see tmp via env: ensure
    # /root/VAULT999 is not preferred — replace os.path.isdir for root paths
    def _isdir(p):
        sp = str(p)
        if sp in ("/root/VAULT999", "/root/.local/share/arifos/vault999"):
            return False
        if sp == str(vault_dir):
            return True
        return os.path.isdir(p)

    monkeypatch.setattr(spine.os.path, "isdir", _isdir)

    result = spine.check_vault_replay()
    assert result["verdict"] == "PASS", result
    assert result["evidence"]["entries_returned"] >= 1
    assert result["evidence"]["chain_ok"] is True
    assert result["evidence"]["file_present"] is True


def test_vault_replay_fails_on_empty_vault(tmp_path, monkeypatch):
    vault_dir = tmp_path / "emptyvault"
    vault_dir.mkdir()
    (vault_dir / "outcomes.jsonl").write_text("")

    def _isdir(p):
        sp = str(p)
        if sp in ("/root/VAULT999", "/root/.local/share/arifos/vault999"):
            return False
        return sp == str(vault_dir)

    monkeypatch.setattr(spine.os.path, "isdir", _isdir)
    monkeypatch.setattr(
        spine.os.path,
        "isfile",
        lambda p: str(p).endswith("outcomes.jsonl") and os.path.getsize(p) > 0,
    )
    monkeypatch.setattr(
        spine.os,
        "listdir",
        lambda p: [] if str(p) == str(vault_dir) else os.listdir(p),
    )
    monkeypatch.setattr(
        spine.urllib.request,
        "urlopen",
        _mock_urlopen_vault_api(None, fail=True),
    )
    monkeypatch.setenv("ARIFOS_VAULT_PATH", str(vault_dir))

    result = spine.check_vault_replay()
    assert result["verdict"] == "FAIL"
    assert result["evidence"]["file_present"] is False or result["evidence"]["entries_returned"] == 0


def test_vault_replay_fails_on_missing_explicit_path(monkeypatch):
    def _isdir(p):
        sp = str(p)
        if sp in ("/root/VAULT999", "/root/.local/share/arifos/vault999"):
            return False
        return False

    monkeypatch.setattr(spine.os.path, "isdir", _isdir)
    monkeypatch.setattr(spine.os.path, "isfile", lambda p: False)
    monkeypatch.setattr(
        spine.urllib.request,
        "urlopen",
        _mock_urlopen_vault_api(None, fail=True),
    )
    monkeypatch.setenv("ARIFOS_VAULT_PATH", "/nonexistent/vault/outcomes.jsonl")

    result = spine.check_vault_replay()
    assert result["verdict"] == "FAIL"
    assert any(
        "missing" in e.lower() or "unreachable" in e.lower() or "empty" in e.lower()
        for e in result["evidence"]["errors"]
    )

# ── Unit test for run_spine fast mode ────────────────────────────────────────


def test_run_spine_fast_mode_skips_live_checks():
    """T6: fast mode skips live checks as SKIPPED, never PASS, never GREEN."""
    report = spine.run_spine(fast=True)
    assert report["spine"] == "ARIF Conformance Spine v0.2"
    assert report["total"] == 9
    # T6 law: SKIPPED ≠ PASS
    assert report.get("skipped", 0) >= 1
    assert report["all_green"] is False
    assert report["substrate_gate"] != "GREEN"
    assert report["verdict"] in ("PARTIAL", "CAUTION", "HOLD", "AMBER", "EXPLAINED_HISTORICAL_GAP")
    assert report.get("constitutional_grade") is False
    assert report.get("fast_mode") is True
    # Every skipped check must say SKIPPED, not PASS
    for c in report.get("checks", []):
        if (c.get("evidence") or {}).get("mode") == "fast":
            assert c["verdict"] == "SKIPPED", f"{c.get('check')} was {c['verdict']}"


def test_run_spine_fast_mode_cannot_seal():
    report = spine.run_spine(fast=True)
    assert report.get("verdict") != "SEAL"
    assert report.get("all_green") is False


# ── Sanity: descriptions are attached by the MCP tool wrapper ────────────────


def test_conformance_report_descriptions_cover_all_checks():
    descriptions = {
        "arifos_alive": "arifOS alive?",
        "mcp_initialize": "MCP initialize works?",
        "protocol_version": "protocol version clear?",
        "schema_echo_stable": "schema echo stable?",
        "session_starts": "session starts?",
        "authority_checked": "authority checked?",
        "hold_blocks_mutation": "888_HOLD blocks mutation?",
        "vault_replay": "VAULT replay verifies?",
        "cooling_ledger": "cooling ledger verifies?",
    }
    for check_name in [name for name, _ in spine.SPINE]:
        assert check_name in descriptions


def test_cooling_ledger_passes_with_vault_and_entropy(monkeypatch):
    """The ninth spine check must pass when vault and entropy evidence exist."""

    class _Resp:
        def __init__(self, payload: dict[str, Any]):
            self._payload = payload
            self.headers = {}

        def read(self) -> bytes:
            return json.dumps(self._payload).encode("utf-8")

    def _urlopen(req, timeout=10):  # noqa: ANN001
        url = req.full_url
        if url.endswith("/health"):
            return _Resp({"status": "healthy"})
        if url.endswith("/vault/status"):
            return _Resp(
                {
                    "vault_seals_total": 265,
                    "chain_integrity": "INTACT",
                    "last_seal": {"action": "well_entropy_seal"},
                }
            )
        raise AssertionError(f"unexpected url {url}")

    monkeypatch.setattr(spine.urllib.request, "urlopen", _urlopen)
    monkeypatch.setattr(spine, "_get_session", lambda: "SEAL-test")
    monkeypatch.setattr(
        spine,
        "_mcp_post",
        lambda *args, **kwargs: _tool_response(
            {"result": {"entries": [{"action": "well_entropy_seal"}]}}
        ),
    )

    result = spine.check_cooling_ledger()
    assert result["verdict"] == "PASS"
    assert result["evidence"]["vault999_healthy"] is True
    assert result["evidence"]["well_entropy_seals_found"] > 0

"""Canonical verbs are a thin client: routing, parsing, failure modes."""

from __future__ import annotations

import json
import urllib.error

import pytest

from arifosmcp import verbs as cli


def test_verbs_are_the_ratified_five():
    assert cli.VERBS == ("state", "observe", "judge", "seal", "witness")


def test_parse_argv_passes_tool_arguments_through():
    args, as_json, wants_help = cli._parse_argv(["--claim", "rm -rf /", "--tier", "T3", "--json"])
    assert args == {"claim": "rm -rf /", "tier": "T3"}
    assert as_json is True
    assert wants_help is False


def test_parse_argv_treats_bare_flag_as_true():
    args, _, _ = cli._parse_argv(["--dry-run"])
    assert args == {"dry_run": True}


def test_parse_argv_rejects_positionals():
    with pytest.raises(ValueError):
        cli._parse_argv(["loose-token"])


def test_decode_accepts_plain_json_and_event_stream():
    assert cli._decode('{"result": {"ok": 1}}') == {"result": {"ok": 1}}
    assert cli._decode('event: message\ndata: {"result": {"ok": 2}}\n') == {"result": {"ok": 2}}


def test_unknown_verb_exits_2(capsys):
    assert cli.run_verb("bogus", []) == 2
    assert "unknown verb" in capsys.readouterr().err


def test_judge_routes_to_arif_judge(monkeypatch, capsys):
    seen = {}

    def fake_rpc(url, method, params):
        seen["method"] = method
        seen["params"] = params
        return {"content": [{"type": "text", "text": "VERDICT: HOLD"}]}

    monkeypatch.setattr(cli, "_rpc", fake_rpc)
    rc = cli.run_verb("judge", ["--claim", "drop table users"])
    assert rc == 0
    assert seen["method"] == "tools/call"
    assert seen["params"]["name"] == "arif_judge"
    assert seen["params"]["arguments"] == {"claim": "drop table users"}
    assert "VERDICT: HOLD" in capsys.readouterr().out


def test_witness_reads_the_chain_head(monkeypatch):
    seen = {}

    def fake_rpc(url, method, params):
        seen["method"] = method
        seen["params"] = params
        return {"contents": [{"text": '{"record_id": "r1"}'}]}

    monkeypatch.setattr(cli, "_rpc", fake_rpc)
    assert cli.run_verb("witness", []) == 0
    assert seen["method"] == "resources/read"
    assert seen["params"] == {"uri": "arifos://vault/head"}


def test_unreachable_kernel_names_the_url(monkeypatch, capsys):
    def boom(*_a, **_k):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(cli, "_http", boom)
    rc = cli.run_verb("state", [])
    assert rc == 1
    assert "kernel unreachable" in capsys.readouterr().err


def test_kernel_error_is_reported(monkeypatch, capsys):
    def fake_rpc(*_a, **_k):
        raise RuntimeError("kernel error -32001: session required")

    monkeypatch.setattr(cli, "_rpc", fake_rpc)
    assert cli.run_verb("seal", []) == 1
    assert "session required" in capsys.readouterr().err


def test_json_output(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_rpc", lambda *a, **k: {"contents": [{"text": "x"}]})
    assert cli.run_verb("witness", ["--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"contents": [{"text": "x"}]}

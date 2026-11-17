# S3c (PLAN-2026-11-10-Q1, ARIF GO S3c): OS-1 canary — dry-run emission tests
import asyncio
import json
import os

import pytest

from arifosmcp.runtime.os1_canary import emit_dry_run, wrap_mutate_verbs


def _line(tmp_path):
    p = tmp_path / "canary.jsonl"
    assert p.exists()
    return json.loads(p.read_text().splitlines()[-1])


def test_env_off_writes_nothing(tmp_path, monkeypatch):
    monkeypatch.delenv("ARIFOS_OS1_CANARY", raising=False)
    assert emit_dry_run("arif_judge", "a", "s", "SEAL") is False
    assert not (tmp_path / "canary.jsonl").exists()


def test_env_on_writes_receipt_shape(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_OS1_CANARY", "1")
    monkeypatch.setenv("ARIFOS_OS1_CANARY_PATH", str(tmp_path / "canary.jsonl"))
    assert emit_dry_run("arif_judge", "qwen-code", "sess-1", "SABAR", mode_param="judge") is True
    line = _line(tmp_path)
    for key in ("actor_id", "session_id", "step_type", "floor_verdict"):
        assert key in line, f"missing arifFlow-contract key: {key}"
    assert line["floor_verdict"] == "Caution"  # SABAR -> Caution mapping
    assert line["mode"] == "dry_run" and line["tool"] == "arif_judge"


def test_unknown_verdict_passes_through_unmapped(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_OS1_CANARY", "1")
    monkeypatch.setenv("ARIFOS_OS1_CANARY_PATH", str(tmp_path / "canary.jsonl"))
    emit_dry_run("arif_seal", "a", "s", "WEIRD")
    assert _line(tmp_path)["floor_verdict"] == "WEIRD"


def test_wrapper_passthrough_and_emit(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_OS1_CANARY", "1")
    monkeypatch.setenv("ARIFOS_OS1_CANARY_PATH", str(tmp_path / "canary.jsonl"))

    async def fake_arif_judge(**kwargs):
        return {"effective_verdict": "SEAL", "session_id": "sess-9",
                "actor": {"actor_id": "qwen-code"}}

    wrapped = wrap_mutate_verbs(fake_arif_judge)
    out = asyncio.run(wrapped(actor_id="ignored", session_id="ignored"))
    assert out["effective_verdict"] == "SEAL"  # result unchanged
    line = _line(tmp_path)
    assert line["tool"] == "fake_arif_judge"
    assert line["floor_verdict"] == "Pass"  # SEAL -> Pass
    assert line["actor_id"] == "qwen-code" and line["session_id"] == "sess-9"


def test_wrapper_extracts_verdict_from_pydantic_result(tmp_path, monkeypatch):
    # 2026-11-18 shape fix: judge/seal handlers return VerdictOutput/SealOutput
    # (pydantic via _echo_standing) — the dict-only ladder read them as Unknown.
    from arifosmcp.schemas.verdict import VerdictOutput

    monkeypatch.setenv("ARIFOS_OS1_CANARY", "1")
    monkeypatch.setenv("ARIFOS_OS1_CANARY_PATH", str(tmp_path / "canary.jsonl"))

    async def fake_arif_judge(**kwargs):
        return VerdictOutput(verdict="HOLD", session_id="sess-pyd",
                             actor_id="qwen-code")

    wrapped = wrap_mutate_verbs(fake_arif_judge)
    out = asyncio.run(wrapped(actor_id="ignored", session_id="ignored"))
    assert isinstance(out, VerdictOutput)  # model returned unchanged
    line = _line(tmp_path)
    assert line["raw_verdict"] == "HOLD", "pydantic verdict must reach raw_verdict"
    assert line["floor_verdict"] == "Hold"
    assert line["session_id"] == "sess-pyd" and line["actor_id"] == "qwen-code"


def test_wrapper_model_dump_failure_degrades_to_unknown(tmp_path, monkeypatch):
    # fail-open: an object that refuses model_dump must not break or mislabel
    class Rigid:
        def model_dump(self, **kw):
            raise RuntimeError("dump refused")

    monkeypatch.setenv("ARIFOS_OS1_CANARY", "1")
    monkeypatch.setenv("ARIFOS_OS1_CANARY_PATH", str(tmp_path / "canary.jsonl"))

    async def fake_arif_judge(**kwargs):
        return Rigid()

    wrapped = wrap_mutate_verbs(fake_arif_judge)
    out = asyncio.run(wrapped())
    assert isinstance(out, Rigid)
    assert _line(tmp_path)["raw_verdict"] == "Unknown"


def test_wrapper_never_breaks_the_verb(tmp_path, monkeypatch):
    monkeypatch.delenv("ARIFOS_OS1_CANARY", raising=False)

    async def boom(**kwargs):
        raise RuntimeError("verb error")

    wrapped = wrap_mutate_verbs(boom)
    with pytest.raises(RuntimeError):
        asyncio.run(wrapped())

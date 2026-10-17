"""E2 regression — arif_heal / arif_guard are read-only diagnostic tools."""

from __future__ import annotations

import asyncio
import json

from arifosmcp.tools.guard import arif_guard
from arifosmcp.tools.heal import arif_heal


def _run(coro):
    return asyncio.run(coro)


def test_heal_strategy_table():
    out = _run(arif_heal(mode="strategy"))
    assert out["status"] == "ok"
    assert out["mutation"] is False
    assert "UNAUTHORIZED_VERB" in out["strategies"]


def test_heal_diagnose_classifies_failure(tmp_path, monkeypatch):
    wal = tmp_path / "receipts.jsonl"
    wal.write_text(
        "\n".join(
            [
                json.dumps({"error": "Tool 'arif_forge' not allowed for authority"}),
                json.dumps({"status": "ok"}),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ARIFOS_WAL_PATH", str(wal))

    out = _run(arif_heal(mode="diagnose"))
    assert out["status"] == "ok"
    assert out["scanned"] == 2
    assert "UNAUTHORIZED_VERB" in out["findings"]
    assert out["findings"]["UNAUTHORIZED_VERB"]["count"] == 1
    assert out["mutation"] is False


def test_guard_verify_is_evidence_only():
    out = _run(arif_guard(mode="verify"))
    assert out["tool"] == "arif_guard"
    assert out["mutation"] is False
    assert isinstance(out["passed"], bool)
    assert "verdict_authority" in out


def test_guard_drift_reports_source_head():
    out = _run(arif_guard(mode="drift"))
    assert out["status"] == "ok"
    assert "source_head" in out
    assert out["mutation"] is False

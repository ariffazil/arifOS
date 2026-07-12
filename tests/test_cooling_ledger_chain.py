"""CLRP-1 — cooling ledger parent_hash chain tests."""

from __future__ import annotations

import json
from pathlib import Path

from arifosmcp.runtime.cooling_ledger_chain import (
    append_cooling_entry,
    verify_cooling_ledger,
)


def test_cooling_ledger_chain_integrity(tmp_path: Path):
    ledger = tmp_path / "cooling_ledger.jsonl"
    e1 = append_cooling_entry(
        agent="test",
        session_id="SEAL-test-1",
        bottleneck="routing_precision",
        fix_type="keyword",
        fix_path="/tmp/x",
        delta_S=-0.2,
        verified=True,
        ledger_path=ledger,
    )
    e2 = append_cooling_entry(
        agent="test",
        session_id="SEAL-test-1",
        bottleneck="false_capital_token",
        fix_type="boundary",
        delta_S=-0.1,
        verified=True,
        ledger_path=ledger,
    )
    assert e1["entry_seq"] == 1
    assert e1["parent_hash"] is None
    assert e2["entry_seq"] == 2
    assert e2["parent_hash"] == e1["entry_hash"]

    report = verify_cooling_ledger(ledger, check_seal_refs=False)
    assert report["chain_integrity"] == "PASS"
    assert report["entry_count"] == 2


def test_cooling_ledger_detects_tamper(tmp_path: Path):
    ledger = tmp_path / "cooling_ledger.jsonl"
    append_cooling_entry(agent="a", bottleneck="b1", ledger_path=ledger)
    append_cooling_entry(agent="a", bottleneck="b2", ledger_path=ledger)
    lines = ledger.read_text().splitlines()
    # tamper first entry body but leave second parent_hash pointing at old hash
    first = json.loads(lines[0])
    first["bottleneck"] = "TAMPERED"
    # keep old entry_hash → hash mismatch
    lines[0] = json.dumps(first)
    ledger.write_text("\n".join(lines) + "\n")
    report = verify_cooling_ledger(ledger, check_seal_refs=False)
    assert report["chain_integrity"].startswith("BROKEN")
    assert any(b["reason"] == "entry_hash_mismatch" for b in report["broken_entries"])

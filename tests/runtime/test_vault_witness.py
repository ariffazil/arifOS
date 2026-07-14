"""
Tests for /root/arifOS/arifosmcp/runtime/rest_routes/vault_witness_routes.py

F1-safe: read-only against the live chain except `/test`, which performs one
ephemeral write. Tests use a temporary VAULT_DIR so the live chain is NEVER
touched.

Forged 2026-07-14 — Phase A of Reality Observatory.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.runtime.rest_routes import vault_witness_routes as vw  # noqa: E402


# ── Hash math ─────────────────────────────────────────────────────────────────
def _canonical_json_local(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _compute_this_hash(prev_hash: str, payload: Any, seq: int, epoch: str) -> str:
    material = "|".join((prev_hash, _canonical_json_local(payload), str(seq), epoch))
    h = hashlib.sha256(material.encode("utf-8"))
    return "sha256:" + h.hexdigest()


def _make_entry(seq: int, prev_hash: str, payload: dict[str, Any], *, ts: str | None = None) -> dict[str, Any]:
    epoch = ts or "2026-07-14T00:00:00.000Z"
    this_hash = _compute_this_hash(prev_hash, payload, seq, epoch)
    return {
        "seq": seq,
        "prev_hash": prev_hash,
        "this_hash": this_hash,
        "epoch": epoch,
        "actor": "test",
        "verdict": "SEAL",
        "payload": payload,
    }


# ── Empty chain ────────────────────────────────────────────────────────────────
def test_verify_empty_chain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Empty VAULT → empty status, no errors."""
    monkeypatch.setattr(vw, "LEDGER_PATH", tmp_path / "seal_chain.jsonl")
    monkeypatch.setattr(vw, "HEAD_PATH", tmp_path / "seal_chain_head.json")
    assert not vw.LEDGER_PATH.exists()
    out = vw.verify_chain_window()
    assert out["status"] == "empty"
    assert out["checked"] == 0
    assert out["mismatches"] == []


def test_replay_missing_seq(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(vw, "LEDGER_PATH", tmp_path / "seal_chain.jsonl")
    out = vw.replay_entry(42)
    assert out["found"] is False


# ── Valid chain fixture ───────────────────────────────────────────────────────
@pytest.fixture
def vault_with_chain(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Write a small valid chain (3 entries, genesis→1→2→3) and point the module at it."""
    ledger = tmp_path / "seal_chain.jsonl"
    head = tmp_path / "seal_chain_head.json"
    monkeypatch.setattr(vw, "LEDGER_PATH", ledger)
    monkeypatch.setattr(vw, "HEAD_PATH", head)

    payloads = [
        {"intent": "genesis_seed", "value": "init"},
        {"intent": "first_seal", "value": "one"},
        {"intent": "second_seal", "value": "two"},
    ]
    entries = []
    prev = vw.GENESIS_PREV_HASH
    for i, payload in enumerate(payloads, start=1):
        e = _make_entry(seq=i, prev_hash=prev, payload=payload)
        entries.append(e)
        prev = e["this_hash"]
    with open(ledger, "w", encoding="utf-8") as fh:
        for e in entries:
            fh.write(_canonical_json_local(e) + "\n")
    head.write_text(json.dumps({"seq": 3, "this_hash": entries[-1]["this_hash"], "epoch": entries[-1]["epoch"]}))

    return entries


def test_verify_chain_ok(vault_with_chain) -> None:
    out = vw.verify_chain_window()
    assert out["status"] == "ok", out
    assert out["checked"] == 3
    assert out["head_seq"] == 3
    assert out["mismatches"] == []
    assert out["first_mismatch_seq"] is None
    assert out["gaps"] == []


def test_verify_window_subset(vault_with_chain) -> None:
    out = vw.verify_chain_window(from_seq=2, to_seq=2)
    assert out["checked"] == 1
    assert out["status"] == "ok"


def test_verify_chain_detects_tampered_payload(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, vault_with_chain) -> None:
    """Modify one entry's payload AFTER it was sealed — verifier must catch it."""
    ledger = vw.LEDGER_PATH
    lines = [ln for ln in ledger.read_text().splitlines() if ln.strip()]
    entries = [json.loads(ln) for ln in lines]
    entries[1]["payload"]["value"] = "TAMPERED"
    ledger.write_text("\n".join(_canonical_json_local(e) for e in entries) + "\n")
    out = vw.verify_chain_window()
    assert out["status"] == "broken_chain"
    assert out["first_mismatch_seq"] == 2
    assert any(m["seq"] == 2 for m in out["mismatches"])


def test_verify_chain_detects_broken_link(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, vault_with_chain) -> None:
    """Force prev_hash to disagree — verifier must flag the chain break."""
    ledger = vw.LEDGER_PATH
    entries = [json.loads(ln) for ln in ledger.read_text().splitlines() if ln.strip()]
    entries[2]["prev_hash"] = "sha256:deadbeef"
    ledger.write_text("\n".join(_canonical_json_local(e) for e in entries) + "\n")
    out = vw.verify_chain_window()
    assert out["status"] == "broken_chain"
    assert any(m["reason"] == "this-hash-mismatch" for m in out["mismatches"])


def test_verify_chain_detects_missing_seq(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, vault_with_chain) -> None:
    """Drop one entry from the middle — gap detector must flag it."""
    ledger = vw.LEDGER_PATH
    entries = [json.loads(ln) for ln in ledger.read_text().splitlines() if ln.strip()]
    entries.pop(1)  # remove seq=2
    ledger.write_text("\n".join(_canonical_json_local(e) for e in entries) + "\n")
    out = vw.verify_chain_window()
    assert 2 in out["gaps"]


# ── Replay ─────────────────────────────────────────────────────────────────────
def test_replay_entry_round_trip(vault_with_chain) -> None:
    out = vw.replay_entry(2)
    assert out["found"] is True
    assert out["hash_chain_ok"] is True
    assert out["payload"]["intent"] == "first_seal"


def test_replay_recomputes_after_tamper(vault_with_chain) -> None:
    """Tamper seq=2's payload: replay.recomputed_this_hash will differ from recorded."""
    ledger = vw.LEDGER_PATH
    entries = [json.loads(ln) for ln in ledger.read_text().splitlines() if ln.strip()]
    entries[1]["payload"]["value"] = "TAMPERED"
    ledger.write_text("\n".join(_canonical_json_local(e) for e in entries) + "\n")
    out = vw.replay_entry(2)
    # Replay_entry's recompute uses the *stored* prev_hash of seq=1 (still valid) but reads
    # the modified payload ⇒ recomputed_this_hash ≠ recorded_this_hash.
    assert out["hash_chain_ok"] is False
    assert out["recomputed_this_hash"] != out["recorded_this_hash"]


# ── Self-test ─────────────────────────────────────────────────────────────────
def test_self_test_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Run self_test against a fresh fixture vault; expect PASS."""
    ledger = tmp_path / "seal_chain.jsonl"
    head = tmp_path / "seal_chain_head.json"
    monkeypatch.setattr(vw, "LEDGER_PATH", ledger)
    monkeypatch.setattr(vw, "HEAD_PATH", head)
    # Seed an empty ledger + an empty head so the writer appends seq=1.
    if not ledger.exists():
        ledger.touch()
    head.write_text(json.dumps({"seq": 0, "this_hash": vw.GENESIS_PREV_HASH, "epoch": "2026-07-14T00:00:00.000Z"}))

    out = vw.self_test()
    assert out["status"] == "PASS", out
    steps = out["steps"]
    assert steps["read"]["ok"] is True
    assert steps["write"]["ok"] is True
    assert steps["read_back"]["ok"] is True
    assert steps["verify"]["ok"] is True
    assert steps["replay"]["ok"] is True
    assert out["head_seq_after"] == 1
    # The ledger should now contain exactly one extra entry with our specialized payload.
    lines = [ln for ln in ledger.read_text().splitlines() if ln.strip()]
    assert len(lines) == 1
    last = json.loads(lines[0])
    assert last["payload"]["_specialized"] == "observatory_test"


def test_self_test_recap_records_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """self_test + recording path → record_test_result writes the test cache."""
    ledger = tmp_path / "seal_chain.jsonl"
    head = tmp_path / "seal_chain_head.json"
    monkeypatch.setattr(vw, "LEDGER_PATH", ledger)
    monkeypatch.setattr(vw, "HEAD_PATH", head)
    ledger.touch()
    head.write_text(json.dumps({"seq": 0, "this_hash": vw.GENESIS_PREV_HASH, "epoch": "2026-07-14T00:00:00.000Z"}))

    # Redirect capability_drift cache to tmp so we don't touch the live one.
    from arifosmcp.runtime import capability_drift as cd

    fake_cache = tmp_path / "cache.json"
    monkeypatch.setattr(cd, "TEST_CACHE_PATH", fake_cache)

    # record_test_result is invoked via the `_test` handler wrapper (not directly from self_test).
    cd.record_test_result("observatory_self_test", passed=True, error=None)
    cache = cd._load_test_cache()
    assert cache["observatory_self_test"]["last_pass"] is True

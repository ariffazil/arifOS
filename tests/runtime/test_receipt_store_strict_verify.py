"""F02 — chain verification must fail on malformed or incomplete records.

External audit (Agentic Thinking, 2026-10-18) finding F02:
``all_receipts()`` skipped malformed lines before ``verify_chain()`` saw
them, so a malformed tail, a malformed-only file, or a corrupted final
record still verified as true.

Contract pinned here:
  * ``verify_chain()`` uses a strict parser and FAILS (False + line
    number in the reason) on any nonblank malformed/incomplete record.
  * Tolerant reading survives as an explicitly named inspection mode,
    ``all_receipts_tolerant()``, and is never used for verification.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from arifosmcp.runtime.receipt_store import (
    GENESIS_PREVIOUS_HASH,
    ReceiptStore,
    _canonical_hash,
    _signing_payload,
    make_receipt,
)

SECRET = b"strict-verify-secret"


def _append_chain(store: ReceiptStore, n: int = 3) -> list:
    receipts = []
    prev = GENESIS_PREVIOUS_HASH
    for i in range(n):
        if i:
            prev = _canonical_hash(_signing_payload(receipts[-1]))
        receipt = make_receipt(
            run_id="run-strict",
            trace_id="trc-strict",
            session_id="SEAL-1",
            actor_id="arif",
            action="arif_seal",
            input_data=f"x-{i}",
            evidence_hashes=(),
            decision="SEAL",
            execution_result="y",
            previous_receipt_hash=prev,
            secret=SECRET,
        )
        store.append(receipt)
        receipts.append(receipt)
    return receipts


def _lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Green paths ───────────────────────────────────────────────────────────


def test_valid_chain_verifies(tmp_path: Path):
    store = ReceiptStore(path=tmp_path / "r.jsonl", secret=SECRET)
    _append_chain(store)
    ok, reason = store.verify_chain()
    assert ok, reason


def test_missing_file_still_verifies(tmp_path: Path):
    store = ReceiptStore(path=tmp_path / "absent.jsonl", secret=SECRET)
    ok, reason = store.verify_chain()
    assert ok, reason


# ── Signature / key failures (must keep failing, not crash) ───────────────


def test_altered_signature_fails(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store)
    lines = _lines(path)
    record = json.loads(lines[1])
    record["signature"] = "0" * 64
    lines[1] = json.dumps(record)
    _write_lines(path, lines)

    ok, reason = store.verify_chain()
    assert not ok
    assert "signature_invalid" in reason


def test_wrong_key_fails(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    _append_chain(ReceiptStore(path=path, secret=SECRET))

    other = ReceiptStore(path=path, secret=b"some-other-key")
    ok, reason = other.verify_chain()
    assert not ok
    assert "signature_invalid" in reason


# ── Malformed / incomplete records (the F02 defect) ───────────────────────


def test_malformed_tail_fails_with_line_number(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store)
    with open(path, "a", encoding="utf-8") as f:
        f.write("{not-json\n")

    ok, reason = store.verify_chain()
    assert not ok, "malformed tail verified as true"
    assert "line 4" in reason


def test_malformed_only_file_fails_with_line_number(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    path.write_text("garbage\n", encoding="utf-8")
    store = ReceiptStore(path=path, secret=SECRET)

    ok, reason = store.verify_chain()
    assert not ok, "malformed-only file verified as true"
    assert "line 1" in reason


def test_corrupted_final_record_fails_with_line_number(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store)
    lines = _lines(path)
    lines[-1] = lines[-1][: len(lines[-1]) // 2]  # truncated JSON
    _write_lines(path, lines)

    ok, reason = store.verify_chain()
    assert not ok, "corrupted final record verified as true"
    assert "line 3" in reason


def test_corrupted_middle_record_fails_with_line_number(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store)
    lines = _lines(path)
    lines[1] = "{oops"
    _write_lines(path, lines)

    ok, reason = store.verify_chain()
    assert not ok, "corrupted middle record verified as true"
    assert "line 2" in reason


def test_missing_fields_fails_with_line_number(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store)
    lines = _lines(path)
    record = json.loads(lines[1])
    del record["signature"]
    lines[1] = json.dumps(record)
    _write_lines(path, lines)

    ok, reason = store.verify_chain()
    assert not ok, "incomplete record verified as true"
    assert "line 2" in reason


def test_non_object_record_fails_with_line_number(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store, n=2)
    lines = _lines(path)
    lines[1] = "[]"
    _write_lines(path, lines)

    ok, reason = store.verify_chain()
    assert not ok
    assert "line 2" in reason


# ── Tolerant inspection stays available, explicitly named ────────────────


def test_tolerant_inspection_mode_skips_bad_lines(tmp_path: Path):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    receipts = _append_chain(store)
    with open(path, "a", encoding="utf-8") as f:
        f.write("{not-json\n")

    tolerant = store.all_receipts_tolerant()
    assert [r.receipt_id for r in tolerant] == [r.receipt_id for r in receipts]


@pytest.mark.parametrize("bad", ["{not-json", "[]"])
def test_strict_parser_raises_with_line_number(tmp_path: Path, bad: str):
    path = tmp_path / "r.jsonl"
    store = ReceiptStore(path=path, secret=SECRET)
    _append_chain(store, n=1)
    with open(path, "a", encoding="utf-8") as f:
        f.write(bad + "\n")

    with pytest.raises(Exception) as excinfo:
        store.all_receipts_strict()
    assert getattr(excinfo.value, "line_number", None) == 2

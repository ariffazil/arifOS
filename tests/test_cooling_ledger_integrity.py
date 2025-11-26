# tests/test_cooling_ledger_integrity.py
#
# Comprehensive integrity tests for Cooling Ledger hash-chain verification.
# Tests tamper detection, chain linkage, and cryptographic integrity.

import json
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Tuple

import pytest

from arifos_core.memory.cooling_ledger import append_entry, verify_chain


def _hash_entry(entry: Dict[str, Any]) -> str:
    """
    Helper to recompute hash using canonical JSON.
    Must match the implementation used by Cooling Ledger.
    """
    excluded = {"hash", "kms_signature", "kms_key_id"}
    data = {k: v for k, v in entry.items() if k not in excluded}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha3_256(canonical.encode("utf-8")).hexdigest()


def _read_ledger(path: Path) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Read first two entries from ledger for sanity tests.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 2, "Expected at least two entries in ledger"
    entry1 = json.loads(lines[0])
    entry2 = json.loads(lines[1])
    return entry1, entry2


# --- Chain linkage tests ------------------------------------------------------

def test_ledger_chain_links_via_prev_hash(tmp_path: Path) -> None:
    """
    Cooling Ledger enforces prev_hash chain without breaks.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry1: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "test_entry_1",
        "payload": {"kind": "test", "idx": 1},
    }
    entry2: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:01Z",
        "event": "test_entry_2",
        "payload": {"kind": "test", "idx": 2},
    }

    append_entry(ledger_path, entry1)
    append_entry(ledger_path, entry2)

    ok, details = verify_chain(ledger_path)
    assert ok, f"Ledger chain broken: {details}"

    # Verify prev_hash linkage
    stored1, stored2 = _read_ledger(ledger_path)

    # Recompute hash for entry1 and ensure stored2.prev_hash matches it
    h1 = _hash_entry(stored1)
    assert stored2["prev_hash"] == h1, "Second entry prev_hash should match first entry hash"


def test_ledger_first_entry_has_null_prev_hash(tmp_path: Path) -> None:
    """
    First entry in ledger should have prev_hash = null.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "genesis",
        "payload": {"kind": "test"},
    }

    append_entry(ledger_path, entry)

    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    assert stored["prev_hash"] is None, "First entry should have prev_hash=null"


# --- Tamper detection tests ---------------------------------------------------

def test_ledger_detects_content_tampering(tmp_path: Path) -> None:
    """
    If someone modifies an entry's content, verify_chain should fail.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    # Build a small chain
    for i in range(3):
        entry = {
            "timestamp": f"2025-11-24T00:00:0{i}Z",
            "event": f"entry_{i}",
            "payload": {"idx": i},
        }
        append_entry(ledger_path, entry)

    # Verify chain is valid before tampering
    ok, _ = verify_chain(ledger_path)
    assert ok, "Chain should be valid before tampering"

    # Tamper with first entry's payload
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["payload"]["idx"] = 999  # modify content
    # Keep the old hash to simulate tampering without updating hash
    lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, details = verify_chain(ledger_path)
    assert not ok, "Tampered ledger should fail verification"
    assert "mismatch" in details.lower() or "hash" in details.lower()


def test_ledger_detects_hash_tampering(tmp_path: Path) -> None:
    """
    If someone modifies an entry's hash field, verify_chain should fail.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    for i in range(2):
        entry = {
            "timestamp": f"2025-11-24T00:00:0{i}Z",
            "event": f"entry_{i}",
            "payload": {"idx": i},
        }
        append_entry(ledger_path, entry)

    # Tamper with first entry's hash
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    first = json.loads(lines[0])
    first["hash"] = "deadbeef" * 8  # invalid hash
    lines[0] = json.dumps(first, sort_keys=True, separators=(",", ":"))
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, details = verify_chain(ledger_path)
    assert not ok
    assert "hash mismatch" in details.lower()


def test_ledger_rejects_broken_prev_hash_link(tmp_path: Path) -> None:
    """
    If prev_hash of an entry does not match the hash of the previous entry,
    verify_chain must fail.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry1: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "first",
        "payload": {"idx": 1},
    }
    entry2: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:01Z",
        "event": "second",
        "payload": {"idx": 2},
    }

    append_entry(ledger_path, entry1)
    append_entry(ledger_path, entry2)

    # Tamper only with prev_hash of second entry
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    second = json.loads(lines[1])
    second["prev_hash"] = "deadbeef" * 8  # invalid prev_hash
    # Need to recompute hash since we changed prev_hash
    second["hash"] = _hash_entry(second)
    lines[1] = json.dumps(second, sort_keys=True, separators=(",", ":"))
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, details = verify_chain(ledger_path)
    assert not ok
    assert "prev_hash mismatch" in details.lower()


# --- Edge cases ---------------------------------------------------------------

def test_ledger_handles_single_entry_chain(tmp_path: Path) -> None:
    """
    A single-entry ledger should still verify successfully.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "single",
        "payload": {"idx": 0},
    }

    append_entry(ledger_path, entry)
    ok, details = verify_chain(ledger_path)
    assert ok, f"Single-entry ledger should verify: {details}"


def test_ledger_handles_empty_file(tmp_path: Path) -> None:
    """
    An empty ledger file should verify as valid (vacuous truth).
    """
    ledger_path = tmp_path / "ledger.jsonl"
    ledger_path.touch()  # create empty file

    ok, details = verify_chain(ledger_path)
    assert ok, f"Empty ledger should verify: {details}"


def test_ledger_rejects_nonexistent_file(tmp_path: Path) -> None:
    """
    Verifying a non-existent file should return False.
    """
    ledger_path = tmp_path / "nonexistent.jsonl"

    ok, details = verify_chain(ledger_path)
    assert not ok
    assert "does not exist" in details.lower()


def test_ledger_handles_malformed_json(tmp_path: Path) -> None:
    """
    Ledger with malformed JSON should fail verification.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "valid",
        "payload": {},
    }
    append_entry(ledger_path, entry)

    # Append malformed JSON
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write("{this is not valid json\n")

    ok, details = verify_chain(ledger_path)
    assert not ok
    assert "json" in details.lower() or "decode" in details.lower()


# --- Long chain tests ---------------------------------------------------------

def test_ledger_verifies_long_chain(tmp_path: Path) -> None:
    """
    Verify that a longer chain (100 entries) validates correctly.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    # Create 100 entries
    for i in range(100):
        entry = {
            "timestamp": f"2025-11-24T00:{i // 60:02d}:{i % 60:02d}Z",
            "event": f"entry_{i}",
            "payload": {"idx": i},
        }
        append_entry(ledger_path, entry)

    ok, details = verify_chain(ledger_path)
    assert ok, f"Long chain should verify: {details}"
    assert "100 entries" in details


def test_ledger_detects_tampering_in_middle_of_long_chain(tmp_path: Path) -> None:
    """
    Tampering with a middle entry in a long chain should be detected.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    # Create 50 entries
    for i in range(50):
        entry = {
            "timestamp": f"2025-11-24T00:{i // 60:02d}:{i % 60:02d}Z",
            "event": f"entry_{i}",
            "payload": {"idx": i},
        }
        append_entry(ledger_path, entry)

    # Verify chain is valid
    ok, _ = verify_chain(ledger_path)
    assert ok

    # Tamper with entry 25 (middle of chain)
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    middle = json.loads(lines[25])
    middle["payload"]["idx"] = 9999
    lines[25] = json.dumps(middle, sort_keys=True, separators=(",", ":"))
    ledger_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    ok, details = verify_chain(ledger_path)
    assert not ok
    assert "25" in details  # Should report the entry number


# --- Cryptographic properties -------------------------------------------------

def test_ledger_uses_sha3_256(tmp_path: Path) -> None:
    """
    Verify that the ledger uses SHA3-256 for hashing.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "crypto_test",
        "payload": {"data": "test"},
    }

    append_entry(ledger_path, entry)

    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    stored = json.loads(lines[0])

    # SHA3-256 produces 64 hex characters
    assert len(stored["hash"]) == 64, "Hash should be 64 hex characters (SHA3-256)"
    assert all(c in "0123456789abcdef" for c in stored["hash"]), "Hash should be lowercase hex"


def test_ledger_hash_is_deterministic(tmp_path: Path) -> None:
    """
    Same entry content should produce same hash.
    """
    ledger_path1 = tmp_path / "ledger1.jsonl"
    ledger_path2 = tmp_path / "ledger2.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "deterministic_test",
        "payload": {"data": "identical"},
    }

    append_entry(ledger_path1, entry.copy())
    append_entry(ledger_path2, entry.copy())

    lines1 = ledger_path1.read_text(encoding="utf-8").splitlines()
    lines2 = ledger_path2.read_text(encoding="utf-8").splitlines()

    stored1 = json.loads(lines1[0])
    stored2 = json.loads(lines2[0])

    assert stored1["hash"] == stored2["hash"], "Identical entries should have identical hashes"


# --- Append-only properties ---------------------------------------------------

def test_ledger_append_creates_parent_directory(tmp_path: Path) -> None:
    """
    append_entry should create parent directory if it doesn't exist.
    """
    ledger_path = tmp_path / "nested" / "dir" / "ledger.jsonl"

    entry: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "test",
        "payload": {},
    }

    append_entry(ledger_path, entry)

    assert ledger_path.exists(), "Ledger file should be created"
    assert ledger_path.parent.exists(), "Parent directory should be created"


def test_ledger_append_preserves_existing_entries(tmp_path: Path) -> None:
    """
    Appending new entries should not modify existing entries.
    """
    ledger_path = tmp_path / "ledger.jsonl"

    # Add first entry
    entry1: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:00Z",
        "event": "first",
        "payload": {"idx": 1},
    }
    append_entry(ledger_path, entry1)

    # Read and save first entry
    lines_before = ledger_path.read_text(encoding="utf-8").splitlines()
    first_entry_before = lines_before[0]

    # Add second entry
    entry2: Dict[str, Any] = {
        "timestamp": "2025-11-24T00:00:01Z",
        "event": "second",
        "payload": {"idx": 2},
    }
    append_entry(ledger_path, entry2)

    # Verify first entry unchanged
    lines_after = ledger_path.read_text(encoding="utf-8").splitlines()
    first_entry_after = lines_after[0]

    assert first_entry_before == first_entry_after, "First entry should remain unchanged"
    assert len(lines_after) == 2, "Should have exactly 2 entries"

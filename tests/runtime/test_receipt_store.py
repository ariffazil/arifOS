"""Tests for the durable, signed, hash-chained ReceiptStore (Epoch 2 / Item 4).

The audit's four independent tests:
  1. Write  — can append.
  2. Read   — exact receipt can be retrieved.
  3. Verify — signature and chain validate.
  4. Replay — the decision sequence can be reconstructed from durable
             records alone.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


# ── Schema ────────────────────────────────────────────────────────────────


def test_receipt_shape_matches_audit_spec():
    """The Receipt dataclass has every field the audit spec requires."""
    from arifosmcp.runtime.receipt_store import (
        Receipt,
        make_receipt,
    )

    r = make_receipt(
        run_id="run-1",
        trace_id="trc-1",
        session_id="SEAL-1",
        actor_id="arif",
        action="arif_seal",
        input_data={"intent": "test"},
        evidence_hashes=("arifos://evidence/e-1",),
        decision="SEAL",
        execution_result={"outcome": "sealed"},
        previous_receipt_hash="0" * 64,
    )
    d = r.to_dict()
    expected_fields = {
        "receipt_id", "run_id", "trace_id", "session_id", "actor_id",
        "action", "input_hash", "evidence_hashes", "decision",
        "decision_hash", "execution_result_hash", "previous_receipt_hash",
        "timestamp", "signature", "state_version",
    }
    assert set(d.keys()) == expected_fields


# ── Test 1: Write ─────────────────────────────────────────────────────────


def test_write_appends_receipt_to_store(tmp_path: Path):
    """append writes a receipt durably to the store."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    r = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
    )
    store.append(r)
    assert path.exists()
    assert path.stat().st_size > 0


def test_write_is_idempotent(tmp_path: Path):
    """Appending the same receipt twice does not duplicate the line."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    r = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
    )
    store.append(r)
    size_after_first = path.stat().st_size
    store.append(r)
    size_after_second = path.stat().st_size
    assert size_after_first == size_after_second


# ── Test 2: Read ──────────────────────────────────────────────────────────


def test_read_retrieves_appended_receipt(tmp_path: Path):
    """get retrieves the exact receipt that was appended."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    r = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
    )
    store.append(r)
    retrieved = store.get(r.receipt_id)
    assert retrieved is not None
    assert retrieved.receipt_id == r.receipt_id
    assert retrieved.run_id == r.run_id
    assert retrieved.decision == r.decision
    assert retrieved.signature == r.signature


def test_read_returns_none_for_unknown_id(tmp_path: Path):
    """get returns None when the receipt id is not in the store."""
    from arifosmcp.runtime.receipt_store import ReceiptStore

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    assert store.get("r-doesnotexist") is None


def test_latest_returns_most_recent(tmp_path: Path):
    """latest() returns the most recently appended receipt."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    r1 = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
    )
    r2 = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=ReceiptStore(path=path)._canonical_hash(
            {"placeholder": "ignored"}
        ) if False else "0"*64,
    )
    # Just append both and verify latest is r2.
    store.append(r1)
    store.append(r2)
    assert store.latest().receipt_id == r2.receipt_id


# ── Test 3: Verify ────────────────────────────────────────────────────────


def test_verify_valid_signature_passes(tmp_path: Path):
    """A receipt signed with the store's key verifies."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    secret = b"test-secret-key"
    store = ReceiptStore(path=path, secret=secret)
    r = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
        secret=secret,
    )
    store.append(r)
    ok, reason = store.verify_one(r)
    assert ok, reason


def test_verify_tampered_signature_fails(tmp_path: Path):
    """A receipt with a tampered signature is rejected."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    secret = b"test-secret-key"
    store = ReceiptStore(path=path, secret=secret)
    r = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
        secret=secret,
    )
    # Tamper with one field.
    from dataclasses import replace
    tampered = replace(r, decision="HOLD")
    ok, reason = store.verify_one(tampered)
    assert not ok
    assert "signature_invalid" in reason


def test_verify_chain_validates_unbroken_chain(tmp_path: Path):
    """An unbroken chain verifies. The second receipt's
    previous_receipt_hash must equal the first's canonical hash."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        _canonical_hash,
        _signing_payload,
        make_receipt,
    )

    path = tmp_path / "receipts.jsonl"
    secret = b"chain-test"
    store = ReceiptStore(path=path, secret=secret)
    r1 = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash=GENESIS_PREVIOUS_HASH,
        secret=secret,
    )
    store.append(r1)
    r2 = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=_canonical_hash(_signing_payload(r1)),
        secret=secret,
    )
    store.append(r2)
    ok, reason = store.verify_chain()
    assert ok, reason


def test_verify_chain_detects_broken_link(tmp_path: Path):
    """A broken chain (modified previous_receipt_hash) is detected."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )
    from dataclasses import replace

    path = tmp_path / "receipts.jsonl"
    secret = b"chain-test"
    store = ReceiptStore(path=path, secret=secret)
    r1 = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash=GENESIS_PREVIOUS_HASH,
        secret=secret,
    )
    store.append(r1)
    r2 = make_receipt(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash="0" * 64,  # wrong: should reference r1
        secret=secret,
    )
    store.append(r2)
    ok, reason = store.verify_chain()
    assert not ok
    assert "chain_broken" in reason


# ── Test 4: Replay ────────────────────────────────────────────────────────


def test_replay_reconstructs_decision_sequence(tmp_path: Path):
    """replay() reconstructs the decision sequence from durable records alone."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        _canonical_hash,
        _signing_payload,
        make_receipt,
    )

    path = tmp_path / "receipts.jsonl"
    secret = b"replay-test"
    store = ReceiptStore(path=path, secret=secret)
    # Build a chain: 3 receipts in the same run, 2 different decisions.
    r1 = make_receipt(
        run_id="run-A", trace_id="t-A", session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
    )
    store.append(r1)
    r2 = make_receipt(
        run_id="run-A", trace_id="t-A", session_id="S", actor_id="a",
        action="arif_observe", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=_canonical_hash(_signing_payload(r1)),
        secret=secret,
    )
    store.append(r2)
    r3 = make_receipt(
        run_id="run-A", trace_id="t-A", session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SABAR", execution_result="y",
        previous_receipt_hash=_canonical_hash(_signing_payload(r2)),
        secret=secret,
    )
    store.append(r3)

    replayed = store.replay(r3.receipt_id)
    assert replayed is not None
    assert replayed["run_id"] == "run-A"
    assert replayed["decision_sequence"] == ["SEAL", "SEAL", "SABAR"]
    assert replayed["first_receipt_id"] == r1.receipt_id
    assert replayed["last_receipt_id"] == r3.receipt_id


def test_replay_requires_no_in_memory_state(tmp_path: Path):
    """replay works from a fresh store instance reading the same file."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )

    path = tmp_path / "receipts.jsonl"
    secret = b"replay-test"
    s1 = ReceiptStore(path=path, secret=secret)
    r = make_receipt(
        run_id="run-Z", trace_id="t-Z", session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
    )
    s1.append(r)
    # A fresh store, same file, same path: replay works without
    # any in-memory state.
    s2 = ReceiptStore(path=path, secret=secret)
    replayed = s2.replay(r.receipt_id)
    assert replayed is not None
    assert replayed["decision_sequence"] == ["SEAL"]


def test_replay_returns_none_for_unknown_receipt(tmp_path: Path):
    from arifosmcp.runtime.receipt_store import ReceiptStore

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    assert store.replay("r-unknown") is None


# ── Hashing helpers ─────────────────────────────────────────────────────


def test_canonical_hash_is_deterministic():
    """Same payload → same hash, regardless of dict insertion order."""
    from arifosmcp.runtime.receipt_store import _canonical_hash

    a = _canonical_hash({"b": 2, "a": 1})
    b = _canonical_hash({"a": 1, "b": 2})
    assert a == b


def test_signature_changes_with_secret(tmp_path: Path):
    """A different secret produces a different signature for the same receipt."""
    from arifosmcp.runtime.receipt_store import ReceiptStore, make_receipt

    path = tmp_path / "receipts.jsonl"
    secret_a = b"secret-a"
    secret_b = b"secret-b"
    s_a = ReceiptStore(path=path, secret=secret_a)
    s_b = ReceiptStore(path=path, secret=secret_b)
    # Use the same arguments to make_receipt (different secrets).
    base = dict(
        run_id="run-1", trace_id="t-1", session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y", previous_receipt_hash="0"*64,
    )
    r_a = make_receipt(**base, secret=secret_a)
    r_b = make_receipt(**base, secret=secret_b)
    # Different secrets → different signatures (overwhelmingly likely).
    assert r_a.signature != r_b.signature


def test_all_receipts_returns_in_append_order(tmp_path: Path):
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    rs = [
        make_receipt(
            run_id=f"run-{i}", trace_id="t", session_id="S", actor_id="a",
            action="arif_init", input_data="x", evidence_hashes=(),
            decision="SEAL", execution_result="y",
            previous_receipt_hash=GENESIS_PREVIOUS_HASH,
        )
        for i in range(3)
    ]
    for r in rs:
        store.append(r)
    ids = [r.receipt_id for r in store.all_receipts()]
    assert ids == [r.receipt_id for r in rs]
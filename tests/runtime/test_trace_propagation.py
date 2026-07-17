"""Phase 2 / Item 5 — Trace propagation across every stage.

The audit's Item 5: "Trace propagation across every stage."

Every consequential action in a run shares one trace_id. The trace_id
flows from start_run through every record_stage, every receipt, every
evidence reference. An operator can pull every record for one trace
from durable stores alone, with no in-memory state.

This file proves:
  1. The trace_id set at start_run is preserved through every transition.
  2. Every receipt records the same trace_id as the run.
  3. by_trace_id() returns every receipt for a given trace.
  4. by_run_id() returns every receipt for a given run.
  5. The trace_id distinguishes concurrent runs with the same intent.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any


def test_trace_id_set_at_start_run_is_preserved_through_every_stage():
    """The trace_id set at start_run is unchanged through every record_stage."""
    from arifosmcp.runtime.run_envelope import (
        record_stage,
        start_run,
    )

    env = start_run(
        session_id="S", actor_id="a", intent="x", trace_id="trc-fixed-1"
    )
    original = env.trace_id
    for tool, _, started, finished, outcome in [
        ("arif_init", (), "t0", "t1", "SEAL"),
        ("arif_observe", (), "t1", "t2", "SEAL"),
        ("arif_think", (), "t2", "t3", "SEAL"),
        ("arif_judge", (), "t3", "t4", "SEAL"),
        ("arif_seal", (), "t4", "t5", "SEAL"),
    ]:
        env = record_stage(
            env, tool=tool, started_at=started, finished_at=finished,
            outcome=outcome,
        )
        assert env.trace_id == original, (
            f"trace_id changed at {tool}: was {original}, now {env.trace_id}"
        )


def test_trace_id_is_auto_generated_when_not_provided():
    """start_run without an explicit trace_id generates a fresh one."""
    from arifosmcp.runtime.run_envelope import start_run

    e1 = start_run(session_id="S", actor_id="a", intent="x")
    e2 = start_run(session_id="S", actor_id="a", intent="x")
    assert e1.trace_id != e2.trace_id
    # Both trace_ids follow the trc- prefix convention.
    assert e1.trace_id.startswith("trc-")
    assert e2.trace_id.startswith("trc-")


def test_every_receipt_shares_the_run_trace_id(tmp_path: Path):
    """A receipt for a run inherits the run's trace_id; by_trace_id collects them all."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        _canonical_hash,
        _signing_payload,
        make_receipt,
    )

    path = tmp_path / "receipts.jsonl"
    secret = b"trace-test"
    store = ReceiptStore(path=path, secret=secret)

    trace_id = "trc-shared-1"
    run_id = "run-shared-1"

    r1 = make_receipt(
        run_id=run_id, trace_id=trace_id, session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
    )
    r2 = make_receipt(
        run_id=run_id, trace_id=trace_id, session_id="S", actor_id="a",
        action="arif_observe", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=_canonical_hash(_signing_payload(r1)),
        secret=secret,
    )
    r3 = make_receipt(
        run_id=run_id, trace_id=trace_id, session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=_canonical_hash(_signing_payload(r2)),
        secret=secret,
    )
    for r in (r1, r2, r3):
        store.append(r)

    # All three receipts share the same trace_id.
    by_trace = store.by_trace_id(trace_id)
    assert len(by_trace) == 3
    assert all(r.trace_id == trace_id for r in by_trace)
    # The by_run_id view also returns all three.
    by_run = store.by_run_id(run_id)
    assert len(by_run) == 3


def test_by_trace_id_filters_correctly_across_concurrent_runs(tmp_path: Path):
    """Two concurrent runs with different trace_ids are queryable separately."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )

    path = tmp_path / "receipts.jsonl"
    secret = b"concurrent-test"
    store = ReceiptStore(path=path, secret=secret)

    # Two interleaved runs: A then B then A then B.
    for trace, run, action in [
        ("trc-A", "run-A", "arif_init"),
        ("trc-B", "run-B", "arif_init"),
        ("trc-A", "run-A", "arif_seal"),
        ("trc-B", "run-B", "arif_seal"),
    ]:
        r = make_receipt(
            run_id=run, trace_id=trace, session_id="S", actor_id="a",
            action=action, input_data="x", evidence_hashes=(),
            decision="SEAL", execution_result="y",
            previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
        )
        store.append(r)

    # Each trace returns 2 receipts.
    assert len(store.by_trace_id("trc-A")) == 2
    assert len(store.by_trace_id("trc-B")) == 2
    # Each run returns 2 receipts.
    assert len(store.by_run_id("run-A")) == 2
    assert len(store.by_run_id("run-B")) == 2
    # The interleaving does not mix the two runs.
    actions_A = [r.action for r in store.by_run_id("run-A")]
    assert actions_A == ["arif_init", "arif_seal"]


def test_trace_id_distinguishes_same_intent_across_runs(tmp_path: Path):
    """Two runs with the same intent get different trace_ids and different runs."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )
    from arifosmcp.runtime.run_envelope import start_run

    path = tmp_path / "receipts.jsonl"
    secret = b"distinct-test"
    store = ReceiptStore(path=path, secret=secret)

    # Two runs, same intent.
    e1 = start_run(session_id="S", actor_id="a", intent="same")
    e2 = start_run(session_id="S", actor_id="a", intent="same")
    assert e1.intent_hash == e2.intent_hash  # same intent, same hash
    assert e1.trace_id != e2.trace_id  # different trace
    assert e1.run_id != e2.run_id  # different run

    # Receipts for each run are queryable.
    r1 = make_receipt(
        run_id=e1.run_id, trace_id=e1.trace_id, session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
    )
    r2 = make_receipt(
        run_id=e2.run_id, trace_id=e2.trace_id, session_id="S", actor_id="a",
        action="arif_init", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
    )
    store.append(r1)
    store.append(r2)
    assert store.by_trace_id(e1.trace_id) == (r1,)
    assert store.by_trace_id(e2.trace_id) == (r2,)


def test_trace_id_survives_run_envelope_reconstruction(tmp_path: Path):
    """The trace_id is preserved through a full envelope reconstruction."""
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )
    from arifosmcp.runtime.run_envelope import (
        finalise_receipt,
        record_stage,
        set_verdict,
        start_run,
    )

    path = tmp_path / "receipts.jsonl"
    secret = b"recon-test"
    store = ReceiptStore(path=path, secret=secret)

    trace_id = "trc-recon-1"
    env = start_run(
        session_id="S", actor_id="a", intent="x", trace_id=trace_id
    )
    env = record_stage(env, tool="arif_init", started_at="t0", finished_at="t1", outcome="SEAL")
    env = record_stage(env, tool="arif_observe", started_at="t1", finished_at="t2", outcome="SEAL")
    env = record_stage(env, tool="arif_judge", started_at="t2", finished_at="t3", outcome="SEAL")
    env = set_verdict(env, "SEAL")
    env = finalise_receipt(env, receipt_ref="arifos://receipt/r-trace")

    # The envelope's trace_id is unchanged through every stage.
    assert env.trace_id == trace_id
    # Issuing a receipt for this run; the receipt's trace_id matches.
    r = make_receipt(
        run_id=env.run_id, trace_id=env.trace_id, session_id="S", actor_id="a",
        action="arif_seal", input_data="x", evidence_hashes=(),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH, secret=secret,
    )
    store.append(r)
    assert r.trace_id == trace_id
    # by_trace_id finds it.
    assert store.by_trace_id(trace_id) == (r,)


def test_by_trace_id_returns_empty_for_unknown_trace(tmp_path: Path):
    from arifosmcp.runtime.receipt_store import ReceiptStore

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    assert store.by_trace_id("trc-unknown") == ()


def test_by_run_id_returns_empty_for_unknown_run(tmp_path: Path):
    from arifosmcp.runtime.receipt_store import ReceiptStore

    path = tmp_path / "receipts.jsonl"
    store = ReceiptStore(path=path)
    assert store.by_run_id("run-unknown") == ()


def test_trace_id_format_is_stable():
    """The auto-generated trace_id follows the trc- prefix convention."""
    from arifosmcp.runtime.run_envelope import start_run

    for _ in range(10):
        env = start_run(session_id="S", actor_id="a", intent="x")
        assert env.trace_id.startswith("trc-")
        # The id portion is hex.
        suffix = env.trace_id[len("trc-"):]
        assert len(suffix) >= 16
        int(suffix, 16)  # parses as hex


def test_evidence_store_references_carry_through_to_receipts(tmp_path: Path):
    """Evidence refs from the run flow into the receipt's evidence_hashes."""
    from arifosmcp.runtime.evidence_store import EvidenceStore
    from arifosmcp.runtime.receipt_store import (
        GENESIS_PREVIOUS_HASH,
        ReceiptStore,
        make_receipt,
    )

    ev_path = tmp_path / "evidence.jsonl"
    rec_path = tmp_path / "receipts.jsonl"
    ev_store = EvidenceStore(path=ev_path)
    rec_store = ReceiptStore(path=rec_path)

    # Two pieces of evidence in the evidence store.
    e1 = ev_store.append({"type": "geox", "id": "obs-1"})
    e2 = ev_store.append({"type": "wealth", "id": "npv-1"})

    # A receipt references both.
    r = make_receipt(
        run_id="run-1", trace_id="trc-1", session_id="S", actor_id="a",
        action="arif_seal", input_data="x",
        evidence_hashes=(e1.ref, e2.ref),
        decision="SEAL", execution_result="y",
        previous_receipt_hash=GENESIS_PREVIOUS_HASH,
    )
    rec_store.append(r)
    retrieved = rec_store.get(r.receipt_id)
    assert retrieved.evidence_hashes == (e1.ref, e2.ref)
    # Both evidence records are still in the evidence store.
    assert ev_store.has(e1.ref)
    assert ev_store.has(e2.ref)
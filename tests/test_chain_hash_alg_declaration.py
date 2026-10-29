"""
tests/test_chain_hash_alg_declaration.py — PACKET C (F13 2026-10-30)

"F13 AUTHORIZE PACKET C" — the chain-hash-algorithm declaration on new
seal-chain rows. Writer stamps (derived, never caller-supplied); the verifier
(scripts/verify_vault_chain.py, unchanged by this packet) already distinguishes
declared-tamper from unknown-algorithm-unmeasured. History is never rewritten.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from arifosmcp.runtime.canonical_vault_chain import (
    _HASH_FIELDS,
    ReceiptEnvelope,
    compute_receipt_hash,
)
from verify_vault_chain import verify_ledger


def _envelope(**over):
    base = dict(
        receipt_id="r-test-1",
        sequence=1,
        previous_hash="sha256:" + "0" * 64,
        receipt_hash="sha256:" + "a" * 64,
        timestamp="2026-10-30T00:00:00Z",
        actor_id="pytest:333",
        actor_verification={"method": "none"},
        session_id="s-test",
        trace_id="t-test",
        operation_id="op-test",
        tool_name="pytest",
        input_hash="sha256:" + "b" * 64,
        authority_state="LOW",
        decision_reference="ref",
        result_hash="sha256:" + "c" * 64,
        reversibility="reversible",
        software_release="test",
        signature="",
    )
    base.update(over)
    return ReceiptEnvelope(**base)


# ── the writer declaration ──────────────────────────────────────────────────


def test_new_envelope_declares_sha256():
    assert _envelope().to_wire()["chain_hash_alg"] == "sha256"


def test_falsifier_declaration_is_derived_not_caller_supplied():
    # a caller trying to lie about the algorithm is overridden post-init
    e = _envelope(chain_hash_alg="md5")
    assert e.chain_hash_alg == "sha256", "caller smuggled a foreign algorithm"


def test_falsifier_declaration_absent_means_dead_stamp():
    # mutation direction: remove the field -> to_wire lacks the key -> dies
    assert "chain_hash_alg" in _envelope().to_wire()


# ── receipt_hash stability ──────────────────────────────────────────────────


def test_declaration_not_in_hash_fields():
    # receipt_hash is computed over _HASH_FIELDS only; the declaration must
    # never perturb it, or every legacy hash comparison would break
    assert "chain_hash_alg" not in _HASH_FIELDS


def test_compute_receipt_hash_ignores_the_declaration():
    fields = {k: "x" for k in _HASH_FIELDS}
    h1 = compute_receipt_hash(fields)
    fields["chain_hash_alg"] = "sha256"
    h2 = compute_receipt_hash(fields)
    assert h1 == h2, "declaration leaked into receipt_hash computation"


# ── the verifier three-way (verifier itself unchanged by this packet) ───────


def _body_for(entry_id: str, prev: str) -> dict:
    return {"id": entry_id, "prev_hash": prev, "ts": "2026-10-30T00:00:00Z"}


def _chain_hash(body: dict) -> str:
    # exact verifier method (verify_vault_chain.py:525-526): sha256 over
    # canonical-json (sort_keys, ensure_ascii=False, default separators) of
    # the entry with chain_hash/signature stripped, 0x-prefixed
    stripped = {k: v for k, v in body.items() if k not in ("chain_hash", "signature")}
    canonical = json.dumps(stripped, sort_keys=True, ensure_ascii=False)
    return "0x" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_ledger(tmp_path, rows):
    p = tmp_path / "chain.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return p


def _spec(p):
    return {
        "name": "test-ledger",
        "path": p,
        "seq_field": "id",
        "prev_field": "prev_hash",
        "chain_field": "chain_hash",
        "genesis_prev_values": {"", "GENESIS", None},
    }


def test_verifier_declared_match_counts_verified(tmp_path):
    body = _body_for("e1", "GENESIS")
    # the verifier hashes the body INCLUDING the declaration (strips only
    # chain_hash/signature) — the declared row's hash covers its own alg field
    row = dict(body, chain_hash_alg="sha256")
    row["chain_hash"] = _chain_hash(row)
    rep = verify_ledger(_spec(_write_ledger(tmp_path, [row])), None)
    ci = rep["chain_hash_integrity"]
    assert ci["checked"] == 1 and ci["verified"] == 1 and ci["tampered"] == 0


def test_verifier_declared_mismatch_is_tamper(tmp_path):
    body = _body_for("e1", "GENESIS")
    row = dict(body, chain_hash="deadbeef", chain_hash_alg="sha256")
    rep = verify_ledger(_spec(_write_ledger(tmp_path, [row])), None)
    ci = rep["chain_hash_integrity"]
    assert ci["tampered"] == 1, "declared algorithm must make mismatch a TAMPER"


def test_verifier_legacy_mismatch_is_unmeasured_not_tamper(tmp_path):
    # F9 honesty: without a declaration, sha256-mismatch cannot distinguish
    # a different algorithm from tampering — UNMEASURED, never a false tamper
    body = _body_for("e1", "GENESIS")
    row = dict(body, chain_hash="deadbeef")  # no chain_hash_alg — legacy shape
    rep = verify_ledger(_spec(_write_ledger(tmp_path, [row])), None)
    ci = rep["chain_hash_integrity"]
    assert ci["unmeasured_unknown_alg"] == 1 and ci["tampered"] == 0


def test_verifier_is_read_only(tmp_path):
    body = _body_for("e1", "GENESIS")
    row = dict(body, chain_hash=_chain_hash(body), chain_hash_alg="sha256")
    p = _write_ledger(tmp_path, [row])
    before = p.read_bytes()
    verify_ledger(_spec(p), None)
    assert p.read_bytes() == before, "verifier must never rewrite history"


def test_verifier_legacy_rows_still_verified_by_inference(tmp_path):
    # a legacy row whose chain_hash IS sha256 verifies without any declaration
    body = _body_for("e1", "GENESIS")
    row = dict(body, chain_hash=_chain_hash(body))
    rep = verify_ledger(_spec(_write_ledger(tmp_path, [row])), None)
    assert rep["chain_hash_integrity"]["verified"] == 1

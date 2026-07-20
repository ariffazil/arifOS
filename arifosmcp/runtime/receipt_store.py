"""
arifOS Receipt Store — durable, signed, hash-chained receipts.

Epoch 2 / Item 4 of the Kernel Senescence Reduction plan.
Every consequential action leaves a receipt. The receipt is signed
(HMAC) and chained (each receipt references the prior receipt's hash).
Replay reconstructs the decision sequence from durable records alone.

Schema (from F13 epoch / audit spec):
    {
      "receipt_id": "...",
      "run_id": "...",
      "trace_id": "...",
      "session_id": "...",
      "actor_id": "...",
      "action": "...",
      "input_hash": "...",
      "evidence_hashes": [],
      "decision": "SEAL",
      "decision_hash": "...",
      "execution_result_hash": "...",
      "previous_receipt_hash": "...",
      "timestamp": "...",
      "signature": "..."
    }

Four independent tests must pass:
  1. Write  — can append.
  2. Read   — exact receipt can be retrieved.
  3. Verify — signature and chain validate.
  4. Replay — the decision sequence can be reconstructed without
             executing the action again. No mutable logs, no in-memory
             state required.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# Schema version. Bump when the canonical shape changes.
RECEIPT_STATE_VERSION = 1

# Default store path.
DEFAULT_RECEIPT_PATH = "/var/lib/arifos/vault/receipts.jsonl"

# Sentinel for the first receipt in a chain.
GENESIS_PREVIOUS_HASH = "0" * 64


# ── Canonical receipt ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class Receipt:
    """A signed, hash-chained record of one consequential action."""

    receipt_id: str
    run_id: str
    trace_id: str
    session_id: str
    actor_id: str
    action: str
    input_hash: str
    evidence_hashes: tuple[str, ...]
    decision: str
    decision_hash: str
    execution_result_hash: str
    previous_receipt_hash: str
    timestamp: str
    signature: str
    state_version: int = RECEIPT_STATE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "run_id": self.run_id,
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "action": self.action,
            "input_hash": self.input_hash,
            "evidence_hashes": list(self.evidence_hashes),
            "decision": self.decision,
            "decision_hash": self.decision_hash,
            "execution_result_hash": self.execution_result_hash,
            "previous_receipt_hash": self.previous_receipt_hash,
            "timestamp": self.timestamp,
            "signature": self.signature,
            "state_version": self.state_version,
        }


# ── Hashing ───────────────────────────────────────────────────────────────


def _canonical_hash(payload: dict[str, Any]) -> str:
    """sha256 of the canonical JSON form, with sha256: prefix."""
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _signing_payload(receipt: Receipt) -> dict[str, Any]:
    """The fields that go into the signature. Signature covers every field
    except `signature` itself."""
    d = receipt.to_dict()
    d.pop("signature", None)
    return d


def _sign_receipt(receipt: Receipt, secret: bytes) -> str:
    """HMAC-SHA256 of the canonical signing payload."""
    payload = _canonical_hash(_signing_payload(receipt))
    return hmac.new(secret, payload.encode("utf-8"), hashlib.sha256).hexdigest()


def _default_secret() -> bytes:
    raw = os.getenv("ARIFOS_RECEIPT_SECRET")
    if raw:
        return raw.encode("utf-8")
    return b"arifos-receipt-default-key-replace-in-prod"


# ── Receipt builder ───────────────────────────────────────────────────────


def make_receipt(
    *,
    run_id: str,
    trace_id: str,
    session_id: str,
    actor_id: str,
    action: str,
    input_data: Any,
    evidence_hashes: tuple[str, ...],
    decision: str,
    execution_result: Any,
    previous_receipt_hash: str,
    timestamp: str | None = None,
    secret: bytes | None = None,
) -> Receipt:
    """Build a signed receipt for one action.

    The input_data and execution_result are hashed but not stored in
    full. To recover them, use replay() against the source systems
    (or store the full data elsewhere and reference by hash).
    """
    ts = timestamp or datetime.now(UTC).isoformat()
    input_hash = _canonical_hash(input_data) if not isinstance(input_data, str) else (
        f"sha256:{hashlib.sha256(input_data.encode('utf-8')).hexdigest()}"
    )
    decision_hash = _canonical_hash({"decision": decision, "ts": ts})
    exec_hash = _canonical_hash(execution_result) if not isinstance(execution_result, str) else (
        f"sha256:{hashlib.sha256(execution_result.encode('utf-8')).hexdigest()}"
    )
    # Build the receipt with placeholder signature, then sign.
    provisional = Receipt(
        receipt_id=f"r-{uuid.uuid4().hex[:16]}",
        run_id=run_id,
        trace_id=trace_id,
        session_id=session_id,
        actor_id=actor_id,
        action=action,
        input_hash=input_hash,
        evidence_hashes=evidence_hashes,
        decision=decision,
        decision_hash=decision_hash,
        execution_result_hash=exec_hash,
        previous_receipt_hash=previous_receipt_hash,
        timestamp=ts,
        signature="",
    )
    sig = _sign_receipt(provisional, secret or _default_secret())
    # Replace signature.
    return Receipt(
        receipt_id=provisional.receipt_id,
        run_id=provisional.run_id,
        trace_id=provisional.trace_id,
        session_id=provisional.session_id,
        actor_id=provisional.actor_id,
        action=provisional.action,
        input_hash=provisional.input_hash,
        evidence_hashes=provisional.evidence_hashes,
        decision=provisional.decision,
        decision_hash=provisional.decision_hash,
        execution_result_hash=provisional.execution_result_hash,
        previous_receipt_hash=provisional.previous_receipt_hash,
        timestamp=provisional.timestamp,
        signature=sig,
        state_version=provisional.state_version,
    )


# ── Store ────────────────────────────────────────────────────────────────


class ReceiptStore:
    """Append-only, signed, hash-chained receipt ledger."""

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        secret: bytes | None = None,
    ) -> None:
        if path is None:
            path = os.getenv("ARIFOS_RECEIPT_PATH", DEFAULT_RECEIPT_PATH)
        self.path = Path(path)
        self.secret = secret if secret is not None else _default_secret()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

    def append(self, receipt: Receipt) -> Receipt:
        """Append a receipt. Returns the same receipt for chaining."""
        # Idempotent: if the same receipt_id is already present, return it.
        if self._find_by_id(receipt.receipt_id) is not None:
            return receipt
        line = json.dumps(receipt.to_dict(), sort_keys=True) + "\n"
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line)
        return receipt

    def get(self, receipt_id: str) -> Receipt | None:
        record = self._find_by_id(receipt_id)
        if record is None:
            return None
        return _record_to_receipt(record)

    def latest(self) -> Receipt | None:
        """The most recently appended receipt (for chain extension)."""
        if not self.path.exists():
            return None
        last_line = None
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last_line = line
        if last_line is None:
            return None
        return _record_to_receipt(json.loads(last_line))

    def all_receipts(self) -> tuple[Receipt, ...]:
        if not self.path.exists():
            return ()
        out: list[Receipt] = []
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    out.append(_record_to_receipt(record))
                except (json.JSONDecodeError, ValueError, KeyError):
                    continue
        return tuple(out)

    def verify_chain(self) -> tuple[bool, str]:
        """Verify the entire chain: every signature is valid, and each
        receipt's previous_receipt_hash matches the previous receipt's
        canonical hash.

        Returns (ok, reason). reason is "" on success.
        """
        if not self.path.exists():
            return (True, "")
        prev_hash = GENESIS_PREVIOUS_HASH
        for i, receipt in enumerate(self.all_receipts()):
            # Verify the signature.
            expected_sig = _sign_receipt(receipt, self.secret)
            if not hmac.compare_digest(expected_sig, receipt.signature):
                return (False, f"signature_invalid at index {i} (id={receipt.receipt_id})")
            # Verify the chain link.
            if receipt.previous_receipt_hash != prev_hash:
                return (
                    False,
                    f"chain_broken at index {i} (id={receipt.receipt_id}): "
                    f"expected previous={prev_hash[:12]}..., "
                    f"got {receipt.previous_receipt_hash[:12]}...",
                )
            prev_hash = _canonical_hash(_signing_payload(receipt))
        return (True, "")

    def verify_one(self, receipt: Receipt) -> tuple[bool, str]:
        """Verify a single receipt's signature."""
        expected_sig = _sign_receipt(receipt, self.secret)
        if not hmac.compare_digest(expected_sig, receipt.signature):
            return (False, "signature_invalid")
        return (True, "")

    def by_trace_id(self, trace_id: str) -> tuple[Receipt, ...]:
        """All receipts sharing the same trace_id, in append order.

        The audit's Item 5: trace propagation must let an operator pull
        every action that happened under one trace, from durable records
        alone.
        """
        return tuple(
            receipt for receipt in self.all_receipts()
            if receipt.trace_id == trace_id
        )

    def by_run_id(self, run_id: str) -> tuple[Receipt, ...]:
        """All receipts sharing the same run_id, in append order."""
        return tuple(
            receipt for receipt in self.all_receipts()
            if receipt.run_id == run_id
        )

    def replay(self, receipt_id: str) -> dict[str, Any] | None:
        """Reconstruct the decision sequence for a run, given a receipt id.

        Returns a dict describing the reconstructed run, or None if the
        receipt is not found. The reconstruction uses only durable
        records (the receipt and the hash chain). No mutable logs, no
        in-memory state.
        """
        target = self.get(receipt_id)
        if target is None:
            return None
        # Walk back through the chain: each receipt's previous_receipt_hash
        # is the canonical hash of the prior receipt. Find the first
        # receipt in this chain.
        all_in_order = self.all_receipts()
        # Find the index of the target receipt.
        try:
            target_idx = next(
                i for i, r in enumerate(all_in_order)
                if r.receipt_id == receipt_id
            )
        except StopIteration:
            return None
        # Walk backward to the start of this run.
        # Two receipts belong to the same run if they share run_id.
        run_receipts: list[Receipt] = []
        for i in range(target_idx, -1, -1):
            r = all_in_order[i]
            if r.run_id == target.run_id:
                run_receipts.append(r)
            else:
                break
        run_receipts.reverse()
        return {
            "run_id": target.run_id,
            "receipts": [r.to_dict() for r in run_receipts],
            "decision_sequence": [r.decision for r in run_receipts],
            "first_receipt_id": run_receipts[0].receipt_id if run_receipts else None,
            "last_receipt_id": target.receipt_id,
        }

    def _find_by_id(self, receipt_id: str) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        with open(self.path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("receipt_id") == receipt_id:
                    return record
        return None


def _record_to_receipt(record: dict[str, Any]) -> Receipt:
    """Reconstruct a Receipt from a stored JSONL record."""
    return Receipt(
        receipt_id=record["receipt_id"],
        run_id=record["run_id"],
        trace_id=record["trace_id"],
        session_id=record["session_id"],
        actor_id=record["actor_id"],
        action=record["action"],
        input_hash=record["input_hash"],
        evidence_hashes=tuple(record.get("evidence_hashes", ())),
        decision=record["decision"],
        decision_hash=record["decision_hash"],
        execution_result_hash=record["execution_result_hash"],
        previous_receipt_hash=record["previous_receipt_hash"],
        timestamp=record["timestamp"],
        signature=record["signature"],
        state_version=record.get("state_version", RECEIPT_STATE_VERSION),
    )


__all__ = [
    "RECEIPT_STATE_VERSION",
    "DEFAULT_RECEIPT_PATH",
    "GENESIS_PREVIOUS_HASH",
    "Receipt",
    "ReceiptStore",
    "make_receipt",
    "_canonical_hash",
    "_sign_receipt",
    "_record_to_receipt",
]
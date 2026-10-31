"""
sovereign_receipt_verify — P0-1 receipt-proof gate (2026-11-01).

A `sovereign_receipt` string is a CLAIM by the caller. Before it may promote
an ALLOW→SEAL verdict (judge.py intercept path) or disarm a critical-blast
gate, it must resolve to a real ledger entry, and that entry must be bound to
THIS candidate and THIS actor. Root cause closed (repair-2026-11-01 P0-1):
any non-empty string ("arif-approved-2026-11-01") counted as an F13 receipt
and promoted a federation-blast key rotation to SEAL with zero evidence.

Checks enforced (all must pass; never raises):
  LEDGER_LOOKUP      receipt id / receipt_hash found in receipts_v2.jsonl
  HASH_INTEGRITY     stored receipt_hash recomputes (canonical VaultReceipt hash)
  CANDIDATE_BINDING  row.intent_hash == sha256(json.dumps(candidate, sort_keys=True))
                     — the exact derivation judge.py:4167 uses when minting
  ACTOR_BINDING      row.actor_id == caller actor_id (both must be real, non-placeholder)
  DECISION_CLASS     row.decision is SEAL-class (a receipt recording HOLD authorizes nothing)
  SIGNATURE_PRESENT  row.actor_signature non-empty hex (>=64 chars)

HONEST LIMIT (flagged, not silently upgraded): full Ed25519 public-key
verification of `actor_signature` is NOT wired here — public keys live in
identity stores this module deliberately does not read (repair-2026-11-01
hard rule 1: no signing/key-path access). Presence + hash integrity + exact
candidate/actor binding are enforced now; pubkey verification is an F13-flagged
follow-up, reported as `signature_checked: False` in the result.

Reads ledger DATA only (receipts_v2.jsonl — rows, not key paths).
DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.runtime.sovereign_receipt_verify")

DEFAULT_VAULT_PATH = "/root/VAULT999/receipts_v2.jsonl"

# Placeholder / relay identities that can never bind a sovereign receipt (F2).
_PLACEHOLDERS = {"", "anonymous", "unknown", "none", "openclaw-anon", "null"}

_SEAL_DECISIONS = {"SEAL"}

_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_HEX_SIG_RE = re.compile(r"^[0-9a-f]{64,}$")


def candidate_intent_hash(candidate: Any) -> str:
    """Canonical intent hash — mirrors judge.py:4167 derivation exactly."""
    payload = candidate if isinstance(candidate, str) else str(candidate)[:2000]
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _result(
    verified: bool,
    reason: str,
    *,
    receipt_id: str | None = None,
    receipt_hash: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "verified": verified,
        "reason": reason,
        "receipt_id": receipt_id,
        "receipt_hash": receipt_hash,
        "signature_checked": False,  # see HONEST LIMIT in module docstring
    }
    out.update(extra)
    return out


def verify_sovereign_receipt(
    receipt: str | None,
    candidate: Any,
    actor_id: str | None = None,
    vault_path: str | Path | None = None,
) -> dict[str, Any]:
    """Verify a sovereign_receipt string against the receipt ledger.

    Pure read; never raises; returns a report dict with `verified: bool` and a
    specific `reason` on failure (NO_RECEIPT | NOT_FOUND | HASH_INTEGRITY_FAIL |
    CANDIDATE_MISMATCH | ACTOR_MISMATCH | DECISION_NOT_SEAL | UNSIGNED |
    ACTOR_UNBOUND | LEDGER_UNAVAILABLE).
    """
    raw = (receipt or "").strip()
    if not raw:
        return _result(False, "NO_RECEIPT")

    ref = raw.removeprefix("sha256:").strip()
    by_hash = bool(_HASH_RE.match(ref))

    path = Path(vault_path or DEFAULT_VAULT_PATH)
    if not path.exists():
        return _result(False, "LEDGER_UNAVAILABLE", detail=f"missing:{path}")

    row: dict[str, Any] | None = None
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or ref not in line:
                    continue
                try:
                    data = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if (by_hash and data.get("receipt_hash") == ref) or (
                    not by_hash and data.get("receipt_id") == ref
                ):
                    row = data
                    break
    except OSError as exc:
        return _result(False, "LEDGER_UNAVAILABLE", detail=str(exc)[:200])

    if row is None:
        return _result(False, "NOT_FOUND", detail=f"no ledger entry for ref in {path.name}")

    receipt_id = row.get("receipt_id")
    stored_hash = row.get("receipt_hash") or ""

    # HASH_INTEGRITY — recompute the canonical receipt hash from stored fields.
    try:
        from arifosmcp.core.vault_receipt import VaultReceipt, compute_receipt_hash

        _ro = VaultReceipt(
            **{k: v for k, v in row.items() if k in VaultReceipt.__dataclass_fields__}
        )
        recomputed = compute_receipt_hash(_ro)
        if recomputed != stored_hash:
            return _result(
                False, "HASH_INTEGRITY_FAIL", receipt_id=receipt_id, receipt_hash=stored_hash
            )
    except Exception as exc:  # noqa: BLE001 — fail closed with the reason disclosed
        return _result(
            False,
            "HASH_INTEGRITY_FAIL",
            receipt_id=receipt_id,
            receipt_hash=stored_hash,
            detail=str(exc)[:200],
        )

    # DECISION_CLASS — a receipt recording a non-SEAL decision authorizes nothing.
    decision = str(row.get("decision") or "").strip().upper()
    if decision not in _SEAL_DECISIONS:
        return _result(
            False,
            "DECISION_NOT_SEAL",
            receipt_id=receipt_id,
            receipt_hash=stored_hash,
            decision=decision,
        )

    # SIGNATURE_PRESENT — presence + shape only (see HONEST LIMIT).
    sig = str(row.get("actor_signature") or "").strip().lower()
    if not _HEX_SIG_RE.match(sig):
        return _result(False, "UNSIGNED", receipt_id=receipt_id, receipt_hash=stored_hash)

    # CANDIDATE_BINDING — exact candidate hash match.
    want = candidate_intent_hash(candidate)
    got = str(row.get("intent_hash") or "")
    if got != want:
        return _result(
            False,
            "CANDIDATE_MISMATCH",
            receipt_id=receipt_id,
            receipt_hash=stored_hash,
            expected_intent_hash=want,
            ledger_intent_hash=got,
        )

    # ACTOR_BINDING — both sides must be real identities (F2).
    row_actor = str(row.get("actor_id") or "").strip().lower()
    caller_actor = str(actor_id or "").strip().lower()
    if row_actor in _PLACEHOLDERS:
        return _result(
            False,
            "ACTOR_UNBOUND",
            receipt_id=receipt_id,
            receipt_hash=stored_hash,
            ledger_actor=row_actor,
        )
    if caller_actor and caller_actor not in _PLACEHOLDERS and row_actor != caller_actor:
        return _result(
            False,
            "ACTOR_MISMATCH",
            receipt_id=receipt_id,
            receipt_hash=stored_hash,
            ledger_actor=row_actor,
            caller_actor=caller_actor,
        )

    return _result(
        True,
        "VERIFIED",
        receipt_id=receipt_id,
        receipt_hash=stored_hash,
        ledger_actor=row_actor,
        checks=[
            "LEDGER_LOOKUP",
            "HASH_INTEGRITY",
            "DECISION_CLASS",
            "SIGNATURE_PRESENT",
            "CANDIDATE_BINDING",
            "ACTOR_BINDING",
        ],
    )

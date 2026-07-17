"""
BRIDGING_SEAL — sovereign override of identity gates with Ed25519.

CONSTITUTIONAL CONSTRAINTS (HARD-CODED, F1/F2/F11):

  1. actor_verified STAYS FALSE. Only actor_override toggles true.
     BRIDGING_SEAL never lies about verification status (F2 TRUTH).

  2. Every BRIDGING_SEAL MUST emit a VAULT999 entry BEFORE the gated
     action is allowed. Audit-first, action-second (F11 AUDIT).

  3. TTL = 900 seconds (15 minutes) OR single_use; whichever expires
     first. There is no standing override (F13 SOVEREIGN — bounded).

  4. FAIL-CLOSED: if VAULT999 is unreachable, BRIDGING_SEAL is refused.
     No fallback bypass. Identity gate stays elevated.

REAL IMPLEMENTATION — Ed25519 sign/verify + VAULT999 persistence.

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
Real crypto landed by FORGE (000Ω), 2026-07-08.
DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.exceptions import InvalidSignature

# ─── Key paths ────────────────────────────────────────────────────────────────

_SECRETS_DIR = Path("/opt/arifos/secrets")
_PRIVATE_KEY_PATH = _SECRETS_DIR / "did_arifos_private.key"
_PUBLIC_KEY_PATH = _SECRETS_DIR / "did_arifos_public.key"

# In-memory consumed seal cache (single-process; reset on restart)
_consumed_seals: set[str] = set()


# ─── Interfaces ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class BridgingSealRequest:
    """Request to bypass L1_IDENTITY gate under sovereign authorization.

    sovereign_authorization: F13 textual ack from Arif ("yes do X")
    intent: human-readable description of the action this seal enables
    ttl_seconds: max 3600 (1 hour), default 900 (15 min) — F13 bounded
    single_use: if True, seal is consumed on first use; default True
    """

    sovereign_authorization: str
    intent: str
    ttl_seconds: int = 900
    single_use: bool = True

    def __post_init__(self) -> None:
        if self.ttl_seconds <= 0 or self.ttl_seconds > 3600:
            raise ValueError(
                f"BRIDGING_SEAL ttl_seconds must be in (0, 3600], got {self.ttl_seconds}"
            )
        if not self.sovereign_authorization.strip():
            raise ValueError("BRIDGING_SEAL requires sovereign_authorization (F13)")
        if not self.intent.strip():
            raise ValueError("BRIDGING_SEAL requires intent (F11 AUDIT)")


@dataclass(frozen=True)
class BridgingSealReceipt:
    """Receipt returned by request_bridging_seal.

    seal_id: VAULT999 sequence id that anchors this seal
    epoch: when the seal was minted
    expires_at: action denied after this instant
    actor_override: True (only this field toggles; actor_verified stays False)
    sovereign_signature: Ed25519 signature over the seal payload
    consumed: True after first use (single_use=True)
    """

    seal_id: str
    epoch: datetime
    expires_at: datetime
    actor_override: bool
    sovereign_signature: str
    consumed: bool = False

    @property
    def is_expired(self) -> bool:
        """Predicate: has the TTL elapsed? Used at verify time."""
        return datetime.now(UTC) >= self.expires_at


# ─── Key helpers ──────────────────────────────────────────────────────────────


def _load_private_key() -> Ed25519PrivateKey:
    pem = _PRIVATE_KEY_PATH.read_bytes()
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError(f"Expected Ed25519PrivateKey, got {type(key).__name__}")
    return key


def _load_public_key() -> Ed25519PublicKey:
    pem = _PUBLIC_KEY_PATH.read_bytes()
    key = serialization.load_pem_public_key(pem)
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError(f"Expected Ed25519PublicKey, got {type(key).__name__}")
    return key


def _sign_payload(payload: str) -> str:
    """Sign payload string with sovereign Ed25519 private key. Returns hex."""
    sig = _load_private_key().sign(payload.encode())
    return sig.hex()


def _verify_signature(payload: str, signature_hex: str) -> bool:
    """Verify Ed25519 signature. Returns True if valid, False otherwise."""
    try:
        sig = bytes.fromhex(signature_hex)
        _load_public_key().verify(sig, payload.encode())
        return True
    except (InvalidSignature, ValueError, Exception):
        return False


# ─── VAULT999 persistence ─────────────────────────────────────────────────────

_VAULT_DIR = Path("/root/arifOS/arifosmcp/VAULT999")
_VAULT_LEDGER = _VAULT_DIR / "outcomes.jsonl"


def _vault_append(entry: dict) -> str:
    """Append to VAULT999 ledger. Returns sequence id.

    FAIL-CLOSED: raises if vault unreachable (F1 AMANAH).
    """
    _VAULT_DIR.mkdir(parents=True, exist_ok=True)

    # Compute next sequence id
    seq = 0
    if _VAULT_LEDGER.exists():
        with open(_VAULT_LEDGER) as f:
            for line in f:
                if line.strip():
                    try:
                        existing = json.loads(line)
                        seq = max(seq, existing.get("seq", 0) + 1)
                    except json.JSONDecodeError:
                        continue

    entry["seq"] = seq
    entry["timestamp"] = datetime.now(UTC).isoformat()

    with open(_VAULT_LEDGER, "a") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")

    return str(seq)


# ─── Real implementations ─────────────────────────────────────────────────────


def request_bridging_seal(req: BridgingSealRequest) -> BridgingSealReceipt:
    """Mint a BRIDGING_SEAL receipt with real Ed25519 signing.

    1. Persist (req.intent, req.sovereign_authorization, req.ttl_seconds,
       req.single_use) to VAULT999
    2. Sign the persisted record with sovereign Ed25519 key
    3. Return receipt whose seal_id is the VAULT999 sequence number
    4. Mark actor_override=True; never set actor_verified=True
    """
    now = datetime.now(UTC)
    expires_at = now + timedelta(seconds=req.ttl_seconds)

    # Build vault entry
    vault_entry = {
        "type": "BRIDGING_SEAL",
        "intent": req.intent,
        "sovereign_authorization_hash": hashlib.sha256(
            req.sovereign_authorization.encode()
        ).hexdigest(),
        "ttl_seconds": req.ttl_seconds,
        "single_use": req.single_use,
        "epoch": now.isoformat(),
        "expires_at": expires_at.isoformat(),
    }

    # Sign the vault entry BEFORE appending to VAULT999
    # (vault_append mutates the dict in-place, adding seq — if we sign after,
    # the signed payload includes seq but verification strips it)
    payload = json.dumps(vault_entry, sort_keys=True)
    signature = _sign_payload(payload)

    # Persist to VAULT999 (fail-closed if unreachable)
    seal_id = _vault_append(vault_entry)

    return BridgingSealReceipt(
        seal_id=seal_id,
        epoch=now,
        expires_at=expires_at,
        actor_override=True,
        sovereign_signature=signature,
        consumed=False,
    )


def verify_bridging_seal(
    receipt: BridgingSealReceipt,
    current_epoch: datetime | None = None,
) -> bool:
    """Verify a BRIDGING_SEAL receipt with real Ed25519 verification.

    1. Read VAULT999 entry by receipt.seal_id; verify it exists
    2. Verify sovereign_signature against sovereign public key
    3. Verify current_epoch < receipt.expires_at
    4. If receipt.single_use AND receipt.consumed, deny
    5. Return True only if all 4 pass; else False

    Reject immediately (return False, do NOT raise) on malformed input —
    the gate must remain fail-closed.
    """
    if current_epoch is None:
        current_epoch = datetime.now(UTC)

    # Check 3: TTL
    if current_epoch >= receipt.expires_at:
        return False

    # Check 4: single_use consumed
    if receipt.seal_id in _consumed_seals:
        return False

    # Check 1: read vault entry
    if not _VAULT_LEDGER.exists():
        return False

    vault_entry = None
    try:
        with open(_VAULT_LEDGER) as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if str(entry.get("seq")) == receipt.seal_id:
                        vault_entry = entry
                        break
    except (json.JSONDecodeError, IOError):
        return False

    if vault_entry is None:
        return False

    # Check 2: verify signature
    payload = json.dumps(
        {k: v for k, v in vault_entry.items() if k not in ("seq", "timestamp")},
        sort_keys=True,
    )
    if not _verify_signature(payload, receipt.sovereign_signature):
        return False

    # Mark consumed if single_use or already consumed
    if receipt.consumed or getattr(receipt, "_consumed", False):
        _consumed_seals.add(receipt.seal_id)

    # Always mark as seen — replay protection for all seals
    if receipt.seal_id not in _consumed_seals:
        _consumed_seals.add(receipt.seal_id)

    return True


def mark_consumed(seal_id: str) -> None:
    """Mark a seal as consumed (for single_use enforcement)."""
    _consumed_seals.add(seal_id)


# ─── Helpers (real; usable today) ────────────────────────────────────────────


def ttl_default_seconds() -> int:
    """The constitutional default TTL: 15 minutes."""
    return 900


def max_ttl_seconds() -> int:
    """The constitutional max TTL: 1 hour."""
    return 3600


def estimated_expiry(req: BridgingSealRequest, start_epoch: datetime | None = None) -> datetime:
    """Compute expires_at for a request. Doesn't mint a seal — just arithmetic."""
    if start_epoch is None:
        start_epoch = datetime.now(UTC)
    return start_epoch + timedelta(seconds=req.ttl_seconds)

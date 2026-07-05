"""
BRIDGING_SEAL — sovereign override of identity gates.

CONSTITUTIONAL CONSTRAINTS (HARD-CODED, F1/F2/F11):

  1. actor_verified STAYS FALSE. Only actor_override toggles true.
     BRIDGING_SEAL never lies about verification status (F2 TRUTH).

  2. Every BRIDGING_SEAL MUST emit a VAULT999 entry BEFORE the gated
     action is allowed. Audit-first, action-second (F11 AUDIT).

  3. TTL = 900 seconds (15 minutes) OR single_use; whichever expires
     first. There is no standing override (F13 SOVEREIGN — bounded).

  4. FAIL-CLOSED: if VAULT999 is unreachable, BRIDGING_SEAL is refused.
     No fallback bypass. Identity gate stays elevated.

INTERFACE STUB ONLY — bodies raise NotImplementedError.

When real Ed25519 lands:

  def request_bridging_seal(req: BridgingSealRequest) -> BridgingSealReceipt:
      # Sign req.intent with sovereign Ed25519 key (from /opt/arifos/secrets/)
      # Persist signing payload to VAULT999 via arif_seal
      # Return receipt with seal_id linking back to vault entry

  def verify_bridging_seal(receipt, current_epoch) -> bool:
      # Read signed payload from VAULT999 by seal_id
      # Verify signature with sovereign public key
      # Check current_epoch < expires_at_epoch
      # Check single_use flag if so

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


# ─── Interfaces (stable; bodies are stubs) ────────────────────────────────────


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
    sovereign_signature: F13 sig, ALG_PLACEHOLDER_ED25519_REPLACE_BEFORE_PROD
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


# ─── Stub bodies ─────────────────────────────────────────────────────────────


def request_bridging_seal(req: BridgingSealRequest) -> BridgingSealReceipt:
    """Mint a BRIDGING_SEAL receipt. STUB — raises NotImplementedError.

    Real impl must:
      1. Persist `(req.intent, req.sovereign_authorization, req.ttl_seconds,
         req.single_use)` to VAULT999 via arif_seal
      2. Sign the persisted record with sovereign Ed25519 key
      3. Return receipt whose seal_id is the VAULT999 sequence number
      4. Mark actor_override=True; never set actor_verified=True
    """
    raise NotImplementedError(
        "BRIDGING_SEAL stub — replace with real Ed25519 sign + VAULT999 persist. "
        "See /root/arifOS/arifosmcp/runtime/identity/STUB_STATUS.md"
    )


def verify_bridging_seal(
    receipt: BridgingSealReceipt,
    current_epoch: datetime | None = None,
) -> bool:
    """Verify a BRIDGING_SEAL receipt. STUB — raises NotImplementedError.

    Real impl must:
      1. Read VAULT999 entry by receipt.seal_id; verify it exists
      2. Verify sovereign_signature against sovereign public key
      3. Verify current_epoch < receipt.expires_at
      4. If receipt.single_use AND receipt.consumed, deny
      5. Return True only if all 4 pass; else False

    Reject immediately (return False, do NOT raise) on malformed input —
    the gate must remain fail-closed.
    """
    raise NotImplementedError(
        "BRIDGING_SEAL stub — replace with Ed25519 verify + VAULT999 lookup. "
        "See /root/arifOS/arifosmcp/runtime/identity/STUB_STATUS.md"
    )


# ─── Helpers (real; usable today) ────────────────────────────────────────────


def ttl_default_seconds() -> int:
    """The constitutional default TTL: 15 minutes."""
    return 900


def max_ttl_seconds() -> int:
    """The constitutional max TTL: 1 hour."""
    return 3600


def estimated_expiry(req: BridgingSealRequest, start_epoch: datetime | None = None) -> datetime:
    """Compute expires_at for a request. Doesn't mint a seal — just arithmetic.

    Useful for UI/explainer surfaces that need to show "this seal will expire at..."
    """
    if start_epoch is None:
        start_epoch = datetime.now(UTC)
    return start_epoch + timedelta(seconds=req.ttl_seconds)

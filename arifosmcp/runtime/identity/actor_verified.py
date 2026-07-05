"""
actor_verified interface — canonical abstraction for "is this actor trusted?".

REPLACES today's scattered `actor_verified: false` literals everywhere with one
interface. Every code path that today says `if not verified: deny` should use
this interface instead.

CONSTITUTIONAL CONSTRAINTS:

  - `verified` is hard-locked to False until real crypto lands.
  - The ONLY way to bypass the L1_IDENTITY gate is `bridge_seal_id`
    (a valid BRIDGING_SEAL receipt). This sets `actor_override=True` —
    NOT `verified=True`. We never lie about verification status (F2 TRUTH).

  - If neither crypto nor bridge_seal is present, is_authorized returns False.
    Default-deny.

INTERFACE STUB — the constructor is real (state can be set), but
is_authorized() will return False until both verified=True (impossible
without real crypto) and a fresh bridge_seal_id are present.

The reason: even with a bridge_seal, is_authorized() should verify TTL
through verify_bridging_seal(). Until real Ed25519 lands, verify() raises,
which the user catches as "not authorized" — the safe default.

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class ActorVerifiedState(Enum):
    """Tri-state for actor identity."""

    UNVERIFIED = "UNVERIFIED"            # default; L1_IDENTITY gate denies
    BRIDGED = "BRIDGED"                 # BRIDGING_SEAL active; actor_override=True
    VERIFIED = "VERIFIED"               # real crypto (NOT IMPLEMENTED today)


# Default expiry in the past so the bridge path always denies in stub mode.
# Defined before the class so `field(default_factory=...)` can resolve it
# when the dataclass decorator runs.
def _epoch_default_expired() -> datetime:
    return datetime(1970, 1, 1, tzinfo=UTC)


@dataclass
class ActorVerified:
    """Canonical actor identity state.

    Single import point. Every L1_IDENTITY gate in the federation should
    ask this object instead of parsing ad-hoc fields.

    Fields:
      state: tri-state per ActorVerifiedState
      verified: True iff state == VERIFIED (requires real crypto)
      bridge_seal_id: VAULT999 sequence id of an active BRIDGING_SEAL receipt
      verified_at_epoch: when crypto verified (None = never)
      bridge_consumed_at_epoch: when bridge seal was first used (None = unused)
      expires_at_epoch: when bridge seal expires (default: now() - 1s = already expired)
      actor_id: identity claim string (the sovereign DID, etc.)
    """

    actor_id: str = ""
    state: ActorVerifiedState = ActorVerifiedState.UNVERIFIED
    verified: bool = False
    bridge_seal_id: str | None = None
    verified_at_epoch: datetime | None = None
    bridge_consumed_at_epoch: datetime | None = None
    expires_at_epoch: datetime = field(default_factory=_epoch_default_expired)

    def is_authorized(self, current_epoch: datetime | None = None) -> bool:
        """Default-deny predicate. Returns True iff actor may act.

        Logic:
          - If state == VERIFIED and not expired → True (real crypto path)
          - Else if state == BRIDGED and bridge_seal_id present
                and current_epoch < expires_at_epoch
                and not consumed OR single_use=False → True (bridge path)
          - Else → False (deny)

        Today's implementation: state is NEVER VERIFIED (crypto absent);
        state can be BRIDGED only via the real bridge_seal() function.
        Until real Ed25519 lands and verify_bridging_seal() works,
        is_authorized always returns False.
        """
        if current_epoch is None:
            current_epoch = datetime.now(UTC)

        if self.state == ActorVerifiedState.VERIFIED and self.verified:
            return True

        if self.state == ActorVerifiedState.BRIDGED and self.bridge_seal_id:
            if current_epoch >= self.expires_at_epoch:
                return False
            # NOTE: a real impl would call verify_bridging_seal() here.
            # Until that works, conservatively return False.
            try:
                from arifosmcp.runtime.identity.bridging_seal import (
                    verify_bridging_seal,
                )
                # In stub world, this raises NotImplementedError → caught → False.
                from arifosmcp.runtime.identity.bridging_seal import (
                    BridgingSealReceipt,
                )
                # If a real receipt exists in caller scope, they pass it explicitly.
                # Our interface can only check the local state.
                _ = verify_bridging_seal  # touch import for linter
                _ = BridgingSealReceipt
                # Without a real receipt object, can't fully verify — be safe.
                return False
            except NotImplementedError:
                return False

        return False

    def to_dict(self) -> dict:
        """Serialisable snapshot for receipt emission."""
        return {
            "actor_id": self.actor_id,
            "state": self.state.value,
            "verified": self.verified,
            "bridge_seal_id": self.bridge_seal_id,
            "verified_at_epoch": (
                self.verified_at_epoch.isoformat() if self.verified_at_epoch else None
            ),
            "bridge_consumed_at_epoch": (
                self.bridge_consumed_at_epoch.isoformat()
                if self.bridge_consumed_at_epoch
                else None
            ),
            "expires_at_epoch": self.expires_at_epoch.isoformat(),
            "note_if_unverified": (
                "actor_verified stays False until real Ed25519 lands. "
                "Bridge seal alone does NOT toggle verified=True (F2 TRUTH)."
            ),
        }


# Default expiry function now defined ABOVE the class (see top of file).

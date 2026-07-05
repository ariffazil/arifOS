"""
arifosmcp/runtime/identity — STUB ONLY as of 2026-07-05.

Real crypto (Ed25519 verification, JWT, DPoP) is NOT IMPLEMENTED.
This package provides clean interfaces; raising NotImplementedError is the contract.

The constitutional design requires:
  - actor_verified stays FALSE until real crypto lands
  - BRIDGING_SEAL toggles actor_override (NOT actor_verified) when sovereign acts
  - Every call path that hits L1_IDENTITY gate is fail-closed

Submodules:
  - bridging_seal  : sovereign override of identity gates (STUB)
  - jwt_dpop       : JWT encode/decode + DPoP proof (STUB)
  - actor_verified : single canonical interface for "is this actor trusted?"
  - STUB_STATUS.md : human-readable map of what needs implementation

When real crypto lands:
  1. Replace the bodies of the four stub functions with real Ed25519 code.
  2. Replace _STUB_ALG constant in jwt_dpop.py with a real signing key derived
     from the rotated sovereign Ed25519 keypair (see /opt/arifos/secrets/).
  3. Update AGENTS.md to remove the "no real crypto yet" disclaimer.
  4. Run conformance spine — must stay 9/9 PASS.

Forged by Kimi Code (FI-008) under F13 SOVEREIGN directive, 2026-07-05.
DITEMPA BUKAN DIBERI.
"""

from .actor_verified import (
    ActorVerified,
    ActorVerifiedState,
)
from .bridging_seal import (
    BridgingSealRequest,
    BridgingSealReceipt,
    request_bridging_seal,
    verify_bridging_seal,
)
from .jwt_dpop import (
    encode_jwt,
    decode_jwt,
    make_dpop_proof,
    verify_dpop_proof,
)

__all__ = [
    "ActorVerified",
    "ActorVerifiedState",
    "BridgingSealRequest",
    "BridgingSealReceipt",
    "request_bridging_seal",
    "verify_bridging_seal",
    "encode_jwt",
    "decode_jwt",
    "make_dpop_proof",
    "verify_dpop_proof",
]

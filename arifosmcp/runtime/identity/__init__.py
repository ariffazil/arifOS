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
    # Temporary bridge for health + rest_routes until full reconcile with legacy identity.py
    "get_identity",
    "get_identity_hash",
    "get_identity_b3_hash",
]

# --- Temporary identity bridge (from legacy runtime/identity.py) ---
# Real implementation lives in runtime/identity.py but is shadowed by this package dir.
# Minimal port here to unblock /health and REST registration. Honest stub per F2.
import hashlib
import os
from pathlib import Path
from typing import Any

try:
    import blake3 as _b3
    _HAS_B3 = True
except ImportError:
    _HAS_B3 = False

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

IDENTITY_TOML_PATH = Path("/opt/arifos/app/identity.toml")
_cached_identity: dict[str, Any] | None = None

def _load_identity_toml() -> dict[str, Any]:
    global _cached_identity
    if _cached_identity is not None:
        return _cached_identity
    try:
        with open(IDENTITY_TOML_PATH, "rb") as f:
            _cached_identity = tomllib.load(f)
        return _cached_identity
    except Exception:
        return {
            "agent_id": "arifos",
            "display_name": "arifOS",
            "owner": "Muhammad Arif bin Fazil",
            "canonical_commit": os.environ.get("ARIFOS_GIT_COMMIT", "unknown")[:7],
            "identity_marker": "arifos-sovereign-runtime",
            "forbidden_self_names": ["Grok", "OpenClaw", "Claude", "Gemini", "ChatGPT"],
            "boot_attestation": True,
            "vault999_required": True,
            "runtime_drift_allowed": False,
            "a2a": {"enabled": True},
        }

def get_identity(running_commit: str = "unknown") -> dict[str, Any]:
    identity = _load_identity_toml()
    return {
        "agent_id": identity.get("agent_id", "arifos"),
        "display_name": identity.get("display_name", "arifOS"),
        "owner": identity.get("owner", "Muhammad Arif bin Fazil"),
        "domain": identity.get("domain", "aaa.arif-fazil.com"),
        "canonical_commit": identity.get("canonical_commit", running_commit),
        "running_commit": running_commit,
        "identity_marker": identity.get("identity_marker", "arifos-sovereign-runtime"),
        "forbidden_self_names": identity.get("forbidden_self_names", []),
        "boot_attestation": identity.get("boot_attestation", True),
        "vault999_required": identity.get("vault999_required", True),
        "runtime_drift_allowed": identity.get("runtime_drift_allowed", False),
        "source": "identity.toml (stub bridge)",
        "status": "healthy",
    }

def get_identity_hash() -> str:
    identity = _load_identity_toml()
    payload = (
        f"{identity.get('agent_id', 'arifos')}"
        f"|{identity.get('canonical_commit', '')}"
        f"|{identity.get('identity_marker', 'arifos-sovereign-runtime')}"
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]

def get_identity_b3_hash() -> dict[str, Any]:
    try:
        with open(IDENTITY_TOML_PATH, "rb") as f:
            content = f.read()
        if _HAS_B3:
            b3_hash = _b3.blake3(content).hexdigest()
        else:
            b3_hash = hashlib.blake2b(content, digest_size=32).hexdigest()
        return {"algorithm": "blake3" if _HAS_B3 else "blake2b", "source": str(IDENTITY_TOML_PATH), "hash": b3_hash}
    except Exception:
        return {"algorithm": "blake2b", "source": "fallback", "hash": hashlib.blake2b(b"arifos-stub", digest_size=32).hexdigest()}


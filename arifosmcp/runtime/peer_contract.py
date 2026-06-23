"""
Peer Federation Contract runtime — arifOS side.

Implements:
  - Loading and serving the canonical arifOS peer contract
  - Validating inbound peer contracts against the Pydantic schema
  - Enforcing constitutional constraints (judge exclusivity, F13 veto, lease rules)
  - Peer forbidding / unforbidding

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
from typing import Any

from arifosmcp.schemas.peer_federation_contract import (
    AuthorityClass,
    PeerFederationContract,
)

# Stable public URL for the arifOS peer contract.
PEER_CONTRACT_URL = os.getenv(
    "ARIFOS_PEER_CONTRACT_URL",
    "https://arifos.arif-fazil.com/.well-known/peer-contract.json",
)

# Canonical on-disk locations, in priority order.
_PEER_CONTRACT_PATHS = (
    "/root/arifOS/static/.well-known/peer-contract.json",
    "/opt/arifos/app/static/.well-known/peer-contract.json",
    "/root/AAA/a2a/peer-contracts/arifos-kernel.json",
)

# Runtime forbidden-organ registry.
_FORBIDDEN_PEERS: set[str] = set()


def _sha256_of_text(text: str) -> str:
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def _load_contract_dict() -> dict[str, Any]:
    """Load the canonical arifOS peer contract dict from disk."""
    for path in _PEER_CONTRACT_PATHS:
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                return json.load(f)
    raise FileNotFoundError("arifOS peer contract not found on disk")


def get_arifos_peer_contract_url() -> str:
    """Return the public URL where the arifOS peer contract is discoverable."""
    return PEER_CONTRACT_URL


def get_arifos_peer_contract() -> PeerFederationContract:
    """Return the canonical arifOS peer contract as a validated Pydantic model."""
    return PeerFederationContract.model_validate(_load_contract_dict())


def get_arifos_peer_contract_hash() -> str:
    """Return a deterministic SHA-256 hash of the canonical contract dict."""
    return _sha256_of_text(json.dumps(_load_contract_dict(), sort_keys=True))


def is_peer_forbidden(organ: str) -> bool:
    """Check whether a peer organ has been forbidden from federation."""
    return organ in _FORBIDDEN_PEERS


def _enforce_constitutional_constraints(
    contract: PeerFederationContract,
) -> list[str]:
    """Return a list of human-readable constraint violations, or empty if clean."""
    errors: list[str] = []
    organ = contract.peer_id.organ

    # F13 SOVEREIGN: only arifOS may hold judge authority.
    if contract.authority_class == AuthorityClass.JUDGE and organ != "arifOS":
        errors.append(f"authority_class 'judge' is exclusive to arifOS; found organ '{organ}'")

    # F1 AMANAH: non-judge peers must require a lease.
    if contract.authority_class != AuthorityClass.JUDGE and not contract.lease_required:
        ac = contract.authority_class.value
        errors.append(f"non-judge authority_class '{ac}' must set lease_required=true")

    # F13 SOVEREIGN: human veto absolute is non-negotiable.
    if not contract.human_veto.f13_absolute:
        errors.append("human_veto.f13_absolute must be true")

    # Every peer must declare at least one forbidden action.
    if not contract.forbidden_actions:
        errors.append("forbidden_actions must not be empty")

    return errors


async def arif_peer_contract_validate(
    contract: dict[str, Any] | None = None,
    contract_url: str | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
    _envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Validate a Peer Federation Contract v1.

    Accepts either an inline contract dict or a URL from which to fetch it.
    Returns constitutional verdict: SEAL, HOLD, or DENY.
    """
    try:
        if contract is None and contract_url:
            with urllib.request.urlopen(contract_url, timeout=10) as resp:
                contract = json.loads(resp.read().decode("utf-8"))

        if contract is None:
            raise ValueError("Provide either contract or contract_url")

        validated = PeerFederationContract.model_validate(contract)
        organ = validated.peer_id.organ

        # Constitutional constraints beyond schema validity.
        errors = _enforce_constitutional_constraints(validated)

        if is_peer_forbidden(organ):
            errors.append(f"peer organ '{organ}' is forbidden")

        forbidden = is_peer_forbidden(organ)
        if errors:
            return {
                "status": "OK",
                "tool": "arif_peer_contract_validate",
                "verdict": "DENY" if forbidden else "HOLD",
                "result": {
                    "valid": False,
                    "organ": organ,
                    "authority_class": validated.authority_class.value,
                    "forbidden": forbidden,
                    "errors": errors,
                },
            }

        return {
            "status": "OK",
            "tool": "arif_peer_contract_validate",
            "verdict": "SEAL",
            "result": {
                "valid": True,
                "organ": organ,
                "authority_class": validated.authority_class.value,
                "contract_version": validated.contract_version,
                "lease_required": validated.lease_required,
                "forbidden": False,
            },
        }
    except Exception as e:
        return {
            "status": "DEGRADED",
            "tool": "arif_peer_contract_validate",
            "verdict": "DEGRADED",
            "result": {"valid": False, "error": str(e)},
        }


async def arif_peer_contract_attest(
    organ: str = "arifOS",
    actor_id: str | None = None,
    session_id: str | None = None,
    _envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Return the arifOS peer federation contract attestation.

    Includes the public contract URL, deterministic contract hash, and the
    contract itself. Only arifOS may hold judge authority.
    """
    try:
        contract = get_arifos_peer_contract()
        return {
            "status": "OK",
            "tool": "arif_peer_contract_attest",
            "verdict": "SEAL",
            "result": {
                "organ": organ,
                "peer_contract_url": PEER_CONTRACT_URL,
                "peer_contract_hash": get_arifos_peer_contract_hash(),
                "authority_class": contract.authority_class.value,
                "forbidden": is_peer_forbidden(organ),
                "contract": contract.model_dump(mode="json"),
            },
        }
    except Exception as e:
        return {
            "status": "DEGRADED",
            "tool": "arif_peer_contract_attest",
            "verdict": "DEGRADED",
            "result": {"error": str(e)},
        }


async def arif_peer_contract_forbid(
    organ: str,
    reason: str = "sovereign_forbid",
    actor_id: str | None = None,
    session_id: str | None = None,
    _envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Forbid a peer organ from the federation contract surface.

    This is a soft runtime gate; it does not mutate the canonical contract on
    disk. A forbidden peer will receive HOLD/DENY from validate until unforbidden.
    """
    _FORBIDDEN_PEERS.add(organ)
    return {
        "status": "OK",
        "tool": "arif_peer_contract_forbid",
        "verdict": "SEAL",
        "result": {"forbidden_organ": organ, "reason": reason},
    }


async def arif_peer_contract_unforbid(
    organ: str,
    actor_id: str | None = None,
    session_id: str | None = None,
    _envelope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Remove a peer organ from the runtime forbidden set."""
    _FORBIDDEN_PEERS.discard(organ)
    return {
        "status": "OK",
        "tool": "arif_peer_contract_unforbid",
        "verdict": "SEAL",
        "result": {"unforbidden_organ": organ},
    }


__all__ = [
    "PEER_CONTRACT_URL",
    "get_arifos_peer_contract_url",
    "get_arifos_peer_contract",
    "get_arifos_peer_contract_hash",
    "is_peer_forbidden",
    "arif_peer_contract_validate",
    "arif_peer_contract_attest",
    "arif_peer_contract_forbid",
    "arif_peer_contract_unforbid",
]

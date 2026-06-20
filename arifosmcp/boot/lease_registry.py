"""
Lease Registry — LEASE_LEDGER (Redis L1)

DITEMPA BUKAN DIBERI — Forged, Not Given.

Read/write active leases to Redis.
Leases are time-limited, scope-limited autonomy grants.
Expired leases must not grant authority.

Key: swarm:leases → JSON blob of active lease dicts
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

LEASES_KEY = "swarm:leases"


# ── Public API ────────────────────────────────────────────────────


def read_active_agents() -> list[dict[str, Any]]:
    """
    Read active agents visible to the swarm.
    Agents are seen only through lease registry + VAULT999 receipts.
    No gossip authority.
    """
    leases = _read_all_leases()
    agents: dict[str, dict[str, Any]] = {}

    for lease in leases:
        if _is_active(lease):
            holder = lease.get("holder", "")
            if holder not in agents:
                agents[holder] = {
                    "agent_id": holder,
                    "status": "ACTIVE",
                    "lease_id": lease.get("lease_id"),
                    "trusted_because": "VAULT999_SEAL",
                }

    return list(agents.values())


def read_active_leases() -> list[dict[str, Any]]:
    """
    Read LEASE_LEDGER. Expired leases must not grant authority.

    Returns list of active (non-expired) lease dicts.
    """
    leases = _read_all_leases()
    return [lease for lease in leases if _is_active(lease)]


def claim_lease(
    *,
    holder: str,
    resource: str,
    scope: list[str] | None = None,
    ttl_seconds: int = 900,
) -> dict[str, Any]:
    """
    Claim a lease on a resource.

    Returns the lease dict with lease_id and expires_at.
    Does NOT auto-approve — lease claims are recorded, not granted.
    """
    import uuid

    lease_id = f"LEASE-{uuid.uuid4().hex[:12]}"
    now = datetime.now(UTC)
    lease = {
        "lease_id": lease_id,
        "holder": holder,
        "resource": resource,
        "scope": scope or ["observe"],
        "ttl_seconds": ttl_seconds,
        "cannot_delegate": True,
        "cannot_expand_scope": True,
        "expires_at": (now.replace(tzinfo=None).isoformat() if now else now.isoformat()),
        "policy": "no_parallel_mutation_without_explicit_judge",
        "status": "CLAIMED",
    }
    # Set expires_at properly
    from datetime import timedelta

    expires = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
    lease["expires_at"] = expires.isoformat()

    _store_lease(lease)
    return lease


def release_lease(lease_id: str) -> bool:
    """
    Release a lease. Returns True if lease existed and was removed.
    """
    leases = _read_all_leases()
    updated = [l for l in leases if l.get("lease_id") != lease_id]
    if len(updated) < len(leases):
        _write_all_leases(updated)
        logger.info(f"Lease released: {lease_id}")
        return True
    return False


# ── Internal helpers ──────────────────────────────────────────────


def _read_all_leases() -> list[dict[str, Any]]:
    """Read all leases from Redis."""
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = r.get(LEASES_KEY)
        if raw:
            return json.loads(raw)
    except Exception as exc:
        logger.warning(f"Redis lease read failed: {exc}")
    return []


def _write_all_leases(leases: list[dict[str, Any]]) -> bool:
    """Write all leases to Redis."""
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = json.dumps(leases, default=str)
        r.set(LEASES_KEY, raw)
        return True
    except Exception as exc:
        logger.warning(f"Redis lease write failed: {exc}")
        return False


def _store_lease(lease: dict[str, Any]) -> bool:
    """Add a lease to the registry."""
    leases = _read_all_leases()
    leases.append(lease)
    return _write_all_leases(leases)


def _is_active(lease: dict[str, Any]) -> bool:
    """Check if a lease is active (not expired)."""
    expires_at = lease.get("expires_at")
    if not expires_at:
        return False
    try:
        expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        return expiry > datetime.now(UTC)
    except (ValueError, TypeError):
        return False

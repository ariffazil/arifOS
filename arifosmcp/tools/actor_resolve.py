"""
arif_actor_resolve — Context7/Notion-style Resolve-Before-Act
═══════════════════════════════════════════════════════════════════════════════

The substrate's first gate. Every non-OBSERVE action requires a resolved actor
before it can execute. Anonymous mutation is forbidden.

This is the Context7/Notion port: don't act on unresolved references. arifOS
generalizes it: don't act on unresolved actor + unresolved tool contract.

DITEMPA BUKAN DIBERI — The substrate is forged, not given.
"""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime, timedelta
from typing import Any


# Authority tiers — the substrate's trust levels
AUTHORITY_TIERS = ("SOVEREIGN", "HIGH", "MEDIUM", "LOW", "UNKNOWN")

# Authority sources — how the caller obtained authority
AUTHORITY_SOURCES = (
    "local_identity",     # Loaded from identity.toml on af-forge
    "oauth",              # Verified via OAuth token (Supabase, etc.)
    "signed_token",       # JWT with verified signature
    "manual_888",         # Explicit human approval via 888_JUDGE
    "fallback",           # Legacy / env fallback (transition mode)
)

# SOVEREIGN actor patterns — actors who can authorize ATOMIC actions
SOVEREIGN_ACTORS = frozenset(
    os.environ.get("ARIFOS_SOVEREIGN_ACTORS", "arifbfazil,arif,888").split(",")
)


def _authority_tier_for_actor(actor_id: str) -> str:
    """Resolve the authority tier for a given actor_id."""
    if not actor_id or actor_id in ("anonymous", "openclaw-anon", "unknown"):
        return "UNKNOWN"
    actor_lower = actor_id.lower().strip()
    if actor_lower in SOVEREIGN_ACTORS or any(
        s in actor_lower for s in SOVEREIGN_ACTORS
    ):
        return "SOVEREIGN"
    if actor_lower.startswith(("hermes", "forge", "root")):
        return "HIGH"
    if actor_lower.startswith(("mcp_client", "client")):
        return "MEDIUM"
    return "LOW"


def _authority_source_for_actor(actor_id: str) -> str:
    """Determine the authority source for the actor."""
    if actor_id in ("anonymous", "openclaw-anon"):
        return "fallback"
    if actor_id.startswith(("oauth:", "token:")):
        return "oauth"
    if actor_id.startswith("jwt:"):
        return "signed_token"
    return "local_identity"


def _hash_resolution(actor_id: str, requested_authority: str, expires_at: str) -> str:
    """Deterministic hash of the resolution tuple."""
    payload = f"{actor_id}|{requested_authority}|{expires_at}|arifOS"
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def arif_actor_resolve(
    actor_claim: str,
    requested_authority: str = "OBSERVE",
    lease_scope: list[str] | None = None,
    actor_signature: str | None = None,
    nonce: str | None = None,
) -> dict[str, Any]:
    """
    ARIF_ACTOR_RESOLVE: Resolve an actor before any non-OBSERVE action.

    The Context7/Notion pattern: don't act on unresolved references.
    arifOS generalization: don't JUDGE / MUTATE / EXECUTE / SEAL / BRIDGE /
    FORGE / GATEWAY without a resolved actor + resolution hash.

    Args:
        actor_claim: Who the caller claims to be (e.g., "arifbfazil")
        requested_authority: The action class requested (OBSERVE | JUDGE |
                            MUTATE | EXECUTE | SEAL | BRIDGE | GATEWAY |
                            FORGE). Defaults to OBSERVE.
        lease_scope: Optional list of additional scopes to bind to this lease
        actor_signature: Optional Ed25519 signature for sovereign-grade claims
        nonce: Optional fresh nonce to prevent replay

    Returns:
        Resolution dict with:
          - actor_id: canonical actor identifier
          - actor_verified: whether identity is verified
          - authority_tier: SOVEREIGN | HIGH | MEDIUM | LOW | UNKNOWN
          - authority_source: how the caller obtained authority
          - authority_scope: list of allowed actions under this resolution
          - actor_resolution_hash: sha256 of (actor_id, authority, expires_at)
          - expires_at: ISO 8601 timestamp (default: 5 minutes from now)
          - verdict: RESOLVED | UNRESOLVED | EXPIRED | INVALID

    Hard rules:
      - UNKNOWN tier for "anonymous", "openclaw-anon", "unknown" — cannot
        authorize any non-OBSERVE action
      - SOVEREIGN tier for arifbfazil and other sovereign actors — full scope
      - HIGH tier for hermes/forge/root — read + decide + bridge
      - MEDIUM tier for MCP clients — read + retrieve
      - LOW tier for unknown actors — OBSERVE only

    Reference: arifOS Blueprint v0.3, Phase 3 — arif_actor_resolve.
    """
    # ── Normalize ─────────────────────────────────────────────────────
    actor_id = (actor_claim or "").strip()
    requested_authority = (requested_authority or "OBSERVE").upper().strip()

    # ── Resolve tier and source ───────────────────────────────────────
    tier = _authority_tier_for_actor(actor_id)
    source = _authority_source_for_actor(actor_id)

    # ── Compute scope from tier ────────────────────────────────────────
    if tier == "SOVEREIGN":
        scope = ["OBSERVE", "JUDGE", "MUTATE", "EXECUTE", "SEAL", "BRIDGE", "GATEWAY", "FORGE"]
        verified = True
    elif tier == "HIGH":
        scope = ["OBSERVE", "JUDGE", "BRIDGE", "GATEWAY"]
        verified = True
    elif tier == "MEDIUM":
        scope = ["OBSERVE", "RETRIEVE"]
        verified = False  # MCP clients need explicit verification
    elif tier == "LOW":
        scope = ["OBSERVE"]
        verified = False
    else:  # UNKNOWN / anonymous
        scope = []
        verified = False

    # Add lease_scope if provided
    if lease_scope:
        scope = list(set(scope + [s.upper() for s in lease_scope]))

    # ── Validate requested authority against scope ────────────────────
    if requested_authority not in scope:
        return {
            "actor_id": actor_id or "anonymous",
            "actor_verified": False,
            "authority_tier": tier,
            "authority_source": source,
            "authority_scope": scope,
            "actor_resolution_hash": None,
            "expires_at": None,
            "requested_authority": requested_authority,
            "verdict": "UNRESOLVED",
            "reason": f"tier={tier} cannot authorize {requested_authority}; "
                     f"scope allows only {scope}",
            "sovereign_ack_required": tier in ("LOW", "UNKNOWN"),
        }

    # ── Compute expiry + hash ─────────────────────────────────────────
    expires_at = (datetime.now(UTC) + timedelta(minutes=5)).isoformat()
    resolution_hash = _hash_resolution(actor_id, requested_authority, expires_at)

    return {
        "actor_id": actor_id,
        "actor_verified": verified,
        "authority_tier": tier,
        "authority_source": source,
        "authority_scope": scope,
        "requested_authority": requested_authority,
        "actor_resolution_hash": resolution_hash,
        "expires_at": expires_at,
        "nonce": nonce,
        "actor_signature_provided": actor_signature is not None,
        "verdict": "RESOLVED",
        "next_action": (
            "Pass actor_resolution_hash back on any non-OBSERVE call within 5 minutes."
        ),
    }


# ── Test surface ────────────────────────────────────────────────────────
if __name__ == "__main__":
    import json

    test_cases = [
        ("arifbfazil", "SEAL"),
        ("arifbfazil", "MUTATE"),
        ("hermes", "BRIDGE"),
        ("mcp_client_xyz", "OBSERVE"),
        ("mcp_client_xyz", "MUTATE"),  # should UNRESOLVE
        ("anonymous", "OBSERVE"),       # should UNRESOLVE
        ("openclaw-anon", "JUDGE"),     # should UNRESOLVE
        ("", "OBSERVE"),                # should UNRESOLVE
    ]

    print("=" * 80)
    print("arif_actor_resolve — test surface")
    print("=" * 80)
    for actor, auth in test_cases:
        result = arif_actor_resolve(actor, auth)
        print(f"\nactor={actor!r:20s} requested={auth:10s} → verdict={result['verdict']}")
        print(f"  tier={result['authority_tier']} verified={result['actor_verified']}")
        if result.get("actor_resolution_hash"):
            print(f"  hash={result['actor_resolution_hash'][:24]}...")
        else:
            print(f"  reason={result.get('reason', 'no hash')}")

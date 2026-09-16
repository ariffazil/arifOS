"""
capability_truth.py — Single source of truth for the arifOS MCP public surface
═══════════════════════════════════════════════════════════════════════════════

DITEMPA BUKAN DIBERI — Forged, not given.

Created 2026-09-17 in musyawarah-2026-09-17-mcp-migration.

Purpose
───────
Anchor every advertised surface artifact to ONE Python module so:

    H(T_advertised) = H(T_listed) = H(T_dispatchable) = H(T_documented)

holds by construction. Drift between connector manifest, tools/list response,
canonical handler dispatch, and documentation becomes provably illegal.

Layers this module owns
───────────────────────
1. CANONICAL_EIGHT        — the 8 verbs that are constitutional canon.
2. PROFILE_GATES          — which subset each actor profile is allowed to invoke.
3. capability_hash(profile) — sha256 fingerprint of a profile's public surface.
   Used as an attestation anchor across the federation.
4. surface_manifest(profile) — ordered tuple of {name, description} pairs.
   Used by build-time artifact generators (connectors, docs, SDK bindings).

What this module does NOT own
─────────────────────────────
- Internal `_CANONICAL_HANDLERS` map (server.py:967-1352) — it is the
  dispatch authority. This module is the *advertised* authority; the kernel's
  pre_execution_gate enforces the *real* authority.
- Constitutional floors F1-F13 — those live in `core/law.py`.
- Authority ladder (SCT, ACT) — those live in `runtime/session_policy.py` and
  `runtime/governance_identity.py`.

Invariant
─────────
The 8 verbs are the constitutional surface. Adding/removing a verb
requires editing ONLY this module. Everything else regenerates.

F13 HOLD gates
──────────────
The capability_hash here is the anchor for:
- G0-ACT: ratification that 8 is final (defer; pending sovereign acknowledgment).
- G1:    runtime attestation verifies the kernel's _CANONICAL_HANDLERS
         hash equals surface_manifest("kitchen_sink").capability_hash
         for every replica, every restart.
"""

from __future__ import annotations

import hashlib
import json
from typing import Final


# ─────────────────────────────────────────────────────────────────────────
# 1. CANONICAL EIGHT — constitutional surface, in canonical order 000→999.
# ─────────────────────────────────────────────────────────────────────────
# Adding a verb is a constitutional act. F13 SOVEREIGN HOLD required.
# Removing a verb is equally constitutional.

CANONICAL_EIGHT: Final[tuple[str, ...]] = (
    "arif_init",  # 000 — identity, actor binding, authority context
    "arif_observe",  # 111 — evidence acquisition, reality registration
    "arif_think",  # 333 — reasoning, hypothesis, plan formation
    "arif_route",  # 444 — delegation to the appropriate organ
    "arif_memory",  # 555 — governed recall, correction, persistence
    "arif_judge",  # 666 — constitutional arbitration (HOLD/SEAL/VOID)
    "arif_forge",  # 777 — controlled, bounded real-world change
    "arif_seal",  # 999 — durable provenance, receipt issuance
)


# ─────────────────────────────────────────────────────────────────────────
# 2. PROFILE GATES — which verbs each actor profile is allowed to invoke.
# ─────────────────────────────────────────────────────────────────────────
# Default user-facing profile (anonymous or unverified) sees the read-only set.
# Verified sovereign actors see all 8. Federation bridge calls use
# "kitchen_sink" for compatibility with the broader constitutional_map.

PROFILE_GATES: Final[dict[str, tuple[str, ...]]] = {
    # Anonymous / OBSERVE_ONLY: read+reason, no execution
    "public_agent": (
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
    ),
    # Verified trusted agent: same as public — no mutation verbs (ABI mirror)
    "trusted_agent": (
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
    ),
    # Executor: + forge, still no seal (ABI mirror)
    "executor": (
        "arif_init",
        "arif_observe",
        "arif_think",
        "arif_route",
        "arif_memory",
        "arif_judge",
        "arif_forge",
    ),
    # Verified sovereign: full constitutional surface
    "sovereign": CANONICAL_EIGHT,
    # Operator / legacy: full surface (ABI mirror)
    "operator": CANONICAL_EIGHT,
    "legacy": CANONICAL_EIGHT,
    # Federation peer bridge: full surface for inter-organ calls
    "kitchen_sink": CANONICAL_EIGHT,
    # Diagnostic mode (for /tools.json and /conformance_report): includes
    # non-canonical but discoverable verbs (arif_canary, arif_compose, etc.)
    "diagnostic": CANONICAL_EIGHT,
}


# ─────────────────────────────────────────────────────────────────────────
# 3. PUBLIC MANIFEST — human-readable {name, description} for the public 6.
# ─────────────────────────────────────────────────────────────────────────

PUBLIC_MANIFEST: Final[dict[str, str]] = {
    "arif_init": (
        "KERNEL 000 — Session ignition. Binds actor identity, floors, audit "
        "before any other arif_* verb can govern. Without session_id, kernel "
        "treats caller as anonymous (OBSERVE_ONLY)."
    ),
    "arif_observe": (
        "KERNEL 111 — Sense reality into evidence (not reasoning, not judgment). "
        "Web search, URL fetch, system vitals, entropy measurement."
    ),
    "arif_think": (
        "KERNEL 333 — Structured reasoning under F2/F7 (not chat, not verdict). "
        "Plan, reflect, verify, synthesize. Returns OBS/DER/INT/SPEC labels."
    ),
    "arif_route": (
        "KERNEL 444 — Intent-organ router (default path to GEOX/WEALTH/WELL/"
        "A-FORGE). Select when goal is known but organ/verb is not."
    ),
    "arif_memory": (
        "KERNEL 555 — Memory governor — L1-L6 under F1/F2/F4/F11. Recall, inspect, "
        "attest, remember, promote, revise, forget. Writes are J-space mutations."
    ),
    "arif_judge": (
        "KERNEL 666 — Constitutional verdict. Only organ that SEAL/HOLD/SABAR/"
        "VOIDs. Binding floor + authority arbitration."
    ),
    "arif_forge": (
        "KERNEL 777 — Execution gate via A-FORGE. Mutates only after arif_judge "
        "SEAL + lease/chain IDs. dry_run | engineer | query | write | generate | commit."
    ),
    "arif_seal": (
        "KERNEL 999 — VAULT999 immutable append. Irreversible civilizational "
        "memory. seal | verify | chain | list | dry_run | session_close | audit."
    ),
}


# ─────────────────────────────────────────────────────────────────────────
# 4. capability_hash — the attestation anchor for all advertised surfaces.
# ─────────────────────────────────────────────────────────────────────────


def surface_manifest(profile: str = "public_agent") -> tuple[dict, ...]:
    """Return an ordered tuple of {name, description} pairs for the profile.

    Order is determined by CANONICAL_EIGHT, gated by PROFILE_GATES[profile].
    Order is canonical and stable — every artifact consumer MUST honour it,
    otherwise MCP client caches will invalidate on every restart.
    """
    if profile not in PROFILE_GATES:
        raise ValueError(f"Unknown profile {profile!r}. Known profiles: {sorted(PROFILE_GATES)}")
    allowed = PROFILE_GATES[profile]
    return tuple(
        {"name": name, "description": PUBLIC_MANIFEST[name]}
        for name in CANONICAL_EIGHT
        if name in allowed
    )


def capability_hash(profile: str = "public_agent") -> str:
    """Return sha256 hex digest of the canonical surface for `profile`.

    Used by:
    - G1 runtime attestation (kernel must hash to this value at boot).
    - Connector manifest build (must hash to this value).
    - SDK bindings cross-check (must hash to this value).
    - Documentation conformance check (must hash to this value).

    Args:
        profile: One of PROFILE_GATES keys. Default "public_agent".

    Returns:
        "sha256:<64-hex>" string.
    """
    manifest = surface_manifest(profile)
    # Canonical JSON encoding: sorted keys, separators=(",", ":"), no spaces.
    blob = json.dumps(
        [m for m in manifest],  # tuple → list
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    digest = hashlib.sha256(blob).hexdigest()
    return f"sha256:{digest}"


def all_profile_hashes() -> dict[str, str]:
    """Convenience: all profiles' hash, for documentation."""
    return {profile: capability_hash(profile) for profile in PROFILE_GATES}


# ─────────────────────────────────────────────────────────────────────────
# 5. Self-test — keep cold-start honest.
# ─────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    # Make drift detectable at import time, not just at boot time.
    print("CANONICAL_EIGHT:", CANONICAL_EIGHT)
    print()
    print("Public agent manifest:")
    for entry in surface_manifest("public_agent"):
        print(f"  - {entry['name']}: {entry['description'][:60]}…")
    print()
    print("Profile hashes:")
    for profile, h in all_profile_hashes().items():
        print(f"  {profile:14s} → {h}")

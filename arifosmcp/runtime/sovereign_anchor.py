"""
arifosmcp/runtime/sovereign_anchor.py
═══════════════════════════════════════════════════════════════════════════════
EUREKA 1: Sovereign Anchor Enforcement

Verifies that a session initiation traces to /000 sovereign key.

Checks:
  1. Session context contains a sovereign_key reference
  2. Sovereign key matches registered /000 attestation
  3. Key has not been revoked or rotated without re-attestation

Constitutional Floors: F1 (Amanah), F11 (Auth), F13 (Sovereign)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────────────
# Internal registry — simulates /000 attested sovereign keys.
# In production this would load from VAULT999/AAA_HUMAN/ and verify against
# the public attestation at https://arif-fazil.com/000/.
# ──────────────────────────────────────────────────────────────────────────────

_REGISTERED_SOVEREIGN_KEYS: set[str] = {
    "af-rootkey-v53-ed25519",
    "arif-fazil-000-attested",
    "compromised-key-2025",
    "rotated-key-alpha",
}

_REVOKED_SOVEREIGN_KEYS: set[str] = {
    "compromised-key-2025",
    "rotated-key-alpha",
}


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────


def verify_sovereign_anchor(session_context: dict) -> tuple[bool, str]:
    """
    Verify that a session initiation traces to /000 sovereign key.

    Checks performed in order:
    1.  ``session_context`` must contain a ``"sovereign_key"`` key with a
        non-empty string value.
    2.  The referenced key must exist in the registered /000 attestation set.
    3.  The key must not appear in the revoked / rotated set.

    Parameters
    ----------
    session_context : dict
        Session initiation payload. Expected to carry at least:

        - ``sovereign_key`` (str):  the key identifier to check.

    Returns
    -------
    tuple[bool, str]
        ``(True, "Sovereign anchor verified")`` on success, or
        ``(False, "<reason>")`` on failure.
    """
    # ── check 1: key reference present ──────────────────────────────────────
    sovereign_key = session_context.get("sovereign_key")

    if not sovereign_key:
        return (False, "No sovereign anchor in session context")
    if not isinstance(sovereign_key, str) or not sovereign_key.strip():
        return (False, "Sovereign key reference is empty or invalid")

    key = sovereign_key.strip()

    # ── check 2: matches registered /000 attestation ───────────────────────
    if key not in _REGISTERED_SOVEREIGN_KEYS:
        return (False, "Sovereign key does not match /000 attestation")

    # ── check 3: not revoked / rotated ─────────────────────────────────────
    if key in _REVOKED_SOVEREIGN_KEYS:
        return (False, "Sovereign key has been revoked; re-attestation required")

    return (True, "Sovereign anchor verified")

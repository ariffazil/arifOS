"""
governance_identity.py — Protected Sovereign Identity Registry (L11/L13)

Defines protected sovereign IDs that require cryptographic proof or explicit
human approval before session anchoring is permitted.

SECURITY NOTE (2026-07-06): SEMANTIC_KEYS removed. The "IM ARIF" hash-based
bypass was dead code (not imported by runtime/tools.py or session.py) but
its existence was a liability. Protected identity verification now requires:
1. Valid Ed25519/ES256 cryptographic signature, OR
2. Explicit human_approval from a verified session, OR
3. Sovereign ack through arif_init(ack_irreversible=True) path.

Semantic phrase matching (IDENTITY_PHRASES) is retained for NLP input
parsing only — it does NOT grant identity verification.
"""

from __future__ import annotations

import re
from typing import Any

# P0: Protected Sovereign IDs (L11 Identity Hardening)
# These IDs cannot be claimed without:
# 1. Valid cryptographic proof (signed token), OR
# 2. Explicit human_approval flag with acknowledgment, OR
# 3. Valid Semantic Key (Naming is the act of creation)
PROTECTED_SOVEREIGN_IDS: set[str] = {
    "arif",
    "ariffazil",
    "sovereign",
    "admin",
    "root",
    "system",
    "arif-fazil",
    "arif_fazil",
    "muhammad_arif",
}

# Semantic identity phrases (NLP input parsing ONLY — NOT authentication)
# These parse natural language identity claims from user input.
# They do NOT grant verification or authority.
IDENTITY_PHRASES: list[tuple[str, str]] = [
    (r"^(i am|im|i'm|saya|aku|hamba)\s+(arif|ariffazil|arif-fazil)$", "arif"),
    (
        r"^(hi|hello|hey|yo)\s+(i am|im|i'm|saya|aku)\s+(arif|ariffazil|arif-fazil)$",
        "arif",
    ),
    (r"^it's\s+(arif|ariffazil|arif-fazil)$", "arif"),
]


def canonicalize_identity_claim(text: str | None) -> str | None:
    """
    Parse raw input for identity claims (Naming as Creation).
    Returns canonical actor_id if matched, else None.
    """
    if not text:
        return None

    clean_text = text.lower().strip().rstrip(".!?")

    for pattern, canonical_id in IDENTITY_PHRASES:
        if re.match(pattern, clean_text):
            return canonical_id

    return None


# P0: Identity claim validation
def is_protected_sovereign_id(actor_id: str | None) -> bool:
    """Check if actor_id is a protected sovereign identity."""
    if not actor_id or actor_id == "anonymous":
        return False
    return actor_id.lower().strip() in PROTECTED_SOVEREIGN_IDS


# P0: Proof validation helper (Harden Bridge v1.0)
def validate_sovereign_proof(actor_id: str, proof: dict | str | Any | None) -> bool:
    """
    Validate cryptographic proof for protected sovereign ID.

    L11: Command Authority
    L13: Sovereign Override

    SECURITY (2026-07-06): Semantic key bypass removed. Only cryptographic
    signatures or explicit human approval through verified sessions are accepted.
    """
    if not proof:
        return False

    # Cryptographic signature path (Ed25519/ES256)
    if isinstance(proof, dict):
        required_fields = ["signature", "nonce", "timestamp"]
        if all(field in proof for field in required_fields):
            # TODO (real): Add Ed25519 signature verification.
            # Until implemented, cryptographic proof structs are accepted
            # but logged as unverified — the session stays OBSERVE_ONLY.
            return False

    # String proof (e.g. "IM ARIF") is NOT accepted for identity verification.
    # It may be used for NLP input parsing via canonicalize_identity_claim(),
    # but that does NOT grant authority or verification status.
    return False

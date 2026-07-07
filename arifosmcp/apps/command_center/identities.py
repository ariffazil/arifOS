"""Sovereign Identity Registry — L11/L13 Identity Hardening.

Extracted from archive: _archived/root_runtime_pre_migration/governance_identities.py
DITEMPA BUKAN DIBERI — Forged, Not Given

SECURITY (2026-07-06): SEMANTIC_KEYS removed. Phrase-based auth eliminated.
"""

from __future__ import annotations

import re
from typing import Any

# P0: Protected Sovereign IDs (L11 Identity Hardening)
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

# Identity phrase patterns (English + Malay) — NLP parsing ONLY, NOT auth
IDENTITY_PHRASES: list[tuple[str, str]] = [
    (r"^(i am|im|i'm|saya|aku|hamba)\s+(arif|ariffazil|arif-fazil)$", "arif"),
    (
        r"^(hi|hello|hey|yo)\s+(i am|im|i'm|saya|aku)\s+(arif|ariffazil|arif-fazil)$",
        "arif",
    ),
    (r"^it's\s+(arif|ariffazil|arif-fazil)$", "arif"),
]


def canonicalize_identity_claim(text: str | None) -> str | None:
    """Parse raw input for identity claims. Returns canonical actor_id if matched."""
    if not text:
        return None
    clean_text = text.lower().strip().rstrip(".!?")
    for pattern, canonical_id in IDENTITY_PHRASES:
        if re.match(pattern, clean_text):
            return canonical_id
    return None


def is_protected_sovereign_id(actor_id: str | None) -> bool:
    """Check if actor_id is a protected sovereign identity."""
    if not actor_id or actor_id == "anonymous":
        return False
    return actor_id.lower().strip() in PROTECTED_SOVEREIGN_IDS


def validate_sovereign_proof(actor_id: str, proof: dict | str | Any | None) -> bool:
    """Validate cryptographic proof for protected sovereign ID.

    SECURITY (2026-07-06): Semantic key bypass removed. Only cryptographic
    signatures or explicit human approval through verified sessions are accepted.
    """
    if not proof:
        return False

    if isinstance(proof, dict):
        required_fields = ["signature", "nonce", "timestamp"]
        if all(field in proof for field in required_fields):
            # TODO (real): Ed25519 verification. Until then, reject.
            return False

    return False

"""Sovereign Identity Registry — F11/F13 Identity Hardening.

Extracted from archive: _archived/root_runtime_pre_migration/governance_identities.py
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

# P0: Protected Sovereign IDs (F11 Identity Hardening)
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

# P0: Semantic Keys (ABI v1.0 — Naming as Creation)
SEMANTIC_KEYS: dict[str, str] = {
    "arif": hashlib.sha256(b"IM ARIF").hexdigest(),
    "ariffazil": hashlib.sha256(b"IM ARIF").hexdigest(),
    "arif-fazil": hashlib.sha256(b"IM ARIF").hexdigest(),
}

# Identity phrase patterns (English + Malay)
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
    """Validate cryptographic or semantic proof for protected sovereign ID."""
    if not proof:
        return False

    actor_id_clean = actor_id.lower().strip()

    # Path 1: Semantic Key (Naming is Creation)
    semantic_candidate = None
    if isinstance(proof, str):
        semantic_candidate = proof
    elif isinstance(proof, dict):
        semantic_candidate = proof.get("semantic_key") or proof.get("key") or proof.get("proof")

    if semantic_candidate and actor_id_clean in SEMANTIC_KEYS:
        if isinstance(semantic_candidate, str):
            candidate_hash = hashlib.sha256(semantic_candidate.strip().upper().encode()).hexdigest()
            if candidate_hash == SEMANTIC_KEYS[actor_id_clean]:
                return True

    # Path 2: Cryptographic Signature (Ed25519 — placeholder for production)
    if isinstance(proof, dict):
        required_fields = ["signature", "nonce", "timestamp"]
        if all(field in proof for field in required_fields):
            # TODO: Add Ed25519 verification
            pass

    return False

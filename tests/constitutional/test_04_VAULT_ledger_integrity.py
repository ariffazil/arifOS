"""
test_04_VAULT_ledger_integrity.py - Vault & Ledger Immutability Validation

AUTHORITY: arifOS Constitutional Law (000_THEORY/000_LAW.md)
ARCHITECT: Arif Fazil (Human Sovereign)
ENGINEER: Claude Sonnet 3.7 / Antigravity (Δ)
VERSION: v49.1.0

PURPOSE:
Validate the integrity of the arifOS memory bands:
1. Vault-999 (Immutable Canon) - Rejects unauthorized writes.
2. Cooling Ledger (Audit Trail) - Cryptographic Merkle tree integrity.
3. Cryptographic Sealing (zkPC) - Proof of consensus.
"""

from typing import Any, Dict

import pytest


def test_vault_write_rejection():
    """
    Ensure that writing to the sealed canon (L1_THEORY/canon) is rejected without proper authority.
    """
    from arifos.core.exceptions import UnauthorizedWriteError
    from arifos.core.vault import VaultManager

    vault = VaultManager()

    # Attempting to overwrite a sealed file without APEX authority
    with pytest.raises(UnauthorizedWriteError):
        vault.write_sealed("000_THEORY/000_LAW.md", "Malicious content", authority="ENGINEER")

def test_ledger_merkle_integrity():
    """
    Validate that the ledger maintains cryptographic integrity (chained hashes).
    """
    from arifos.core.ledger import LedgerManager

    ledger = LedgerManager()

    # Get last two entries
    entries = ledger.get_latest_entries(count=2)
    if len(entries) < 2:
        pytest.skip("Not enough ledger entries for integrity check")

    e1, e2 = entries[0], entries[1]

    # Verify that e2 points to e1's hash (assuming chronological order)
    # The actual implementation might differ, but the principle is a chain.
    assert e2["previous_hash"] == e1["entry_hash"]

def test_zkpc_seal_verification():
    """
    Validate that a SEAL receipt can be cryptographically verified.
    """
    from arifos.core.crypto import zkPCVerifier
    from arifos.core.metabolizer import Metabolizer

    m = Metabolizer()
    verifier = zkPCVerifier()

    # Generate a legitimate seal
    seal_receipt = m.seal(verdict={"F2_Truth": 1.0, "F1_Amanah": True})

    # Verify the proof
    is_valid = verifier.verify_proof(
        proof=seal_receipt["proof"],
        public_inputs=seal_receipt["public_inputs"]
    )
    assert is_valid is True

def test_ledger_tamper_detection():
    """
    Verify that tampering with a historical ledger entry is detected.
    """
    from arifos.core.exceptions import LedgerCorruptedError
    from arifos.core.ledger import LedgerManager

    ledger = LedgerManager()

    # Simulate manual tamper with the underlying storage
    # This is a mock/simulation of a corruption event
    ledger._tamper_last_entry()

    with pytest.raises(LedgerCorruptedError):
        ledger.verify_chain()

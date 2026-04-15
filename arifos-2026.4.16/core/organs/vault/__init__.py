"""
arifOS.vault — The Immutable Constitutional Ledger for Judgment

Vault is for PROOF:
- Seal verdicts, evidence, lineage, governance events
- Append-only / immutable
- Hash-linked / Merkle proof
- Tamper detection
- Replay of judgment history

Memory is for use. Vault is for proof.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from .vault_organ import VaultOrgan, get_vault_organ
from .types import VaultEntry, SealReceipt, VerifyReport

__all__ = [
    "VaultOrgan",
    "get_vault_organ",
    "VaultEntry",
    "SealReceipt",
    "VerifyReport",
]

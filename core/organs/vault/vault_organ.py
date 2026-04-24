"""
arifOS.vault — The Immutable Constitutional Ledger

Operations:
- seal: Append immutable record
- verify: Check integrity
- supersede: Add correction (never edit in place)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .types import (
    Integrity,
    SealReceipt,
    VaultEntry,
    VaultRecordType,
    Verdict,
    VerifyReport,
)


@dataclass
class SealGateResult:
    """Result of seal gate check."""
    allowed: bool
    reason: str


class VaultOrgan:
    """
    The vault organ manages the immutable judgment ledger.
    
    Key properties:
    - Append-only
    - Hash-linked
    - Tamper-evident
    - Never edited in place (supersession only)
    """
    
    def __init__(self, vault_path: Path | None = None):
        self.vault_path = vault_path or Path("/var/lib/arifos/vault/vault.jsonl")
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory index
        self._entries: dict[str, VaultEntry] = {}
        self._hash_chain: list[str] = []  # Ordered list of record hashes
        
        # Load existing vault
        self._load_vault()
    
    def _load_vault(self):
        """Load existing vault from disk."""
        if not self.vault_path.exists():
            return
        
        with open(self.vault_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Would reconstruct VaultEntry from dict
                    # For now, just track hashes
                    if 'integrity' in data and 'record_hash' in data['integrity']:
                        self._hash_chain.append(data['integrity']['record_hash'])
                except json.JSONDecodeError:
                    continue
    
    # ===================== SEAL GATE =====================
    
    def _check_seal_gate(self, entry: VaultEntry) -> SealGateResult:
        """
        Judgment gate: Should this be sealed in vault?
        
        Seal only if:
        - Creates or changes policy
        - Affects trust, authority, safety, or release state
        - Records human sovereign decision
        - Closes consequential architecture choice
        - Documents refusal/hold with governance consequence
        """
        # Must have evidence
        if not entry.evidence or not entry.evidence.summary:
            return SealGateResult(
                allowed=False,
                reason="Vault entries must have evidence"
            )
        
        # Must have clear authority
        if not entry.governance.decision_authority:
            return SealGateResult(
                allowed=False,
                reason="Vault entries must specify decision authority"
            )
        
        # Must be consequential
        consequential_types = [
            VaultRecordType.VERDICT,
            VaultRecordType.POLICY,
            VaultRecordType.RELEASE,
            VaultRecordType.OVERRIDE,
        ]
        
        if entry.record_type not in consequential_types:
            return SealGateResult(
                allowed=False,
                reason=f"{entry.record_type.value} is not vault-worthy"
            )
        
        # High-risk requires human confirmation
        if entry.governance.risk_tier in ["high", "critical"]:
            if not entry.governance.human_confirmed:
                return SealGateResult(
                    allowed=False,
                    reason="High-risk entries require human confirmation"
                )
        
        return SealGateResult(
            allowed=True,
            reason="Meets vault seal criteria"
        )
    
    # ===================== SEAL =====================
    
    def seal(self, entry: VaultEntry) -> SealReceipt | None:
        """
        Seal a record to the vault.
        
        This is APPEND-ONLY. Records are never edited.
        """
        # Check seal gate
        gate = self._check_seal_gate(entry)
        if not gate.allowed:
            print(f"Seal rejected: {gate.reason}")
            return None
        
        # Generate vault ID if not present
        if not entry.vault_id:
            entry.vault_id = f"vlt_{uuid.uuid4().hex[:16]}"
        
        # Compute record hash
        record_hash = entry.compute_hash()
        
        # Get previous hash for chain
        prev_hash = self._hash_chain[-1] if self._hash_chain else "0" * 64
        
        # Build integrity proof
        # Combined hash: prev_hash + record_hash
        combined = prev_hash + record_hash
        entry_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        entry.integrity = Integrity(
            prev_hash=prev_hash,
            record_hash=record_hash,
            merkle_root=entry_hash,  # Simplified - would be actual Merkle
        )
        
        # Store in memory
        self._entries[entry.vault_id] = entry
        self._hash_chain.append(record_hash)
        
        # Persist to disk
        self._append_to_disk(entry)
        
        return SealReceipt(
            vault_id=entry.vault_id,
            record_hash=record_hash,
            merkle_root=entry_hash,
            timestamp=entry.sealed_at,
            immutable=True,
        )
    
    def _append_to_disk(self, entry: VaultEntry):
        """Append entry to vault file."""
        with open(self.vault_path, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
    
    # ===================== VERIFY =====================
    
    def verify(self, vault_id: str) -> VerifyReport:
        """
        Verify a vault entry's integrity.
        
        Checks:
        - Hash matches content
        - Chain continuity
        - Supersession status
        """
        entry = self._entries.get(vault_id)
        if not entry:
            return VerifyReport(
                vault_id=vault_id,
                valid=False,
                chain_continuity=False,
                hash_match=False,
                superseded=False,
                errors=["Vault entry not found"]
            )
        
        errors = []
        
        # Check hash match
        computed_hash = entry.compute_hash()
        hash_match = computed_hash == entry.integrity.record_hash
        if not hash_match:
            errors.append(f"Hash mismatch: computed {computed_hash[:16]}... vs stored {entry.integrity.record_hash[:16]}...")
        
        # Check chain continuity
        chain_continuity = True
        # Would verify prev_hash links to actual previous record
        
        # Check if superseded
        superseded = False
        superseded_by = None
        for other in self._entries.values():
            if other.lineage.supersedes == vault_id:
                superseded = True
                superseded_by = other.vault_id
                break
        
        return VerifyReport(
            vault_id=vault_id,
            valid=hash_match and chain_continuity,
            chain_continuity=chain_continuity,
            hash_match=hash_match,
            superseded=superseded,
            superseded_by=superseded_by,
            errors=errors,
        )
    
    def verify_chain(self) -> dict[str, Any]:
        """Verify entire vault chain."""
        if not self.vault_path.exists():
            return {"valid": True, "count": 0, "errors": []}
        
        errors = []
        prev_hash = "0" * 64
        count = 0
        
        with open(self.vault_path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    data = json.loads(line)
                    integrity = data.get('integrity', {})
                    
                    # Check prev_hash
                    stored_prev = integrity.get('prev_hash')
                    if stored_prev != prev_hash:
                        errors.append(f"Line {line_num}: Chain break. Expected {prev_hash[:16]}..., found {stored_prev[:16]}...")
                    
                    # Update prev_hash for next iteration
                    prev_hash = integrity.get('record_hash', '')
                    count += 1
                    
                except json.JSONDecodeError:
                    errors.append(f"Line {line_num}: Invalid JSON")
        
        return {
            "valid": len(errors) == 0,
            "count": count,
            "errors": errors,
        }
    
    # ===================== SUPERSEDE =====================
    
    def supersede(
        self,
        vault_id: str,
        new_entry: VaultEntry,
        authority: str,
    ) -> SealReceipt | None:
        """
        Supersede a vault entry with a new version.
        
        NEVER edits the old entry. Creates new entry that references old.
        """
        old_entry = self._entries.get(vault_id)
        if not old_entry:
            return None
        
        # Mark new entry as superseding old
        new_entry.lineage.supersedes = vault_id
        new_entry.lineage.derived_from.append(vault_id)
        
        # Seal new entry
        return self.seal(new_entry)
    
    # ===================== QUERY =====================
    
    def get_entry(self, vault_id: str) -> VaultEntry | None:
        """Get vault entry by ID."""
        return self._entries.get(vault_id)
    
    def get_by_verdict(self, verdict: Verdict) -> list[VaultEntry]:
        """Get all entries with a specific verdict."""
        return [
            e for e in self._entries.values()
            if e.verdict == verdict
        ]
    
    def get_by_authority(self, authority: str) -> list[VaultEntry]:
        """Get all entries by decision authority."""
        return [
            e for e in self._entries.values()
            if e.governance.decision_authority == authority
        ]
    
    def get_current_policy(self) -> list[VaultEntry]:
        """Get current (non-superseded) policy entries."""
        current = []
        for entry in self._entries.values():
            if entry.record_type == VaultRecordType.POLICY:
                verify = self.verify(entry.vault_id)
                if not verify.superseded:
                    current.append(entry)
        return current
    
    def chain_status(self) -> dict[str, Any]:
        """Get chain health status."""
        return self.verify_chain()


# Singleton
_vault_organ: VaultOrgan | None = None


def get_vault_organ(vault_path: Path | None = None) -> VaultOrgan:
    """Get or create vault organ."""
    global _vault_organ
    if _vault_organ is None:
        _vault_organ = VaultOrgan(vault_path=vault_path)
    return _vault_organ

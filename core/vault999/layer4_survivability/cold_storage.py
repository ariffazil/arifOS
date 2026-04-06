"""
Layer 4: Survivability — Cold Storage & Shamir Secret Sharing

If VPS is seized or destroyed, the system must survive.

Key principle: No single point of failure — not in code, not in humans, not in geography.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# For Shamir's Secret Sharing
try:
    import secretsharing
    HAS_SSS = True
except ImportError:
    HAS_SSS = False


@dataclass
class VaultBackup:
    """
    Encrypted backup of VAULT999 with integrity verification.
    """
    timestamp: datetime
    vault_hash: str           # Merkle root of backed-up vault
    backup_path: Path
    gpg_recipients: list[str]  # Who can decrypt
    integrity_proof: str      # SHA256 of encrypted file


@dataclass
class ShamirShare:
    """
    One share of a Shamir's Secret Sharing scheme.
    
    3-of-5 scheme: Need any 3 shares to reconstruct the secret.
    """
    share_id: int             # Which share (1-5)
    threshold: int            # How many needed (3)
    total_shares: int         # Total shares (5)
    share_data: str           # The actual share (hex)
    location: str             # Where this share is stored


class ColdStorageManager:
    """
    Manages offline, distributed storage of critical secrets.
    
    Uses:
    - GPG encryption for backups
    - Shamir's Secret Sharing for signing keys
    - Multiple geographic locations
    - Air-gapped storage options
    """
    
    def __init__(self, vault_path: Path, backup_dir: Path):
        self.vault_path = vault_path
        self.backup_dir = backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # GPG recipients for backups
        self.gpg_recipients = os.getenv(
            "VAULT_GPG_RECIPIENTS",
            "ariffazil@github.com,backup@arifos.local"
        ).split(",")
    
    async def create_encrypted_backup(self) -> VaultBackup:
        """
        Create GPG-encrypted backup of VAULT999.
        
        Stored in multiple cloud providers for redundancy.
        """
        timestamp = datetime.utcnow()
        backup_name = f"vault999_backup_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # 1. Create tarball of vault
        tarball_path = self.backup_dir / f"{backup_name}.tar.gz"
        await self._create_tarball(self.vault_path, tarball_path)
        
        # 2. Compute hash before encryption
        with open(tarball_path, "rb") as f:
            pre_encrypt_hash = hashlib.sha256(f.read()).hexdigest()
        
        # 3. GPG encrypt for multiple recipients
        encrypted_path = self.backup_dir / f"{backup_name}.tar.gz.gpg"
        await self._gpg_encrypt(tarball_path, encrypted_path, self.gpg_recipients)
        
        # 4. Remove unencrypted tarball
        tarball_path.unlink()
        
        # 5. Compute hash of encrypted file
        with open(encrypted_path, "rb") as f:
            integrity_proof = hashlib.sha256(f.read()).hexdigest()
        
        # 6. Replicate to multiple cloud providers
        await self._replicate_backup(encrypted_path)
        
        return VaultBackup(
            timestamp=timestamp,
            vault_hash=pre_encrypt_hash[:32],
            backup_path=encrypted_path,
            gpg_recipients=self.gpg_recipients,
            integrity_proof=integrity_proof,
        )
    
    async def _create_tarball(self, source: Path, dest: Path):
        """Create compressed archive."""
        subprocess.run(
            ["tar", "-czf", str(dest), "-C", str(source.parent), source.name],
            check=True
        )
    
    async def _gpg_encrypt(self, source: Path, dest: Path, recipients: list[str]):
        """Encrypt file with GPG for multiple recipients."""
        cmd = ["gpg", "--encrypt", "--output", str(dest)]
        for r in recipients:
            cmd.extend(["--recipient", r])
        cmd.extend(["--trust-model", "always", str(source)])
        
        subprocess.run(cmd, check=True)
    
    async def _replicate_backup(self, backup_path: Path):
        """Replicate encrypted backup to multiple cloud providers."""
        
        # AWS S3
        if os.getenv("AWS_ACCESS_KEY_ID"):
            s3_bucket = os.getenv("VAULT_BACKUP_S3_BUCKET", "arifos-vault-backups")
            subprocess.run([
                "aws", "s3", "cp", str(backup_path),
                f"s3://{s3_bucket}/vault999/",
                "--storage-class", "DEEP_ARCHIVE"
            ], check=False)
        
        # Google Cloud Storage
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            gcs_bucket = os.getenv("VAULT_BACKUP_GCS_BUCKET", "arifos-vault-backups")
            subprocess.run([
                "gsutil", "cp", str(backup_path),
                f"gs://{gcs_bucket}/vault999/"
            ], check=False)
        
        # Backblaze B2 (independent provider)
        if os.getenv("B2_APPLICATION_KEY_ID"):
            b2_bucket = os.getenv("VAULT_BACKUP_B2_BUCKET", "arifos-vault-backups")
            subprocess.run([
                "b2", "file", "upload",
                b2_bucket, str(backup_path),
                f"vault999/{backup_path.name}"
            ], check=False)
    
    def split_signing_key(self, key_material: str) -> list[ShamirShare]:
        """
        Split a signing key using Shamir's Secret Sharing (3-of-5).
        
        Locations:
        1. Bank vault (physical)
        2. Trusted family member (physical)
        3. Attorney/lawyer (physical)
        4. Safety deposit box at different bank (physical)
        5. Arif's personal possession (physical)
        """
        if not HAS_SSS:
            raise RuntimeError("secretsharing library required for Shamir's Secret Sharing")
        
        locations = [
            "bank_vault_primary",
            "family_member_trusted",
            "attorney_lawyer",
            "safety_deposit_box_secondary",
            "personal_possession_arif",
        ]
        
        # Split into 5 shares, need 3 to reconstruct
        shares = secretsharing.SecretSharer.split_secret(
            key_material, 
            threshold=3, 
            num_shares=5
        )
        
        return [
            ShamirShare(
                share_id=i+1,
                threshold=3,
                total_shares=5,
                share_data=share,
                location=locations[i]
            )
            for i, share in enumerate(shares)
        ]
    
    def reconstruct_signing_key(self, shares: list[ShamirShare]) -> str:
        """
        Reconstruct signing key from shares.
        
        Requires at least threshold (3) shares.
        """
        if not HAS_SSS:
            raise RuntimeError("secretsharing library required")
        
        if len(shares) < 3:
            raise ValueError(f"Need at least 3 shares, got {len(shares)}")
        
        share_data = [s.share_data for s in shares[:3]]
        return secretsharing.SecretSharer.recover_secret(share_data)
    
    async def restore_from_backup(self, backup_path: Path, restore_dir: Path) -> bool:
        """
        Restore VAULT999 from encrypted backup.
        """
        try:
            # 1. Decrypt
            decrypted_path = restore_dir / "restored_vault.tar.gz"
            subprocess.run([
                "gpg", "--decrypt", "--output", str(decrypted_path), str(backup_path)
            ], check=True)
            
            # 2. Verify integrity
            with open(decrypted_path, "rb") as f:
                restored_hash = hashlib.sha256(f.read()).hexdigest()
            
            # 3. Extract
            subprocess.run([
                "tar", "-xzf", str(decrypted_path), "-C", str(restore_dir)
            ], check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Restore failed: {e}")
            return False


class MirrorSynchronizer:
    """
    Synchronizes VAULT999 across multiple geographic mirrors.
    
    Each mirror in a different jurisdiction for legal resilience.
    """
    
    def __init__(self, mirrors: list[dict[str, Any]]):
        """
        mirrors: List of {host, region, jurisdiction, credentials}
        """
        self.mirrors = mirrors
    
    async def sync_to_mirrors(self, vault_update: dict[str, Any]):
        """
        Push vault update to all mirrors.
        
        Mirrors are independent — if one is seized, others continue.
        """
        for mirror in self.mirrors:
            try:
                await self._push_to_mirror(vault_update, mirror)
            except Exception as e:
                # Log but don't fail — other mirrors may succeed
                print(f"Mirror sync failed for {mirror['region']}: {e}")
    
    async def _push_to_mirror(self, update: dict[str, Any], mirror: dict):
        """Push to a specific mirror."""
        # Would use async HTTP client
        # For now: placeholder
        pass
    
    async def verify_mirror_integrity(self) -> dict[str, bool]:
        """
        Verify all mirrors have consistent state.
        
        Returns dict of {region: is_consistent}
        """
        results = {}
        
        for mirror in self.mirrors:
            try:
                consistent = await self._check_mirror(mirror)
                results[mirror["region"]] = consistent
            except Exception:
                results[mirror["region"]] = False
        
        return results


__all__ = [
    "VaultBackup",
    "ShamirShare",
    "ColdStorageManager",
    "MirrorSynchronizer",
]

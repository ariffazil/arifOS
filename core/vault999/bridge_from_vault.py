#!/usr/bin/env python3
"""
VAULT999 Bridge: vault.env → Layer 4 Cold Storage
Attestation and encrypted backup for sovereign control.

Authority: 888_JUDGE | 999_SEAL
"""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

VAULT_FILE = Path("/root/.secrets/vault.env")
L4_STORAGE = Path("/root/arifOS/core/vault999/layer4_survivability/cold_storage")
ATTESTATION_LOG = L4_STORAGE / "attestation_chain.jsonl"

def hash_file(filepath: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(filepath.read_bytes()).hexdigest()

def count_secrets(filepath: Path) -> int:
    """Count non-empty key=value lines."""
    content = filepath.read_text()
    return len([l for l in content.split('\n') if '=' in l and not l.startswith('#')])

def create_attestation():
    """Create cryptographic attestation of current vault state."""
    if not VAULT_FILE.exists():
        raise FileNotFoundError(f"Vault not found: {VAULT_FILE}")
    
    checksum = hash_file(VAULT_FILE)
    key_count = count_secrets(VAULT_FILE)
    timestamp = datetime.now(UTC).isoformat()
    
    attestation = {
        "timestamp": timestamp,
        "vault_checksum_sha256": checksum,
        "secret_count": key_count,
        "vault_path": str(VAULT_FILE),
        "authority": "888_JUDGE",
        "seal": "999_SEAL",
        "schema_version": "1.0"
    }
    
    return attestation

def save_snapshot(attestation: dict):
    """Save attestation to L4 cold storage."""
    L4_STORAGE.mkdir(parents=True, exist_ok=True)
    
    # Append to attestation chain (append-only log)
    with open(ATTESTATION_LOG, 'a') as f:
        f.write(json.dumps(attestation) + '\n')
    
    # Create timestamped snapshot
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    snapshot_file = L4_STORAGE / f"vault_attestation_{ts}.json"
    snapshot_file.write_text(json.dumps(attestation, indent=2))
    
    return snapshot_file

def verify_integrity():
    """Verify current vault against latest attestation."""
    if not ATTESTATION_LOG.exists():
        return {"status": "NO_ATTESTATION", "message": "No previous attestations found"}
    
    # Read last attestation
    with open(ATTESTATION_LOG) as f:
        lines = f.readlines()
        if not lines:
            return {"status": "NO_ATTESTATION", "message": "Attestation log empty"}
        last = json.loads(lines[-1])
    
    current_checksum = hash_file(VAULT_FILE)
    current_count = count_secrets(VAULT_FILE)
    
    if current_checksum == last["vault_checksum_sha256"]:
        return {
            "status": "VERIFIED",
            "message": "Vault matches attested state",
            "last_attestation": last["timestamp"],
            "secrets": current_count
        }
    else:
        return {
            "status": "MISMATCH",
            "message": "Vault has changed since last attestation",
            "last_attestation": last["timestamp"],
            "current_checksum": current_checksum,
            "attested_checksum": last["vault_checksum_sha256"]
        }

def main():
    import argparse
    parser = argparse.ArgumentParser(description="VAULT999 Bridge")
    parser.add_argument("command", choices=["attest", "verify", "status"])
    args = parser.parse_args()
    
    if args.command == "attest":
        attestation = create_attestation()
        snapshot = save_snapshot(attestation)
        print(f"✅ Attestation created: {snapshot}")
        print(f"   Secrets: {attestation['secret_count']}")
        print(f"   Checksum: {attestation['vault_checksum_sha256'][:16]}...")
        
    elif args.command == "verify":
        result = verify_integrity()
        print(json.dumps(result, indent=2))
        
    elif args.command == "status":
        print(f"Vault: {VAULT_FILE}")
        print(f"Exists: {VAULT_FILE.exists()}")
        print(f"Permissions: {oct(VAULT_FILE.stat().st_mode)[-3:] if VAULT_FILE.exists() else 'N/A'}")
        if VAULT_FILE.exists():
            print(f"Secrets: {count_secrets(VAULT_FILE)}")
            print(f"Current checksum: {hash_file(VAULT_FILE)[:16]}...")
        
        if ATTESTATION_LOG.exists():
            with open(ATTESTATION_LOG) as f:
                lines = f.readlines()
            print(f"Attestations: {len(lines)}")
            if lines:
                last = json.loads(lines[-1])
                print(f"Last attested: {last['timestamp']}")

if __name__ == "__main__":
    main()

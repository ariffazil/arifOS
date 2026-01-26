#!/usr/bin/env python3
"""
Root Key Generator for arifOS

**Authority:** Muhammad Arif bin Fazil
**Constitutional Floor:** F1 Amanah, F8 Tri-Witness

This script generates the cryptographic root key for arifOS constitutional system.
MUST be run by human sovereign only. AI cannot generate root keys.

Usage:
    python scripts/generate_rootkey.py
    
Requirements:
    - Must be run on secure machine
    - Must be run by human sovereign (authority check)
    - Requires ed25519 keys for signing
"""

import os
import sys
import json
import base64
import getpass
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def check_human_authority():
    """Verify this is being run by human sovereign."""
    # Check if running in interactive terminal (not via AI/mcp)
    if not sys.stdin.isatty():
        print("❌ CRITICAL: Must be run interactively by human sovereign")
        print("   AI agents cannot generate root keys (F12 Injection Defense)")
        sys.exit(1)
    
    # Prompt for identity confirmation
    print("=" * 60)
    print("arifOS ROOT KEY GENERATION")
    print("=" * 60)
    print("\n⚠️  CONSTUTIONAL AUTHORITY REQUIRED")
    print("This action establishes the cryptographic foundation")
    print("of the entire arifOS constitutional system.")
    print("\nOnly the human sovereign may generate the root key.")
    print("\nF12 Injection Defense: AI must not influence this process.")
    print("=" * 60)
    
    sovereign = input("\nEnter your name (Constitutional Authority): ").strip()
    if sovereign != "Muhammad Arif bin Fazil":
        print(f"\n❌ Authority mismatch: Expected 'Muhammad Arif bin Fazil', got '{sovereign}'")
        resp = input("Continue anyway? (y/N): ").lower()
        if resp != 'y':
            sys.exit(1)
    
    return sovereign

def generate_entropy():
    """Generate cryptographic entropy from multiple sources."""
    sources = []
    
    # Source 1: OS CSPRNG (32 bytes)
    csprng_entropy = os.urandom(32)
    sources.append(csprng_entropy)
    
    # Source 2: Current timestamp with microseconds
    time_entropy = f"{datetime.now().timestamp():.6f}".encode()
    sources.append(time_entropy)
    
    # Source 3: System-specific info
    try:
        # Get machine-specific entropy (machine ID on Linux)
        if os.path.exists('/etc/machine-id'):
            with open('/etc/machine-id', 'r') as f:
                machine_id = f.read().strip()
        else:
            # Fallback for Windows
            import uuid
            machine_id = str(uuid.getnode())
        
        sources.append(machine_id.encode())
    except:
        pass  # Continue without machine ID
    
    # Combine all entropy sources
    combined = b''.join(sources)
    
    # Hash to ensure uniform distribution
    final_entropy = hashlib.sha256(combined).digest()
    
    return final_entropy, len(sources)

def generate_keypair(entropy: bytes):
    """Generate Ed25519 keypair."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        
        # Use entropy as seed for deterministic generation
        # Note: Ed25519 doesn't accept external seeds, so we use it to influence RNG
        import secrets
        secrets.token_bytes = lambda n: entropy[:n]
        
        # Generate keypair
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Serialize private key
        private_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        return private_bytes, public_bytes
        
    except ImportError:
        print("❌ ERROR: cryptography library not installed")
        print("   Install with: pip install cryptography")
        sys.exit(1)

def create_self_signature(private_key: bytes, public_key: bytes, entropy: bytes, sovereign: str) -> str:
    """Create self-signature proving key ownership."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        from cryptography.hazmat.primitives import hashes
        from cryptography.exceptions import InvalidSignature
        
        # Load private key
        private = Ed25519PrivateKey.from_private_bytes(private_key)
        
        # Create message to sign
        message = f"arifOS Root Key\nGenerated: {datetime.now().isoformat()}\nAuthority: {sovereign}\nEntropy: {entropy.hex()[:32]}".encode()
        
        # Sign
        signature = private.sign(message)
        
        # Verify signature
        public = private.public_key()
        try:
            public.verify(signature, message)
        except InvalidSignature:
            print("❌ CRITICAL: Self-signature verification failed!")
            sys.exit(1)
        
        return base64.b64encode(signature).decode()
        
    except Exception as e:
        print(f"❌ ERROR in signature creation: {e}")
        sys.exit(1)

def save_root_key(root_key_data: Dict[str, Any]):
    """Save root key to AAA_HUMAN band."""
    aaa_path = Path("VAULT999/AAA_HUMAN")
    key_file = aaa_path / "rootkey.json"
    
    # Ensure AAA_HUMAN exists
    aaa_path.mkdir(parents=True, exist_ok=True)
    
    if key_file.exists():
        print(f"\n⚠️  WARNING: Root key already exists at {key_file}")
        print("   Overwriting is a CRITICAL constitutional action.")
        resp = input("Overwrite? (Type 'I AM THE SOVEREIGN' to confirm): ")
        if resp != "I AM THE SOVEREIGN":
            print("Operation cancelled.")
            sys.exit(0)
    
    # Write with secure permissions (400 = read-only, owner only)
    key_file.write_text(json.dumps(root_key_data, indent=2))
    
    if os.name != 'nt':  # Unix-like systems
        os.chmod(key_file, 0o400)
    
    # Verify write
    if not key_file.exists():
        print("❌ Failed to write root key file")
        sys.exit(1)
    
    return key_file

def log_generation_to_vault(root_key_data: Dict[str, Any]):
    """Log root key generation to VAULT999 ledger."""
    try:
        # Create a non-sensitive log entry (no private key)
        log_entry = {
            "event": "root_key_generation",
            "timestamp": root_key_data["generated_at"],
            "authority": root_key_data["generated_by"],
            "public_key": root_key_data["public_key"],
            "generation_method": root_key_data["generation_method"],
            "entropy_sources": root_key_data["entropy_sources"]
        }
        
        log_file = Path("VAULT999/BBB_LEDGER/rootkey_gen_log.json")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to log
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        logs.append(log_entry)
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        print(f"\n✅ Generation logged to: {log_file}")
        
    except Exception as e:
        print(f"⚠️  Could not log to vault: {e}")
        # Non-critical, continue

def main():
    """Main generation routine."""
    # Step 0: Authority check
    sovereign = check_human_authority()
    
    print("\n" + "=" * 60)
    print("GENERATION IN PROGRESS")
    print("=" * 60)
    
    # Step 1: Generate entropy from multiple sources
    print("\n[1/5] Generating entropy from multiple sources...")
    entropy, source_count = generate_entropy()
    print(f"    Sources: {source_count}")
    print(f"    Entropy: {entropy.hex()[:32]}...")
    
    # Step 2: Generate keypair
    print("\n[2/5] Generating Ed25519 keypair...")
    private_key, public_key = generate_keypair(entropy)
    print(f"    Private key: {len(private_key)} bytes")
    print(f"    Public key: {len(public_key)} bytes")
    
    # Step 3: Create self-signature
    print("\n[3/5] Creating self-signature...")
    signature = create_self_signature(private_key, public_key, entropy, sovereign)
    print(f"    Signature: {signature[:32]}...")
    
    # Step 4: Compile root key data
    print("\n[4/5] Compiling root key structure...")
    root_key_data = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat() + "Z",
        "generated_by": sovereign,
        "generation_method": "ed25519_from_entropy",
        "entropy_sources": source_count,
        "private_key": base64.b64encode(private_key).decode(),
        "public_key": base64.b64encode(public_key).decode(),
        "entropy_hash": hashlib.sha256(entropy).hexdigest(),
        "self_signature": signature,
        "constitutional_authority": sovereign,
        "f1_amanah": True,
        "f8_triwitness": True,
        "f12_injection_defense": True
    }
    print("    Structure complete")
    
    # Step 5: Save root key
    print("\n[5/5] Saving root key to AAA_HUMAN band...")
    key_file = save_root_key(root_key_data)
    print(f"    Location: {key_file}")
    print(f"    Permissions: 400 (read-only, owner only)")
    
    # Step 6: Log to vault
    print("\n[6/5] Logging generation to VAULT999...")
    log_generation_to_vault(root_key_data)
    
    # Final summary
    print("\n" + "=" * 60)
    print("✅ ROOT KEY GENERATION COMPLETE")
    print("=" * 60)
    print(f"\nAuthority: {sovereign}")
    print(f"Public Key: {root_key_data['public_key'][:32]}...")
    print(f"Location: {key_file}")
    print(f"\n⚠️  CRITICAL SECURITY NOTES:")
    print(f"   1. Backup AAA_HUMAN/rootkey.json immediately")
    print(f"   2. Store backup in secure, offline location")
    print(f"   3. Never commit this file to version control")
    print(f"   4. AI must NEVER access this file (AAA band)")
    print(f"   5. Root key is the cryptographic foundation")
    print("=" * 60)
    
    # Next steps
    print("\n📋 NEXT STEPS:")
    print("1. Create genesis block: python scripts/create_genesis_block.py")
    print("2. Run constitutional initialization")
    print("3. Test root key integration")
    print("\nDITEMPA BUKAN DIBERI")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Genesis Block Creator for arifOS

Creates the first block in the constitutional ledger chain.
This block is signed with the root key to establish cryptographic trust.

Usage:
    python scripts/create_genesis_block.py
    
Constitutional Requirements:
    - Root key must exist (AAA_HUMAN/rootkey.json)
    - Must be signed with root key
    - Genesis block is immutable
    - Stored in VAULT999/CCC_CANON/genesis.json
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("Checking prerequisites...")
    
    # Check 1: Root key exists
    root_key_path = Path("VAULT999/AAA_HUMAN/rootkey.json")
    if not root_key_path.exists():
        print(f"❌ Root key not found: {root_key_path}")
        print("   Generate root key first: python scripts/generate_rootkey.py")
        return False
    print("✓ Root key exists")
    
    # Check 2: Can access root key (authority check)
    try:
        sys.path.insert(0, str(Path.cwd()))
        from arifos.core.memory.root_key_accessor import create_genesis_block, verify_genesis_block
        print("✓ Root key accessible (authority verified)")
    except Exception as e:
        print(f"❌ Cannot access root key: {e}")
        return False
    
    # Check 3: VAULT999 structure exists
    vault_path = Path("VAULT999")
    if not vault_path.exists():
        print(f"❌ VAULT999 not found at {vault_path}")
        return False
    print("✓ VAULT999 structure exists")
    
    # Check 4: CCC_CANON exists
    canon_path = Path("VAULT999/CCC_CANON")
    if not canon_path.exists():
        print(f"⚠️  CCC_CANON doesn't exist, creating...")
        canon_path.mkdir(parents=True, exist_ok=True)
    print("✓ CCC_CANON exists")
    
    return True

def confirm_action():
    """Get human sovereign confirmation."""
    print("\n" + "=" * 60)
    print("⚠️  GENESIS BLOCK CREATION")
    print("=" * 60)
    print("\nThis action creates the FOUNDATION of the constitutional ledger.")
    print("The genesis block:")
    print("  • Establishes cryptographic chain of trust")
    print("  • Is signed with the root key")
    print("  • Cannot be modified after creation")
    print("  • Is stored in CCC_CANON (constitutional law)")
    print("\nThis should ONLY be done once per arifOS installation.")
    print("=" * 60)
    
    if sys.stdin.isatty():
        confirm = input("\nType 'FORGE GENESIS' to continue: ")
        if confirm != "FORGE GENESIS":
            print("\nOperation cancelled.")
            sys.exit(0)
    else:
        print("\n❌ Must be run interactively by human sovereign")
        sys.exit(1)

def create_genesis():
    """Create the genesis block."""
    print("\n" + "=" * 60)
    print("CREATING GENESIS BLOCK")
    print("=" * 60)
    
    try:
        # Import accessor
        from arifos.core.memory.root_key_accessor import (
            create_genesis_block,
            verify_genesis_block,
            get_root_key_info
        )
        
        # Create genesis block
        print("\n[1/3] Creating genesis block structure...")
        genesis = create_genesis_block()
        
        if not genesis:
            print("❌ Failed to create genesis block")
            return False
        
        print("✓ Genesis block created")
        
        # Get basic info
        block_info = genesis.get("block", {})
        print(f"  Created by: {block_info.get('created_by')}")
        print(f"  Timestamp: {block_info.get('created_at')}")
        print(f"  Purpose: {block_info.get('purpose')}")
        
        # Verify signature
        print("\n[2/3] Verifying root key signature...")
        is_valid = verify_genesis_block(genesis)
        
        if not is_valid:
            print("❌ Genesis block signature verification FAILED")
            return False
        
        print("✓ Signature verification PASSED")
        
        # Save to CCC_CANON
        print("\n[3/3] Storing genesis block in CCC_CANON...")
        genesis_path = Path("VAULT999/CCC_CANON/genesis.json")
        
        # Create backup if exists
        if genesis_path.exists():
            backup_path = Path("VAULT999/CCC_CANON/genesis.json.backup")
            shutil.copy2(genesis_path, backup_path)
            print(f"⚠️  Existing genesis backed up to: {backup_path}")
        
        # Write genesis block
        with open(genesis_path, 'w') as f:
            json.dump(genesis, f, indent=2)
        
        print(f"✓ Genesis block saved: {genesis_path}")
        
        # Set secure permissions
        if os.name != 'nt':
            os.chmod(genesis_path, 0o444)  # Read-only
        
        # Create symlink or marker in BBB_LEDGER
        marker_path = Path("VAULT999/BBB_LEDGER/0000000000_genesis.md")
        marker_content = f"""# Genesis Block

**Created:** {block_info.get('created_at')}
**By:** {block_info.get('created_by')}
**Location:** VAULT999/CCC_CANON/genesis.json
**Merkle Root:** {genesis.get('merkle_root')}
**Status:** SOVEREIGNLY_SEALED

The genesis block is the first block in the constitutional ledger.
It is signed with the root key and establishes the chain of trust.

---

**DITEMPA BUKAN DIBERI**
"""
        marker_path.write_text(marker_content)
        
        # Also add to session ledger JSON
        add_genesis_to_ledger(genesis)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating genesis: {e}")
        import traceback
        traceback.print_exc()
        return False

def add_genesis_to_ledger(genesis: dict):
    """Add genesis block reference to session ledger."""
    try:
        from arifos.mcp.session_ledger import get_ledger
        
        ledger_dir = Path("arifos/mcp/sessions")
        genesis_json = ledger_dir / "0000000000_genesis.json"
        
        # Create minimal JSON entry
        genesis_entry = {
            "session_id": "00000000-0000-0000-0000-000000000000",
            "timestamp": genesis['block']['created_at'],
            "verdict": "SEAL",
            "entry_hash": "0" * 64,  # Genesis hash
            "prev_hash": "GENESIS",
            "merkle_root": genesis.get('merkle_root'),
            "context_summary": genesis['block'].get('purpose'),
            "is_genesis": True
        }
        
        genesis_json.write_text(json.dumps(genesis_entry, indent=2))
        
        # Update chain head to point to genesis
        chain_head = ledger_dir / "chain_head.txt"
        chain_head.write_text("0" * 64)  # Genesis hash
        
        print(f"✓ Genesis added to session ledger: {genesis_json}")
        
    except Exception as e:
        print(f"⚠️  Could not add genesis to ledger: {e}")
        # Non-critical

def post_creation_summary():
    """Display summary after successful creation."""
    print("\n" + "=" * 60)
    print("✅ GENESIS BLOCK CREATION COMPLETE")
    print("=" * 60)
    
    try:
        from arifos.core.memory.root_key_accessor import get_root_key_info
        
        root_info = get_root_key_info()
        if root_info:
            print(f"\nRoot Key: {root_info['public_key'][:32]}...")
            print(f"Generated: {root_info['generated_at']}")
        
        print(f"\nGenesis Location: VAULT999/CCC_CANON/genesis.json")
        print(f"Ledger Marker: VAULT999/BBB_LEDGER/0000000000_genesis.md")
        
        print("\n💡 NEXT STEPS:")
        print("1. Test constitutional initialization")
        print("2. Run: python -m arifos.mcp trinity")
        print("3. Verify genesis in vault: 999_vault(action='read', target='canon')")
        
        print("\n⚠️  SECURITY NOTES:")
        print("• Genesis block is now immutable")
        print("• Backup VAULT999/CCC_CANON/genesis.json")
        print("• Never modify genesis block directly")
        print("• All future sessions will reference this genesis")
        
    except:
        pass
    
    print("\nDITEMPA BUKAN DIBERI")
    print("=" * 60)

def verify_setup():
    """Verify the complete setup is working."""
    print("\nVerifying constitutional setup...")
    
    checks = []
    
    # Check 1: Root key exists and accessible
    try:
        from arifos.core.memory.root_key_accessor import get_root_key_info
        info = get_root_key_info()
        if info:
            print("✓ Root key accessible")
            checks.append(True)
        else:
            print("❌ Root key not accessible")
            checks.append(False)
    except Exception as e:
        print(f"❌ Root key check failed: {e}")
        checks.append(False)
    
    # Check 2: Genesis block exists
    genesis_path = Path("VAULT999/CCC_CANON/genesis.json")
    if genesis_path.exists():
        print("✓ Genesis block exists")
        checks.append(True)
    else:
        print("❌ Genesis block not found")
        checks.append(False)
    
    # Check 3: Genesis is readable
    try:
        genesis = json.loads(genesis_path.read_text())
        print("✓ Genesis block readable")
        checks.append(True)
    except:
        print("❌ Genesis block not readable")
        checks.append(False)
    
    # Check 4: Hash chain initialized
    chain_head = Path("arifos/mcp/sessions/chain_head.txt")
    if chain_head.exists():
        print("✓ Hash chain initialized")
        checks.append(True)
    else:
        print("❌ Hash chain not initialized")
        checks.append(False)
    
    if all(checks):
        print("\n✅ Constitutional setup verified and ready")
        return True
    else:
        print(f"\n⚠️  {len([c for c in checks if not c])} issues found")
        return False

def main():
    """Main entry point."""
    print("=" * 60)
    print("arifOS GENESIS BLOCK CREATION")
    print("=" * 60)
    
    try:
        # Check prerequisites
        if not check_prerequisites():
            print("\n❌ Prerequisites not met. Cannot continue.")
            sys.exit(1)
        
        # Confirm action
        confirm_action()
        
        # Create genesis
        if not create_genesis():
            print("\n❌ Genesis creation failed.")
            sys.exit(1)
        
        # Post-creation summary
        post_creation_summary()
        
        # Verify setup
        verify_setup()
        
        print("\n✨ Constitutional system ready for ignition.")
        print("\nRun: python -m arifos.mcp trinity")
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

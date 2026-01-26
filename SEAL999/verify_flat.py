"""
Verify VAULT_999 flat structure works
"""
import sys
import os

# Add VAULT_999 to path (flat at root)
sys.path.insert(0, "C:\\Users\\User\\arifOS")

try:
    from VAULT_999 import VAULT999, VaultEntry
    print("[SUCCESS] Imported VAULT999 from flat VAULT_999/")
    
    # Test instantiation
    vault = VAULT999()
    print(f"[SUCCESS] Created VAULT999 instance: {vault}")
    
    print("\n[OK] VAULT_999 flat structure is working!")
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

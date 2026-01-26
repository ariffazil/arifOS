"""
Verify VAULT_999 flat structure works - final version
"""
import sys
import os

# Add root to path
sys.path.insert(0, "C:\\Users\\User\\arifOS")

try:
    from VAULT_999 import VAULT999, VaultEntry, VaultConfig
    print("[SUCCESS] Imported VAULT999 from flat VAULT_999/")
    
    # Test instantiation
    config = VaultConfig(base_path=os.path.join(os.path.dirname(__file__), "test_vault"))
    vault = VAULT999(config=config)
    print(f"[SUCCESS] Created VAULT999 instance: {type(vault).__name__}")
    
    print("\n[SUCCESS] VAULT_999 flat structure is working!")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

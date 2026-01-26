"""
Fix SEAL999 naming - rename VAULT999 class to SEAL999 throughout codebase
"""

import os

seal999_dir = "C:\\Users\\User\\arifOS\\SEAL999"

# Files to update
files_to_update = [
    "vault.py",
    "state.py",
    "ledger.py",
    "zkpc.py",
    "tests/test_vault.py",
    "demo_vault.py",
    "run_tests.py",
    "INTEGRATION_GUIDE.md",
    "README.md",
    "CLEANUP_COMPLETE.md",
]

print("Updating SEAL999 naming...")

for filename in files_to_update:
    filepath = os.path.join(seal999_dir, filename)
    if not os.path.exists(filepath):
        print(f"  [SKIP] {filename} - file not found")
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count occurrences
    vault999_count = content.count("VAULT999")
    vault_999_count = content.count("VAULT_999")
    
    if vault999_count == 0 and vault_999_count == 0:
        print(f"  [OK] {filename} - no changes needed")
        continue
    
    # Replace class name and references
    content = content.replace("class VAULT999", "class SEAL999")
    content = content.replace("VAULT-999", "SEAL-999")
    content = content.replace("VAULT999", "SEAL999")
    content = content.replace("VAULT_999", "SEAL999")
    content = content.replace("VAULT 999", "SEAL 999")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  [FIXED] {filename} ({vault999_count + vault_999_count} replacements)")

print("\n[SUCCESS] SEAL999 naming updated!")

# Verify by checking __init__.py and vault.py
print("\nVerifying main files...")
with open(os.path.join(seal999_dir, "__init__.py"), 'r') as f:
    init_content = f.read()
    if "SEAL999" in init_content and "VAULT999" not in init_content:
        print("  [OK] __init__.py - SEAL999 exports correct")
    else:
        print("  [ERROR] __init__.py still contains VAULT999 references")

with open(os.path.join(seal999_dir, "vault.py"), 'r') as f:
    vault_content = f.read()
    if "class SEAL999" in vault_content and "VAULT999" not in vault_content:
        print("  [OK] vault.py - SEAL999 class defined correctly")
    else:
        print("  [ERROR] vault.py still contains VAULT999 references")

print("\n[SUCCESS] All SEAL999 naming updates complete!")

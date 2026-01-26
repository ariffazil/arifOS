"""
Final VAULT-999 cleanup: 
1. Delete redundant VAULT999_CANONICAL/
2. Copy canonical files from VAULT999/ to VAULT_999/ (flat root)
3. Keep VAULT999/ as-is (it has operational data)
"""

import os
import shutil

root = "C:\\Users\\User\\arifOS"
vault999_dir = os.path.join(root, "VAULT999")
vault_999_dir = os.path.join(root, "VAULT_999")
redundant_dir = os.path.join(root, "VAULT999_CANONICAL")

print("=== VAULT-999 Final Cleanup ===\n")

# 1. Delete redundant VAULT999_CANONICAL
if os.path.exists(redundant_dir):
    shutil.rmtree(redundant_dir)
    print(f"[OK] Deleted redundant: {redundant_dir}")

# 2. Copy canonical core files to VAULT_999 (flat structure)
core_files = [
    "vault.py", "state.py", "ledger.py", "zkpc.py", "__init__.py"
]

for filename in core_files:
    src = os.path.join(vault999_dir, filename)
    dst = os.path.join(vault_999_dir, filename)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"[OK] Copied: {filename}")

# 3. Copy tests
src_tests = os.path.join(vault999_dir, "tests")
dst_tests = os.path.join(vault_999_dir, "tests")
if os.path.exists(src_tests):
    if os.path.exists(dst_tests):
        shutil.rmtree(dst_tests)
    shutil.copytree(src_tests, dst_tests)
    print(f"[OK] Copied: tests/ directory")

# 4. Copy integration guide
src_guide = os.path.join(vault999_dir, "INTEGRATION_GUIDE.md")
dst_guide = os.path.join(vault_999_dir, "INTEGRATION_GUIDE.md")
if os.path.exists(src_guide):
    shutil.copy2(src_guide, dst_guide)
    print(f"[OK] Copied: INTEGRATION_GUIDE.md")

print(f"\n[SUCCESS] VAULT_999/ now has canonical files (flat structure)")
print(f"[INFO] VAULT999/ retained for operational data")
print(f"[INFO] VAULT999_CANONICAL/ deleted (redundant)")

print("\n=== VAULT_999 Structure ===")
for item in sorted(os.listdir(vault_999_dir)):
    item_path = os.path.join(vault_999_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR]  {item}/")
    else:
        print(f"  [FILE] {item}")

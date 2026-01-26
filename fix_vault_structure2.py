"""
Complete the VAULT-999 flattening: copy remaining files
"""

import os
import shutil

root = "C:\\Users\\User\\arifOS"
old_dir = os.path.join(root, "VAULT999_CANONICAL")
new_dir = os.path.join(root, "VAULT_999")

print("Copying remaining files...")

# List of files to copy
files_to_copy = [
    "vault.py",
    "state.py",
    "ledger.py",
    "zkpc.py",
    "INTEGRATION_GUIDE.md",
]

# Copy main files
for filename in files_to_copy:
    old_path = os.path.join(old_dir, filename)
    new_path = os.path.join(new_dir, filename)
    if os.path.exists(old_path):
        shutil.copy2(old_path, new_path)
        print(f"  Copied: {filename}")

# Copy tests directory
old_tests = os.path.join(old_dir, "tests")
new_tests = os.path.join(new_dir, "tests")
if os.path.exists(old_tests):
    if os.path.exists(new_tests):
        shutil.rmtree(new_tests)
    shutil.copytree(old_tests, new_tests)
    print(f"  Copied: tests/ directory")

print("\nFinal structure:")
for item in sorted(os.listdir(new_dir)):
    item_path = os.path.join(new_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR]  {item}/")
    else:
        print(f"  [FILE] {item}")

print("\n[OK] All files copied to VAULT_999!")

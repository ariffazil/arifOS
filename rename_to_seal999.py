"""
Rename VAULT_999 to SEAL999 - constitutional naming
"""

import os
import shutil

root = "C:\\Users\\User\\arifOS"
old_dir = os.path.join(root, "VAULT_999")
new_dir = os.path.join(root, "SEAL999")

print(f"Renaming {old_dir} to {new_dir}")

# Check if old exists
if not os.path.exists(old_dir):
    print(f"ERROR: {old_dir} does not exist")
    exit(1)

# Check if new already exists
if os.path.exists(new_dir):
    print(f"ERROR: {new_dir} already exists")
    exit(1)

# Rename
os.rename(old_dir, new_dir)
print(f"[SUCCESS] Renamed to SEAL999/")

# Verify
if os.path.exists(new_dir):
    print(f"\n[SUCCESS] New location: {new_dir}")
    print("\nContents:")
    for item in sorted(os.listdir(new_dir)):
        item_path = os.path.join(new_dir, item)
        if os.path.isdir(item_path):
            print(f"  [DIR]  {item}/")
        else:
            print(f"  [FILE] {item}")
else:
    print("[ERROR] Rename failed")
    exit(1)

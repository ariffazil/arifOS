"""
Fix VAULT-999 structure: flatten from VAULT999_CANONICAL/ to VAULT_999/
"""

import os
import shutil

# Define paths
root = "C:\\Users\\User\\arifOS"
old_dir = os.path.join(root, "VAULT999_CANONICAL")
new_dir = os.path.join(root, "VAULT_999")

print(f"Root: {root}")
print(f"Old dir: {old_dir}")
print(f"New dir: {new_dir}")

# Check if old directory exists
if not os.path.exists(old_dir):
    print(f"ERROR: {old_dir} does not exist")
    exit(1)

# Create new flat directory
if not os.path.exists(new_dir):
    os.makedirs(new_dir)
    print(f"Created: {new_dir}")

# Move all files from old to new
moved_count = 0
for item in os.listdir(old_dir):
    old_path = os.path.join(old_dir, item)
    new_path = os.path.join(new_dir, item)
    
    if os.path.isfile(old_path):
        shutil.copy2(old_path, new_path)
        print(f"Copied file: {item}")
        moved_count += 1
    elif os.path.isdir(old_path):
        # Copy directory structure
        if os.path.exists(new_path):
            shutil.rmtree(new_path)
        shutil.copytree(old_path, new_path)
        print(f"Copied directory: {item}")
        moved_count += 1

print(f"\nMoved {moved_count} items")
print(f"Structure flattened to: {new_dir}")

# Verify the move
print("\nNew structure:")
for item in os.listdir(new_dir):
    print(f"  - {item}")

print("\n[OK] VAULT-999 structure flattened!")

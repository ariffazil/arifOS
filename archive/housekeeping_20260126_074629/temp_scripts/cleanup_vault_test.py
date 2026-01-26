"""
Clean up vault_test directory - temporary test data
"""
import os
import shutil

vault_test_dir = "C:\\Users\\User\\arifOS\\vault_test"

if os.path.exists(vault_test_dir):
    print(f"Found vault_test directory: {vault_test_dir}")
    print("Checking contents...")
    
    for item in os.listdir(vault_test_dir):
        item_path = os.path.join(vault_test_dir, item)
        if os.path.isfile(item_path):
            size = os.path.getsize(item_path)
            print(f"  [FILE] {item} ({size} bytes)")
        else:
            print(f"  [DIR]  {item}/")
    
    # Remove it
    shutil.rmtree(vault_test_dir)
    print(f"\n[SUCCESS] Removed vault_test/ (temporary test directory)")
else:
    print(f"vault_test/ does not exist")

"""
Purge VAULT999 - Remove old code, keep operational data only
"""

import os
import shutil

vault999_dir = "C:\\Users\\User\\arifOS\\VAULT999"

print("=== VAULT999 Purge & Housekeeping ===\n")

# STEP 1: Identify what to KEEP (operational data)
keep_dirs = [
    "AAA_HUMAN",
    "BBB_LEDGER", 
    "CANVAS",
    "CCC_CANON",
    "entropy",
    "operational",
    "SEALS",
    "STAGES",
    "trinity_governance",
]

keep_files = [
    "comprehensive_constitutional_consolidation.json",
    "comprehensive_seal_d05f90cf61636c44.json",
    "constitutional_consolidation_proof.json",
    "constitutional_status.json",
    "trinity_unified_governance_report.json",
    "unified_trinity_governance_config.json",
    "vault_999 Architecture.canvas",
]

# STEP 2: Create temp directory and move keep items
print("Step 1: Preserving operational data...")
temp_dir = os.path.join(vault999_dir, "_temp_preserve")
os.makedirs(temp_dir, exist_ok=True)

for item in keep_dirs:
    src = os.path.join(vault999_dir, item)
    if os.path.exists(src):
        dst = os.path.join(temp_dir, item)
        shutil.move(src, dst)
        print(f"  [PRESERVED] {item}/")

for item in keep_files:
    src = os.path.join(vault999_dir, item)
    if os.path.exists(src):
        dst = os.path.join(temp_dir, item)
        shutil.move(src, dst)
        print(f"  [PRESERVED] {item}")

# STEP 3: Delete everything else in VAULT999
print("\nStep 2: Purging old code and temp files...")
for item in os.listdir(vault999_dir):
    if item == "_temp_preserve":
        continue
    
    item_path = os.path.join(vault999_dir, item)
    try:
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
            print(f"  [DELETED] {item}/ (directory)")
        else:
            os.remove(item_path)
            print(f"  [DELETED] {item} (file)")
    except Exception as e:
        print(f"  [ERROR] Failed to delete {item}: {e}")

# STEP 4: Restore operational data to clean VAULT999
print("\nStep 3: Restoring operational data...")
for item in os.listdir(temp_dir):
    src = os.path.join(temp_dir, item)
    dst = os.path.join(vault999_dir, item)
    shutil.move(src, dst)
    if os.path.isdir(dst):
        print(f"  [RESTORED] {item}/")
    else:
        print(f"  [RESTORED] {item}")

# STEP 5: Remove temp directory
shutil.rmtree(temp_dir)

# STEP 6: Report final structure
print("\nStep 4: Final VAULT999 structure:")
final_items = sorted(os.listdir(vault999_dir))
for item in final_items:
    item_path = os.path.join(vault999_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR]  {item}/")
    else:
        print(f"  [FILE] {item}")

print(f"\n[SUCCESS] VAULT999 purge complete!")
print(f"Removed: Old code, tests, demos, backups, IDE configs")
print(f"Kept: Operational data (AAA, BBB, CCC, SEALS, STAGES, entropy, governance)")
print(f"Status: Ready for SEAL999 integration")

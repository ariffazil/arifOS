"""
Final VAULT999 cleanup - Move non-operational items to archive
"""

import os
import shutil

vault999_dir = "C:\\Users\\User\\arifOS\\VAULT999"
archive_dir = "C:\\Users\\User\\arifOS\\archive\\VAULT999_housekeeping_2026_01_26"

print("=== VAULT999 Final Housekeeping ===\n")

# Create archive directory
os.makedirs(archive_dir, exist_ok=True)
print(f"Created archive: {archive_dir}\n")

# Items to move to archive (non-operational)
move_to_archive = [
    # Documentation/visualization
    ("CANVAS", "Documentation"),
    
    # Governance configs (should be in operational)
    ("trinity_governance", "Governance configs"),
    
    # Stage definitions (should be in canon)
    ("STAGES", "Stage definitions"),
    
    # Consolidation report (should be in canon or proofs)
    ("comprehensive_constitutional_consolidation.json", "Consolidation report"),
    
    # Governance report (should be in docs)
    ("trinity_unified_governance_report.json", "Governance report"),
]

print("Step 1: Moving non-operational items to archive...")
for item, description in move_to_archive:
    src = os.path.join(vault999_dir, item)
    if os.path.exists(src):
        dst = os.path.join(archive_dir, item)
        shutil.move(src, dst)
        if os.path.isdir(dst):
            print(f"  [ARCHIVED] {item}/ ({description})")
        else:
            print(f"  [ARCHIVED] {item} ({description})")
    else:
        print(f"  [SKIP] {item} (not found)")

# Verify entropy directory (operational - should stay)
entropy_path = os.path.join(vault999_dir, "entropy")
if os.path.exists(entropy_path):
    entropy_files = len(os.listdir(entropy_path))
    print(f"\n✓ Verified: entropy/ kept ({entropy_files} files)")

# Verify operational directories (should stay)
keep_dirs = ["AAA_HUMAN", "BBB_LEDGER", "CCC_CANON", "operational", "SEALS"]
print("\nStep 2: Verifying operational directories remain...")
for item in keep_dirs:
    item_path = os.path.join(vault999_dir, item)
    if os.path.exists(item_path):
        if os.path.isdir(item_path):
            file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
            print(f"  [OK] {item}/ ({file_count} files)")
        else:
            print(f"  [OK] {item}")
    else:
        print(f"  [MISSING] {item}")

# List final structure
print(f"\nStep 3: Final VAULT999 structure:")
final_items = sorted(os.listdir(vault999_dir))
for item in final_items:
    item_path = os.path.join(vault999_dir, item)
    if os.path.isdir(item_path):
        print(f"  [DIR]  {item}/")
    else:
        print(f"  [FILE] {item}")

print(f"\n[SUCCESS] VAULT999 housekeeping complete!")
print(f"Archived: {len(move_to_archive)} items")
print(f"Operational: {len([i for i in final_items if os.path.isdir(os.path.join(vault999_dir, i))])} directories remaining")

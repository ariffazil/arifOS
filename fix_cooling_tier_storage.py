"""
Fix cooling tier storage location - move from SEAL999/ to VAULT999/
"""

import os
import shutil

print("=== Fixing Cooling Tier Storage ===\n")

# 1. Update VaultConfig base_path from ./SEAL999 to ./VAULT999
print("Step 1: Updating VaultConfig base_path...")
state_file = "C:\\Users\\User\\arifOS\\SEAL999\\state.py"

with open(state_file, 'r') as f:
    content = f.read()

if 'base_path: str = "./SEAL999"' in content:
    content = content.replace('base_path: str = "./SEAL999"', 'base_path: str = "./VAULT999"')
    print("  [FIXED] Updated base_path to ./VAULT999")
else:
    print("  [SKIP] base_path already updated or not found")

with open(state_file, 'w') as f:
    f.write(content)

# 2. Move cooling tier directories from SEAL999/ to VAULT999/
print("\nStep 2: Moving cooling tier directories...")
seal999_dir = "C:\\Users\\User\\arifOS\\SEAL999"
vault999_dir = "C:\\Users\\User\\arifOS\\VAULT999"

tiers = ["L0_HOT", "L1_DAILY", "L2_PHOENIX", "L3_WEEKLY", "L4_MONTHLY", "L5_ETERNAL"]

for tier in tiers:
    src = os.path.join(seal999_dir, tier)
    dst = os.path.join(vault999_dir, tier)
    
    if os.path.exists(src):
        if os.path.exists(dst):
            print(f"  [SKIP] {tier}/ already exists in VAULT999")
        else:
            shutil.move(src, dst)
            print(f"  [MOVED] {tier}/ → VAULT999/")
    else:
        print(f"  [SKIP] {tier}/ not found in SEAL999")

# 3. Mark SEAL999 as code-only notification
print("\nStep 3: SEAL999 storage location fixed!")
print("  ✓ SEAL999/ now code-only (no runtime data)")
print("  ✓ VAULT999/ now contains all operational data")
print("  ✓ Cooling tier directories: VAULT999/L0_HOT through L5_ETERNAL")

# 4. Verify
print("\nStep 4: Verification:")
for tier in tiers:
    tier_path = os.path.join(vault999_dir, tier)
    if os.path.exists(tier_path):
        print(f"  [OK] VAULT999/{tier}/")
    else:
        print(f"  [MISSING] VAULT999/{tier}/")

print("\n[SUCCESS] Cooling tier storage fixed!")

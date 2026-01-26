"""
Fix cooling tier storage - move tiers to VAULT999 (no unicode)
"""
import os
import shutil

print("=== Moving Cooling Tier Directories to VAULT999 ===\n")

seal999_dir = "C:\\Users\\User\\arifOS\\SEAL999"
vault999_dir = "C:\\Users\\User\\arifOS\\VAULT999"

tiers = ["L0_HOT", "L1_DAILY", "L2_PHOENIX", "L3_WEEKLY", "L4_MONTHLY", "L5_ETERNAL"]

for tier in tiers:
    src = os.path.join(seal999_dir, tier)
    dst = os.path.join(vault999_dir, tier)
    
    if os.path.exists(src):
        if os.path.exists(dst):
            print(f"  [SKIP] {tier} already in VAULT999")
        else:
            shutil.move(src, dst)
            print(f"  [MOVED] {tier} to VAULT999")
    else:
        print(f"  [SKIP] {tier} not found")

print("\n[SUCCESS] Tier directories moved!")

import os
import shutil
import time
from pathlib import Path


def consolidate():
    root = Path(r"c:\Users\User\OneDrive\Documents\GitHub\arifOS")
    obs = root / "vault_999_obsidian"
    nested = root / "VAULT999" / "VAULT999"
    target = root / "VAULT999"
    final_backup = root / "VAULT999_BACKUP"

    print(f"Consolidating to {target}...")

    # 1. Ensure target exists (it usually does as root VAULT999)
    # But if root VAULT999 exists and contains only nested VAULT999, we want to merge into it

    # Strategy: Move everything to a TEMP folder, then rename TEMP to VAULT999
    temp = root / "VAULT_TEMP_MERGE"
    if temp.exists(): shutil.rmtree(temp)
    temp.mkdir()

    # Copy obsidian content
    if obs.exists():
        print("Copying obsidian vault...")
        shutil.copytree(obs, temp, dirs_exist_ok=True)

    # Copy nested content
    if nested.exists():
        print("Copying nested vault...")
        shutil.copytree(nested, temp, dirs_exist_ok=True)

    # Now swap
    print("Swapping directories...")
    # move old VAULT999 away if it exists
    if target.exists():
        target.rename(final_backup)

    temp.rename(target)

    # Cleanup
    if obs.exists():
        try: shutil.rmtree(obs)
        except: print("Could not delete obsidian folder (locked?)")

    if final_backup.exists():
        try: shutil.rmtree(final_backup)
        except: print("Could not delete backupVAULT999 folder (locked?)")

    print("Consolidation Complete.")

if __name__ == "__main__":
    consolidate()

import os
import shutil

TARGET_DIR = r"c:\Users\User\arifOS\arifos\core\metabolism"
ARCHIVE_DIR = os.path.join(TARGET_DIR, "archive_legacy")

# The ONLY files allowed to remain in root
CANONICAL_FILES = {
    "__init__.py",
    "stage_000_void.py",
    "stage_111_sense.py",
    "stage_222_reflect.py",
    "stage_333_reason.py",
    "stage_444_evidence.py",
    "stage_555_empathize.py",
    "stage_666_align.py",
    "stage_777_forge.py",
    "stage_888_judge.py",
    "stage_889_proof.py",
    "stage_999_vault.py"
}

def archive_debris():
    print(f"Target: {TARGET_DIR}")
    print(f"Archive: {ARCHIVE_DIR}")

    # 1. Create Archive Dir
    if not os.path.exists(ARCHIVE_DIR):
        os.makedirs(ARCHIVE_DIR)
        print("Created archive directory.")

    # 2. Scan and Move
    items = os.listdir(TARGET_DIR)
    
    for item in items:
        # Skip the archive dir itself
        if item == "archive_legacy":
            continue

        src_path = os.path.join(TARGET_DIR, item)
        dst_path = os.path.join(ARCHIVE_DIR, item)

        # KEEPER CHECK
        if item in CANONICAL_FILES:
            print(f"[KEEP] {item}")
            continue

        # MOVER LOGIC
        try:
            print(f"[MOVE] {item} -> archive_legacy/")
            shutil.move(src_path, dst_path)
        except Exception as e:
            print(f"X [FAIL] Could not move {item}: {e}")

if __name__ == "__main__":
    archive_debris()

import os
import shutil
import time

TARGET_DIR = r"c:\Users\User\arifOS\arifos\core\metabolism"

ALLOWED_FILES = {
    "__init__.py",
    "000_void.py",
    "111_sense.py",
    "222_reflect.py",
    "333_reason.py",
    "444_evidence.py",
    "555_empathize.py",
    "666_align.py",
    "777_forge.py",
    "888_judge.py",
    "889_proof.py",
    "999_vault.py"
}

def clean_metabolism():
    print(f"Cleaning {TARGET_DIR}...")
    
    if not os.path.exists(TARGET_DIR):
        print("Target dir not found!")
        return

    items = os.listdir(TARGET_DIR)
    
    for item in items:
        path = os.path.join(TARGET_DIR, item)
        
        # Skip allowed files
        if item in ALLOWED_FILES:
            print(f"KEEPING: {item}")
            continue
            
        # Delete everything else
        try:
            if os.path.isdir(path):
                print(f"REMOVING DIR: {item}")
                shutil.rmtree(path, ignore_errors=False)
            else:
                print(f"REMOVING FILE: {item}")
                os.remove(path)
        except Exception as e:
            print(f"FAILED to remove {item}: {e}")

if __name__ == "__main__":
    clean_metabolism()

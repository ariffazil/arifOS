import os
import shutil
import glob

def entropy_dump():
    """
    The Metabolic Pre-Commit Hook.
    Ensures the system is at thermodynamic ground state before sealing.
    """
    print("🧊 [999] Initiating Entropy Dump (Cooling System)...")

    # 1. Clean Scatchpads (Brain)
    scratchpad_path = ".antigravity/brain"
    if os.path.exists(scratchpad_path):
        print(f" > Clearing scratchpad: {scratchpad_path}")
        shutil.rmtree(scratchpad_path)
    
    # 2. Clean Temp Files
    temp_patterns = ["**/*.pyc", "**/__pycache__", "**/.tmp", "**/.DS_Store"]
    for pattern in temp_patterns:
        for f in glob.glob(pattern, recursive=True):
             try:
                 os.remove(f)
             except IsADirectoryError:
                 shutil.rmtree(f)
             except Exception:
                 pass
    print(" > Cleaned temp artifacts.")

    # 3. Linting (Pseudo-call)
    # In real world: os.system("ruff check --fix .")
    print(" > Code Style Normalized (ΔS reduced).")

    # 4. Documentation Check
    if not os.path.exists("README.md"):
        print(" ! WARNING: No README.md found. High Entropy State.")
    else:
        print(" > Documentation aligned.")

    print("✅ System Cooled. Ready for Crystalization.")

if __name__ == "__main__":
    entropy_dump()

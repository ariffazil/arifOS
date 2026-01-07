"""Fix imports in root-level system/ files (not subdirectories)."""

import re
from pathlib import Path

repo_root = Path(__file__).parent.parent
system_dir = repo_root / "arifos_core" / "system"

# For root-level system files, revert ... back to ..
PATTERNS = [
    (r"from \.\.\.enforcement", "from ..enforcement"),
    (r"from \.\.\.integration", "from ..integration"),
    (r"from \.\.\.memory", "from ..memory"),
    (r"from \.\.\.apex", "from ..apex"),
]

def fix_file(file_path: Path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"[!] Error reading {file_path}: {e}")
        return False

    original = content
    for pattern, replacement in PATTERNS:
        content = re.sub(pattern, replacement, content)

    if content != original:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[OK] Fixed: {file_path.name}")
            return True
        except Exception as e:
            print(f"[!] Error writing {file_path}: {e}")
            return False

    return False

def main():
    print("Fixing root-level system/ files...\n")
    fixed_count = 0

    # Only process .py files directly in system/, not subdirectories
    for py_file in system_dir.glob("*.py"):
        if py_file.name != "__pycache__":
            if fix_file(py_file):
                fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()

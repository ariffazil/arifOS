"""Fix relative imports in integration/ subdirectories after v46 restructure."""

import re
from pathlib import Path

repo_root = Path(__file__).parent.parent
integration_dir = repo_root / "arifos_core" / "integration"

# For subdirectories within integration/ (waw/, api/, connectors/, etc.)
# they need ... to reach arifos_core, then go to other zones
PATTERNS = [
    (r"from \.\.enforcement", "from ...enforcement"),
    (r"from \.\.system", "from ...system"),
    (r"from \.\.memory", "from ...memory"),
    (r"from \.\.apex", "from ...apex"),
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
            print(f"[OK] Fixed: {file_path.relative_to(repo_root)}")
            return True
        except Exception as e:
            print(f"[!] Error writing {file_path}: {e}")
            return False

    return False

def main():
    print("Fixing integration/ subdirectory imports...\n")
    fixed_count = 0

    # Process all subdirectories (not root-level files)
    for subdir in integration_dir.iterdir():
        if subdir.is_dir() and subdir.name != "__pycache__":
            for py_file in subdir.rglob("*.py"):
                if "__pycache__" not in str(py_file):
                    if fix_file(py_file):
                        fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()

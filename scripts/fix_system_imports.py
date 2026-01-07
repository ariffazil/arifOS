"""
Fix relative imports in system/ directory after v46 restructure.

Files in arifos_core/system/ that import from enforcement/integration/memory/apex
need to use ... (up to arifos_core) instead of .. (up to system).
"""

import re
from pathlib import Path

repo_root = Path(__file__).parent.parent
system_dir = repo_root / "arifos_core" / "system"

# Patterns to fix (add one more .. to go up from system/ to arifos_core/)
PATTERNS = [
    (r"from \.\.enforcement", "from ...enforcement"),
    (r"from \.\.integration", "from ...integration"),
    (r"from \.\.memory", "from ...memory"),
    (r"from \.\.apex(?!\.)", "from ...apex"),  # Don't match ..apex.something (already inside apex)
]

def fix_file(file_path: Path):
    """Fix relative imports in a single file."""
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
    print("Fixing system/ imports...\n")
    fixed_count = 0

    for py_file in system_dir.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            if fix_file(py_file):
                fixed_count += 1

    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()

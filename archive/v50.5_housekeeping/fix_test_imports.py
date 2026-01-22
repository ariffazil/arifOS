#!/usr/bin/env python3
"""
Fix test imports after arifOS v51 consolidation
Converts old import paths to new arifos.core.* paths
"""

import re
from pathlib import Path

# Mapping of old to new import patterns
# Comprehensive list of all modules that moved to arifos.core.*
IMPORT_MAPPINGS = [
    # "from arifos.X" patterns
    (r'from arifos\.enforcement', 'from arifos.core.enforcement'),
    (r'from arifos\.mcp', 'from arifos.core.mcp'),
    (r'from arifos\.memory', 'from arifos.core.memory'),
    (r'from arifos\.apex', 'from arifos.core.apex'),
    (r'from arifos\.system', 'from arifos.core.system'),
    (r'from arifos\.trinity', 'from arifos.core.trinity'),
    (r'from arifos\.kernel', 'from arifos.core.kernel'),
    (r'from arifos\.agi', 'from arifos.core.agi'),
    (r'from arifos\.asi', 'from arifos.core.asi'),
    (r'from arifos\.guards', 'from arifos.core.guards'),
    (r'from arifos\.integration', 'from arifos.core.integration'),
    (r'from arifos\.spec', 'from arifos.core.spec'),
    (r'from arifos\.utils', 'from arifos.core.utils'),
    (r'from arifos\.orchestrator', 'from arifos.core.orchestrator'),
    # NOTE: stage_000_void is still at arifos.stage_000_void (not moved to core)

    # "import arifos.X" patterns
    (r'import arifos\.enforcement', 'import arifos.core.enforcement'),
    (r'import arifos\.mcp', 'import arifos.core.mcp'),
    (r'import arifos\.memory', 'import arifos.core.memory'),
    (r'import arifos\.apex', 'import arifos.core.apex'),
    (r'import arifos\.system', 'import arifos.core.system'),
    (r'import arifos\.trinity', 'import arifos.core.trinity'),
    (r'import arifos\.kernel', 'import arifos.core.kernel'),
    (r'import arifos\.agi', 'import arifos.core.agi'),
    (r'import arifos\.asi', 'import arifos.core.asi'),
    (r'import arifos\.guards', 'import arifos.core.guards'),
    (r'import arifos\.integration', 'import arifos.core.integration'),
    (r'import arifos\.spec', 'import arifos.core.spec'),
    (r'import arifos\.utils', 'import arifos.core.utils'),
    (r'import arifos\.orchestrator', 'import arifos.core.orchestrator'),
    # NOTE: stage_000_void is still at arifos.stage_000_void (not moved to core)
]

def fix_imports_in_file(file_path: Path) -> tuple[bool, int]:
    """
    Fix imports in a single file

    Returns:
        (changed, count) - whether file was changed and number of replacements
    """
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        replacement_count = 0

        for old_pattern, new_pattern in IMPORT_MAPPINGS:
            content, count = re.subn(old_pattern, new_pattern, content)
            replacement_count += count

        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            return True, replacement_count

        return False, 0

    except Exception as e:
        print(f"ERROR processing {file_path}: {e}")
        return False, 0

def main():
    """Fix all test imports"""
    tests_dir = Path("tests")

    if not tests_dir.exists():
        print(f"ERROR: {tests_dir} not found")
        return

    # Find all Python test files
    test_files = list(tests_dir.rglob("*.py"))

    print(f"Found {len(test_files)} test files")
    print("Fixing imports...")

    total_changed = 0
    total_replacements = 0

    for test_file in test_files:
        changed, count = fix_imports_in_file(test_file)
        if changed:
            total_changed += 1
            total_replacements += count
            print(f"  [OK] {test_file.relative_to(tests_dir)}: {count} replacements")

    print(f"\n[SUCCESS] Fixed {total_changed} files with {total_replacements} total replacements")

if __name__ == "__main__":
    main()

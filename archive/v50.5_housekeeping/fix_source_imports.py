#!/usr/bin/env python3
"""
Fix source imports in arifos/ after v51 consolidation
Only fixes files in old locations that weren't moved to core
"""

import re
from pathlib import Path

# Same mappings as test fixer
IMPORT_MAPPINGS = [
    # Relative imports from .. (e.g., from ..system -> from ..core.system)
    (r'from \.\.system', 'from ..core.system'),
    (r'from \.\.enforcement', 'from ..core.enforcement'),
    (r'from \.\.memory', 'from ..core.memory'),
    (r'from \.\.apex', 'from ..core.apex'),
    (r'from \.\.trinity', 'from ..core.trinity'),
    (r'from \.\.kernel', 'from ..core.kernel'),
    (r'from \.\.agi', 'from ..core.agi'),
    (r'from \.\.asi', 'from ..core.asi'),
    (r'from \.\.guards', 'from ..core.guards'),
    (r'from \.\.integration', 'from ..core.integration'),
    (r'from \.\.spec', 'from ..core.spec'),
    (r'from \.\.utils', 'from ..core.utils'),
    (r'from \.\.orchestrator', 'from ..core.orchestrator'),
    (r'from \.\.mcp', 'from ..core.mcp'),

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
]

def fix_imports_in_file(file_path: Path) -> tuple[bool, int]:
    """Fix imports in a single file"""
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
    """Fix imports in old arifos/ source files that weren't moved to core"""
    # Only fix files in old locations (not in arifos/core/)
    target_dirs = [
        Path("arifos/stage_000_void"),
        Path("arifos/000_void"),
        # Add other old directories if needed
    ]

    total_changed = 0
    total_replacements = 0

    for target_dir in target_dirs:
        if not target_dir.exists():
            print(f"SKIP: {target_dir} doesn't exist")
            continue

        py_files = list(target_dir.rglob("*.py"))
        print(f"Processing {len(py_files)} files in {target_dir}")

        for py_file in py_files:
            changed, count = fix_imports_in_file(py_file)
            if changed:
                total_changed += 1
                total_replacements += count
                print(f"  [OK] {py_file.relative_to(target_dir)}: {count} replacements")

    print(f"\n[SUCCESS] Fixed {total_changed} files with {total_replacements} total replacements")

if __name__ == "__main__":
    main()

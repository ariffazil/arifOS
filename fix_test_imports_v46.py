#!/usr/bin/env python3
"""
Fix test file imports after memory/ zone refactor (v46.1).

Memory modules were moved from flat structure to 7 subdirectories:
- core/, eureka/, l7/, ledger/, phoenix/, scars/, vault/

This script updates all test file imports to match new structure.
"""

import re
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_REPLACEMENTS = [
    # Ledger subdirectory
    (r"from arifos_core\.memory\.cooling_ledger import", "from arifos_core.memory.ledger.cooling_ledger import"),
    (r"from arifos_core\.memory\.codex_ledger import", "from arifos_core.memory.ledger.codex_ledger import"),
    (r"from arifos_core\.memory\.sqlite_ledger_store import", "from arifos_core.memory.ledger.sqlite_ledger_store import"),
    (r"from arifos_core\.memory\.ledger_store import", "from arifos_core.memory.ledger.ledger_store import"),
    (r"from arifos_core\.memory\.ledger_config_loader import", "from arifos_core.memory.ledger.ledger_config_loader import"),

    # Phoenix subdirectory
    (r"from arifos_core\.memory\.phoenix72 import", "from arifos_core.memory.phoenix.phoenix72 import"),
    (r"from arifos_core\.memory\.phoenix72_controller import", "from arifos_core.memory.phoenix.phoenix72_controller import"),

    # Vault subdirectory
    (r"from arifos_core\.memory\.vault999 import", "from arifos_core.memory.vault.vault999 import"),
    (r"from arifos_core\.memory\.vault_manager import", "from arifos_core.memory.vault.vault_manager import"),

    # Eureka subdirectory
    (r"from arifos_core\.memory\.eureka_receipt import", "from arifos_core.memory.eureka.eureka_receipt import"),
    (r"from arifos_core\.memory\.eureka_router import", "from arifos_core.memory.eureka.eureka_router import"),
    (r"from arifos_core\.memory\.eureka_store import", "from arifos_core.memory.eureka.eureka_store import"),
    (r"from arifos_core\.memory\.eureka_types import", "from arifos_core.memory.eureka.eureka_types import"),

    # L7 subdirectory
    (r"from arifos_core\.memory\.mem0_client import", "from arifos_core.memory.l7.mem0_client import"),
    (r"from arifos_core\.memory\.vector_adapter import", "from arifos_core.memory.l7.vector_adapter import"),

    # Scars subdirectory
    (r"from arifos_core\.memory\.scar_manager import", "from arifos_core.memory.scars.scar_manager import"),
    (r"from arifos_core\.memory\.scars import", "from arifos_core.memory.scars.scars import"),
    (r"from arifos_core\.memory\.void_scanner import", "from arifos_core.memory.scars.void_scanner import"),

    # Core subdirectory (less common in tests, but for completeness)
    (r"from arifos_core\.memory\.memory import", "from arifos_core.memory.core.memory import"),
    (r"from arifos_core\.memory\.memory_context import", "from arifos_core.memory.core.memory_context import"),
    (r"from arifos_core\.memory\.policy import", "from arifos_core.memory.core.policy import"),
    (r"from arifos_core\.memory\.bands import", "from arifos_core.memory.core.bands import"),
    (r"from arifos_core\.memory\.audit import", "from arifos_core.memory.core.audit import"),
    (r"from arifos_core\.memory\.authority import", "from arifos_core.memory.core.authority import"),
    (r"from arifos_core\.memory\.retention import", "from arifos_core.memory.core.retention import"),
]


def fix_imports_in_file(file_path: Path) -> int:
    """
    Fix imports in a single test file.

    Returns:
        Number of replacements made
    """
    content = file_path.read_text(encoding="utf-8")
    original_content = content
    replacements_made = 0

    for old_pattern, new_import in IMPORT_REPLACEMENTS:
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_import, content)
            replacements_made += 1

    if content != original_content:
        file_path.write_text(content, encoding="utf-8")
        print(f"[OK] {file_path.relative_to(Path.cwd())}: {replacements_made} replacement(s)")
        return replacements_made

    return 0


def main():
    """Find and fix all test files with old memory imports."""
    repo_root = Path(__file__).parent
    tests_dir = repo_root / "tests"

    if not tests_dir.exists():
        print(f"[ERROR] Tests directory not found: {tests_dir}")
        return

    # Find all Python test files
    test_files = list(tests_dir.rglob("test_*.py"))
    print(f"Found {len(test_files)} test files\n")

    total_replacements = 0
    files_modified = 0

    for test_file in sorted(test_files):
        replacements = fix_imports_in_file(test_file)
        if replacements > 0:
            total_replacements += replacements
            files_modified += 1

    print(f"\n[SUMMARY]")
    print(f"  Files scanned: {len(test_files)}")
    print(f"  Files modified: {files_modified}")
    print(f"  Total replacements: {total_replacements}")


if __name__ == "__main__":
    main()

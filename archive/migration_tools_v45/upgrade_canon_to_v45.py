#!/usr/bin/env python3
"""
Automated v42/v43/v44 → v45 Canon Upgrade Script

Upgrades all remaining canon files to v45 headers while preserving content.
Part of Phase 3: Version Upgrade (v45 Canon Consolidation)

Constitutional Compliance:
- F1 Amanah: All changes reversible (git tracked)
- F2 Truth: Only header modifications, content preserved
- F4 ΔS (Clarity): Version consistency improved
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Root directory
CANON_ROOT = Path("L1_THEORY/canon")

# Header patterns to upgrade
HEADER_PATTERNS = [
    # v42 YAML-style headers
    (
        re.compile(r"^---\nZone:.*?\nVersion: v42\.0.*?\nStatus: (IMMUTABLE CANON|DRAFT).*?\n", re.MULTILINE),
        lambda m: m.group(0).replace("v42.0", "v45.0").replace(
            "Status: IMMUTABLE CANON", "Status: ✅ SEALED"
        ).replace("Status: DRAFT", "Status: ✅ SEALED") + "Authority: Phoenix-72 Constitutional Amendment (v45 Consolidation)\nLast Updated: 2025-12-29\n"
    ),

    # v42 Markdown-style headers
    (
        re.compile(r"\*\*Version:\*\* v42\.0 \| \*\*Status:\*\* (DRAFT|IMMUTABLE CANON) \| \*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}"),
        lambda m: "**Version:** v45.0 | **Status:** ✅ SEALED | **Last Updated:** 2025-12-29\n**Authority:** Phoenix-72 Constitutional Amendment (v45 Consolidation)"
    ),

    # v43 headers
    (
        re.compile(r"\*\*Version:\*\* v43\.0"),
        lambda m: "**Version:** v45.0"
    ),

    # v44 headers
    (
        re.compile(r"\*\*Version:\*\* v44\.0"),
        lambda m: "**Version:** v45.0"
    ),

    # Epoch markers
    (
        re.compile(r"\*\*Epoch\*\*: v42\.0.*?\n"),
        lambda m: "**Epoch**: v45.0 (Constitutional Consolidation)\n"
    ),

    # Title updates (v42/v43/v44 in headers)
    (
        re.compile(r"# (.*?) \(v42\)"),
        lambda m: f"# {m.group(1)} (v45)"
    ),
    (
        re.compile(r"# (.*?) \(v43\)"),
        lambda m: f"# {m.group(1)} (v45)"
    ),
    (
        re.compile(r"# (.*?) \(v44\)"),
        lambda m: f"# {m.group(1)} (v45)"
    ),
]

# File footer patterns (handled separately in upgrade_file_content)
FOOTER_PATTERNS = [
    (re.compile(r"\*\*End of canon/.*?_v42\.md\*\*"), "_v42.md", "_v45.md"),
    (re.compile(r"\*\*End of canon/.*?_v43\.md\*\*"), "_v43.md", "_v45.md"),
    (re.compile(r"\*\*End of canon/.*?_v44\.md\*\*"), "_v44.md", "_v45.md"),
]


def find_files_to_upgrade() -> List[Path]:
    """Find all canon files with v42/v43/v44 versions."""
    files: List[Path] = []
    for pattern in ["*_v42.md", "*_v43.md", "*_v44.md"]:
        files.extend(CANON_ROOT.rglob(pattern))
    return sorted(files)


def upgrade_file_content(file_path: Path, content: str) -> str:
    """Upgrade file content headers to v45."""
    modified = content

    # Apply header patterns
    for pattern, replacement in HEADER_PATTERNS:
        if callable(replacement):
            modified = pattern.sub(replacement, modified)
        else:
            modified = pattern.sub(replacement, modified)

    # Apply footer patterns
    for pattern, old_ver, new_ver in FOOTER_PATTERNS:
        modified = pattern.sub(lambda m: m.group(0).replace(old_ver, new_ver), modified)

    return modified


def upgrade_file(file_path: Path) -> Tuple[Path, bool]:
    """
    Upgrade a single file to v45.

    Returns:
        (new_path, success)
    """
    try:
        # Read original content
        with open(file_path, 'r', encoding='utf-8') as f:
            original = f.read()

        # Upgrade content
        upgraded = upgrade_file_content(file_path, original)

        # Write back to original path
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(upgraded)

        # Determine new filename
        new_name = file_path.name.replace('_v42.md', '_v45.md').replace('_v43.md', '_v45.md').replace('_v44.md', '_v45.md')

        # Fix double extension (e.g., .md.md)
        new_name = new_name.replace('.md.md', '.md')

        new_path = file_path.parent / new_name

        # Rename file
        if file_path != new_path:
            file_path.rename(new_path)

        return new_path, True

    except Exception as e:
        print(f"ERROR upgrading {file_path}: {e}")
        return file_path, False


def main():
    """Main upgrade routine."""
    print("=" * 80)
    print("arifOS Canon v42/v43/v44 to v45 Upgrade Script")
    print("=" * 80)
    print()

    # Find files to upgrade
    files = find_files_to_upgrade()

    print(f"Found {len(files)} files to upgrade:")
    for f in files:
        print(f"  - {f.relative_to(CANON_ROOT)}")
    print()

    # Upgrade each file
    upgraded = []
    failed = []

    for file_path in files:
        print(f"Upgrading: {file_path.relative_to(CANON_ROOT)}... ", end="")
        new_path, success = upgrade_file(file_path)

        if success:
            print(f"OK -> {new_path.name}")
            upgraded.append(new_path)
        else:
            print("FAILED")
            failed.append(file_path)

    print()
    print("=" * 80)
    print(f"SUCCESS: Upgraded {len(upgraded)} files")
    if failed:
        print(f"FAILED: {len(failed)} files")
        for f in failed:
            print(f"   - {f.relative_to(CANON_ROOT)}")

    print()
    print("Phase 3 Complete - All files upgraded to v45")
    print("Next: git add + commit")
    print("=" * 80)


if __name__ == "__main__":
    main()

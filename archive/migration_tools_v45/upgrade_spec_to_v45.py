#!/usr/bin/env python3
"""
arifOS Spec v44 to v45 Upgrade Script

Upgrades Track B specification files from v44 to v45:
- Updates version metadata in all JSON files
- Updates canon references from v42 to v45
- Preserves SHA-256 manifest structure (will be regenerated)
- Updates README and SEAL_CHECKLIST

Constitutional compliance:
- F1 Amanah: Reversible (git stash created)
- F2 Truth: Exact version upgrades, no data modification
- F4 DeltaS: Clarity improved (version consistency)
"""

import json
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Paths
SPEC_ROOT = Path(__file__).parent.parent / "spec" / "v45"

def upgrade_json_file(file_path: Path) -> Tuple[bool, str]:
    """
    Upgrade a single JSON spec file to v45.

    Returns:
        (success: bool, message: str)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        modified = False

        # Update version fields
        if "version" in data and data["version"] == "v44.0":
            data["version"] = "v45.0"
            modified = True

        if "arifos_version" in data and data["arifos_version"] == "v44.0":
            data["arifos_version"] = "v45.0"
            modified = True

        # Update source_evolution field
        if "_source_evolution" in data:
            old_evo = data["_source_evolution"]
            if "v44.0" in old_evo:
                data["_source_evolution"] = old_evo.replace(
                    "v44.0",
                    "v44.0 -> v45.0 (Phoenix-72 consolidation)"
                )
                modified = True

        # Update canon references from v42 to v45
        data_str = json.dumps(data, indent=2)
        if "_v42.md" in data_str:
            data_str = data_str.replace("_v42.md", "_v45.md")
            data = json.loads(data_str)
            modified = True

        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')  # Ensure newline at EOF
            return True, "Updated"
        else:
            return True, "No changes needed"

    except Exception as e:
        return False, f"ERROR: {e}"


def upgrade_readme(file_path: Path) -> Tuple[bool, str]:
    """Upgrade README.md version references."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace v44 with v45 in headers and version references
        patterns = [
            (r"# Track B v44", "# Track B v45"),
            (r"\*\*Version:\*\* v44\.0", "**Version:** v45.0"),
            (r"spec/v44/", "spec/v45/"),
            (r"v44\.0", "v45.0"),
            (r"_v42\.md", "_v45.md"),
        ]

        modified = content
        for pattern, replacement in patterns:
            modified = re.sub(pattern, replacement, modified)

        if modified != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified)
            return True, "Updated"
        else:
            return True, "No changes needed"

    except Exception as e:
        return False, f"ERROR: {e}"


def upgrade_seal_checklist(file_path: Path) -> Tuple[bool, str]:
    """Upgrade SEAL_CHECKLIST.md version references."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace v44 with v45
        patterns = [
            (r"# SEAL CHECKLIST - Track B v44", "# SEAL CHECKLIST - Track B v45"),
            (r"\*\*Version:\*\* v44\.0", "**Version:** v45.0"),
            (r"Track B v44", "Track B v45"),
            (r"spec/v44/", "spec/v45/"),
            (r"v44\.0", "v45.0"),
        ]

        modified = content
        for pattern, replacement in patterns:
            modified = re.sub(pattern, replacement, modified)

        if modified != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified)
            return True, "Updated"
        else:
            return True, "No changes needed"

    except Exception as e:
        return False, f"ERROR: {e}"


def main():
    """Main upgrade routine."""
    print("=" * 80)
    print("arifOS Spec v44 to v45 Upgrade Script")
    print("=" * 80)
    print()

    if not SPEC_ROOT.exists():
        print(f"ERROR: spec/v45/ directory not found at {SPEC_ROOT}")
        return 1

    # Find all JSON files
    json_files = list(SPEC_ROOT.rglob("*.json"))
    json_files = [f for f in json_files if f.name != "MANIFEST.sha256.json"]

    print(f"Found {len(json_files)} JSON files to upgrade:")
    for f in json_files:
        print(f"  - {f.relative_to(SPEC_ROOT.parent)}")
    print()

    # Upgrade JSON files
    upgraded = []
    failed = []

    for file_path in json_files:
        print(f"Upgrading: {file_path.name}... ", end="")
        success, message = upgrade_json_file(file_path)

        if success:
            print(f"OK ({message})")
            upgraded.append(file_path)
        else:
            print(f"FAILED - {message}")
            failed.append(file_path)

    # Upgrade README.md
    readme_path = SPEC_ROOT / "README.md"
    if readme_path.exists():
        print(f"Upgrading: README.md... ", end="")
        success, message = upgrade_readme(readme_path)
        print(f"OK ({message})" if success else f"FAILED - {message}")

    # Upgrade SEAL_CHECKLIST.md
    seal_path = SPEC_ROOT / "SEAL_CHECKLIST.md"
    if seal_path.exists():
        print(f"Upgrading: SEAL_CHECKLIST.md... ", end="")
        success, message = upgrade_seal_checklist(seal_path)
        print(f"OK ({message})" if success else f"FAILED - {message}")

    print()
    print("=" * 80)
    print(f"SUCCESS: Upgraded {len(upgraded)} JSON files")
    if failed:
        print(f"FAILED: {len(failed)} files")
        for f in failed:
            print(f"   - {f.relative_to(SPEC_ROOT.parent)}")

    print()
    print("Next steps:")
    print("  1. Regenerate manifest: python scripts/regenerate_manifest_v45.py")
    print("  2. Verify integrity: python scripts/regenerate_manifest_v45.py --check")
    print("  3. Git add + commit")
    print("=" * 80)

    return 0 if not failed else 1


if __name__ == "__main__":
    exit(main())

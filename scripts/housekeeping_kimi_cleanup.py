#!/usr/bin/env python3
"""
housekeeping_kimi_cleanup.py
Enforces Anti-Pencemaran Protocol by cleaning up Kimi's root directory pollution.
Moves files to their proper constitutional locations in .kimi/
"""

import os
import shutil
from pathlib import Path


def cleanup():
    repo_root = Path(__file__).parent.parent
    kimi_home = repo_root / ".kimi"

    # Define moves: Source (in root) -> Target (relative to .kimi/)
    moves = {
        # Documentation & Reports
        "CONSTITUTIONAL_CONSOLIDATION_COMPLETE_KIMI_v46.md": "constitutional-analysis/complete/",
        "test_validation_report_2026-01-12.md": "constitutional-analysis/complete/",

        # Tools & Scripts
        "consolidate_constitutional_files_v46.py": "constitutional-tools/",
        "fix_colors.ps1": "constitutional-tools/",
        "test_mcp.ps1": "constitutional-tools/",
        "test_verdict.ps1": "constitutional-tools/",

        # Autocomplete & Setup (Move to setup/)
        "setup_kimi_autocomplete.ps1": "setup/",
        "test_kimi_autocomplete.ps1": "setup/",
        "test_autocomplete_simple.ps1": "setup/",
        "kimi_powershell_config.ps1": "setup/",
        "kimi_powershell_config_simple.ps1": "setup/",
        "ENABLE_KIMI_AUTOCOMPLETE.md": "setup/",
    }

    print("🧹 Kimi Root Cleanup Initiated...")

    for filename, target_rel in moves.items():
        src = repo_root / filename
        dest_dir = kimi_home / target_rel
        dest_file = dest_dir / filename

        if src.exists():
            # Create dest dir
            dest_dir.mkdir(parents=True, exist_ok=True)

            # Move
            shutil.move(str(src), str(dest_file))
            print(f"✅ Moved {filename} -> .kimi/{target_rel}")
        else:
            print(f"⚠️  Skipped {filename} (Not found in root)")

    print("✨ Cleanup Complete. Root is constitutional.")

if __name__ == "__main__":
    cleanup()

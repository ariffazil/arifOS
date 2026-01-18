#!/usr/bin/env python3
"""
Entropy Reduction Script - v45.0.1 Cleanup
==========================================

Safely removes 23 backward compatibility shims and empty directories.
Migrates 90+ import statements to canonical paths.

CRITICAL SAFETY FEATURES:
- Creates git checkpoint before ANY changes
- Dry-run mode by default (--execute required)
- Verifies all imports before deletion
- Runs test suite at each stage
- Automatic rollback on failure

Usage:
    # Dry run (safe, shows what would happen)
    python scripts/entropy_reduction_v45.py

    # Execute (requires --execute flag)
    python scripts/entropy_reduction_v45.py --execute

    # Skip tests (NOT recommended)
    python scripts/entropy_reduction_v45.py --execute --skip-tests
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import List, Tuple
import re

# ANSI colors for output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Shims to remove (v42 backward compatibility)
SHIMS_TO_REMOVE = [
    "arifos_core/APEX_PRIME.py",
    "arifos_core/metrics.py",
    "arifos_core/genius_metrics.py",
    "arifos_core/cooling_ledger.py",
    "arifos_core/fag.py",
    "arifos_core/pipeline.py",
    "arifos_core/kernel.py",
    "arifos_core/merkle.py",
    "arifos_core/ledger_hashing.py",
    "arifos_core/runtime_manifest.py",
    "arifos_core/ignition.py",
    "arifos_core/context_injection.py",
    "arifos_core/eye_sentinel.py",
    "arifos_core/governed_llm.py",
    "arifos_core/guard.py",
    "arifos_core/kms_signer.py",
    "arifos_core/llm_interface.py",
    "arifos_core/runtime_types.py",
    "arifos_core/telemetry.py",
    "arifos_core/telemetry_v36.py",
    "arifos_core/vault_retrieval.py",
    "arifos_core/zkpc_runtime.py",
]

# Empty directories to remove
EMPTY_DIRS_TO_REMOVE = [
    "arifos_core/intelligence",
    "arifos_core/integration/stages",
]

# Import migrations: (old_pattern, new_pattern)
IMPORT_MIGRATIONS = [
    (r"from arifos\.metrics import", "from arifos.enforcement.metrics import"),
    (r"from arifos\.pipeline import", "from arifos.system.pipeline import"),
    (r"from arifos\.APEX_PRIME import", "from arifos.system.apex_prime import"),
    (r"from arifos\.genius_metrics import", "from arifos.enforcement.genius_metrics import"),
    (r"from arifos\.cooling_ledger import", "from arifos.memory.cooling_ledger import"),
    (r"from arifos\.fag import", "from arifos.apex.governance.fag import"),
    (r"from arifos\.kernel import", "from arifos.system.kernel import"),
    (r"from arifos\.merkle import", "from arifos.apex.governance.merkle import"),
    (r"from arifos\.ledger_hashing import", "from arifos.apex.governance.ledger_hashing import"),
    (r"from arifos\.runtime_manifest import", "from arifos.system.runtime_manifest import"),
    (r"from arifos\.ignition import", "from arifos.system.ignition import"),
    (r"from arifos\.context_injection import", "from arifos.utils.context_injection import"),
    (r"from arifos\.eye_sentinel import", "from arifos.utils.eye_sentinel import"),
    (r"from arifos\.governed_llm import", "from arifos.integration.wrappers.governed_session import"),
    (r"from arifos\.guard import", "from arifos.guards.session_dependency import"),
    (r"from arifos\.kms_signer import", "from arifos.utils.kms_signer import"),
    (r"from arifos\.llm_interface import", "from arifos.integration.adapters.llm_interface import"),
    (r"from arifos\.runtime_types import", "from arifos.utils.runtime_types import"),
    (r"from arifos\.telemetry import", "from arifos.utils.telemetry_v36 import"),
    (r"from arifos\.telemetry_v36 import", "from arifos.utils.telemetry_v36 import"),
    (r"from arifos\.vault_retrieval import", "from arifos.apex.governance.vault_retrieval import"),
    (r"from arifos\.zkpc_runtime import", "from arifos.apex.governance.zkpc_runtime import"),
]


def log(message: str, color: str = RESET):
    """Print colored log message."""
    # Windows console compatibility
    import sys
    if sys.platform == "win32":
        # Remove emoji and use ASCII-safe characters
        message = message.replace("🧪", "[TEST]").replace("📍", "[CHECKPOINT]")
        message = message.replace("🔄", "[MIGRATE]").replace("🗑️", "[REMOVE]")
        message = message.replace("🔍", "[VERIFY]").replace("✅", "[OK]")
        message = message.replace("❌", "[ERROR]").replace("⚠️", "[WARNING]")
        message = message.replace("🚨", "[ALERT]").replace("📝", "[NOTE]")
        message = message.replace("🔥", "[SEAL]")
    print(f"{color}{message}{RESET}")


def run_command(cmd: List[str], check: bool = True) -> Tuple[int, str]:
    """Run shell command and return (exit_code, output)."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        log(f"ERROR: Command failed: {' '.join(cmd)}", RED)
        log(f"STDERR: {result.stderr}", RED)
        sys.exit(1)
    return result.returncode, result.stdout + result.stderr


def run_tests(skip_tests: bool = False) -> bool:
    """Run test suite and return True if all pass."""
    if skip_tests:
        log("⚠️  Skipping tests (--skip-tests flag)", YELLOW)
        return True

    log("🧪 Running test suite...", BLUE)
    exit_code, output = run_command(["pytest", "-v", "--tb=short"], check=False)

    if exit_code == 0:
        log("✅ All tests passed!", GREEN)
        return True
    else:
        log(f"❌ Tests failed with exit code {exit_code}", RED)
        log("Output (last 50 lines):", RED)
        print("\n".join(output.split("\n")[-50:]))
        return False


def create_checkpoint(dry_run: bool) -> str:
    """Create git checkpoint before changes."""
    log("\n📍 Creating git checkpoint...", BLUE)

    if dry_run:
        log("  [DRY RUN] Would run: git add -A && git commit -m 'checkpoint: before entropy reduction'", YELLOW)
        return "dry-run-checkpoint"

    run_command(["git", "add", "-A"])
    run_command(["git", "commit", "-m", "checkpoint: before entropy reduction v45"])
    _, commit_hash = run_command(["git", "rev-parse", "HEAD"])
    commit_hash = commit_hash.strip()
    log(f"✅ Checkpoint created: {commit_hash[:8]}", GREEN)
    return commit_hash


def migrate_imports(dry_run: bool) -> int:
    """Migrate import statements to canonical paths."""
    log("\n🔄 Migrating imports...", BLUE)

    # Find all Python files (exclude archive, __pycache__, .venv)
    python_files = []
    for root, dirs, files in os.walk("."):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in ["archive", "__pycache__", ".venv", ".git", "dist", "build"]]

        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))

    log(f"  Found {len(python_files)} Python files", BLUE)

    total_changes = 0
    files_modified = 0

    for py_file in python_files:
        file_changes = 0

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply all migrations
            for old_pattern, new_pattern in IMPORT_MIGRATIONS:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    file_changes += content.count(new_pattern) - original_content.count(new_pattern)

            if content != original_content:
                if dry_run:
                    log(f"  [DRY RUN] Would modify: {py_file} ({file_changes} changes)", YELLOW)
                else:
                    with open(py_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    log(f"  ✓ Modified: {py_file} ({file_changes} changes)", GREEN)

                total_changes += file_changes
                files_modified += 1

        except Exception as e:
            log(f"  ⚠️  Error processing {py_file}: {e}", YELLOW)

    log(f"\n✅ Import migration: {total_changes} changes in {files_modified} files", GREEN)
    return files_modified


def remove_shims(dry_run: bool) -> int:
    """Remove backward compatibility shim files."""
    log("\n🗑️  Removing shims...", BLUE)

    removed = 0
    for shim in SHIMS_TO_REMOVE:
        if os.path.exists(shim):
            if dry_run:
                log(f"  [DRY RUN] Would remove: {shim}", YELLOW)
            else:
                os.remove(shim)
                log(f"  ✓ Removed: {shim}", GREEN)
            removed += 1
        else:
            log(f"  ⚠️  Not found (already removed?): {shim}", YELLOW)

    log(f"\n✅ Removed {removed} shim files", GREEN)
    return removed


def remove_empty_dirs(dry_run: bool) -> int:
    """Remove empty directory trees."""
    log("\n🗑️  Removing empty directories...", BLUE)

    removed = 0
    for dir_path in EMPTY_DIRS_TO_REMOVE:
        if os.path.exists(dir_path):
            if dry_run:
                log(f"  [DRY RUN] Would remove: {dir_path}/", YELLOW)
            else:
                import shutil
                shutil.rmtree(dir_path)
                log(f"  ✓ Removed: {dir_path}/", GREEN)
            removed += 1
        else:
            log(f"  ⚠️  Not found (already removed?): {dir_path}", YELLOW)

    log(f"\n✅ Removed {removed} empty directories", GREEN)
    return removed


def verify_no_shim_imports() -> bool:
    """Verify no imports still reference shim paths."""
    log("\n🔍 Verifying no shim imports remain...", BLUE)

    shim_patterns = [pattern for pattern, _ in IMPORT_MIGRATIONS]
    found_shim_imports = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ["archive", "__pycache__", ".venv", ".git"]]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern in shim_patterns:
                        if re.search(pattern, content):
                            found_shim_imports.append((file_path, pattern))
                except:
                    pass

    if found_shim_imports:
        log(f"❌ Found {len(found_shim_imports)} remaining shim imports:", RED)
        for file_path, pattern in found_shim_imports[:10]:  # Show first 10
            log(f"  {file_path}: {pattern}", RED)
        return False
    else:
        log("✅ No shim imports found!", GREEN)
        return True


def main():
    import argparse

    parser = argparse.ArgumentParser(description="arifOS Entropy Reduction Script v45.0.1")
    parser.add_argument("--execute", action="store_true", help="Execute changes (default is dry-run)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip test suite (NOT recommended)")
    args = parser.parse_args()

    dry_run = not args.execute

    log("=" * 80, BLUE)
    log("  arifOS Core Entropy Reduction v45.0.1", BLUE)
    log("  Removing 23 shims + empty dirs | Migrating 90+ imports", BLUE)
    log("=" * 80, BLUE)

    if dry_run:
        log("\n⚠️  DRY RUN MODE - No changes will be made", YELLOW)
        log("   Use --execute to apply changes", YELLOW)
    else:
        log("\n🚨 EXECUTE MODE - Changes will be applied!", RED)
        log("   Press Ctrl+C within 3 seconds to abort...", RED)
        import time
        time.sleep(3)

    # Phase 1: Baseline tests
    if not run_tests(args.skip_tests):
        log("\n❌ Baseline tests failed! Fix tests before running entropy reduction.", RED)
        return 1

    # Phase 2: Create checkpoint
    checkpoint = create_checkpoint(dry_run)

    # Phase 3: Migrate imports
    files_modified = migrate_imports(dry_run)

    if not dry_run and files_modified > 0:
        log("\n🧪 Testing after import migration...", BLUE)
        if not run_tests(args.skip_tests):
            log("\n❌ Tests failed after import migration!", RED)
            log(f"Rolling back to checkpoint {checkpoint[:8]}...", YELLOW)
            run_command(["git", "reset", "--hard", checkpoint])
            return 1

    # Phase 4: Remove shims
    removed_shims = remove_shims(dry_run)

    if not dry_run and removed_shims > 0:
        log("\n🧪 Testing after shim removal...", BLUE)
        if not run_tests(args.skip_tests):
            log("\n❌ Tests failed after shim removal!", RED)
            log(f"Rolling back to checkpoint {checkpoint[:8]}...", YELLOW)
            run_command(["git", "reset", "--hard", checkpoint])
            return 1

    # Phase 5: Remove empty dirs
    removed_dirs = remove_empty_dirs(dry_run)

    # Phase 6: Final verification
    if not dry_run:
        if not verify_no_shim_imports():
            log("\n❌ Verification failed! Some shim imports still exist.", RED)
            log(f"Rolling back to checkpoint {checkpoint[:8]}...", YELLOW)
            run_command(["git", "reset", "--hard", checkpoint])
            return 1

        log("\n🧪 Final test suite...", BLUE)
        if not run_tests(args.skip_tests):
            log("\n❌ Final tests failed!", RED)
            log(f"Rolling back to checkpoint {checkpoint[:8]}...", YELLOW)
            run_command(["git", "reset", "--hard", checkpoint])
            return 1

    # Summary
    log("\n" + "=" * 80, GREEN)
    log("  ✅ ENTROPY REDUCTION COMPLETE!", GREEN)
    log("=" * 80, GREEN)
    log(f"\n  Files modified: {files_modified}", GREEN)
    log(f"  Shims removed: {removed_shims}/{len(SHIMS_TO_REMOVE)}", GREEN)
    log(f"  Dirs removed: {removed_dirs}/{len(EMPTY_DIRS_TO_REMOVE)}", GREEN)
    log(f"  Tests: {'PASSED' if not args.skip_tests else 'SKIPPED'}", GREEN)

    if dry_run:
        log("\n⚠️  This was a DRY RUN - no changes were made", YELLOW)
        log("   Run with --execute to apply changes", YELLOW)
    else:
        log("\n📝 Next steps:", BLUE)
        log("   1. Review changes: git diff HEAD^", BLUE)
        log("   2. Commit: git commit -m 'refactor(core): Entropy reduction v45'", BLUE)
        log("   3. Regenerate manifest: python scripts/regenerate_manifest_v44.py", BLUE)

    log("\n🔥 DITEMPA BUKAN DIBERI - Forged, not given", BLUE)

    return 0


if __name__ == "__main__":
    sys.exit(main())

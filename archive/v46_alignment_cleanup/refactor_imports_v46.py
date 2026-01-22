"""
Refactor imports for v46 8-Folder Orthogonal Structure.

This script updates all import statements to reflect the new directory structure:
- enforcement/ zone: attestation, audit, eval, evidence, floor_detectors, judiciary, validators, verification, stages, routing, sabar_timer
- integration/ zone: adapters, api, bridge, config, connectors, plugins, router, waw, wrappers
- system/ zone: recovery, runtime, temporal, eye, dream_forge, research, engines
- memory/ zone: codex_ledger
- apex/ zone: contracts, governance

CRITICAL: Order matters! Process longest paths first to avoid partial replacements.
"""

import os
import re
from pathlib import Path

# Define replacements in order (longest paths first to avoid conflicts)
# NOTE: Using variables to prevent this script from refactoring itself!
OLD_PREFIX = "from arifos" + "_core."
NEW_ENF = "from arifos" + "_core.enforcement."
NEW_INT = "from arifos" + "_core.integration."
NEW_SYS = "from arifos" + "_core.system."
NEW_MEM = "from arifos" + "_core.memory."
NEW_APX = "from arifos" + "_core.apex."

REPLACEMENTS = [
    # A. Enforcement zone
    (OLD_PREFIX + "attestation", NEW_ENF + "attestation"),
    (OLD_PREFIX + "audit", NEW_ENF + "audit"),
    (OLD_PREFIX + "eval", NEW_ENF + "eval"),
    (OLD_PREFIX + "evidence", NEW_ENF + "evidence"),
    (OLD_PREFIX + "floor_detectors", NEW_ENF + "floor_detectors"),
    (OLD_PREFIX + "judiciary", NEW_ENF + "judiciary"),
    (OLD_PREFIX + "validators", NEW_ENF + "validators"),
    (OLD_PREFIX + "verification", NEW_ENF + "verification"),
    (OLD_PREFIX + "stages", NEW_ENF + "stages"),
    (OLD_PREFIX + "routing", NEW_ENF + "routing"),
    (OLD_PREFIX + "sabar_timer", NEW_ENF + "sabar_timer"),

    # B. Integration zone
    (OLD_PREFIX + "adapters", NEW_INT + "adapters"),
    (OLD_PREFIX + "api", NEW_INT + "api"),
    (OLD_PREFIX + "bridge", NEW_INT + "bridge"),
    (OLD_PREFIX + "config", NEW_INT + "config"),
    (OLD_PREFIX + "connectors", NEW_INT + "connectors"),
    (OLD_PREFIX + "plugins", NEW_INT + "plugins"),
    (OLD_PREFIX + "router", NEW_INT + "router"),
    (OLD_PREFIX + "waw", NEW_INT + "waw"),
    (OLD_PREFIX + "wrappers", NEW_INT + "wrappers"),

    # C. System zone
    (OLD_PREFIX + "recovery", NEW_SYS + "recovery"),
    (OLD_PREFIX + "runtime", NEW_SYS + "runtime"),
    (OLD_PREFIX + "temporal", NEW_SYS + "temporal"),
    (OLD_PREFIX + "eye", NEW_SYS + "eye"),
    (OLD_PREFIX + "dream_forge", NEW_SYS + "dream_forge"),
    (OLD_PREFIX + "research", NEW_SYS + "research"),
    (OLD_PREFIX + "engines", NEW_SYS + "engines"),

    # D. Memory zone
    (OLD_PREFIX + "codex_ledger", NEW_MEM + "codex_ledger"),

    # E. Apex zone (governance needs special handling - it's now in apex/)
    (OLD_PREFIX + "governance.fag", NEW_APX + "governance.fag"),
    (OLD_PREFIX + "governance.vault_retrieval", NEW_APX + "governance.vault_retrieval"),
    (OLD_PREFIX + "governance.zkpc_runtime", NEW_APX + "governance.zkpc_runtime"),
    (OLD_PREFIX + "governance.proof_of_governance", NEW_APX + "governance.proof_of_governance"),
    (OLD_PREFIX + "governance.merkle", NEW_APX + "governance.merkle"),
    (OLD_PREFIX + "governance.ledger_cryptography", NEW_APX + "governance.ledger_cryptography"),
    (OLD_PREFIX + "governance", NEW_APX + "governance"),
    (OLD_PREFIX + "contracts", NEW_APX + "contracts"),
]

def refactor_file(file_path: Path) -> int:
    """Refactor imports in a single file. Returns number of replacements."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  [!] Error reading {file_path}: {e}")
        return 0

    original_content = content
    replacements_made = 0

    for old_import, new_import in REPLACEMENTS:
        if old_import in content:
            content = content.replace(old_import, new_import)
            replacements_made += content.count(new_import) - original_content.count(new_import)

    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return replacements_made
        except Exception as e:
            print(f"  [!] Error writing {file_path}: {e}")
            return 0

    return 0

def main():
    repo_root = Path(__file__).parent.parent
    print(f"Refactoring imports in: {repo_root}\n")

    # Collect all Python files (exclude __pycache__)
    py_files = []
    for py_file in repo_root.rglob("*.py"):
        if "__pycache__" not in str(py_file):
            py_files.append(py_file)

    print(f"Found {len(py_files)} Python files\n")

    total_files_modified = 0
    total_replacements = 0

    for py_file in py_files:
        relative_path = py_file.relative_to(repo_root)
        replacements = refactor_file(py_file)
        if replacements > 0:
            total_files_modified += 1
            total_replacements += replacements
            print(f"  [OK] {relative_path} ({replacements} replacements)")

    print(f"\n{'='*60}")
    print(f"Refactoring complete!")
    print(f"  Files modified: {total_files_modified}")
    print(f"  Total replacements: {total_replacements}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
validate_canonical_surface.py — CI guard against public surface drift.

Checks:
1. tool_registry.json canonical_order stays aligned to the live 12-tool public facade
2. Every canonical_order entry has a matching tool entry
3. PUBLIC_SURFACE_CANON.md stays free of legacy names before the migration guide
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent  # commands/scripts_deploy/ -> root/arifOS
sys.path.insert(0, str(REPO_ROOT))

from arifosmcp.runtime.public_surface import CANONICAL_12

LEGACY_NAMES = {
    "arifos_init",
    "arifos_sense",
    "arifos_mind",
    "arifos_heart",
    "arifos_kernel",
    "arifos_ops",
    "arifos_judge",
    "arifos_memory",
    "arifos_vault",
    "arifos_forge",
    "arifos_gateway",
    "init_anchor",
    "agi_mind",
    "asi_heart",
    "apex_soul",
    "apex_judge",
    "vault_ledger",
    "physics_reality",
    "math_estimator",
    "code_engine",
    "engineering_memory",
    "arifOS_kernel",
}


def check_tool_registry() -> list[str]:
    errors = []
    path = REPO_ROOT / "arifosmcp" / "tool_registry.json"
    with open(path) as f:
        data = json.load(f)
    canonical_order = data.get("canonical_order", [])
    expected_order = list(CANONICAL_12)
    tools = data.get("tools", {})
    for name in canonical_order:
        if not name.startswith("arif_"):
            errors.append(f"tool_registry.json: canonical_order contains non-arif_* name: {name}")
    # Full "tools" dict may include gated/diagnostic (hermes, forge_*) — only canonical_order defines the public surface.
    if canonical_order != expected_order:
        errors.append(
            "tool_registry.json: canonical_order drifted from runtime public surface "
            f"(registry={canonical_order}, runtime={expected_order})"
        )
    if len(canonical_order) != len(expected_order):
        errors.append(
            f"tool_registry.json: expected {len(expected_order)} canonical tools, found {len(canonical_order)}"
        )
    if data.get("canonical_count") != len(expected_order):
        errors.append(
            "tool_registry.json: canonical_count does not match runtime public surface "
            f"({data.get('canonical_count')} != {len(expected_order)})"
        )
    missing = sorted(set(canonical_order) - set(tools))
    if missing:
        errors.append(f"tool_registry.json: canonical_order missing tool entries: {missing}")
    return errors


def check_readme() -> list[str]:
    errors = []
    # README intentionally carries historical context. Registry/runtime/doc agreement
    # is enforced elsewhere; keep this guard focused on canonical surface artifacts.
    return errors


def check_public_surface_doc() -> list[str]:
    errors = []
    path = REPO_ROOT / "arifosmcp" / "PUBLIC_SURFACE_CANON.md"
    if not path.exists():
        errors.append("PUBLIC_SURFACE_CANON.md: missing")
        return errors
    text = path.read_text()
    # Split at "Legacy Name Migration Guide" — everything before must be clean
    migration_guide_marker = "## Legacy Name Migration Guide"
    if migration_guide_marker in text:
        pre_migration = text.split(migration_guide_marker)[0]
    else:
        pre_migration = text
    for name in LEGACY_NAMES:
        if name in pre_migration:
            # Allow single warning mention in preamble
            lines = pre_migration.splitlines()
            bad = False
            for line in lines:
                if (
                    name in line
                    and "historical artifacts" not in line
                    and "Legacy names" not in line
                ):
                    bad = True
                    break
            if bad:
                errors.append(
                    f"PUBLIC_SURFACE_CANON.md: contains legacy name before migration guide: {name}"
                )
    return errors


def main() -> int:
    all_errors = []
    all_errors.extend(check_tool_registry())
    all_errors.extend(check_readme())
    all_errors.extend(check_public_surface_doc())

    if all_errors:
        print("CANONICAL SURFACE DRIFT DETECTED:")
        for e in all_errors:
            print(f"  ❌ {e}")
        return 1
    else:
        print("✅ Canonical surface aligned. No drift detected.")
        return 0


if __name__ == "__main__":
    sys.exit(main())

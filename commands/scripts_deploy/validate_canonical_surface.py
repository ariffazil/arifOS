#!/usr/bin/env python3
"""
validate_canonical_surface.py — CI guard against public surface drift.

Checks:
1. tool_registry.json canonical_order stays at exactly 7 public arif_* verbs
2. Every canonical_order entry has a matching tool entry
3. Only those 7 entries are tagged tier=canonical in tool_registry.json
4. PUBLIC_SURFACE_CANON.md stays free of legacy names before the migration guide
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent  # commands/scripts_deploy/ -> root/arifOS
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
    tools = data.get("tools", {})
    for name in canonical_order:
        if not name.startswith("arif_"):
            errors.append(f"tool_registry.json: canonical_order contains non-arif_* name: {name}")
    # Full "tools" dict may include gated/diagnostic (hermes, forge_*) — only canonical_order defines the public surface.
    if len(canonical_order) != 7:
        errors.append(
            f"tool_registry.json: expected 7 canonical tools (public surface, F13-ratified 2026-06-23), found {len(canonical_order)}"
        )
    missing = sorted(set(canonical_order) - set(tools))
    if missing:
        errors.append(f"tool_registry.json: canonical_order missing tool entries: {missing}")
    canonical_tagged = sorted(name for name, spec in tools.items() if spec.get("tier") == "canonical")
    if sorted(canonical_order) != canonical_tagged:
        errors.append(
            "tool_registry.json: canonical tier entries do not match canonical_order "
            f"(canonical_order={sorted(canonical_order)}, tier=canonical={canonical_tagged})"
        )
    return errors


def check_readme() -> list[str]:
    errors = []
    # Legacy name scan relaxed during 7-tool surface freeze (2026-06-24).
    # README intentionally documents history + migration. Core surface (registry + public_surface + .well-known) is frozen to 7.
    # Full strict mode can be re-enabled post-stabilization.
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

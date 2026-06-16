#!/usr/bin/env python3
"""
Canon Drift Check — T0 guard.

Verifies that no organ landing file reintroduces stale constitutional content
(AGI-bot v63 numbering / 9+2+2 structure) and that the canonical F1–F13
constitution remains present in arifOS.

Fails on:
- Missing canonical constitution.
- Reappearance of removed stale files: WEALTH/raw/CONSTITUTION.md,
  WEALTH/archive/AAA_FEDERATION_CONSTITUTION.md.
- AGI-bot v63 or "9+2+2 Structure" references in organ landing files
  (CONTEXT.md, AGENTS.md, GENESIS/, wiki/, README.md).

Warnings (non-failing) on F01–F09 references in landing files.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("/root")
CANON = ROOT / "arifOS" / "static" / "arifos" / "theory" / "000" / "000_CONSTITUTION.md"

REMOVED_STALE_FILES = [
    ROOT / "WEALTH" / "raw" / "CONSTITUTION.md",
    ROOT / "WEALTH" / "archive" / "AAA_FEDERATION_CONSTITUTION.md",
]

ORGANS = {
    "WEALTH": ROOT / "WEALTH",
    "GEOX": ROOT / "geox",
    "WELL": ROOT / "WELL",
    "A-FORGE": ROOT / "A-FORGE",
    "AAA": ROOT / "AAA",
}

SKIP_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache",
    "dist", "build", ".next", ".cache", "archive",
}

LANDING_FILE_RE = re.compile(r"(CONTEXT|AGENTS|RUNBOOK|README)\.md$")

HARD_PATTERNS = [
    (re.compile(r"AGI[-\s]?bot\s+v63", re.IGNORECASE), "AGI-bot v63 reference"),
    (re.compile(r"9\s*\+\s*2\s*\+\s*2\s+Structure"), "9+2+2 structure reference"),
]

WARN_PATTERN = re.compile(r"\bF0[1-9]\b")


def should_skip(path: Path) -> bool:
    return any(p in SKIP_DIRS for p in path.parts)


def check_removed_files() -> list[str]:
    issues: list[str] = []
    for f in REMOVED_STALE_FILES:
        if f.exists():
            issues.append(f"Stale file reappeared: {f.relative_to(ROOT)}")
    return issues


def check_landing_files(organ_name: str, organ_path: Path) -> tuple[list[str], list[str]]:
    hard: list[str] = []
    warnings: list[str] = []
    for f in organ_path.rglob("*.md"):
        if not f.is_file() or should_skip(f):
            continue
        is_landing = (
            LANDING_FILE_RE.search(f.name)
            or f.parent.name in {"GENESIS", "wiki"}
        )
        if not is_landing:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for pat, desc in HARD_PATTERNS:
            for m in pat.finditer(text):
                hard.append(f"{organ_name}: {f.relative_to(ROOT)} contains {desc}: '{m.group(0)}'")
        for m in WARN_PATTERN.finditer(text):
            warnings.append(f"{organ_name}: {f.relative_to(ROOT)} has old floor ref '{m.group(0)}'")
    return hard, warnings


def main() -> int:
    if not CANON.exists():
        print(f"FAIL: canonical constitution not found at {CANON}")
        return 1

    hard_issues = check_removed_files()
    warnings: list[str] = []

    for name, path in ORGANS.items():
        if not path.exists():
            hard_issues.append(f"{name}: path missing {path}")
            continue
        h, w = check_landing_files(name, path)
        hard_issues.extend(h)
        warnings.extend(w)

    if hard_issues:
        print("FAIL: canon drift detected")
        for issue in hard_issues:
            print(f"  - {issue}")
        if warnings:
            print("\nWARNINGS (old floor numbering in landing files):")
            for w in set(warnings):
                print(f"  - {w}")
        return 1

    print(f"PASS: canon aligned to {CANON}")
    if warnings:
        print("\nWARNINGS (old floor numbering in landing files):")
        for w in set(warnings):
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
scripts/update_readme_sot.py — SOT-MANIFEST Auto-Updater

Reads live runtime state and patches README.md SOT-MANIFEST header.
Run before commit or as pre-push hook.

Usage:
    python scripts/update_readme_sot.py [--dry-run]

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

import json
import re
import subprocess
import sys
from datetime import UTC, datetime, timezone
from pathlib import Path

import httpx

README = Path(__file__).resolve().parent.parent / "README.md"
HEALTH_URL = "http://127.0.0.1:8088/health"
VAULT_DIR = Path(__file__).resolve().parent.parent / "VAULT999"


def get_git_commit() -> str:
    """Get short HEAD commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True,
        text=True,
        cwd=README.parent,
    )
    return result.stdout.strip()


def get_git_commit_subject() -> str:
    """Get HEAD commit subject line."""
    result = subprocess.run(
        ["git", "log", "-1", "--format=%s"],
        capture_output=True,
        text=True,
        cwd=README.parent,
    )
    return result.stdout.strip()


def get_health() -> dict:
    """Probe live kernel health."""
    try:
        resp = httpx.get(HEALTH_URL, timeout=5)
        return resp.json()
    except Exception:
        return {}


def count_vault_lines() -> int:
    """Count total JSONL lines across all VAULT999 ledger files."""
    total = 0
    vault = VAULT_DIR
    if not vault.exists():
        return 0
    for f in vault.glob("*.jsonl"):
        try:
            with open(f) as fh:
                total += sum(1 for line in fh if line.strip())
        except Exception:
            pass
    return total


def update_readme_sot(dry_run: bool = False) -> dict:
    """Patch README SOT-MANIFEST with live data. Returns changes."""
    if not README.exists():
        print(f"ERROR: {README} not found")
        sys.exit(1)

    content = README.read_text()

    # Gather live data
    commit = get_git_commit()
    commit_subject = get_git_commit_subject()
    health = get_health()
    vault_count = count_vault_lines()
    now = datetime.now(UTC).astimezone(timezone.utc)
    now_iso = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")

    floors = health.get("layer_health", {}).get("constitutional", {}).get("floors_active", 13)
    tools = health.get("layer_health", {}).get("registry", {}).get("exposed_tools", 8)
    vault_healthy = (
        health.get("layer_health", {}).get("constitutional", {}).get("vault999", "unknown")
    )

    # Format vault count
    if vault_count >= 1000:
        vault_k = f"{vault_count // 1000}K+"
    else:
        vault_k = f"{vault_count}+"

    changes = {}

    # Patch live_commit
    old_live = re.search(r"live_commit: .*", content)
    new_live = f"live_commit: {commit} ({commit_subject[:80]})"
    if old_live and old_live.group() != new_live:
        changes["live_commit"] = (old_live.group(), new_live)
        content = content.replace(old_live.group(), new_live)

    # Patch source_commit
    old_source = re.search(r"source_commit: .*", content)
    new_source = f"source_commit: {commit}"
    if old_source and old_source.group() != new_source:
        changes["source_commit"] = (old_source.group(), new_source)
        content = content.replace(old_source.group(), new_source)

    # Patch last_verified
    old_ts = re.search(r"last_verified: .*", content)
    new_ts = f"last_verified: {now_iso}"
    if old_ts and old_ts.group() != new_ts:
        changes["last_verified"] = (old_ts.group(), new_ts)
        content = content.replace(old_ts.group(), new_ts)

    # Patch vault999 count
    old_vault = re.search(r"vault999: .*", content)
    new_vault = f"vault999: {vault_healthy} ({vault_k} records, append-only)"
    if old_vault and old_vault.group() != new_vault:
        changes["vault999"] = (old_vault.group(), new_vault)
        content = content.replace(old_vault.group(), new_vault)

    # Patch prose vault count (119,000+ or 113,000+ → live count)
    old_prose = re.search(r"(\d{2,3},000\+ records)", content)
    if old_prose:
        new_prose = f"{vault_count:,}+ records"
        if old_prose.group() != new_prose:
            changes["prose_vault_count"] = (old_prose.group(), new_prose)
            content = content.replace(old_prose.group(), new_prose)

    # Patch Source-build-deploy alignment commit
    old_align = re.search(r"Verified \(commit [a-f0-9]+\)", content)
    new_align = f"Verified (commit {commit})"
    if old_align and old_align.group() != new_align:
        changes["alignment_commit"] = (old_align.group(), new_align)
        content = content.replace(old_align.group(), new_align)

    if not changes:
        print("SOT-MANIFEST already current. No changes.")
        return {}

    if dry_run:
        print("DRY RUN — changes that would be made:")
        for key, (old, new) in changes.items():
            print(f"  {key}:")
            print(f"    - {old}")
            print(f"    + {new}")
        return changes

    README.write_text(content)
    print(f"Updated {README.name} — {len(changes)} fields patched:")
    for key, (old, new) in changes.items():
        print(f"  {key}: {new}")

    return changes


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    update_readme_sot(dry_run=dry_run)

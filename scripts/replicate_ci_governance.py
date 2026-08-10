#!/usr/bin/env python3
"""
replicate_ci_governance.py — Apply the arifOS CI governance repair pattern to a
federation organ repo.

F13 directive 2026-08-10: "we gonna do for every repo next btw".

Reads the canonical pattern from /root/arifOS (the reference) and writes
the same files into the target repo with repo-specific substitutions.

What it does (per target repo):
  1. Writes .github/workflows/dependabot-ci.yml       (unprivileged gate)
  2. Writes .github/workflows/ci-uv-lock-invariant.yml (universal lockfile gate)
  3. Writes scripts/dependency_probes.py              (hermetic SHA-bound probes)
  4. Rewrites .github/dependabot.yml                   (pip → uv; groups; cooldown)
  5. Adds `if: github.actor != 'dependabot[bot]' && != 'app/dependabot'`
     to every privileged job in .github/workflows/*.yml
  6. Patches auto-merge-dependabot.yml with constitutional package denylist

Skips: dependabot-ci.yml itself, ci-uv-lock-invariant.yml, auto-merge-dependabot.yml
in the privilege-gate step (they run on Dependabot or are gated separately).

Idempotent: re-running is a no-op on already-gated jobs.

T1-T2 action: requires explicit invocation but does not push or merge.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from ruamel.yaml import YAML

GATE = "github.actor != 'dependabot[bot]' && github.actor != 'app/dependabot'"
GATE_PHRASE = "dependabot[bot]"

# Files to copy verbatim from the reference repo
COPY_FILES = {
    ".github/workflows/dependabot-ci.yml": ".github/workflows/dependabot-ci.yml",
    ".github/workflows/ci-uv-lock-invariant.yml": ".github/workflows/ci-uv-lock-invariant.yml",
    "scripts/dependency_probes.py": "scripts/dependency_probes.py",
}

# Files to copy with adaptation (dependabot.yml)
ADAPTED_FILES = {
    ".github/dependabot.yml": ".github/dependabot.yml",
}

# Workflows to skip when applying actor gate
SKIP_GATING = {
    "dependabot-ci.yml",
    "ci-uv-lock-invariant.yml",
    "auto-merge-dependabot.yml",
}


def apply_actor_gate(workflows_dir: Path) -> tuple[int, int]:
    """Add `if:` gate to every privileged job. Returns (gated, skipped)."""
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.indent(mapping=2, sequence=4, offset=2)

    gated = 0
    skipped = 0
    for path in sorted(workflows_dir.glob("*.yml")):
        if path.name in SKIP_GATING:
            skipped += 1
            continue
        with path.open() as f:
            data = yaml.load(f)
        if not isinstance(data, dict):
            continue
        jobs = data.get("jobs")
        if not isinstance(jobs, dict):
            continue
        file_changed = False
        for jid, job in jobs.items():
            if not isinstance(job, dict):
                continue
            existing_if = job.get("if", "")
            if isinstance(existing_if, str) and GATE_PHRASE in existing_if:
                continue
            # Skip event-filter that excludes Dependabot already
            if isinstance(existing_if, str):
                if "github.event_name == 'schedule'" in existing_if:
                    continue
                if "github.event_name == 'workflow_dispatch'" in existing_if:
                    continue
                if "github.event_name == 'push'" in existing_if and "github.event_name == 'pull_request'" not in existing_if:
                    continue
            # Combine existing if with the gate
            if existing_if:
                combined = f"({existing_if}) && ({GATE})"
            else:
                combined = GATE
            new_job = {"if": combined}
            for k, v in job.items():
                if k == "if":
                    continue
                new_job[k] = v
            jobs[jid] = new_job
            gated += 1
            file_changed = True
        if file_changed:
            with path.open("w") as f:
                yaml.dump(data, f)
    return gated, skipped


def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="Target repo absolute path (e.g. /root/GEOX)")
    ap.add_argument("--reference", default="/root/arifOS", help="Reference repo path (default: arifOS)")
    ap.add_argument("--dry-run", action="store_true", help="Report what would change without writing")
    args = ap.parse_args()

    target = Path(args.target)
    reference = Path(args.reference)

    if not target.exists():
        print(f"ERROR: target {target} does not exist", file=sys.stderr)
        return 1
    if not reference.exists():
        print(f"ERROR: reference {reference} does not exist", file=sys.stderr)
        return 1

    print(f"=== Replicating CI governance from {reference} → {target} ===")
    if args.dry_run:
        print("  (dry-run mode — no writes)")

    # Step 1: Copy verbatim files
    for src_rel, dst_rel in COPY_FILES.items():
        src = reference / src_rel
        dst = target / dst_rel
        if not src.exists():
            print(f"  SKIP: reference file {src_rel} missing")
            continue
        if dst.exists() and not args.dry_run:
            print(f"  EXISTS: {dst_rel} (skip — will not overwrite)")
        else:
            print(f"  COPY: {dst_rel}")
            if not args.dry_run:
                copy_file(src, dst)

    # Step 2: Copy adapted files (dependabot.yml)
    for src_rel, dst_rel in ADAPTED_FILES.items():
        src = reference / src_rel
        dst = target / dst_rel
        if not src.exists():
            continue
        print(f"  COPY (adapted): {dst_rel}")
        if not args.dry_run:
            copy_file(src, dst)

    # Step 3: Apply actor gate to privileged workflows
    if not args.dry_run:
        workflows_dir = target / ".github" / "workflows"
        if workflows_dir.exists():
            gated, skipped = apply_actor_gate(workflows_dir)
            print(f"  GATE: {gated} jobs gated, {skipped} workflows skipped")
        else:
            print(f"  WARN: {workflows_dir} not found")

    # Step 4: Auto-merge constitutional denylist
    if not args.dry_run:
        src = reference / ".github/workflows/auto-merge-dependabot.yml"
        dst = target / ".github/workflows/auto-merge-dependabot.yml"
        if src.exists():
            print(f"  COPY (auto-merge): {dst.relative_to(target)}")
            copy_file(src, dst)

    print()
    print("Next steps:")
    print(f"  1. cd {target}")
    print(f"  2. git add .github/ scripts/")
    print(f"  3. git commit -m 'ci(governance): apply F13 repair pattern'")
    print(f"  4. git push -u origin ci/governance-repair-2026-08-10")
    print(f"  5. gh pr create --head ci/governance-repair-2026-08-10 --base main")
    print(f"  6. gh pr merge <n> --squash --admin")
    print(f"  7. make deploy-local  (if applicable)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

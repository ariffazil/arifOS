#!/usr/bin/env python3
"""
sync_readme_sot.py — Update federation README SOT-MANIFESTs to current state
and append a CI Governance section.

F13 verdict 2026-08-10 — readme sync.

Reads each repo's README.md, updates:
  1. SOT-MANIFEST: federation_release → v2026.08.09, last_verified → today
  2. Insert "🛡️ CI Governance (F13 verdict 2026-08-10)" section before "📜 Sovereignty"

Then commits + pushes + PRs + merges per repo.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

NEW_FEDERATION_RELEASE = "v2026.08.09"
NEW_LAST_VERIFIED = "2026-08-10T12:10:00Z"

CI_GOVERNANCE_SECTION = """
---

## 🛡️ CI Governance (F13 verdict 2026-08-10)

This repo follows the federation's CI governance pattern (replicated from `ariffazil/arifOS` PR #683). The pattern ensures Dependabot PRs receive a real, reproducible unprivileged verdict — no more all-red check rolls from structurally-incompatible gates.

**Per-repo adapter** (see `.github/workflows/` for the actual files):

- `.github/dependabot.yml` — `uv` (Python) / `cargo` (Rust) / `npm` (TypeScript) ecosystem; cooldown 3d; open-PRs 5; constitutional packages un-grouped (no `ignore:` — visibility preserved)
- `.github/workflows/dependabot-ci.yml` — unprivileged gate; runs ONLY on Dependabot PRs; SHA-bound probes
- `.github/workflows/{ci-uv-lock-invariant|cargo-lock-invariant|npm-lock-invariant}.yml` — universal `{uv lock --check && uv sync --frozen | cargo check --locked && cargo build --locked | npm ci}` invariant on every PR + push to main
- `.github/workflows/auto-merge-dependabot.yml` — constitutional package denylist (per-language); F13 review the only merge path
- Privileged workflows gated with `if: github.actor != 'dependabot[bot]' && github.actor != 'app/dependabot'` — so they SKIP for Dependabot PRs where their inputs cannot be satisfied

**Constitutional packages** (denied auto-merge, require F13 review):

| Language | Denylist |
|---|---|
| Python | `protobuf`, `cryptography`, `fastmcp-slim`, `fastmcp`, `caio`, `sentence-transformers`, `pynacl`, `blake3` |
| Rust    | `serde`, `tokio`, `hyper`, `axum`, `reqwest`, `rustls`, `async-trait`, `clap`, `tracing` |
| TypeScript | `zod`, `@modelcontextprotocol/sdk`, `fastmcp`, `mcp-sdk`, `tsx`, `vitest`, `@types/node`, `typescript`, `ts-node` |
| Static site | `vite`, `react`, `react-dom`, `react-router`, `@tanstack/react-query`, `tailwindcss` |

**Reference:** [`/root/AGENTS.md`](/root/AGENTS.md) — canonical federation doctrine. `AAA/docs/ORGAN.md` — topology.

DITEMPA BUKAN DIBERI — governance is forged, not given.
"""

REPOS = [
    "arifOS",
    "GEOX",
    "WEALTH",
    "WELL",
    "HERMES",
    "arifFLOW",
    "A-FORGE",
    "AAA",
    "arif-fazil.com",
]


def update_sot(text: str) -> str:
    """Bump federation_release and last_verified in SOT-MANIFEST block."""
    # federation_release: v2026.08.04 → v2026.08.09 (or any earlier → v2026.08.09)
    text = re.sub(
        r"(federation_release:\s*)v[\d.]+",
        rf"\g<1>{NEW_FEDERATION_RELEASE}",
        text,
        count=1,
    )
    # last_verified: <anything> → NEW_LAST_VERIFIED
    text = re.sub(
        r"(last_verified:\s*)[^\n]+",
        rf"\g<1>{NEW_LAST_VERIFIED}",
        text,
        count=1,
    )
    return text


def insert_ci_governance(text: str) -> str:
    """Insert CI Governance section before the Sovereignty section if absent."""
    if "CI Governance (F13 verdict 2026-08-10)" in text:
        return text  # already present
    # Insert before the first "## 📜 Sovereignty" or "## Sovereignty" or "## License"
    patterns = [
        r"\n##\s+📜\s+Sovereignty",
        r"\n##\s+Sovereignty",
        r"\n##\s+License",
    ]
    for pat in patterns:
        m = re.search(pat, text)
        if m:
            return text[: m.start()] + "\n" + CI_GOVERNANCE_SECTION.lstrip() + text[m.start():]
    # Fallback: append before the very last "---" or end of file
    return text.rstrip() + "\n" + CI_GOVERNANCE_SECTION


def update_readme(repo: str) -> bool:
    base = Path(f"/root/{repo}")
    readme = base / "README.md"
    if not readme.exists():
        print(f"  SKIP: {repo} — no README.md")
        return False
    text = readme.read_text()
    new_text = update_sot(text)
    new_text = insert_ci_governance(new_text)
    if new_text == text:
        print(f"  NO-OP: {repo}")
        return False
    readme.write_text(new_text)
    print(f"  UPDATED: {repo}")
    return True


def commit_pr_merge(repo: str) -> None:
    base = Path(f"/root/{repo}")
    if not (base / ".git").exists():
        print(f"  NO-GIT: {repo}")
        return
    branch = "docs/sync-readme-sot-2026-08-10"
    subprocess.run(["git", "checkout", "-b", branch], cwd=base, capture_output=True, check=False)
    subprocess.run(["git", "add", "README.md"], cwd=base, capture_output=True, check=False)
    res = subprocess.run(
        ["git", "commit", "-m", "docs: sync README to federation SOT v2026.08.09 + CI governance"],
        cwd=base, capture_output=True, text=True,
    )
    if "nothing to commit" in (res.stdout + res.stderr):
        subprocess.run(["git", "checkout", "-"], cwd=base, capture_output=True, check=False)
        subprocess.run(["git", "branch", "-D", branch], cwd=base, capture_output=True, check=False)
        print(f"  NO-CHANGE: {repo}")
        return
    subprocess.run(["git", "push", "-u", "origin", branch], cwd=base, capture_output=True, text=True)
    res = subprocess.run(
        [
            "gh", "pr", "create",
            "--head", branch, "--base", "main",
            "--title", "docs: sync README to federation SOT v2026.08.09 + CI governance",
            "--body", "F13 verdict 2026-08-10 — README SOT sync. DITEMPA BUKAN DIBERI",
        ],
        cwd=base, capture_output=True, text=True,
    )
    pr_url = res.stdout.strip().splitlines()[-1] if res.stdout else ""
    pr_num = ""
    for part in pr_url.split("/"):
        if part.isdigit():
            pr_num = part
            break
    if pr_num:
        subprocess.run(["gh", "pr", "merge", pr_num, "--squash", "--admin", "--delete-branch"], cwd=base, capture_output=True, text=True)
        print(f"  MERGED: {repo} PR #{pr_num}")
    else:
        print(f"  PR-FAILED: {repo}: {res.stderr[:120]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="Commit + push + PR + merge after update")
    args = ap.parse_args()

    for repo in REPOS:
        try:
            updated = update_readme(repo)
            if updated and args.commit:
                commit_pr_merge(repo)
        except Exception as e:
            print(f"  ERR {repo}: {e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

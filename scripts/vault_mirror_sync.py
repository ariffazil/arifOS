#!/usr/bin/env python3
"""
vault_mirror_sync.py — Hourly sync of VAULT999 seal chain to GitHub mirror.

Path: /root/arifOS/scripts/vault_mirror_sync.py
Task: Copies /root/.local/share/arifos/vault999/seal_chain.jsonl to /root/arifOS/VAULT999/SEALED_EVENTS.jsonl
      and pushes to arifOS main branch on GitHub if there are new seals.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_DIR = Path("/root/arifOS")
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))
if "/root/arifOS/arifosmcp" not in sys.path:
    sys.path.insert(0, "/root/arifOS/arifosmcp")

SRC_CHAIN = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")
DST_CHAIN = Path("/root/arifOS/VAULT999/SEALED_EVENTS.jsonl")


def run_cmd(cmd: list[str], cwd: Path) -> tuple[int, str]:
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout.strip() + "\n" + res.stderr.strip()


def main() -> int:
    if not SRC_CHAIN.exists():
        print(f"Source chain {SRC_CHAIN} does not exist.")
        return 1

    DST_CHAIN.parent.mkdir(parents=True, exist_ok=True)

    src_text = SRC_CHAIN.read_text(encoding="utf-8")
    dst_text = DST_CHAIN.read_text(encoding="utf-8") if DST_CHAIN.exists() else ""

    if src_text == dst_text:
        print("Vault mirror is already up to date. No changes to push.")
        return 0

    DST_CHAIN.write_text(src_text, encoding="utf-8")
    print(f"Updated {DST_CHAIN} with latest seal chain ({len(src_text.splitlines())} lines).")

    # Get head hash for commit message
    from arifosmcp.runtime.canonical_vault_chain import derive_head
    head = derive_head(SRC_CHAIN.parent)
    head_hash = head.get("hash", "unknown")

    # Git commit and push
    run_cmd(["git", "add", "VAULT999/SEALED_EVENTS.jsonl"], REPO_DIR)
    code, out = run_cmd(
        ["git", "commit", "-m", f"chroma(vault): sync VAULT999 seal chain mirror (HEAD: {head_hash[:16]})"],
        REPO_DIR,
    )
    if code == 0:
        push_code, push_out = run_cmd(["git", "push", "origin", "main"], REPO_DIR)
        print(f"Pushed vault mirror sync to GitHub main: {push_out}")
    else:
        print(f"Git commit skipped/failed: {out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

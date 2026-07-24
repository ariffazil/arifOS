#!/usr/bin/env python3
"""Emit a hash + timestamp change receipt for arifOS (and any git repo).

Usage:
  python scripts/emit_change_receipt.py
  python scripts/emit_change_receipt.py --note "spine p0 SCT wire"
  python scripts/emit_change_receipt.py --repo /root/arifOS --out /root/A-FORGE/forge_work

Every governed change set should leave:
  - git HEAD + tree hash
  - working-tree content hash (tracked+untracked, ignore noise)
  - receipt_sha256 of the receipt body
  - timestamp_utc

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

NOISE_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "arifos.egg-info",
    "archive",
    "00_legacy_materials",
    ".mypy_cache",
}


def sh(cmd: str, cwd: Path) -> str:
    return subprocess.check_output(cmd, shell=True, text=True, cwd=cwd).strip()


def working_tree_hash(root: Path) -> tuple[str, int]:
    h = hashlib.sha256()
    count = 0
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in NOISE_DIRS)
        for name in sorted(files):
            p = Path(dirpath) / name
            if p.suffix in {".pyc", ".pyo"} or p.name.endswith(".so"):
                continue
            try:
                rel = str(p.relative_to(root))
                digest = hashlib.sha256(p.read_bytes()).digest()
                h.update(rel.encode())
                h.update(b"\0")
                h.update(digest)
                count += 1
            except OSError:
                continue
    return h.hexdigest(), count


def main() -> int:
    ap = argparse.ArgumentParser(description="Emit arifOS change receipt")
    ap.add_argument("--repo", default="/root/arifOS")
    ap.add_argument(
        "--out",
        default="/root/A-FORGE/forge_work",
        help="Parent dir; writes under YYYY-MM-DD/",
    )
    ap.add_argument("--note", default="")
    ap.add_argument("--actor", default="grok-build")
    ap.add_argument("--session-id", default="")
    args = ap.parse_args()

    root = Path(args.repo).resolve()
    if not (root / ".git").exists():
        print(f"ERROR: not a git repo: {root}", file=sys.stderr)
        return 2

    now = datetime.now(UTC)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    day = now.strftime("%Y-%m-%d")

    head = sh("git rev-parse HEAD", root)
    short = head[:7]
    tree = sh("git rev-parse HEAD^{tree}", root)
    branch = sh("git rev-parse --abbrev-ref HEAD", root)
    dirty = sh("git status --porcelain", root)
    try:
        remote = sh("git remote get-url origin", root)
    except subprocess.CalledProcessError:
        remote = ""

    wt, nfiles = working_tree_hash(root)

    receipt: dict = {
        "receipt_type": "GIT_CHANGE_RECEIPT",
        "receipt_id": f"change-{day}-{short}-{now.strftime('%H%M%S')}",
        "timestamp_utc": ts,
        "actor": args.actor,
        "session_id": args.session_id or None,
        "note": args.note or None,
        "repo": {
            "path": str(root),
            "remote": remote,
            "branch": branch,
            "head": head,
            "short": short,
            "tree_hash": tree,
            "working_tree_content_hash_sha256": wt,
            "files_hashed": nfiles,
            "dirty": bool(dirty),
            "dirty_paths": [line[3:] for line in dirty.splitlines()] if dirty else [],
        },
    }

    # self-hash without receipt_sha256 first
    body = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(body).hexdigest()

    out_dir = Path(args.out) / day
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"CHANGE-RECEIPT-{short}-{now.strftime('%H%M%S')}.json"
    out_path.write_text(json.dumps(receipt, indent=2) + "\n")

    # also keep a latest pointer for the day
    latest = out_dir / "CHANGE-RECEIPT-LATEST.json"
    latest.write_text(json.dumps(receipt, indent=2) + "\n")

    print(
        json.dumps(
            {
                "ok": True,
                "path": str(out_path),
                "receipt_id": receipt["receipt_id"],
                "receipt_sha256": receipt["receipt_sha256"],
                "head": short,
                "tree": tree[:12],
                "working_tree": wt[:16],
                "dirty": bool(dirty),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""boundary_ratchet — fail-on-NEW architecture boundary gate (F4/F11).

Reads contracts from boundary/.importlinter (INI), evaluates via import-linter
CLI (handles multi-root-packages), diffs against EXCEPTIONS-LEDGER.json.

Ratchet doctrine (AAA/domain-atlas/code-intel/RATIFICATION-2026-09-16.md):
  - CI fails ONLY on NEW contract-edge violations or EXPIRED ledger entries.
  - Ledger expiry auto-tightens; extending is a deliberate, diff-visible edit.
  - Violation identity = contract-level edge (source_pkg -> forbidden_pkg),
    parsed from the stable header line "X is not allowed to import Y:".

Usage:
  python3 boundary/boundary_ratchet.py [--repo-root DIR] [--config PATH]
Exit: 0 pass / 1 new-or-expired / 2 tooling error.
Deps: import-linter (pip install import-linter).
"""

import argparse
import configparser
import datetime
import json
import pathlib
import re
import subprocess
import sys

HEADER_RE = re.compile(r"^([\w.]+) is not allowed to import ([\w.]+):")


def load_contracts(cfg_path: pathlib.Path) -> tuple[list[str], list[dict]]:
    cp = configparser.ConfigParser()
    if not cp.read(cfg_path):
        raise FileNotFoundError(cfg_path)
    root_packages = [p.strip() for p in cp["importlinter"]["root_packages"].split()]
    contracts = []
    for section in cp.sections():
        if not section.startswith("importlinter:contract:"):
            continue
        c = cp[section]
        contracts.append(
            {
                "id": section.split(":", 2)[2],
                "sources": [s.strip() for s in c["source_modules"].split()],
                "forbidden": [s.strip() for s in c["forbidden_modules"].split()],
            }
        )
    return root_packages, contracts


def run_lint(cfg: pathlib.Path, repo_root: pathlib.Path) -> tuple[int, list[str]]:
    proc = subprocess.run(
        ["lint-imports", "--config", str(cfg), "--no-cache"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    edges: list[str] = []
    for line in (proc.stdout + "\n" + proc.stderr).splitlines():
        m = HEADER_RE.match(line.strip())
        if m:
            edges.append(f"{m.group(1)} -> {m.group(2)}")
    return proc.returncode, sorted(set(edges))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", type=pathlib.Path)
    ap.add_argument("--config", default=None, type=pathlib.Path)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    cfg = (args.config or root / "boundary" / ".importlinter").resolve()
    ledger_path = cfg.parent / "EXCEPTIONS-LEDGER.json"

    try:
        root_packages, contracts = load_contracts(cfg)
    except Exception as e:
        print(f"BOUNDARY RATCHET: TOOLING ERROR (config): {e}")
        return 2

    proc_rc, current_edges = run_lint(cfg, root)
    src_of = {}
    for c in contracts:
        for s in c["sources"]:
            src_of[s] = c["id"]
    current: dict[str, list[str]] = {}
    for edge in current_edges:
        src = edge.split(" -> ")[0]
        cid = src_of.get(src)
        if cid is None:
            for s, c_id in src_of.items():
                if src == s or src.startswith(s + "."):
                    cid = c_id
                    break
        if cid:
            current.setdefault(cid, []).append(edge)

    try:
        ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {"violations": []}
    except json.JSONDecodeError as e:
        print(f"BOUNDARY RATCHET: TOOLING ERROR (ledger json): {e}")
        return 2
    allowed = {v["contract"] + "|" + v["path"]: v["expires"] for v in ledger.get("violations", [])}

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    new_v, expired_v, kept = [], [], []
    current_keys = set()
    for cid, edges in current.items():
        for e in edges:
            key = f"{cid}|{e}"
            current_keys.add(key)
            if key not in allowed:
                new_v.append(key)
            elif allowed[key] < today:
                expired_v.append(key)
            else:
                kept.append(key)
    stale = [k for k in allowed if k not in current_keys]

    for k in new_v:
        print(f"NEW VIOLATION: {k}")
    for k in expired_v:
        print(f"EXPIRED EXCEPTION (now failing): {k}")
    for k in stale:
        print(f"note: fixed upstream — remove ledger entry to shrink debt: {k}")

    if new_v or expired_v:
        print(
            f"BOUNDARY RATCHET: FAIL ({len(new_v)} new, {len(expired_v)} expired, {len(kept)} known)"
        )
        return 1
    print(
        f"BOUNDARY RATCHET: PASS ({len(kept)} known violations under exception, {len(stale)} stale ledger)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

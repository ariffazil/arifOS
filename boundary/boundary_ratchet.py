#!/usr/bin/env python3
"""boundary_ratchet — fail-on-NEW architecture boundary gate (F4/F11).

Design: reads contracts from boundary/.importlinter (INI), evaluates them
DIRECTLY via grimp (no CLI output parsing), diffs against EXCEPTIONS-LEDGER.json.

Ratchet doctrine (AAA/domain-atlas/code-intel/INDEX.md):
  - CI fails ONLY on NEW contract-edge violations or EXPIRED ledger entries.
  - Ledger expiry auto-tightens; extending is a deliberate, diff-visible edit.
  - Violation identity = contract-level edge (source_pkg -> forbidden_pkg),
    immune to line-number churn.

Usage:
  python3 boundary/boundary_ratchet.py            # repo root = cwd
Exit: 0 pass / 1 new-or-expired / 2 tooling error.
Deps: grimp (pip install grimp).
"""

import argparse
import configparser
import datetime
import json
import pathlib
import sys

import grimp


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
                "type": c.get("type", "forbidden"),
                "sources": [s.strip() for s in c["source_modules"].split()],
                "forbidden": [s.strip() for s in c["forbidden_modules"].split()],
            }
        )
    return root_packages, contracts


def evaluate(root_packages: list[str], contracts: list[dict]) -> dict[str, list]:
    graphs = {p: grimp.build_graph(p) for p in root_packages}
    violated: dict[str, list] = {}
    for c in contracts:
        edges = []
        for src in c["sources"]:
            for dst in c["forbidden"]:
                for pkg, g in graphs.items():
                    if not (
                        pkg == src
                        or pkg in src
                        or src in pkg
                        or pkg == dst
                        or pkg in dst
                        or dst in pkg
                    ):
                        continue
                    try:
                        chains = g.find_shortest_chains(src, dst)
                    except (ValueError, KeyError):
                        continue
                    if chains:
                        chain = sorted(chains)[0]
                        edges.append({"edge": f"{src} -> {dst}", "chain": list(chain)})
        if edges:
            violated[c["id"]] = edges
    return violated


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".", type=pathlib.Path)
    ap.add_argument("--config", default=None, type=pathlib.Path)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    cfg = (args.config or root / "boundary" / ".importlinter").resolve()
    here = cfg.parent
    ledger_path = here / "EXCEPTIONS-LEDGER.json"

    try:
        root_packages, contracts = load_contracts(cfg)
        current = evaluate(root_packages, contracts)
    except Exception as e:
        print(f"BOUNDARY RATCHET: TOOLING ERROR: {e}")
        return 2

    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {"violations": []}
    allowed = {v["contract"] + "|" + v["path"]: v["expires"] for v in ledger.get("violations", [])}

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    new_v, expired_v, kept_edges = [], [], []
    for cid, edges in current.items():
        for e in edges:
            key = f"{cid}|{e['edge']}"
            if key not in allowed:
                new_v.append((key, e["chain"]))
            elif allowed[key] < today:
                expired_v.append(key)
            else:
                kept_edges.append(key)
    stale = [
        k
        for k in allowed
        if k.split("|")[0] not in current
        or not any(f"{cid}|{e['edge']}" == k for cid in current for e in current[cid])
    ]

    for k, chain in new_v:
        print(f"NEW VIOLATION: {k}\n  chain: {' -> '.join(chain)}")
    for k in expired_v:
        print(f"EXPIRED EXCEPTION (now failing): {k}")
    for k in stale:
        print(f"note: fixed upstream — remove ledger entry to shrink debt: {k}")

    if new_v or expired_v:
        print(
            f"BOUNDARY RATCHET: FAIL ({len(new_v)} new, {len(expired_v)} expired, {len(kept_edges)} known)"
        )
        return 1
    print(
        f"BOUNDARY RATCHET: PASS ({len(kept_edges)} known violations under exception, {len(stale)} stale ledger)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

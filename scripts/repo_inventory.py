#!/usr/bin/env python3
"""repo_inventory.py — 000 INIT read-only inventory (H_0 = measure, don't guess).

Classifies the arifOS tree WITHOUT moving, creating, or deleting anything.
Produces repo-inventory.json: disposition buckets + entropy signals + migration plan
INPUT (not executed). Respects the 888 HOLD: no live path is changed.

Disposition buckets:
  KEEP_CANON  KEEP_RUNTIME  GENERATE  MIGRATE  COMPATIBILITY_SHIM
  ARCHIVE  DELETE_AFTER_PROOF  UNKNOWN_HOLD
"""

from __future__ import annotations
import os, re, json, hashlib, datetime

ROOT = "/root/arifOS"
OUT = os.path.join(ROOT, "repo-inventory.json")

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "build",
    "node_modules",
    "__pycache__",
    ".ua",
    ".claude",
    ".config",
    ".grimp_cache",
    ".import_linter_cache",
    ".arifos",
    ".collab",
    "dist",
    "egg-info",
    ".github",
}

# ── entropy signal patterns ────────────────────────────────────────────────────
SOT_LIKE = re.compile(
    r"(sot|capability_registry|tool_registry|tool_charter|mcp\.charter|"
    r"tool_manifest|CANONICAL_SPEC|constitutional_map|tools\.yaml|"
    r"toolssot|tools_sot|kernel-sot)",
    re.I,
)
SERVER_LIKE = re.compile(
    r"(^|/)(server|main|app|__main__)(_|\.|\d|new|real|fixed|v2|2)?\.py$", re.I
)
ENTROPY_NAME = re.compile(
    r"(\.pre-forged|\.bak|\.bak-|final2?\.|_new\.|_old\.|_copy\.|"
    r"_v2\.|_fixed\.|_real\.|2\.py$|-copy\.|-old\.)",
    re.I,
)
ARCHIVE_IN_ACTIVE = re.compile(r"(archive|deprecated|legacy|stub|shim|compat)", re.I)


def disposition(path: str, rel: str) -> str:
    base = os.path.basename(path)
    if rel.startswith(("archive/", "experiments/", "deprecated/", "legacy/")):
        return "ARCHIVE"
    if ENTROPY_NAME.search(base) or ENTROPY_NAME.search(rel):
        return "DELETE_AFTER_PROOF"
    if "/generated/" in rel or "/static/manifest/" in rel:
        return "GENERATE"
    if SOT_LIKE.search(base):
        return "KEEP_CANON" if base in ("kernel-sot.yaml",) else "MIGRATE"
    if SERVER_LIKE.search(base):
        return "KEEP_RUNTIME"
    return "UNKNOWN_HOLD"


def scan():
    entries = []  # (relpath, disposition, kind, size, sha)
    signals = {
        "parallel_sot": [],
        "multiple_server": [],
        "entropy_names": [],
        "archive_in_active": [],
    }
    tops = {}

    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, ROOT)
            # top-level classification (first path segment)
            seg = rel.split("/")[0]
            tops.setdefault(seg, {"files": 0, "bytes": 0})
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            tops[seg]["files"] += 1
            tops[seg]["bytes"] += size

            base = fn
            disp = disposition(path, rel)
            entries.append(
                {
                    "rel": rel,
                    "disposition": disp,
                    "size": size,
                }
            )

            # signals
            if SOT_LIKE.search(base) and disp != "KEEP_CANON":
                signals["parallel_sot"].append(rel)
            if SERVER_LIKE.search(base) and "test" not in rel:
                signals["multiple_server"].append(rel)
            if ENTROPY_NAME.search(base) or ENTROPY_NAME.search(rel):
                signals["entropy_names"].append(rel)
            if ARCHIVE_IN_ACTIVE.search(rel) and not rel.startswith("archive/"):
                signals["archive_in_active"].append(rel)

    # cap signal lists (huge tree)
    for k in signals:
        signals[k] = sorted(set(signals[k]))[:80]

    buckets = {}
    for e in entries:
        buckets.setdefault(e["disposition"], 0)
        buckets[e["disposition"]] += 1

    return {
        "root": ROOT,
        "top_level": {k: v for k, v in sorted(tops.items(), key=lambda x: -x[1]["files"])},
        "total_files": len(entries),
        "disposition_buckets": dict(sorted(buckets.items())),
        "signals": signals,
        "signal_counts": {k: len(v) for k, v in signals.items()},
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    result = scan()
    with open(OUT, "w") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)

    print(f"repo_inventory — {result['total_files']} files scanned → {OUT}\n")
    print("=== TOP-LEVEL DIRECTORIES (by file count) ===")
    for d, v in list(result["top_level"].items())[:30]:
        print(f"  {d:<28} files={v['files']:<5} bytes={v['bytes']}")
    print("\n=== DISPOSITION BUCKETS ===")
    for k, v in result["disposition_buckets"].items():
        print(f"  {k:<22} {v}")
    print("\n=== ENTROPY SIGNALS (counts) ===")
    for k, v in result["signal_counts"].items():
        print(f"  {k:<22} {v}")
    print("\n=== PARALLEL SOT-LIKE FILES (candidates for migration) ===")
    for f in result["signals"]["parallel_sot"][:40]:
        print(f"  {f}")
    print("\n=== MULTIPLE SERVER/ENTRYPOINT FILES ===")
    for f in result["signals"]["multiple_server"][:30]:
        print(f"  {f}")
    print("\n=== ENTROPY NAMES (.bak/.pre-forged/final/v2/copy) — sample ===")
    for f in result["signals"]["entropy_names"][:30]:
        print(f"  {f}")

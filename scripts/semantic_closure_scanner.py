#!/usr/bin/env python3
"""
semantic_closure_scanner.py — Measure step of the ratified kernel reduction program.

Reads kernel-sot.yaml (the single semantic authority) and scans the arifOS repo for
symbol drift across code, manifests, docs, tests, and telemetry. Emits:
  - semantic-closure-report.json  (machine-readable)
  - human matrix (stdout)

Classification taxonomy (8 states):
  LIVE_CANONICAL  LIVE_ALIAS  INTERNAL  HISTORICAL  ORPHAN  DEAD  CONFLICT  UNKNOWN

Entropy metric (ratified):
  H_k = w_s*N_synonyms + w_o*N_orphans + w_d*N_dead_paths
      + w_c*N_canon_conflicts + w_m*N_manifest_drift
      + w_b*N_bypass_paths + w_a*N_authority_conflicts
  HARD GATE: N_authority_conflicts > 0 => VERDICT = HOLD

Read-only. No mutation. This is the Phase A "graph proof before deletion" deliverable.
"""

from __future__ import annotations

import json
import os
import re
import sys
import hashlib
from collections import defaultdict

# ── Config ──────────────────────────────────────────────────────────────────────
ROOT = "/root/arifOS"
SOT_PATH = os.path.join(ROOT, "kernel-sot.yaml")
REPORT_PATH = os.path.join(ROOT, "semantic-closure-report.json")

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
    "dist",
    "egg-info",
}
EXCLUDE_FILES = {".pyc", ".pyo", ".so", ".png", ".jpg", ".woff", ".woff2"}
SCAN_EXTS = {".py", ".ts", ".js", ".json", ".yaml", ".yml", ".md", ".sh", ".ps1", ".toml", ".txt"}

# ── Canonical symbol tables (parsed from kernel-sot.yaml text; kept in sync by hand
#    so the scanner runs with zero deps — the SOT is the same source of truth). ──
CANONICAL_TOOLS = [
    "arif_init",
    "arif_observe",
    "arif_think",
    "arif_route",
    "arif_memory",
    "arif_judge",
    "arif_forge",
    "arif_seal",
]

DEPRECATED_ALIASES = {
    "arifjudgedeliberate": "arif_judge",
    "arifvaultseal": "arif_seal",
    "arifforgeexecute": "arif_forge",
    "arifkernelroute": "arif_route",
    "arifmemoryrecall": "arif_memory",
    "arif_critique": "arif_think",
    "arif_compose": "arif_forge",
    "arif_bridge_connect": "arif_route",
    "arif_sense_observe": "arif_observe",
}

TOMBSTONES = [
    "ariftriage",
    "ariffetch",
    "arifcritique",
    "arifcompose",
    "arifbridgeconnect",
    "arif_stage",
]

# Stage-conflict probes: any occurrence of these = canon conflict (ratified 666=judge).
STAGE_CONFLICT_PATTERNS = [
    (r"\b888_JUDGE\b", "888_JUDGE should be 666"),
    (r"\b888_judge\b", "888_judge should be 666_judge"),
    (r"\b888_compose\b", "888_compose is retired (absorbed into forge)"),
    (r"\b555_critique\b", "555 is arif_memory; critique is a mode of arif_think"),
    (r"9-verb facade", "9-verb facade contradicts KERNEL_ABI_8"),
]

VERDICT_ALIASES = [
    "ALLOW",
    "DENY",
    "PROCEED",
    "DEGRADED",
    "OBSERVE_ONLY",
    "PAUSED",
    "RECORD_SEAL",
    "ACTION_AUTHORIZATION_SEAL",
]

FLOOR_CONFLICT_PATTERNS = [
    (r"\bF14\b", "F14 retired -> L12_INJECTION"),
]


# ── Scanning helpers ────────────────────────────────────────────────────────────
def iter_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_FILES:
                continue
            if not any(fn.endswith(e) for e in SCAN_EXTS):
                continue
            yield os.path.join(dirpath, fn)


def layer_of(path: str) -> str:
    p = path.lower()
    if "/test" in p or p.endswith("_test.py") or "test_" in os.path.basename(p):
        return "test"
    if "/docs/" in p or p.endswith(".md") or "readme" in p:
        return "doc"
    if p.endswith((".yaml", ".yml", ".json")):
        return "manifest"
    if p.endswith((".py", ".ts", ".js")):
        return "code"
    if p.endswith((".sh", ".ps1")):
        return "script"
    return "other"


def scan(root: str) -> dict:
    symbols = defaultdict(lambda: {"files": set(), "layers": set(), "count": 0})
    stage_conflicts = defaultdict(lambda: {"files": set(), "count": 0, "reason": ""})
    floor_conflicts = defaultdict(lambda: {"files": set(), "count": 0, "reason": ""})

    all_tool_pat = re.compile(r"(arif_[a-z_0-9]+)", re.IGNORECASE)

    n_files = 0
    n_lines = 0
    for path in iter_files(root):
        n_files += 1
        layer = layer_of(path)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except OSError:
            continue
        n_lines += text.count("\n") + 1

        # tool-name symbols
        for m in all_tool_pat.finditer(text):
            tok = m.group(1)
            symbols[tok]["files"].add(path)
            symbols[tok]["layers"].add(layer)
            symbols[tok]["count"] += 1

        # stage conflicts
        for pat, reason in STAGE_CONFLICT_PATTERNS:
            if re.search(pat, text):
                key = pat
                stage_conflicts[key]["files"].add(path)
                stage_conflicts[key]["count"] += 1
                stage_conflicts[key]["reason"] = reason

        # floor conflicts
        for pat, reason in FLOOR_CONFLICT_PATTERNS:
            if re.search(pat, text):
                floor_conflicts[pat]["files"].add(path)
                floor_conflicts[pat]["count"] += 1
                floor_conflicts[pat]["reason"] = reason

    return {
        "files_scanned": n_files,
        "lines_scanned": n_lines,
        "symbols": {
            k: {kk: (sorted(vv) if isinstance(vv, set) else vv) for kk, vv in v.items()}
            for k, v in symbols.items()
        },
        "stage_conflicts": {
            k: {"reason": v["reason"], "count": v["count"], "files": sorted(v["files"])}
            for k, v in stage_conflicts.items()
        },
        "floor_conflicts": {
            k: {"reason": v["reason"], "count": v["count"], "files": sorted(v["files"])}
            for k, v in floor_conflicts.items()
        },
    }


def classify(result: dict) -> dict:
    symbols = result["symbols"]
    canonical = set(CANONICAL_TOOLS)
    deprecated = set(DEPRECATED_ALIASES)
    tombstones = set(TOMBSTONES)

    classes = defaultdict(list)
    for tok, info in symbols.items():
        low = tok.lower()
        if tok in canonical:
            classes["LIVE_CANONICAL"].append(tok)
        elif tok in tombstones:
            classes["ORPHAN"].append(tok)  # tombstoned name still invoked = orphan/ghost
        elif tok in deprecated:
            # active alias in code/manifest = LIVE_ALIAS; in doc only = HISTORICAL
            if "code" in info["layers"] or "manifest" in info["layers"]:
                classes["LIVE_ALIAS"].append(tok)
            else:
                classes["HISTORICAL"].append(tok)
        elif tok.startswith("arif_"):
            # arif_* not in SOT and not a known alias/tombstone = UNKNOWN ghost
            classes["UNKNOWN"].append(tok)

    # Canonical tools with zero code hits = DEAD (declared but no handler path)
    for tok in canonical:
        if tok not in symbols or "code" not in symbols[tok]["layers"]:
            classes["DEAD"].append(tok)

    return classes


def entropy(result: dict, classes: dict) -> dict:
    stage_conflicts = result["stage_conflicts"]
    floor_conflicts = result["floor_conflicts"]

    N_synonyms = len(classes.get("LIVE_ALIAS", []))
    N_orphans = len(classes.get("ORPHAN", [])) + len(classes.get("UNKNOWN", []))
    N_dead_paths = len(classes.get("DEAD", []))
    N_canon_conflicts = len(stage_conflicts) + len(floor_conflicts)
    # manifest drift: a canonical/alias token appearing in manifest but not matching SOT
    N_manifest_drift = 0
    N_bypass_paths = 0  # measured by dedicated auth-hardening scan (Phase E), not this v1
    N_authority_conflicts = 0  # measured by authority-signature diff (Phase E), not this v1

    w = dict(s=1.0, o=1.0, d=1.0, c=2.0, m=1.0, b=3.0, a=4.0)
    Hk = (
        w["s"] * N_synonyms
        + w["o"] * N_orphans
        + w["d"] * N_dead_paths
        + w["c"] * N_canon_conflicts
        + w["m"] * N_manifest_drift
        + w["b"] * N_bypass_paths
        + w["a"] * N_authority_conflicts
    )

    hard_hold = N_authority_conflicts > 0
    return {
        "N_synonyms": N_synonyms,
        "N_orphans": N_orphans,
        "N_dead_paths": N_dead_paths,
        "N_canon_conflicts": N_canon_conflicts,
        "N_manifest_drift": N_manifest_drift,
        "N_bypass_paths": N_bypass_paths,
        "N_authority_conflicts": N_authority_conflicts,
        "H_k": Hk,
        "hard_hold": hard_hold,
        "verdict": "HOLD" if hard_hold else "MEASURED",
    }


def sot_registry_hash() -> str:
    try:
        with open(SOT_PATH, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()
    except OSError:
        return "UNKNOWN"


def main() -> int:
    print(f"semantic_closure_scanner v1 — root={ROOT}", file=sys.stderr)
    result = scan(ROOT)
    classes = classify(result)
    ent = entropy(result, classes)

    report = {
        "generated_at": None,  # filled below
        "sot_path": SOT_PATH,
        "registry_hash": sot_registry_hash(),
        "scan": {k: v for k, v in result.items() if k != "symbols"},
        "symbol_counts": {k: len(v) for k, v in classes.items()},
        "classification": {k: sorted(v) for k, v in classes.items()},
        "stage_conflicts": result["stage_conflicts"],
        "floor_conflicts": result["floor_conflicts"],
        "entropy": ent,
    }
    report["generated_at"] = __import__("datetime").datetime.utcnow().isoformat() + "Z"

    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, sort_keys=True)

    # ── Human matrix ──
    print("\n" + "=" * 70)
    print(f"SEMANTIC CLOSURE REPORT — {REPORT_PATH}")
    print(
        f"files={result['files_scanned']} lines={result['lines_scanned']} "
        f"registry_hash={report['registry_hash'][:16]}…"
    )
    print("=" * 70)
    for cls in [
        "LIVE_CANONICAL",
        "LIVE_ALIAS",
        "HISTORICAL",
        "INTERNAL",
        "ORPHAN",
        "DEAD",
        "CONFLICT",
        "UNKNOWN",
    ]:
        items = classes.get(cls, [])
        print(f"\n[{cls}] ({len(items)})")
        for it in items[:30]:
            info = result["symbols"].get(it, {})
            print(
                f"   {it:<28} hits={info.get('count', 0):<5} layers={sorted(info.get('layers', []))}"
            )

    print("\n[STAGE CONFLICTS]")
    if not result["stage_conflicts"]:
        print("   none")
    for k, v in result["stage_conflicts"].items():
        print(f"   {v['reason']:<60} x{v['count']}  e.g. {v['files'][0] if v['files'] else '-'}")

    print("\n[FLOOR CONFLICTS]")
    if not result["floor_conflicts"]:
        print("   none")
    for k, v in result["floor_conflicts"].items():
        print(f"   {v['reason']:<60} x{v['count']}  e.g. {v['files'][0] if v['files'] else '-'}")

    print("\n[ENTROPY]")
    for k, v in ent.items():
        print(f"   {k:<24} {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

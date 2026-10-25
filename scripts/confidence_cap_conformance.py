#!/usr/bin/env python3
"""
F7 confidence-cap conformance scan (2026-10-20)
═══════════════════════════════════════════════

WHY
---
F13 ratified the F7 clarification (GENESIS/FLOOR_TABLE.json, sealed range,
2026-08-09): Ω₀ ∈ [0.03, 0.05] is an UNCERTAINTY FLOOR, not a confidence cap.
The derived cap is 1 − Ω₀ ∈ [0.95, 0.97].

The canon spells out why it matters:

    "If you cap confidence at 0.90, the system stops at '90% sure.'
     If you floor uncertainty at 0.03, the system can reach 99% confidence
     but must still ask: 'What would falsify this?' The difference is the
     difference between a wall and a door."

The amendment reached the canon. It did not reach the code. This script
MEASURES that gap. It does not decide it: changing an enforcement clamp is
a constitutional mutation that belongs to F13.

WHAT IT SEPARATES
-----------------
  CLAMP      code that physically limits a value (min(x, 0.90), le=0.90,
             a validator that raises above 0.90). Behaviour-changing.
  ASSERTION  prose/policy that states the ceiling. Display-only, but it
             teaches agents the wrong number.
  UNRELATED  0.90 that means something else entirely (e.g. "90% DERIVED
             output = regurgitation" is not a confidence cap). Never touch.

USAGE
    python scripts/confidence_cap_conformance.py [--json PATH] [--md PATH]
Exit code 0 always — this is an instrument, not a gate.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PKG = REPO / "arifosmcp"

CANON = {
    "omega_band": [0.03, 0.05],
    "confidence_cap_operational": 0.96,
    "confidence_cap_max": 0.97,
    "authority": "GENESIS/FLOOR_TABLE.json F7 + 000_KERNEL_CANON.md §3.2",
    "ratified": "2026-08-09 (F13 clarification)",
}

# 0.90 occurrences that are NOT the F7 confidence cap. Matched by line context.
UNRELATED_HINTS = (
    "regurgitation",
    "target ≥",
    "target >=",
    "omega stability ratio",
    "derived",
)

CLAMP_PATTERNS = (
    re.compile(r"\bmin\(\s*(?:[A-Za-z_][\w.]*\s*,\s*)?0\.90\b"),
    re.compile(r"\ble\s*=\s*0\.90\b"),
    re.compile(r">\s*0\.90\b"),
    re.compile(r"cannot exceed 0\.90"),
    re.compile(r"exceeds 0\.90"),
    re.compile(r"exceeds F7 cap \(0\.90\)"),
    re.compile(r"=\s*0\.90\b"),
)


def classify(line: str) -> str:
    low = line.lower()
    if any(h in low for h in UNRELATED_HINTS):
        return "UNRELATED"
    if re.search(r"\bmin\(|le\s*=|\braise\b|return False|HARD_CAP|CONFIDENCE_CAP", line):
        return "CLAMP"
    return "ASSERTION"


def scan() -> dict:
    findings: list[dict] = []
    for path in sorted(PKG.rglob("*.py")):
        parts = path.parts
        if "test" in parts or "build" in parts or "__pycache__" in parts:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (UnicodeDecodeError, OSError):
            continue
        for n, line in enumerate(lines, 1):
            if "0.90" not in line:
                continue
            low = line.lower()
            # only lines that talk about confidence / F7 / a cap
            if not ("confiden" in low or "f7" in low or "omega" in low or "capped" in low):
                continue
            kind = classify(line)
            findings.append(
                {
                    "file": str(path.relative_to(REPO)),
                    "line": n,
                    "kind": kind,
                    "text": line.strip()[:200],
                }
            )
    by_kind: dict[str, int] = {}
    for f in findings:
        by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
    return {
        "scanned_at_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(timespec="seconds"),
        "canon": CANON,
        "totals": {"sites": len(findings), **by_kind},
        "findings": findings,
        "verdict": (
            "CONFORMANT" if by_kind.get("CLAMP", 0) == 0 else "AMENDMENT_NOT_PROPAGATED"
        ),
        "note": (
            "CLAMP sites change behaviour: the kernel refuses what canon permits. "
            "Migrating them is an F13 decision, not a refactor."
        ),
    }


def render_md(report: dict) -> str:
    c = report["canon"]
    lines = [
        "# F7 Confidence-Cap Conformance — measured",
        "",
        f"Measured: `{report['scanned_at_utc']}`",
        f"Verdict: **{report['verdict']}**",
        "",
        "## Canon (sealed)",
        "",
        f"- Ω₀ band: `{c['omega_band']}` — an **uncertainty floor**, not a cap",
        f"- Derived confidence cap: `1 − Ω₀` ∈ "
        f"`[{c['confidence_cap_operational']}, {c['confidence_cap_max']}]`",
        f"- Authority: {c['authority']}, ratified {c['ratified']}",
        "",
        "## Measured",
        "",
        "| Kind | Sites | Meaning |",
        "|---|---|---|",
    ]
    meaning = {
        "CLAMP": "code refuses what canon permits — behaviour change",
        "ASSERTION": "prose states the wrong ceiling — display drift",
        "UNRELATED": "0.90 means something else — leave alone",
    }
    for k in ("CLAMP", "ASSERTION", "UNRELATED"):
        lines.append(f"| {k} | {report['totals'].get(k, 0)} | {meaning[k]} |")
    lines += ["", "## CLAMP sites (the real gap)", "", "| File | Line | Code |", "|---|---|---|"]
    clamps = [f for f in report["findings"] if f["kind"] == "CLAMP"]
    for f in clamps:
        txt = f["text"].replace("|", "\\|")
        lines.append(f"| `{f['file']}` | {f['line']} | `{txt}` |")
    lines += [
        "",
        "## Reading",
        "",
        "The amendment that raised the ceiling from 0.90 to 0.97 reached the",
        "canon and the doctrine prose. It did not reach the enforcement code,",
        "which still clamps at 0.90 in the paths above. No compiler in any",
        "language catches this: Rust and TypeScript would both compile thirty",
        "copies of a stale constant without complaint. The remedy is one",
        "constant with one owner plus a test that fails on drift — which is",
        "what `arifosmcp/constitutional_canon.py` now provides.",
        "",
        f"_{report['note']}_",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--md", default=None)
    args = ap.parse_args()

    report = scan()
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=2), encoding="utf-8")
    if args.md:
        Path(args.md).write_text(render_md(report), encoding="utf-8")

    t = report["totals"]
    print(f"F7 cap conformance: {report['verdict']}")
    print(f"  sites={t['sites']} clamp={t.get('CLAMP', 0)} "
          f"assertion={t.get('ASSERTION', 0)} unrelated={t.get('UNRELATED', 0)}")
    for f in report["findings"]:
        if f["kind"] == "CLAMP":
            print(f"  CLAMP {f['file']}:{f['line']}  {f['text'][:110]}")


if __name__ == "__main__":
    main()

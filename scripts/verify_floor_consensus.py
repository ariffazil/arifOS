#!/usr/bin/env python3
"""
verify_floor_consensus.py — Post-Fix Floor Consensus Verifier
─────────────────────────────────────────────────────────────
Created: 2026-06-02
Purpose: Run after applying floor fixes to verify all sources agree.
         Prints a side-by-side comparison table of pre-fix vs post-fix
         state, and queries the live /health endpoint to confirm
         runtime matches canonical doctrine.

Usage:   python scripts/verify_floor_consensus.py
Exit:    0 on consensus, 1 on disagreement
"""

import json
import sys
import urllib.request


# ──────────────────────────────────────────────────────────────
# CANONICAL DOCTRINE (from core/shared/laws.py THRESHOLDS, L-prefix display)
# Per 2026-06-06 ratification (000_LAWS_TRINITY_ANCHOR.md), output is L-prefix.
# Internal class names retain F-prefix (backward compat); display layer
# translates F→L. /health emits L01-L13 since this commit.
# ──────────────────────────────────────────────────────────────
CANONICAL = {
    "L01": ("AMANAH", "HARD"),
    "L02": ("TRUTH", "HARD"),
    "L03": ("QUAD_WITNESS", "DERIVED"),
    "L04": ("CLARITY", "HARD"),
    "L05": ("PEACE2", "SOFT"),
    "L06": ("EMPATHY", "SOFT"),
    "L07": ("HUMILITY", "HARD"),
    "L08": ("GENIUS", "DERIVED"),
    "L09": ("ANTI_HANTU", "HARD"),  # FIX applied: was SOFT
    "L10": ("ONTOLOGY", "HARD"),
    "L11": ("COMMAND_AUTH", "HARD"),
    "L12": ("INJECTION", "HARD"),
    "L13": ("SOVEREIGN", "HARD"),
}


# ──────────────────────────────────────────────────────────────
# PRE-FIX STATE (what /health USED to report — L-prefix display)
# ──────────────────────────────────────────────────────────────
PRE_FIX_HEALTH = {
    "L01": "hard",
    "L02": "hard",
    "L03": "soft",  # WRONG: should be derived
    "L04": "soft",  # WRONG: should be hard
    "L05": "soft",
    "L06": "hard",  # WRONG: should be soft
    "L07": "soft",  # WRONG: should be hard
    "L08": "soft",  # WRONG: should be derived
    "L09": "hard",  # kernel enforces hard; doctrine said soft
    "L10": "hard",
    "L11": "hard",
    "L12": "soft",  # WRONG: should be hard
    "L13": "hard",
}


def fetch_health() -> dict | None:
    """Fetch live /health and extract governance fields."""
    try:
        with urllib.request.urlopen("http://localhost:8088/health", timeout=5) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        print(f"  WARN: could not fetch /health: {e}", file=sys.stderr)
        return None


def main() -> int:
    print("=" * 90)
    print("  arifOS FLOOR CONSENSUS VERIFICATION — 2026-06-02")
    print("=" * 90)
    print()

    # ── Step 1: Pull live /health ──
    health = fetch_health()
    if health is None:
        print("  ABORT: /health unreachable. Is arifOS service active?")
        return 1

    gov = health.get("governance", {})
    live_hard = set(gov.get("laws_hard_active", []))
    live_soft_full = set(gov.get("floors_soft_doctrinal", []))
    live_derived = set(gov.get("floors_derived_doctrinal", []))
    live_report = gov.get("floors_health_report", {})

    # ── Step 2: Build canonical expected sets ──
    canon_hard = {fid for fid, (_, lvl) in CANONICAL.items() if lvl == "HARD"}
    canon_soft = {fid for fid, (_, lvl) in CANONICAL.items() if lvl == "SOFT"}
    canon_derived = {fid for fid, (_, lvl) in CANONICAL.items() if lvl == "DERIVED"}
    # Combined soft + derived (matches legacy soft_doctrinal field for backward compat)
    canon_soft_combined = canon_soft | canon_derived

    # ── Step 3: Print side-by-side table ──
    hdr = "  {:5} {:14} {:10} {:10} {:10} {:10}  {}".format(
        "Floor", "Name", "Canonical", "Pre-Fix", "Live/Health", "Expected", "Status"
    )
    print(hdr)
    print("  " + "─" * 86)

    fixes_applied = []
    for fid, (name, canon_level) in sorted(CANONICAL.items()):
        pre = PRE_FIX_HEALTH[fid]
        live = live_report.get(fid, "—")
        expected = canon_level.lower()
        match = live == expected

        if pre != expected:
            fixes_applied.append((fid, name, pre, expected))

        row = "  {:5} {:14} {:10} {:10} {:10} {:10}  {}".format(
            fid, name, canon_level, pre, live, expected, "✓" if match else "✗"
        )
        print(row)

    print()
    print("  " + "─" * 86)
    print()

    # ── Step 4: Compare sets ──
    hard_match = live_hard == canon_hard
    soft_match = live_soft_full == canon_soft_combined
    derived_match = live_derived == canon_derived
    report_complete = set(live_report.keys()) == set(CANONICAL.keys())
    all_match = hard_match and soft_match and derived_match and report_complete

    print("  LIVE /health vs CANONICAL")
    print("  ──────────────────────────")
    print(f"  laws_hard_active    : {sorted(live_hard)}")
    print(f"  canonical hard           : {sorted(canon_hard)}")
    print(f"  match                    : {'✓' if hard_match else '✗'}")
    print()
    print(f"  floors_soft_doctrinal    : {sorted(live_soft_full)}")
    print(f"  canonical soft+derived   : {sorted(canon_soft_combined)}")
    print(f"  match                    : {'✓' if soft_match else '✗'}")
    print()
    print(f"  floors_derived_doctrinal : {sorted(live_derived)}")
    print(f"  canonical derived        : {sorted(canon_derived)}")
    print(f"  match                    : {'✓' if derived_match else '✗'}")
    print()
    print(f"  floors_health_report keys: {len(live_report)} / {len(CANONICAL)}")
    print(f"  match                    : {'✓' if report_complete else '✗'}")
    print()

    # ── Step 5: Summary ──
    total = len(CANONICAL)
    fixed = len(fixes_applied)
    clean = total - fixed
    fail_closed = len(canon_hard)

    print("  SUMMARY")
    print("  ───────")
    print(f"  Total floors      : {total}")
    print(f"  Fixed this patch  : {fixed}")
    print(f"  Already correct   : {clean}")
    print(f"  Fail-closed (HARD): {fail_closed} / {total} ({100 * fail_closed // total}%)")
    print()

    if fixes_applied:
        print("  FIXES APPLIED:")
        for fid, name, pre, expected in fixes_applied:
            print(f"    * {fid} {name}: {pre} → {expected}")
        print()

    print(
        f"  Runtime consensus : {'YES — all floors aligned with canonical doctrine' if all_match else 'NO — see mismatches above'}"
    )
    print()
    print("  DITEMPA BUKAN DIBERI")
    print("=" * 90)

    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())

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
# CANONICAL DOCTRINE (from patched core/shared/floors.py THRESHOLDS)
# ──────────────────────────────────────────────────────────────
CANONICAL = {
    "F1":  ("AMANAH",        "HARD"),
    "F2":  ("TRUTH",         "HARD"),
    "F3":  ("QUAD_WITNESS",  "DERIVED"),
    "F4":  ("CLARITY",       "HARD"),
    "F5":  ("PEACE2",        "SOFT"),
    "F6":  ("EMPATHY",       "SOFT"),
    "F7":  ("HUMILITY",      "HARD"),
    "F8":  ("GENIUS",        "DERIVED"),
    "F9":  ("ANTI_HANTU",    "HARD"),      # FIX applied: was SOFT
    "F10": ("ONTOLOGY",      "HARD"),
    "F11": ("COMMAND_AUTH",  "HARD"),
    "F12": ("INJECTION",     "HARD"),
    "F13": ("SOVEREIGN",     "HARD"),
}


# ──────────────────────────────────────────────────────────────
# PRE-FIX STATE (what /health USED to report)
# ──────────────────────────────────────────────────────────────
PRE_FIX_HEALTH = {
    "F1":  "hard",
    "F2":  "hard",
    "F3":  "soft",     # WRONG: should be derived
    "F4":  "soft",     # WRONG: should be hard
    "F5":  "soft",
    "F6":  "hard",     # WRONG: should be soft
    "F7":  "soft",     # WRONG: should be hard
    "F8":  "soft",     # WRONG: should be derived
    "F9":  "hard",     # kernel enforces hard; doctrine said soft
    "F10": "hard",
    "F11": "hard",
    "F12": "soft",     # WRONG: should be hard
    "F13": "hard",
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
    live_hard = set(gov.get("floors_hard_doctrinal", []))
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
        match = (live == expected)

        if pre != expected:
            fixes_applied.append((fid, name, pre, expected))

        row = "  {:5} {:14} {:10} {:10} {:10} {:10}  {}".format(
            fid, name, canon_level, pre, live, expected,
            "✓" if match else "✗"
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
    print(f"  floors_hard_doctrinal    : {sorted(live_hard)}")
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
    print(f"  Fail-closed (HARD): {fail_closed} / {total} ({100*fail_closed//total}%)")
    print()

    if fixes_applied:
        print("  FIXES APPLIED:")
        for fid, name, pre, expected in fixes_applied:
            print(f"    * {fid} {name}: {pre} → {expected}")
        print()

    print(f"  Runtime consensus : {'YES — all floors aligned with canonical doctrine' if all_match else 'NO — see mismatches above'}")
    print()
    print("  DITEMPA BUKAN DIBERI")
    print("=" * 90)

    return 0 if all_match else 1


if __name__ == "__main__":
    sys.exit(main())

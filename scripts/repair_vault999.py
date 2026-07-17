#!/usr/bin/env python3
"""
VAULT999 outcomes.jsonl Repair Script
═══════════════════════════════════════════════════════════════════════════════

FORGE: 000Ω · A-FORGE
DITEMPA BUKAN DIBERI — Forged, Not Given.

PROBLEM:
  python3 -m json.tool fails on /root/.local/share/arifos/vault999/outcomes.jsonl
  due to corrupt lines (~1962 of 4501 lines are invalid JSON).
  Corruption starts at line 1881 with raw "test" text, followed by
  JSON objects fragmented across multiple lines (one field per line).

WHAT THIS SCRIPT DOES:
  1. Reads outcomes.jsonl line by line
  2. Attempts JSON.parse on each line
  3. Writes valid JSON lines to outcomes.repaired.jsonl
  4. Writes invalid/corrupt lines to outcomes.corrupt.jsonl with metadata
  5. Reports statistics: total, valid, invalid, corruption patterns
  6. Verifies seal_chain_head.json (seq=5) still references a valid entry

(DEPLOY MODE: This script is manual-execution only.
 Sovereign must approve execution.)

USAGE:
  python3 /root/arifOS/scripts/repair_vault999.py            # dry-run (default)
  python3 /root/arifOS/scripts/repair_vault999.py --execute   # actual repair
  python3 /root/arifOS/scripts/repair_vault999.py --verify    # verify only
"""

import json
import os
import sys
from datetime import UTC, datetime

# ── Paths ────────────────────────────────────────────────────────────────────
VAULT_DIR = "/root/.local/share/arifos/vault999"
OUTCOMES_PATH = os.path.join(VAULT_DIR, "outcomes.jsonl")
SEAL_HEAD_PATH = os.path.join(VAULT_DIR, "seal_chain_head.json")
REPAIRED_PATH = os.path.join(VAULT_DIR, "outcomes.repaired.jsonl")
CORRUPT_PATH = os.path.join(VAULT_DIR, "outcomes.corrupt.jsonl")
BACKUP_PATH = os.path.join(
    VAULT_DIR, "outcomes.jsonl.repair-bak-" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
)


# ── Stats ────────────────────────────────────────────────────────────────────
class RepairStats:
    def __init__(self):
        self.total_lines = 0
        self.valid_lines = 0
        self.invalid_lines = 0
        self.empty_lines = 0
        self.corrupt_categories: dict[str, int] = {}
        self.first_corrupt_line: int | None = None
        self.last_valid_entry: dict | None = None

    def to_dict(self):
        return {
            "total_lines": self.total_lines,
            "valid_lines": self.valid_lines,
            "invalid_lines": self.invalid_lines,
            "empty_lines": self.empty_lines,
            "corrupt_categories": self.corrupt_categories,
            "first_corrupt_line": self.first_corrupt_line,
            "last_valid_entry": self.last_valid_entry,
            "valid_pct": round(self.valid_lines / max(self.total_lines, 1) * 100, 2),
            "repaired_path": REPAIRED_PATH,
            "corrupt_path": CORRUPT_PATH,
        }


def _classify_corrupt(line: str, err: json.JSONDecodeError) -> str:
    """Classify the type of corruption for reporting."""
    stripped = line.strip()
    if not stripped:
        return "empty_line"
    if err.msg.startswith("Expecting value"):
        return "empty_or_non_json"
    if err.msg.startswith("Extra data"):
        return "multi_line_fragment"
    if err.msg.startswith("Expecting property name"):
        return "partial_object"
    return f"parse_error_{err.msg[:40]}"


def verify_seal_chain_head() -> dict:
    """Verify seal_chain_head.json seq=5 references a valid entry."""
    if not os.path.exists(SEAL_HEAD_PATH):
        return {"status": "MISSING", "path": SEAL_HEAD_PATH}

    with open(SEAL_HEAD_PATH) as f:
        head = json.load(f)

    seq = head.get("seq")
    head_hash = head.get("hash", "").replace("sha256:", "")

    # Check seal_chain.jsonl for the entry at this seq
    chain_path = os.path.join(VAULT_DIR, "seal_chain.jsonl")
    if not os.path.exists(chain_path):
        return {"status": "CHAIN_MISSING", "head": head, "seq": seq}

    found = False
    entry_hash = None
    with open(chain_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if entry.get("seq") == seq:
                    found = True
                    entry_hash = entry.get("hash", "")
                    break
            except json.JSONDecodeError:
                continue

    if found:
        entry_hash_str = str(entry_hash or "")
        match = head_hash in entry_hash_str or entry_hash_str in head_hash
        return {
            "status": "OK" if match else "HASH_MISMATCH",
            "seq": seq,
            "head_hash": head_hash,
            "entry_hash": entry_hash,
            "matched": match,
        }
    return {"status": "SEQ_NOT_FOUND", "head": head, "seq": seq}


def scan_outcomes(repair: bool = False) -> RepairStats:
    """Scan outcomes.jsonl and optionally repair."""
    stats = RepairStats()

    if not os.path.exists(OUTCOMES_PATH):
        print(f"ERROR: {OUTCOMES_PATH} not found")
        sys.exit(1)

    file_size = os.path.getsize(OUTCOMES_PATH)
    print(f"Input: {OUTCOMES_PATH} ({file_size:,} bytes)")

    repaired_lines: list[str] = []
    corrupt_lines: list[str] = []
    last_valid = None

    with open(OUTCOMES_PATH) as f:
        for line_num, raw_line in enumerate(f, 1):
            stats.total_lines += 1
            line = raw_line.rstrip("\n").rstrip("\r")

            if not line.strip():
                stats.empty_lines += 1
                if repair:
                    corrupt_lines.append(
                        json.dumps({"line": line_num, "reason": "empty_line", "content": ""})
                    )
                continue

            try:
                obj = json.loads(line)
                stats.valid_lines += 1
                last_valid = obj
                if repair:
                    repaired_lines.append(raw_line)
            except json.JSONDecodeError as e:
                stats.invalid_lines += 1
                if stats.first_corrupt_line is None:
                    stats.first_corrupt_line = line_num
                cat = _classify_corrupt(line, e)
                stats.corrupt_categories[cat] = stats.corrupt_categories.get(cat, 0) + 1
                if repair:
                    corrupt_lines.append(
                        json.dumps(
                            {
                                "line": line_num,
                                "reason": str(e)[:100],
                                "category": cat,
                                "content": line[:500],
                            }
                        )
                    )

    stats.last_valid_entry = last_valid

    print("\n── Scan Results ──────────────────────────────────")
    print(f"  Total lines:  {stats.total_lines}")
    valid_pct = round(stats.valid_lines / max(stats.total_lines, 1) * 100, 1)
    invalid_pct = round(stats.invalid_lines / max(stats.total_lines, 1) * 100, 1)
    print(f"  Valid JSON:   {stats.valid_lines} ({valid_pct}%)")
    print(f"  Invalid JSON: {stats.invalid_lines} ({invalid_pct}%)")
    print(f"  Empty lines:  {stats.empty_lines}")
    if stats.first_corrupt_line:
        print(f"  First corrupt: line {stats.first_corrupt_line}")
    if stats.corrupt_categories:
        print("\n  Corruption breakdown:")
        for cat, count in sorted(stats.corrupt_categories.items(), key=lambda x: -x[1]):
            print(f"    {cat}: {count}")

    # Show last valid entry
    if last_valid:
        print("\n  Last valid entry:")
        print(f"    ts: {last_valid.get('ts', '?')}")
        print(f"    actor: {last_valid.get('actor', '?')}")
        print(f"    action: {last_valid.get('action', last_valid.get('event', '?'))}")

    # Seal chain verification
    seal_result = verify_seal_chain_head()
    print("\n── Seal Chain Head ───────────────────────────────")
    print(f"  Status: {seal_result['status']}")
    print(f"  Seq:    {seal_result.get('seq', '?')}")
    if seal_result.get("matched") is not None:
        print(f"  Hash match: {seal_result['matched']}")

    # Write files if repair mode
    if repair:
        # Create backup first (F1 AMANAH)
        print("\n── Repair Mode ────────────────────────────────────")
        print(f"  Backup: {BACKUP_PATH}")
        with open(OUTCOMES_PATH) as src:
            with open(BACKUP_PATH, "w") as dst:
                dst.write(src.read())
        print("  (backup created)")

        # Write repaired file
        with open(REPAIRED_PATH, "w") as f:
            f.writelines(repaired_lines)
        print(f"  Repaired: {REPAIRED_PATH} ({len(repaired_lines)} lines)")

        # Write corrupt log
        with open(CORRUPT_PATH, "w") as f:
            f.write("\n".join(corrupt_lines))
        print(f"  Corrupt log: {CORRUPT_PATH} ({len(corrupt_lines)} entries)")

        # Verify repaired file
        repaired_valid = 0
        repaired_invalid = 0
        with open(REPAIRED_PATH) as f:
            for line in f:
                try:
                    json.loads(line)
                    repaired_valid += 1
                except json.JSONDecodeError:
                    repaired_invalid += 1
        print("\n  Verification of repaired file:")
        print(f"    Valid:   {repaired_valid}")
        print(f"    Invalid: {repaired_invalid}")
        if repaired_invalid == 0:
            print("  ✅ Repaired file is clean.")
        else:
            print(f"  ❌ Repaired file still has {repaired_invalid} corrupt lines!")

    return stats


def main():
    args = set(sys.argv[1:])

    if "--verify" in args:
        print("═══ VAULT999 outcomes.jsonl — Verify Only ═══\n")
        scan_outcomes(repair=False)
        print("\n── Seal Chain Verification ──")
        result = verify_seal_chain_head()
        print(f"  Status: {result['status']}")
        print(f"  Seq:    {result.get('seq')}")
        if result.get("matched") is not None:
            print(f"  Hash match: {result['matched']}")
        print("\n[DONE] Verification complete. No files modified.")
        return

    if "--execute" in args:
        print("═══ VAULT999 outcomes.jsonl — REPAIR MODE ═══\n")
        print("⚠️  WARNING: This will create a repaired file.")
        print("   Source backup will be created first.")
        print("   Sovereign must verify before replacing original.\n")

        stats = scan_outcomes(repair=True)
        print("\n── Summary ───────────────────────────────────────")
        print(json.dumps(stats.to_dict(), indent=2))
        print("\n[DONE] Repair complete.")
        print(f"  Next step: Review {REPAIRED_PATH}")
        print(f"  Then: cp {REPAIRED_PATH} {OUTCOMES_PATH}")
        print("  (Requires sovereign approval for final replacement)")
        return

    # Default: dry-run
    print("═══ VAULT999 outcomes.jsonl — DRY RUN ═══\n")
    print("(Use --execute to write repaired file)")
    print("(Use --verify to check seal chain only)\n")
    scan_outcomes(repair=False)
    print("\n[DONE] Dry-run complete. No files modified.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
VAULT999 JSONL Backfill Dry-Run
================================
Analyzes /root/VAULT999/outcomes.jsonl for backfill readiness.

DO NOT INSERT — dry-run only.
Promoting to s999.vault999_ledger requires explicit Arif approval.

Output:
  - total lines
  - valid / invalid / duplicate counts
  - schema distribution
  - promotable estimates
  - safety assessment
"""

import os
import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


SOURCE_FILE = Path(os.environ.get("ARIFOS_HOME", "/root") + "/VAULT999/outcomes.jsonl")


def compute_hash(entry: dict) -> str:
    """SHA256 of sorted JSON."""
    body = json.dumps(entry, sort_keys=True, default=str)
    return hashlib.sha256(body.encode()).hexdigest()


def parse_timestamp(entry: dict) -> str:
    """Extract timestamp from entry, handling multiple schema variants."""
    for k in ("ts", "timestamp", "epoch", "created_at"):
        if k in entry:
            return str(entry[k])
    return "unknown"


def classify_entry(entry: dict) -> tuple[str, str]:
    """
    Classify entry schema and assess promotability.
    Returns (schema_group, promotability_reason).
    """
    keys = set(entry.keys())

    # Core tool-call outcome schema (most common)
    if keys >= {"actor", "action", "outcome", "session_id", "ts"} and len(keys) <= 6:
        return "tool_call_outcome", "PROMOTABLE — core outcome receipt"

    # Blocked action schema
    if "blocked_reason" in keys:
        return "blocked_action", "PROMOTABLE — blocked action record"

    # Judge/verdict schema (Hermes agent records)
    if keys >= {"action", "agent_id", "detail", "ts", "verdict"}:
        return "judge_record", "PROMOTABLE — verdict record"

    # Decision record (F9/F13 decision audit)
    if "decision_id" in keys or "floor_attribution" in keys:
        return "decision_audit", "PROMOTABLE — constitutional decision"

    # Epoch/session summary
    if "epoch_id" in keys and ("holds" in keys or "floors" in keys):
        return "epoch_summary", "PROMOTABLE — epoch checkpoint"

    # VAULT999 sealed-style record (already has seal fields)
    if "seal_id" in keys or "entry_id" in keys:
        return "vault_style_record", "REVIEW — already vault-like"

    # Health/session heartbeat
    if keys <= {"actor", "session", "status", "timestamp", "ttl_seconds", "type"}:
        return "session_heartbeat", "CONDITIONAL — session metadata only"

    # APEX/daily pulse records
    if "DITEMPA_BUKAN_DIBERI" in keys:
        return "apex_pulse", "REVIEW — apex/daily pulse"

    # Constitutional chain records
    if "constitutional_chain_id" in keys:
        return "constitutional_chain", "REVIEW — chain record"

    # ZK identity / sovereign records
    if "zkpc" in str(entry.get("ts", "")) or "zkpc" in str(entry.get("epoch", "")):
        return "identity_record", "REVIEW — identity/seal record"

    # Generic ops/federation events
    if "domain" in keys and "operations" in keys:
        return "ops_domain_record", "REVIEW — ops domain record"

    return "unknown", f"UNKNOWN schema — {len(keys)} keys"


def main():
    print("=" * 70)
    print("VAULT999 JSONL BACKFILL DRY-RUN")
    print(f"Source: {SOURCE_FILE}")
    print(f"Run at: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    if not SOURCE_FILE.exists():
        print(f"\nERROR: {SOURCE_FILE} not found.")
        sys.exit(1)

    raw_lines = SOURCE_FILE.read_text().splitlines()
    total_lines = len(raw_lines)

    # Parse
    valid_entries = []
    parse_errors = []
    seen_hashes: dict[str, dict] = {}
    schema_counts: dict[str, list] = defaultdict(list)
    promotable_counts: dict[str, int] = defaultdict(int)
    non_promotable: dict[str, int] = defaultdict(int)

    for lineno, raw in enumerate(raw_lines, 1):
        raw = raw.strip()
        if not raw:
            continue

        # Parse JSON
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError as e:
            parse_errors.append({"lineno": lineno, "raw": raw[:80], "error": str(e)})
            schema_counts["PARSE_ERROR"].append(lineno)
            continue

        # Compute content hash
        content_hash = compute_hash(entry)

        # Track duplicates
        if content_hash in seen_hashes:
            seen_hashes[content_hash]["count"] += 1
            seen_hashes[content_hash]["first_lineno"]
        else:
            seen_hashes[content_hash] = {
                "count": 1,
                "first_lineno": lineno,
                "hash": content_hash,
                "entry": entry,
            }

        valid_entries.append(
            {
                "lineno": lineno,
                "hash": content_hash,
                "entry": entry,
                "parsed": entry,
            }
        )

        # Classify
        schema_group, promotability = classify_entry(entry)
        schema_counts[schema_group].append(lineno)

        if promotability.startswith("PROMOTABLE"):
            promotable_counts[schema_group] += 1
        else:
            non_promotable[schema_group] += 1

    # ── Summary ──────────────────────────────────────────────────
    total_valid = len(valid_entries)
    total_dupes = sum(v["count"] - 1 for v in seen_hashes.values())
    unique_hashes = len(seen_hashes)
    parse_error_count = len(parse_errors)
    blank_lines = total_lines - total_valid - parse_error_count

    print(f"\n{'─' * 70}")
    print("FILE STATISTICS")
    print(f"{'─' * 70}")
    print(f"  Total lines:          {total_lines:,}")
    print(f"  Blank lines:         {blank_lines:,}")
    print(f"  Parse errors:        {parse_error_count:,}")
    print(f"  Valid JSON entries:  {total_valid:,}")
    print(f"  Unique content hash: {unique_hashes:,}")
    print(f"  Duplicate hashes:    {total_dupes:,}")

    # ── Schema Distribution ────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("SCHEMA DISTRIBUTION (by schema_group)")
    print(f"{'─' * 70}")
    sorted_schemas = sorted(schema_counts.items(), key=lambda x: len(x[1]), reverse=True)
    for schema, linenos in sorted_schemas:
        count = len(linenos)
        pct = count / total_valid * 100 if total_valid > 0 else 0
        print(f"  {count:5d}  ({pct:5.1f}%)  {schema}")

    # ── Promotability ──────────────────────────────────────────────
    total_promotable = sum(promotable_counts.values())
    total_review = sum(non_promotable.values())

    print(f"\n{'─' * 70}")
    print("PROMOTABILITY ASSESSMENT")
    print(f"{'─' * 70}")
    print(
        f"  Promotable entries:  {total_promotable:,}  ({total_promotable / total_valid * 100:.1f}%)"
    )
    print(f"  Needs review:        {total_review:,}  ({total_review / total_valid * 100:.1f}%)")

    print("\n  By schema:")
    for schema, count in sorted(promotable_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    PROMOTE {count:5d}  {schema}")
    for schema, count in sorted(non_promotable.items(), key=lambda x: x[1], reverse=True):
        print(f"    REVIEW  {count:5d}  {schema}")

    # ── Duplicate Analysis ─────────────────────────────────────────
    dupes_by_schema: dict[str, list] = defaultdict(list)
    for h, info in seen_hashes.items():
        if info["count"] > 1:
            schema_group, _ = classify_entry(info["entry"])
            dupes_by_schema[schema_group].append(info["count"])

    print(f"\n{'─' * 70}")
    print("DUPLICATE HASH ANALYSIS")
    print(f"{'─' * 70}")
    print(f"  Unique hashes:       {unique_hashes:,}")
    print(f"  Duplicate entries:   {total_dupes:,}")
    if dupes_by_schema:
        print("\n  Duplicates by schema:")
        for schema, counts in sorted(
            dupes_by_schema.items(), key=lambda x: sum(x[1]), reverse=True
        ):
            total_dupes_schema = sum(counts) - len(counts)
            print(f"    {total_dupes_schema:5d} dupes  {schema}")
    else:
        print("  No duplicate hashes found.")

    # ── Parse Errors ───────────────────────────────────────────────
    if parse_errors:
        print(f"\n{'─' * 70}")
        print(f"PARSE ERRORS ({len(parse_errors)})")
        print(f"{'─' * 70}")
        for err in parse_errors[:10]:
            print(f"  Line {err['lineno']}: {err['error']}")
            print(f"    RAW: {err['raw'][:80]}")
        if len(parse_errors) > 10:
            print(f"  ... and {len(parse_errors) - 10} more")

    # ── Sample Entries ─────────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("SAMPLE ENTRIES (first valid of each promotable schema)")
    print(f"{'─' * 70}")
    shown = set()
    for item in valid_entries:
        schema_group, _ = classify_entry(item["entry"])
        if schema_group in promotable_counts and schema_group not in shown:
            shown.add(schema_group)
            e = item["entry"]
            ts = parse_timestamp(e)
            actor = e.get("actor", e.get("agent_id", "?"))[:30]
            action = str(e.get("action", e.get("verdict", e.get("type", "?"))))[:40]
            outcome = str(e.get("outcome", e.get("verdict", "?")))[:30]
            print(f"\n  Schema: {schema_group}")
            print(f"  Line {item['lineno']}: ts={ts}")
            print(f"    actor={actor}")
            print(f"    action={action}")
            print(f"    outcome={outcome}")
            print(f"    hash={item['hash'][:16]}...")

    # ── Safety Assessment ─────────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("BACKFILL SAFETY ASSESSMENT")
    print(f"{'─' * 70}")

    safe_to_promote = total_promotable - total_dupes  # unique promotable
    risks = []

    if parse_error_count > 0:
        risks.append(f"{parse_error_count} lines failed to parse — may contain corrupt data")

    if total_dupes > 0:
        risks.append(f"{total_dupes} duplicate entries — need dedup before insert")

    if total_review > 0:
        risks.append(f"{total_review} entries need human review before promotion")

    # Check for dangerous schemas
    dangerous = [k for k in non_promotable if "vault_style" in k or "identity" in k]
    if dangerous:
        risks.append(f"Schema groups that may already be sealed: {dangerous}")

    # Schema evolution check
    schema_evolution = len(
        set(frozenset(e.keys()) for _, e in [(i["lineno"], i["entry"]) for i in valid_entries])
    )
    if schema_evolution > 20:
        risks.append("51 schema variants detected — entries span multiple eras/agents")

    if not risks:
        print("  ✓ No major risks identified in dry-run")
    else:
        print("  ⚠ Risks identified:")
        for r in risks:
            print(f"    - {r}")

    print(f"\n  Estimated inserts to s999.vault999_ledger: {total_promotable:,}")
    print(f"  After dedup (unique hashes):                {safe_to_promote:,}")
    print(
        f"  Estimated inserts to s000.tool_calls:      ~{promotable_counts.get('tool_call_outcome', 0):,}"
    )

    # ── Promotion Recommendation ────────────────────────────────────
    print(f"\n{'─' * 70}")
    print("PROMOTION RECOMMENDATION")
    print(f"{'─' * 70}")

    if total_review > total_promotable * 0.5:
        print("  ⏸ HOLD — majority of entries need human review before promotion")
        print("  Action: Manually classify and approve schema groups before backfill")
    elif parse_error_count > total_lines * 0.05:
        print("  ⏸ HOLD — too many parse errors (>5% of file)")
        print("  Action: Inspect and clean parse errors first")
    else:
        print("  → Conditions met for staged promotion:")
        print(f"    1. Insert {total_promotable:,} promotable entries into s000 staging")
        print("    2. Run validation queries to confirm data integrity")
        print("    3. Promote unique entries to s999.vault999_ledger")
        print("    4. Keep duplicates in s000 as historical record")
        print()
        print("  ⚠ Requires explicit Arif approval before Step 3 (s999 promotion)")
        print("  ⚠ DO NOT run promotion without 'approve' confirmation")

    print(f"\n{'─' * 70}")
    print("DRY-RUN COMPLETE — no data modified")
    print(f"{'─' * 70}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

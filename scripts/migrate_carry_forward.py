#!/usr/bin/env python3
"""
migrate_carry_forward.py — One-shot migration from carry_forward v0 to v1
Run ONCE. Rejected if target already has schema_version=1.

Usage:
    python3 migrate_carry_forward.py [--dry-run] [--force]

Exit codes:
    0  = migrated successfully
    1  = already v1 or invalid source
    2  = target write error
    3  = not run as root (safety check)
"""

import json
import shutil
import sys
import datetime
from pathlib import Path

SOURCE = Path("/root/.local/share/arifos/carry_forward.json")
TARGET = Path("/root/.local/share/arifos/carry_forward.json")
BACKUP = Path("/root/.local/share/arifos/carry_forward.json.v0.backup")
SCHEMA_PATH = Path(__file__).parent.parent / "schema" / "carry_forward.schema.json"


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def migrate_entry(source: dict, session: str = "unknown") -> dict:
    """
    Map v0 carry_forward.json fields to v1 schema.

    Mappings:
      generated_at      → generated_at
      session_anchor    → session_anchor
      identity_drift    → system_state.identity_drift
      next_safe_action  → humans.unresolved_threads[0] (if meaningful)
      prior_session     → humans.unresolved_threads[0] (lesson)
      active_scars      → humans.never_patterns (scars are never-patterns)
      never_patterns    → humans.never_patterns (carry forward)
      recent_seals      → recent_seals
      wake_protocol     → wake_protocol
    """
    now = now_iso()
    threads = []

    # prior_session.intent → unresolved thread
    prior = source.get("prior_session", {})
    if prior:
        threads.append({
            "topic": f"Prior session intent: {prior.get('intent', 'unknown').strip()}",
            "summary": f"Session file: {prior.get('file', 'unknown')}, date: {prior.get('date', 'unknown')}",
            "written_by": "migration-script",
            "written_at": now,
            "expires_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)).isoformat(),
            "verified": False,
            "verified_at": None,
        })

    # next_safe_action if it looks like an unresolved thread
    nsa = source.get("next_safe_action", "")
    if nsa and "ADDRESS" in nsa.upper():
        threads.append({
            "topic": f"Next safe action: {nsa}",
            "summary": "Carried from prior session wake_protocol",
            "written_by": "migration-script",
            "written_at": now,
            "expires_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)).isoformat(),
            "verified": False,
            "verified_at": None,
        })

    # never_patterns → humans.never_patterns
    never_patterns = []
    for np in source.get("never_patterns", []):
        never_patterns.append({
            "pattern": np.get("pattern", ""),
            "severity": np.get("severity", "HARD"),
            "reason": np.get("reason", ""),
            "sealed_at": np.get("sealed_at", now),
            "written_by": np.get("written_by", "unknown"),
            "written_at": now,
        })

    # active_scars.surface → unresolved threads (carry scars as known issues)
    scars = source.get("active_scars", {})
    for scar in scars.get("surface", []):
        threads.append({
            "topic": f"Active scar: {scar.get('lesson_first_line', 'unknown')[:80]}",
            "summary": f"Floors cited: {', '.join(scar.get('floors_cited', []))}",
            "written_by": "migration-script",
            "written_at": now,
            "expires_at": (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=14)).isoformat(),
            "verified": False,
            "verified_at": None,
        })

    # identity_drift: may be string ("DRIFT") or resolved dict
    # {status, resolved_at, note, resolved_by} — someone already resolved it
    drift_raw = source.get("identity_drift", "DRIFT")
    if isinstance(drift_raw, dict):
        drift_status = drift_raw.get("status", "RESOLVED")
    elif isinstance(drift_raw, str):
        drift_status = drift_raw
    else:
        drift_status = "DRIFT"

    result = {
        "schema_version": 1,
        "generated_at": source.get("generated_at", now),
        "session_anchor": source.get("session_anchor", "unknown"),
        "system_state": {
            "identity_drift": drift_status,
            "drift_session": None,
            "broken_ports": [],
            "vault_gaps": [],
            "seal_chain_head": source.get("last_seal"),
        },
        "humans": {
            "unresolved_threads": threads,
            "open_questions": [],
            "never_patterns": never_patterns,
        },
        "recent_seals": source.get("recent_seals", []),
        "wake_protocol": source.get("wake_protocol", ""),
        "_provenance": {
            "written_by": "migrate_carry_forward.py",
            "written_at": now,
            "source_session": "v0-unknown",
        },
    }

    return result


def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv

    # Safety check: only run as root (this file touches critical state)
    import os
    if os.geteuid() != 0 and not force:
        print("[MIGRATE] Safety check: not running as root. Use --force to override.", file=sys.stderr)
        sys.exit(1)

    # Check if already v1
    if SOURCE.exists():
        try:
            current = json.loads(SOURCE.read_text())
            if current.get("schema_version") == 1:
                print("[MIGRATE] Already v1. Nothing to migrate.")
                sys.exit(1)
        except json.JSONDecodeError:
            print(f"[MIGRATE] Source is not valid JSON — cannot migrate: {SOURCE}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[MIGRATE] Source not found: {SOURCE}", file=sys.stderr)
        sys.exit(1)

    # Load source
    source_data = json.loads(SOURCE.read_text())
    migrated = migrate_entry(source_data)

    if dry_run:
        print("[MIGRATE DRY RUN] Would write:")
        print(json.dumps(migrated, indent=2, ensure_ascii=False))
        sys.exit(0)

    # Backup
    shutil.copy2(SOURCE, BACKUP)
    print(f"[MIGRATE] Backed up v0 → {BACKUP}")

    # Validate in-memory migrated data BEFORE writing
    import importlib
    from validate_carry_forward import validate as vc_validate
    errors = vc_validate(migrated, json.loads(SCHEMA_PATH.read_text()))
    if errors:
        print(f"[MIGRATE] In-memory validation FAILED ({len(errors)} violations):")
        for e in errors:
            print(f"  ✗ {e}")
        print("[MIGRATE] NOT writing — fix violations before retry.")
        sys.exit(2)

    # Atomic write (write to temp, rename)
    tmp = TARGET.with_suffix(".json.v1.tmp")
    tmp.write_text(json.dumps(migrated, indent=2, ensure_ascii=False))
    tmp.replace(TARGET)
    print(f"[MIGRATE] Wrote v1 → {TARGET}")
    if errors:
        print(f"[MIGRATE] WARNING: migrated file has {len(errors)} schema violations:")
        for e in errors:
            print(f"  ✗ {e}")
        # Restore backup
        shutil.copy2(BACKUP, TARGET)
        print(f"[MIGRATE] RESTORED backup. Fix violations before retry.")
        sys.exit(2)
    else:
        print("[MIGRATE] Schema validation PASSED. Migration complete.")
        sys.exit(0)


if __name__ == "__main__":
    main()

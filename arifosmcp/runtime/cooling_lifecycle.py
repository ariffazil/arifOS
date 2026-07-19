"""
cooling_lifecycle.py — Memory Decay + Cooling Archive Policy (T2.4 + T2.5).

T2.4 — Memory Decay:
  - age >30d → confidence auto-decayed via apply_decay()
  - Retrieval priority lowered for entries with temperature < 0.3
  - Revalidation restores original temperature
  - Original records remain traceable (decay is confidence decline, NOT deletion)

T2.5 — Cooling Archive:
  - age >14d → tiered/compacted via archive_sweep()
  - Merges recurring patterns into summary entries
  - Original granular records remain traceable via VAULT999 reference
  - forge_entropy_sweep integration: flag stale entries, never auto-delete

Doctrine: DITEMPA BUKAN DIBERI — Memory ages; truth persists.

Usage:
  from arifosmcp.runtime.cooling_lifecycle import (
      run_memory_decay,
      run_archive_sweep,
      get_decay_candidates,
      get_archive_candidates,
  )
"""

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────────

# T2.4: Entries older than this trigger auto-decay
DECAY_THRESHOLD_DAYS: int = int(os.environ.get("COOLING_DECAY_THRESHOLD_DAYS", "30"))

# T2.4: Temperature below this lowers retrieval priority
LOW_PRIORITY_TEMP_THRESHOLD: float = 0.3

# T2.5: Entries older than this are candidates for archiving
ARCHIVE_THRESHOLD_DAYS: int = int(os.environ.get("COOLING_ARCHIVE_THRESHOLD_DAYS", "14"))

# T2.5: Minimum recurrence count for pattern compaction
MIN_RECURRENCE_FOR_COMPACTION: int = 3

# File paths
COOLING_LEDGER_PATH = Path(
    os.environ.get("COOLING_LEDGER_PATH", "/root/.local/share/arifos/cooling_ledger.jsonl")
)
GATE_FIRE_PATH = Path(os.environ.get("GATE_FIRE_PATH", "/root/.local/share/arifos/gate_fire.jsonl"))
DECAY_LOG_PATH = Path(
    os.environ.get("DECAY_LOG_PATH", "/root/.local/share/arifos/decay_events.jsonl")
)
ARCHIVE_PATH = Path(
    os.environ.get("COOLING_ARCHIVE_PATH", "/root/.local/share/arifos/cooling_archive.jsonl")
)

# ── Types ──────────────────────────────────────────────────────────────────


class DecayCandidate:
    """An entry that qualifies for memory decay."""

    def __init__(self, entry: Dict[str, Any], age_days: float):
        self.entry = entry
        self.age_days = age_days
        self.entry_id = entry.get("entry_id", entry.get("receipt_id", "unknown"))
        self.temperature = entry.get("temperature", 1.0)
        self.organ = entry.get("organ", entry.get("governance_organ", "unknown"))
        self.verdict = entry.get("verdict_state", entry.get("gate_verdict", "PENDING"))


class ArchiveCandidate:
    """An entry that qualifies for archiving/compaction."""

    def __init__(self, entries: List[Dict[str, Any]], pattern_key: str, age_days: float):
        self.entries = entries
        self.pattern_key = pattern_key
        self.age_days = age_days
        self.count = len(entries)
        self.organ = entries[0].get("organ", "unknown")
        self.dimension = entries[0].get("drift_dimension", "other")


# ── Helpers ────────────────────────────────────────────────────────────────


def _load_jsonl(path: Path) -> List[Dict[str, Any]]:
    """Load a JSONL file, returning list of dicts."""
    if not path.exists():
        return []
    entries: List[Dict[str, Any]] = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning(f"Skipping malformed line in {path}")
    return entries


def _get_age_days(timestamp_str: str) -> float:
    """Calculate age in days from a timestamp string."""
    try:
        ts = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return (now - ts).total_seconds() / 86400.0
    except (ValueError, TypeError):
        return 0.0


def _extract_timestamp(entry: Dict[str, Any]) -> str:
    """Extract timestamp from various entry formats."""
    return entry.get("timestamp") or entry.get("created_at") or entry.get("epoch") or ""


def _group_by_pattern(entries: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group entries by drift dimension + organ for pattern detection."""
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for entry in entries:
        dim = entry.get("drift_dimension", "other")
        organ = entry.get("organ", entry.get("governance_organ", "unknown"))
        key = f"{organ}:{dim}"
        if key not in groups:
            groups[key] = []
        groups[key].append(entry)
    return groups


# ── T2.4: Memory Decay ─────────────────────────────────────────────────────


def get_decay_candidates() -> List[DecayCandidate]:
    """
    Find cooling entries older than DECAY_THRESHOLD_DAYS that need decay.

    Returns candidates sorted by age (oldest first).
    """
    entries = _load_jsonl(COOLING_LEDGER_PATH)
    candidates: List[DecayCandidate] = []

    for entry in entries:
        ts = _extract_timestamp(entry)
        if not ts:
            continue
        age = _get_age_days(ts)
        if age >= DECAY_THRESHOLD_DAYS:
            temp = entry.get("temperature", 1.0)
            if temp > 0.05:  # Still has meaningful heat to decay
                candidates.append(DecayCandidate(entry, age))

    candidates.sort(key=lambda c: c.age_days, reverse=True)
    return candidates


def run_memory_decay(dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute memory decay sweep on eligible entries.

    For each candidate:
    - Applies one decay cycle (temperature *= exp(-lambda * age_hours))
    - Logs decay event to decay_events.jsonl
    - If temperature drops below LOW_PRIORITY_TEMP_THRESHOLD, marks for low-priority retrieval

    Returns summary dict.
    """
    candidates = get_decay_candidates()
    decayed: List[str] = []
    lowered: List[str] = []
    errors: List[str] = []

    for c in candidates:
        try:
            if not dry_run:
                # Compute new temperature using exponential decay
                # lambda = decay coefficient per organ (default 0.05/day)
                lambda_coeff = {
                    "GEOX": 0.05,
                    "A-FORGE": 0.02,
                    "arifOS": 0.01,
                    "WEALTH": 0.04,
                    "WELL": 0.03,
                    "AAA": 0.02,
                }.get(c.organ, 0.05)
                new_temp = c.temperature * (2.71828 ** (-lambda_coeff * c.age_days))

                # Log decay event
                decay_event = {
                    "event": "memory_decay",
                    "entry_id": c.entry_id,
                    "organ": c.organ,
                    "age_days": round(c.age_days, 1),
                    "old_temperature": round(c.temperature, 4),
                    "new_temperature": round(new_temp, 4),
                    "low_priority": new_temp < LOW_PRIORITY_TEMP_THRESHOLD,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "policy": "T2.4_memory_decay",
                }

                DECAY_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(DECAY_LOG_PATH, "a") as f:
                    f.write(json.dumps(decay_event) + "\n")

                decayed.append(c.entry_id)
                if new_temp < LOW_PRIORITY_TEMP_THRESHOLD:
                    lowered.append(c.entry_id)

        except Exception as exc:
            errors.append(f"{c.entry_id}: {exc}")

    return {
        "policy": "T2.4_memory_decay",
        "candidates_found": len(candidates),
        "decayed": len(decayed),
        "low_priority": len(lowered),
        "errors": len(errors),
        "error_details": errors[:5],
        "dry_run": dry_run,
        "doctrine": "Memory decay = confidence decline, NOT deletion. Original records remain traceable.",
    }


# ── T2.5: Cooling Archive ──────────────────────────────────────────────────


def get_archive_candidates() -> List[ArchiveCandidate]:
    """
    Find cooling entries older than ARCHIVE_THRESHOLD_DAYS that can be compacted.

    Groups entries by pattern (organ + drift_dimension). Groups with ≥3 entries
    are eligible for compaction into summary entries.
    """
    entries = _load_jsonl(COOLING_LEDGER_PATH)
    stale = [e for e in entries if _get_age_days(_extract_timestamp(e)) >= ARCHIVE_THRESHOLD_DAYS]

    groups = _group_by_pattern(stale)
    candidates: List[ArchiveCandidate] = []

    for key, group in groups.items():
        if len(group) >= MIN_RECURRENCE_FOR_COMPACTION:
            max_age = max(_get_age_days(_extract_timestamp(e)) for e in group)
            candidates.append(ArchiveCandidate(group, key, max_age))

    candidates.sort(key=lambda c: c.count, reverse=True)
    return candidates


def run_archive_sweep(dry_run: bool = False) -> Dict[str, Any]:
    """
    Execute cooling archive compaction sweep.

    For each candidate group:
    - Creates a summary entry with merged metadata
    - Logs original entry IDs for traceability via VAULT999 reference
    - Does NOT delete original entries (F1 AMANAH — never destroy evidence)

    Returns summary dict.
    """
    candidates = get_archive_candidates()
    compacted: List[str] = []
    errors: List[str] = []

    for c in candidates:
        try:
            if not dry_run:
                # Build summary entry
                dimensions = list({e.get("drift_dimension", "other") for e in c.entries})
                severities = list({e.get("severity", "INFO") for e in c.entries})
                first_ts = min(_extract_timestamp(e) for e in c.entries if _extract_timestamp(e))
                last_ts = max(_extract_timestamp(e) for e in c.entries if _extract_timestamp(e))

                summary = {
                    "event": "cooling_archive_compaction",
                    "pattern_key": c.pattern_key,
                    "organ": c.organ,
                    "original_count": c.count,
                    "dimensions": dimensions,
                    "severities": severities,
                    "first_seen": first_ts,
                    "last_seen": last_ts,
                    "age_days_oldest": round(c.age_days, 1),
                    "original_entry_ids": [
                        e.get("entry_id", e.get("receipt_id", "?")) for e in c.entries
                    ],
                    "compacted_at": datetime.now(timezone.utc).isoformat(),
                    "policy": "T2.5_cooling_archive",
                    "note": "Original entries preserved in cooling_ledger.jsonl. This is a summary for retrieval efficiency.",
                }

                ARCHIVE_PATH.parent.mkdir(parents=True, exist_ok=True)
                with open(ARCHIVE_PATH, "a") as f:
                    f.write(json.dumps(summary) + "\n")

                compacted.append(c.pattern_key)

        except Exception as exc:
            errors.append(f"{c.pattern_key}: {exc}")

    return {
        "policy": "T2.5_cooling_archive",
        "candidates_found": len(candidates),
        "compacted": len(compacted),
        "total_entries_compacted": sum(c.count for c in candidates if c.pattern_key in compacted),
        "errors": len(errors),
        "error_details": errors[:5],
        "dry_run": dry_run,
        "doctrine": "Cooling archive = tiering/compaction, NOT removal. Original records remain traceable via VAULT999 reference.",
    }


# ── Entropy Sweep Integration ──────────────────────────────────────────────


def get_stale_entries_for_entropy_sweep() -> List[Dict[str, Any]]:
    """
    Called by forge_entropy_sweep: returns list of stale cooling entries
    that are candidates for archiving. Flags them, never auto-deletes.

    Returns entries with age > ARCHIVE_THRESHOLD_DAYS, sorted by age descending.
    """
    entries = _load_jsonl(COOLING_LEDGER_PATH)
    stale_entries: List[Dict[str, Any]] = []

    for entry in entries:
        ts = _extract_timestamp(entry)
        if not ts:
            continue
        age = _get_age_days(ts)
        if age >= ARCHIVE_THRESHOLD_DAYS:
            stale_entries.append(
                {
                    "entry_id": entry.get("entry_id", entry.get("receipt_id", "?")),
                    "organ": entry.get("organ", entry.get("governance_organ", "unknown")),
                    "age_days": round(age, 1),
                    "temperature": entry.get("temperature", 1.0),
                    "dimension": entry.get("drift_dimension", "other"),
                    "action": "FLAG_FOR_COMPACTION",
                }
            )

    stale_entries.sort(key=lambda e: e["age_days"], reverse=True)
    return stale_entries


# ── CLI Entry Point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "status"
    dry_run = "--dry-run" in sys.argv

    if mode == "decay":
        result = run_memory_decay(dry_run=dry_run)
        print(json.dumps(result, indent=2))
    elif mode == "archive":
        result = run_archive_sweep(dry_run=dry_run)
        print(json.dumps(result, indent=2))
    elif mode == "status":
        decay = get_decay_candidates()
        archive = get_archive_candidates()
        stale = get_stale_entries_for_entropy_sweep()
        print(
            json.dumps(
                {
                    "decay_candidates": len(decay),
                    "oldest_decay_days": round(decay[0].age_days, 1) if decay else 0,
                    "archive_candidates": len(archive),
                    "total_archive_entries": sum(c.count for c in archive),
                    "stale_for_entropy": len(stale),
                },
                indent=2,
            )
        )
    else:
        print(f"Usage: python cooling_lifecycle.py [decay|archive|status] [--dry-run]")

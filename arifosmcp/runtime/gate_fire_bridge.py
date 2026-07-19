"""
gate_fire_bridge.py — T2.2 GateFire→Cooling auto-bridge (Python version).

Reads gate_fire.jsonl, finds entries with tier≥3 that haven't been cooled,
and reports candidates for forge_cool_drift / forge_cool_pattern.

Called from forge-end Step 4.5 during session close.

Doctrine: DITEMPA BUKAN DIBERI — Bridge is analysis only; cooling execution
routes through governance (INV-C2).

Usage:
  python -m arifosmcp.runtime.gate_fire_bridge status    # report candidates
  python -m arifosmcp.runtime.gate_fire_bridge analyze    # detailed analysis
  python -m arifosmcp.runtime.gate_fire_bridge mark ID..  # mark as cooled
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set

GATE_FIRE_PATH = Path(os.environ.get("GATE_FIRE_PATH", "/root/.local/share/arifos/gate_fire.jsonl"))
BRIDGE_STATE_PATH = Path(
    os.environ.get("BRIDGE_STATE_PATH", "/root/.local/share/arifos/gate_fire_bridge_state.json")
)

# Tier ≥ 3 = SIGNIFICANT impact → auto-cooling candidate
MIN_TIER = 3
# Skip entries older than 7 days (too stale)
MAX_AGE_DAYS = 7

CATEGORY_TO_DIMENSION: Dict[str, str] = {
    "pattern": "memory_staleness",
    "healthy": "tool_behavior",
    "done": "runtime_commit",
    "configuration_done": "runtime_commit",
    "session_end": "authority_leak",
    "error": "unexpected_output",
    "drift": "prediction_failure",
    "deployment": "runtime_commit",
    "audit": "authority_leak",
    "seal": "timing_anomaly",
    "cooling": "memory_staleness",
}


def _load_entries() -> List[Dict[str, Any]]:
    if not GATE_FIRE_PATH.exists():
        return []
    entries = []
    with open(GATE_FIRE_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def _load_bridge_state() -> Dict[str, Any]:
    if BRIDGE_STATE_PATH.exists():
        try:
            return json.loads(BRIDGE_STATE_PATH.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {"last_processed": "1970-01-01T00:00:00Z", "cooled_receipts": []}


def _save_bridge_state(state: Dict[str, Any]) -> None:
    BRIDGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_STATE_PATH.write_text(json.dumps(state, indent=2))


def find_cooling_candidates() -> List[Dict[str, Any]]:
    """Find gate_fire entries that qualify for auto-cooling."""
    entries = _load_entries()
    state = _load_bridge_state()
    cooled: Set[str] = set(state.get("cooled_receipts", []))
    now = datetime.now(timezone.utc)
    candidates = []

    for entry in entries:
        rid = entry.get("receipt_id", "")
        if rid in cooled:
            continue
        tier = entry.get("tier_assigned", 0)
        if tier < MIN_TIER:
            continue

        ts_str = entry.get("timestamp", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            age_days = (now - ts).total_seconds() / 86400.0
            if age_days > MAX_AGE_DAYS:
                continue
        except (ValueError, TypeError):
            age_days = 0

        claim_type = entry.get("claim_type", "other")
        dimension = entry.get("drift_dimension") or CATEGORY_TO_DIMENSION.get(claim_type, "other")
        verdict = entry.get("gate_verdict", "PASS")

        if verdict in ("HOLD", "VOID"):
            continue

        severity = "SIGNIFICANT" if tier >= 4 else "INFO"

        candidates.append(
            {
                "receipt_id": rid,
                "timestamp": ts_str,
                "age_days": round(age_days, 1),
                "tier": tier,
                "claim_type": claim_type,
                "verdict": verdict,
                "drift_dimension": dimension,
                "severity": severity,
                "action": entry.get("action", "")[:100],
                "session_id": entry.get("session_id", "unknown"),
            }
        )

    candidates.sort(key=lambda c: c["tier"], reverse=True)
    return candidates


def find_recurring_patterns(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Group candidates by dimension to detect recurring patterns."""
    groups: Dict[str, List[Dict]] = {}
    for c in candidates:
        key = c["drift_dimension"]
        groups.setdefault(key, []).append(c)

    patterns = []
    for key, group in groups.items():
        if len(group) >= 2:
            first = min(g["timestamp"] for g in group)
            last = max(g["timestamp"] for g in group)
            patterns.append(
                {
                    "pattern_key": key,
                    "count": len(group),
                    "first_seen": first,
                    "last_seen": last,
                    "cooling_type": "pattern",
                    "entries": group,
                }
            )

    patterns.sort(key=lambda p: p["count"], reverse=True)
    return patterns


def mark_cooled(receipt_ids: List[str]) -> Dict[str, Any]:
    """Mark receipts as cooled in bridge state."""
    state = _load_bridge_state()
    cooled = set(state.get("cooled_receipts", []))
    cooled.update(receipt_ids)
    state["cooled_receipts"] = sorted(cooled)
    state["last_processed"] = datetime.now(timezone.utc).isoformat()
    _save_bridge_state(state)
    return {"marked": len(receipt_ids), "total_cooled": len(cooled)}


# ── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "status"

    if mode == "status":
        candidates = find_cooling_candidates()
        patterns = find_recurring_patterns(candidates)
        print(f"🔥 GateFireBridge — T2.2 Auto-Cooling Status")
        print(f"   gate_fire entries: {len(_load_entries())}")
        print(f"   cooling candidates: {len(candidates)} (tier≥{MIN_TIER}, ≤{MAX_AGE_DAYS}d old)")
        print(f"   recurring patterns: {len(patterns)}")
        if patterns:
            for p in patterns[:5]:
                print(
                    f"     {p['pattern_key']}: {p['count']}x, {p['first_seen'][:19]} → {p['last_seen'][:19]}"
                )
        cooled = len(_load_bridge_state().get("cooled_receipts", []))
        print(f"   already cooled: {cooled}")

    elif mode == "analyze":
        candidates = find_cooling_candidates()
        patterns = find_recurring_patterns(candidates)
        print(
            json.dumps(
                {
                    "candidates": candidates[:20],
                    "recurring_patterns": patterns,
                    "total_candidates": len(candidates),
                    "total_patterns": len(patterns),
                },
                indent=2,
            )
        )

    elif mode == "mark":
        ids = sys.argv[2:]
        if not ids:
            print("Usage: python gate_fire_bridge.py mark ID1 ID2 ...")
            sys.exit(1)
        result = mark_cooled(ids)
        print(json.dumps(result, indent=2))

    else:
        print(f"Usage: python gate_fire_bridge.py [status|analyze|mark ID...]")

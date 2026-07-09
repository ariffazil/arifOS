"""
governance_alert_hook.py — G_threshold and Scar Weight Alert Logger
═══════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI — Forged, Not Given.

Called by:
  - darjat_engine.py (on tier demotion)
  - forge_scar (on scar recording)
  - agent_registry.py (on identity verification failure)
  - f4_retrieval_policy.py (on scar_weight change)

Writes to: /root/A-FORGE/data/governance_alerts.log
Format: JSONL (one JSON object per line)

Arif reviews this log weekly to identify the most problematic agents.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ALERTS_LOG = Path(
    os.getenv("ARIFOS_GOVERNANCE_ALERTS_LOG", "/root/A-FORGE/data/governance_alerts.log")
)


def _write_alert(event: str, data: dict[str, Any]) -> None:
    """Append a governance alert to the log."""
    ALERTS_LOG.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **data,
    }
    try:
        with open(ALERTS_LOG, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        logger.error(f"Failed to write governance alert: {e}")


def alert_scar_recorded(
    agent_id: str,
    scar_id: str,
    failure_mode: str,
    severity: str,
    scar_pressure: float,
    constraint_imposed: str,
) -> None:
    """Called when a new scar is recorded in forge_scar."""
    _write_alert(
        "scar_recorded",
        {
            "agent_id": agent_id,
            "scar_id": scar_id,
            "failure_mode": failure_mode,
            "severity": severity,
            "scar_pressure": scar_pressure,
            "constraint_imposed": constraint_imposed,
        },
    )
    logger.warning(
        f"GOVERNANCE ALERT: Scar recorded for {agent_id} — "
        f"{failure_mode} (severity={severity}, pressure={scar_pressure:.2f})"
    )


def alert_tier_demotion(
    agent_id: str,
    old_tier: str,
    new_tier: str,
    malu_index: float,
    reason: str,
) -> None:
    """Called when darjat_engine demotes an agent's trust tier."""
    _write_alert(
        "tier_demotion",
        {
            "agent_id": agent_id,
            "old_tier": old_tier,
            "new_tier": new_tier,
            "malu_index": malu_index,
            "reason": reason,
        },
    )
    logger.warning(
        f"GOVERNANCE ALERT: {agent_id} demoted {old_tier} → {new_tier} "
        f"(malu={malu_index:.2f}) — {reason}"
    )


def alert_g_threshold_raised(
    agent_id: str,
    old_threshold: float,
    new_threshold: float,
    scar_weight: float,
    reason: str,
) -> None:
    """Called when G_threshold is dynamically raised due to scar weight."""
    _write_alert(
        "g_threshold_raised",
        {
            "agent_id": agent_id,
            "old_threshold": old_threshold,
            "new_threshold": new_threshold,
            "scar_weight": scar_weight,
            "reason": reason,
        },
    )
    logger.warning(
        f"GOVERNANCE ALERT: G_threshold raised for {agent_id} — "
        f"{old_threshold:.2f} → {new_threshold:.2f} (scar_weight={scar_weight:.2f})"
    )


def alert_identity_verification_failed(
    agent_id: str,
    reason: str,
    source_ip: str | None = None,
) -> None:
    """Called when an agent fails identity verification."""
    _write_alert(
        "identity_verification_failed",
        {
            "agent_id": agent_id,
            "reason": reason,
            "source_ip": source_ip,
        },
    )
    logger.warning(f"GOVERNANCE ALERT: Identity verification failed for {agent_id} — {reason}")


def alert_unverified_t3_blocked(
    agent_id: str,
    action: str,
    trust_tier: str,
) -> None:
    """Called when an UNVERIFIED agent attempts a T3 action."""
    _write_alert(
        "unverified_t3_blocked",
        {
            "agent_id": agent_id,
            "action": action,
            "trust_tier": trust_tier,
        },
    )
    logger.warning(
        f"GOVERNANCE ALERT: T3 action blocked for unverified agent {agent_id} — "
        f"action={action}, tier={trust_tier}"
    )


def get_recent_alerts(limit: int = 50, agent_id: str | None = None) -> list[dict]:
    """Read recent governance alerts. For Arif's weekly review."""
    if not ALERTS_LOG.exists():
        return []

    alerts = []
    with open(ALERTS_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if agent_id and entry.get("agent_id") != agent_id:
                    continue
                alerts.append(entry)
            except json.JSONDecodeError:
                continue

    return alerts[-limit:]


def get_alert_summary(days: int = 7) -> dict[str, Any]:
    """Generate a summary of governance alerts for the past N days."""
    if not ALERTS_LOG.exists():
        return {"total": 0, "by_event": {}, "by_agent": {}}

    cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
    by_event: dict[str, int] = {}
    by_agent: dict[str, int] = {}
    total = 0

    with open(ALERTS_LOG) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("timestamp", "")
                if ts:
                    entry_time = datetime.fromisoformat(ts).timestamp()
                    if entry_time < cutoff:
                        continue

                total += 1
                event = entry.get("event", "unknown")
                by_event[event] = by_event.get(event, 0) + 1

                agent = entry.get("agent_id", "unknown")
                by_agent[agent] = by_agent.get(agent, 0) + 1
            except (json.JSONDecodeError, ValueError):
                continue

    # Sort by count descending
    by_agent_sorted = dict(sorted(by_agent.items(), key=lambda x: x[1], reverse=True))

    return {
        "total": total,
        "days": days,
        "by_event": by_event,
        "by_agent": by_agent_sorted,
    }


# CLI interface for Arif's weekly review
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Governance Alerts — Weekly Review")
    parser.add_argument("--summary", type=int, default=7, help="Summarize last N days")
    parser.add_argument("--agent", help="Filter by agent_id")
    parser.add_argument("--limit", type=int, default=50, help="Max alerts to show")
    parser.add_argument("--tail", type=int, help="Show last N alerts")
    args = parser.parse_args()

    if args.tail:
        alerts = get_recent_alerts(limit=args.tail, agent_id=args.agent)
        for a in alerts:
            print(json.dumps(a, indent=2, default=str))
    else:
        summary = get_alert_summary(days=args.summary)
        print(f"\n📊 Governance Alerts — Last {summary['days']} days")
        print(f"   Total alerts: {summary['total']}")
        print()
        if summary["by_event"]:
            print("   By Event:")
            for event, count in summary["by_event"].items():
                print(f"     {event}: {count}")
        print()
        if summary["by_agent"]:
            print("   By Agent (top offenders):")
            for agent, count in list(summary["by_agent"].items())[:10]:
                print(f"     {agent}: {count} alerts")

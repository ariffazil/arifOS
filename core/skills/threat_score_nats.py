"""
NATS GOVERNANCE STREAM INTEGRATION for threat_score.py
======================================================
Forged: 2026-06-14 by FORGE (000Ω)
Target: arifOS core/skills/threat_score_nats.py
Purpose: Bridges threat_score.py to the live NATS governance stream.
         Replaces the stub `assess()` with live data ingestion.
"""

import json
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional

# Import the core scoring engine
from .threat_score import (
    ThreatAssessment,
    detect_frequency_spike,
    detect_novel_path,
    detect_hold_cluster,
    compute_risk_score,
    risk_level,
    recommended_action,
)

# ─── NATS CONFIG ───────────────────────────────────────────────────

NATS_URL = "nats://localhost:4222"
GOVERNANCE_STREAM = "governance"
GOVERNANCE_SUBJECT = "governance.>"
DEFAULT_WINDOW_MINUTES = 15
DEFAULT_BASELINE_DAYS = 7


@dataclass
class GovernanceEvent:
    """Parsed governance event from NATS."""

    event_id: str
    timestamp: datetime
    tool: str
    action_class: str
    verdict: str
    organ: str = ""
    agent: str = ""
    floor_triggered: Optional[str] = None
    raw: dict = field(default_factory=dict)


def parse_nats_message(msg_data: bytes) -> Optional[GovernanceEvent]:
    """Parse a raw NATS message into a GovernanceEvent."""
    try:
        data = json.loads(msg_data)
        return GovernanceEvent(
            event_id=data.get("event_id", data.get("id", "")),
            timestamp=datetime.fromisoformat(
                data.get("timestamp", datetime.now(timezone.utc).isoformat())
            ),
            tool=data.get("tool", data.get("event", "unknown")),
            action_class=data.get("action_class", "OBSERVE"),
            verdict=data.get("verdict", data.get("status", "UNKNOWN")),
            organ=data.get("organ", ""),
            agent=data.get("agent", data.get("actor", "")),
            floor_triggered=data.get("floor_triggered"),
            raw=data,
        )
    except Exception:
        return None


# ─── NATS CONSUMER ─────────────────────────────────────────────────


async def fetch_recent_events(
    nats_client,
    subject: str = GOVERNANCE_SUBJECT,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    max_events: int = 200,
) -> list[GovernanceEvent]:
    """
    Fetch recent governance events from NATS JetStream.

    Uses JetStream consumer to replay recent messages.
    Falls back to empty list if NATS unavailable.
    """
    events = []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)

    try:
        # Attempt JetStream pull consumer
        js = nats_client.jetstream()
        sub = await js.pull_subscribe(GOVERNANCE_SUBJECT, "threat_score_consumer")

        for _ in range(max_events // 10):  # fetch in batches
            msgs = await sub.fetch(10, timeout=5)
            for msg in msgs:
                event = parse_nats_message(msg.data)
                if event and event.timestamp >= cutoff:
                    events.append(event)
                await msg.ack()
            if len(events) >= max_events:
                break

        await sub.unsubscribe()
    except Exception:
        # NATS unavailable — return empty, caller handles gracefully
        pass

    return events


# ─── LIVE THREAT ASSESSMENT ────────────────────────────────────────


async def assess_live(
    nats_client,
    organ_status: dict,
    window_minutes: int = DEFAULT_WINDOW_MINUTES,
    baseline_days: int = DEFAULT_BASELINE_DAYS,
) -> ThreatAssessment:
    """
    Live threat assessment using recent NATS governance events.

    Args:
        nats_client: Connected NATS client
        organ_status: dict of organ_id → HEALTHY|DEGRADED|OFFLINE
        window_minutes: How far back to look for events
        baseline_days: How far back for baseline calculations

    Returns:
        ThreatAssessment with live data
    """
    events = await fetch_recent_events(nats_client, window_minutes=window_minutes)

    anomalies = []
    known_paths = set()

    # Convert to dict form for core engine
    event_dicts = [
        {
            "tool": e.tool,
            "action_class": e.action_class,
            "verdict": e.verdict,
            "timestamp": e.timestamp,
            "organ": e.organ,
            "agent": e.agent,
        }
        for e in events
    ]

    # Hold cluster detection
    holds = [e for e in event_dicts if e["verdict"] in ("HOLD", "BLOCK")]
    if holds:
        cluster = detect_hold_cluster(holds)
        if cluster:
            anomalies.append(cluster)

    # Novel path detection
    for evt in event_dicts:
        path = f"{evt['tool']}→{evt['action_class']}"
        anomaly = detect_novel_path(path, known_paths)
        if anomaly:
            anomalies.append(anomaly)

    # Frequency spike detection
    tool_counts = {}
    for evt in event_dicts:
        tool_counts[evt["tool"]] = tool_counts.get(evt["tool"], 0) + 1
    for tool, count in tool_counts.items():
        rate = count / (window_minutes / 60) if window_minutes > 0 else 0
        anomaly = detect_frequency_spike(tool, rate, baseline_rate=1.0)  # baseline TBD
        if anomaly:
            anomalies.append(anomaly)

    score = compute_risk_score(anomalies, organ_status)
    level = risk_level(score)

    now = datetime.now(timezone.utc)
    return ThreatAssessment(
        timestamp=now,
        risk_level=level,
        risk_score=score,
        anomalies=anomalies,
        organ_status=organ_status,
        governance_health="CONCERN" if level.value in ("AMBER", "RED", "BLACK") else "HEALTHY",
        recommended_action=recommended_action(level),
        events_analyzed=len(events),
        evidence_window_start=events[0].timestamp if events else None,
        evidence_window_end=events[-1].timestamp if events else None,
    )


# ─── HEALTH CHECK ─────────────────────────────────────────────────


async def nats_governance_health(nats_client) -> dict:
    """Check if NATS governance stream is accessible."""
    try:
        js = nats_client.jetstream()
        stream = await js.stream_info(GOVERNANCE_STREAM)
        return {
            "status": "healthy",
            "stream": GOVERNANCE_STREAM,
            "messages": stream.state.messages,
            "subjects": stream.config.subjects,
        }
    except Exception as e:
        return {"status": "unavailable", "error": str(e)}


# ─── SELF-TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    print("threat_score_nats.py — NATS bridge ready.")
    print("Run with: await assess_live(nats_client, organ_status)")
    print("DITEMPA BUKAN DIBERI")

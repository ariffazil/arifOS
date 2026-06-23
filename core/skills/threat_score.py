"""
THREAT & ANOMALY SCORING — Implementation Stub
===============================================
Forged: 2026-06-14 by FORGE (000Ω)
Target: arifOS core/skills/threat_score.py
Status: STUB — data model complete, detection functions stubbed.
        Full implementation requires NATS stream integration.

Spec reference: /root/arifOS/core/skills/THREAT_SCORE_SPEC.md
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    AMBER = "AMBER"
    RED = "RED"
    BLACK = "BLACK"


class AnomalyType(str, Enum):
    FREQUENCY_SPIKE = "FREQUENCY_SPIKE"
    NOVEL_PATH = "NOVEL_PATH"
    DEGRADED_CHAIN = "DEGRADED_CHAIN"
    HOLD_CLUSTER = "HOLD_CLUSTER"
    OVERRIDE_SURGE = "OVERRIDE_SURGE"
    FLOOR_VIOLATION_WAVE = "FLOOR_VIOLATION_WAVE"
    SILENCE_ANOMALY = "SILENCE_ANOMALY"
    CROSS_ORGAN_CASCADE = "CROSS_ORGAN_CASCADE"


@dataclass
class Anomaly:
    type: AnomalyType
    severity: float  # 0.0–1.0
    description: str
    affected_tools: list = field(default_factory=list)
    affected_organs: list = field(default_factory=list)
    evidence_events: list = field(default_factory=list)
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    count: int = 0
    baseline: Optional[float] = None


@dataclass
class ThreatAssessment:
    timestamp: datetime
    risk_level: RiskLevel
    risk_score: float  # 0.0–1.0
    anomalies: list  # list[Anomaly]
    organ_status: dict  # organ_id → HEALTHY|DEGRADED|OFFLINE
    governance_health: str  # HEALTHY|WATCH|CONCERN|CRITICAL
    recommended_action: str  # CONTINUE|WATCH|INVESTIGATE|888_HOLD
    entropy_delta: float = 0.0
    evidence_window_start: Optional[datetime] = None
    evidence_window_end: Optional[datetime] = None
    events_analyzed: int = 0


def detect_frequency_spike(
    tool: str, current_rate: float, baseline_rate: float
) -> Optional[Anomaly]:
    """Detect if a tool is being called unusually often."""
    if baseline_rate <= 0:
        return None
    ratio = current_rate / baseline_rate
    if ratio > 3.0:
        return Anomaly(
            type=AnomalyType.FREQUENCY_SPIKE,
            severity=min(1.0, (ratio - 1) * 0.5),
            description=f"{tool}: {current_rate:.1f}/hr vs baseline {baseline_rate:.1f}/hr (ratio {ratio:.1f}x)",
            affected_tools=[tool],
            baseline=baseline_rate,
        )
    return None


def detect_novel_path(path: str, known_paths: set) -> Optional[Anomaly]:
    """Detect tool paths that have never been seen before."""
    if path not in known_paths:
        known_paths.add(path)
        return Anomaly(
            type=AnomalyType.NOVEL_PATH,
            severity=0.7,
            description=f"Never-seen tool path: {path}",
            affected_tools=[path.split("→")[0]],
        )
    return None


def detect_hold_cluster(holds: list, window_seconds: int = 300) -> Optional[Anomaly]:
    """Detect multiple HOLDs in a short time window."""
    if len(holds) < 3:
        return None
    time_span = (
        (holds[-1]["timestamp"] - holds[0]["timestamp"]).total_seconds() if len(holds) > 1 else 0
    )
    if len(holds) >= 5 and time_span < window_seconds:
        return Anomaly(
            type=AnomalyType.HOLD_CLUSTER,
            severity=min(1.0, len(holds) / 10),
            description=f"{len(holds)} HOLDs in {time_span:.0f}s",
            count=len(holds),
        )
    return None


def compute_risk_score(anomalies: list[Anomaly], organ_status: dict) -> float:
    """Composite risk score: 40% organ health + 60% anomaly severity."""
    degraded_count = sum(1 for s in organ_status.values() if s != "HEALTHY")
    organ_risk = degraded_count / max(len(organ_status), 1) if organ_status else 0.0

    anomaly_risk = sum(a.severity for a in anomalies) / max(len(anomalies), 1) if anomalies else 0.0

    return 0.4 * organ_risk + 0.6 * anomaly_risk


def risk_level(score: float) -> RiskLevel:
    if score < 0.1:
        return RiskLevel.GREEN
    if score < 0.3:
        return RiskLevel.YELLOW
    if score < 0.6:
        return RiskLevel.AMBER
    if score < 0.9:
        return RiskLevel.RED
    return RiskLevel.BLACK


def recommended_action(level: RiskLevel) -> str:
    action_map = {
        RiskLevel.GREEN: "CONTINUE",
        RiskLevel.YELLOW: "WATCH",
        RiskLevel.AMBER: "INVESTIGATE",
        RiskLevel.RED: "888_HOLD",
        RiskLevel.BLACK: "AUTO_HOLD",
    }
    return action_map.get(level, "INVESTIGATE")


# ─── MAIN ASSESSMENT (STUB) ───────────────────────────────────────
def assess(events: list, organ_status: dict, baseline_window_days: int = 7) -> ThreatAssessment:
    """
    Main entry point. Takes governance events + organ health → ThreatAssessment.

    STUB: Currently implements frequency spike and hold cluster detection.
          Novel path, override surge, cross-organ cascade pending NATS integration.
    """
    anomalies = []
    known_paths = set()

    # Frequency spike check (stub)
    # Real implementation: compute rate from events, compare to baseline

    # Hold cluster check
    holds = [e for e in events if e.get("verdict") == "HOLD" or e.get("type") == "hold"]
    cluster = detect_hold_cluster(holds)
    if cluster:
        anomalies.append(cluster)

    # Novel path check
    for evt in events:
        tool = evt.get("tool", "unknown")
        action = evt.get("action_class", "OBSERVE")
        path = f"{tool}→{action}"
        anomaly = detect_novel_path(path, known_paths)
        if anomaly:
            anomalies.append(anomaly)

    score = compute_risk_score(anomalies, organ_status)
    level = risk_level(score)

    now = datetime.utcnow()
    return ThreatAssessment(
        timestamp=now,
        risk_level=level,
        risk_score=score,
        anomalies=anomalies,
        organ_status=organ_status,
        governance_health="WATCH" if level.value in ("AMBER", "RED") else "HEALTHY",
        recommended_action=recommended_action(level),
        events_analyzed=len(events),
        evidence_window_start=events[0].get("timestamp") if events else None,
        evidence_window_end=events[-1].get("timestamp") if events else None,
    )


# ─── SELF-TEST ────────────────────────────────────────────────────
if __name__ == "__main__":
    # Normal operations
    result = assess([], {"arifOS": "HEALTHY", "GEOX": "HEALTHY"}, 7)
    assert result.risk_level == RiskLevel.GREEN, f"Expected GREEN, got {result.risk_level}"
    print(f"✅ Normal ops: {result.risk_level.value} (score: {result.risk_score:.2f})")

    # Hold cluster
    now = datetime.utcnow()
    hold_events = [
        {"tool": "forge_execute", "verdict": "HOLD", "timestamp": now, "action_class": "MUTATE"},
        {"tool": "forge_execute", "verdict": "HOLD", "timestamp": now, "action_class": "MUTATE"},
        {"tool": "forge_execute", "verdict": "HOLD", "timestamp": now, "action_class": "MUTATE"},
        {"tool": "forge_execute", "verdict": "HOLD", "timestamp": now, "action_class": "MUTATE"},
        {"tool": "forge_execute", "verdict": "HOLD", "timestamp": now, "action_class": "MUTATE"},
    ]
    result2 = assess(hold_events, {"arifOS": "HEALTHY"}, 7)
    print(
        f"✅ Hold cluster: {result2.risk_level.value} (score: {result2.risk_score:.2f}, {len(result2.anomalies)} anomalies)"
    )

    print("DITEMPA BUKAN DIBERI — threat_score stub verified.")

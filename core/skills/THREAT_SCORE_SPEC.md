# SKILL: Threat & Anomaly Scoring (`threat_score`)
> **Target Organ:** arifOS — `core/skills/threat_score.py`
> **Class:** OBSERVE + DERIVE (read-only analysis)
> **Forged:** 2026-06-14 by FORGE (000Ω)
> **Status:** SPEC — implementation pending

---

## PURPOSE

Convert messy signals (NATS governance events, tool_failures, unusual sequences) into a single risk score and labeled anomaly list for E7/AAA consumption.

This skill gives the kernel **situational awareness** — not just "something happened" but "this pattern is unusual and may need attention."

---

## ARCHITECTURE

```
NATS governance stream ──→ ThreatScorer ──→ RISK_LEVEL + anomalies[]
    organ heartbeats ──→                ──→ E7 envelope enrichment
    tool_failure counts ──→            ──→ AAA cockpit widget
```

**Input:** Last N governance events + organ heartbeat snapshots
**Output:** `ThreatAssessment` with risk level + anomaly list

---

## DATA MODEL

```python
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime

class RiskLevel(str, Enum):
    GREEN = "GREEN"       # normal operations
    YELLOW = "YELLOW"     # one anomaly, low severity
    AMBER = "AMBER"       # multiple anomalies or medium severity
    RED = "RED"           # critical anomaly — recommend 888_HOLD
    BLACK = "BLACK"       # system integrity suspect — auto-HOLD

class AnomalyType(str, Enum):
    FREQUENCY_SPIKE = "FREQUENCY_SPIKE"           # tool called unusually often
    NOVEL_PATH = "NOVEL_PATH"                     # tool/target combination never seen
    DEGRADED_CHAIN = "DEGRADED_CHAIN"             # organ health chain breaking
    HOLD_CLUSTER = "HOLD_CLUSTER"                 # multiple HOLDs in short window
    OVERRIDE_SURGE = "OVERRIDE_SURGE"             # unusual override rate
    FLOOR_VIOLATION_WAVE = "FLOOR_VIOLATION_WAVE" # multiple floor violations
    SILENCE_ANOMALY = "SILENCE_ANOMALY"           # expected events missing
    CROSS_ORGAN_CASCADE = "CROSS_ORGAN_CASCADE"   # failure propagating across organs

class Anomaly(BaseModel):
    type: AnomalyType
    severity: float          # 0.0–1.0
    description: str
    affected_tools: list[str]
    affected_organs: list[str]
    evidence_events: list[str]  # event IDs from governance stream
    first_seen: datetime
    last_seen: datetime
    count: int
    baseline: Optional[float]   # expected value for comparison

class ThreatAssessment(BaseModel):
    timestamp: datetime
    risk_level: RiskLevel
    risk_score: float          # 0.0–1.0 composite
    anomalies: list[Anomaly]
    organ_status: dict[str, str]  # organ_id → HEALTHY|DEGRADED|OFFLINE
    governance_health: str     # HEALTHY | WATCH | CONCERN | CRITICAL
    recommended_action: str    # CONTINUE | WATCH | INVESTIGATE | 888_HOLD
    entropy_delta: float       # dS since last assessment
    evidence_window_start: datetime
    evidence_window_end: datetime
    events_analyzed: int
```

---

## SCORING ALGORITHM

### 1. Baseline Calculation (per tool, per action_class)
```
For each tool T and action_class A:
  baseline_frequency[T][A] = avg(calls per hour over last 7 days)
  baseline_hold_rate[T][A] = avg(HOLDs / total_calls over last 7 days)
  baseline_override_rate[T][A] = avg(overrides / HOLDs over last 7 days)
```

### 2. Anomaly Detection (per event window)

```python
def detect_anomalies(events: list[GovernanceEvent], baselines: dict) -> list[Anomaly]:
    anomalies = []
    
    # 2a. Frequency spike
    for tool in tools:
        current_rate = count_calls(events, tool) / window_hours
        if current_rate > baseline_frequency[tool] * 3:
            anomalies.append(Anomaly(
                type=AnomalyType.FREQUENCY_SPIKE,
                severity=min(1.0, (current_rate / baseline_frequency[tool] - 1) * 0.5),
                description=f"{tool} called {current_rate:.1f}/hr vs baseline {baseline_frequency[tool]:.1f}/hr"
            ))
    
    # 2b. Novel tool path
    for event in events:
        path = f"{event.tool}→{event.action_class}"
        if path not in known_paths:
            anomalies.append(Anomaly(
                type=AnomalyType.NOVEL_PATH,
                severity=0.7,  # novel paths always suspicious
                description=f"Never-seen path: {path}"
            ))
            known_paths.add(path)
    
    # 2c. Hold cluster
    holds = [e for e in events if e.verdict == "HOLD"]
    if len(holds) >= 5 and time_between_first_last(holds) < 300:  # 5min window
        anomalies.append(Anomaly(
            type=AnomalyType.HOLD_CLUSTER,
            severity=min(1.0, len(holds) / 10),
            description=f"{len(holds)} HOLDs in {time_between_first_last(holds)}s"
        ))
    
    # 2d. Override surge
    overrides = [e for e in events if e.verdict == "OVERRIDE"]
    if len(overrides) > 0:
        override_rate = len(overrides) / len(holds) if holds else 1.0
        if override_rate > 0.3:  # more than 30% of HOLDs being overridden
            anomalies.append(Anomaly(
                type=AnomalyType.OVERRIDE_SURGE,
                severity=override_rate,
                description=f"Override rate {override_rate:.0%}"
            ))
    
    # 2e. Cross-organ cascade
    # If organ A's failure correlates with organ B's failure within 60s
    organ_failures = group_by_organ([e for e in events if e.status == "FAILURE"])
    for (org_a, org_b) in combinations(organ_failures.keys(), 2):
        if correlation_time(organ_failures[org_a], organ_failures[org_b]) < 60:
            anomalies.append(Anomaly(
                type=AnomalyType.CROSS_ORGAN_CASCADE,
                severity=0.8,
                description=f"Cascading failure: {org_a} → {org_b}"
            ))
    
    return anomalies
```

### 3. Risk Score Composite

```python
def compute_risk_score(anomalies: list[Anomaly], organ_status: dict) -> float:
    # Base: organ health
    degraded_count = sum(1 for s in organ_status.values() if s != "HEALTHY")
    organ_risk = degraded_count / max(len(organ_status), 1)
    
    # Anomaly contribution (weighted by severity)
    if anomalies:
        anomaly_risk = sum(a.severity for a in anomalies) / len(anomalies)
    else:
        anomaly_risk = 0.0
    
    # Composite: organ health 40%, anomalies 60%
    return 0.4 * organ_risk + 0.6 * anomaly_risk

def risk_level(score: float) -> RiskLevel:
    if score < 0.1:  return RiskLevel.GREEN
    if score < 0.3:  return RiskLevel.YELLOW
    if score < 0.6:  return RiskLevel.AMBER
    if score < 0.9:  return RiskLevel.RED
    return RiskLevel.BLACK
```

---

## INTEGRATION POINTS

### Input (read from):
- NATS `governance.>` stream — tool calls, verdicts, floor violations
- `arif_organ_attest_all()` — organ health snapshots
- VAULT999 chain — historical baselines

### Output (write to):
- AAA cockpit widget: `threat_level` gauge
- E7 envelope enrichment: `threat_score` field on every tool call
- NATS `governance.threat` subject: ThreatAssessment published
- 888_HOLD trigger: when risk_level ≥ RED

---

## INVOCATION

```python
# Called by arifOS runtime periodically or on event spike
from core.skills.threat_score import ThreatScorer

scorer = ThreatScorer()
assessment = scorer.assess(
    events=nats_consumer.fetch_last(100, subject="governance.>"),
    organ_status=arif_organ_attest_all(),
    baseline_window_days=7
)

# Publish result
nats.publish("governance.threat", assessment.json())

# If critical, trigger 888_HOLD
if assessment.risk_level in (RiskLevel.RED, RiskLevel.BLACK):
    arif_judge_deliberate(mode="judge", candidate="auto-hold", action_class="ATOMIC")
```

---

## TEST SCENARIOS

| Scenario | Expected Risk Level |
|----------|-------------------|
| Normal operations, 0 anomalies | GREEN |
| One FREQUENCY_SPIKE on low-risk tool | YELLOW |
| Three HOLDs in 2 minutes | AMBER |
| NOVEL_PATH + OVERRIDE_SURGE | RED |
| CROSS_ORGAN_CASCADE + degraded > 50% organs | BLACK |

---

## DEPENDENCIES

- `pydantic >= 2.13.4` (already in arifOS)
- `nats-py` (already deployed)
- No new external libraries required

---

*SPEC forged: 2026-06-14. Implementation target: `/root/arifOS/core/skills/threat_score.py`*
*DITEMPA BUKAN DIBERI — This skill must be FORGED, not imported.*

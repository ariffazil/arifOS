"""
Anomaly Scorer schemas — typed signal contracts for federation anomaly detection.

Consumes: NATS GOVERNANCE, FEEDBACK, GRADIENT, E7 streams
Produces: AnomalyScore → cockpit views, agent decisions, autonomy calibration

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class AnomalyDimension(StrEnum):
    """The five dimensions the anomaly scorer tracks."""
    GOVERNANCE_DRIFT = "governance_drift"
    FEEDBACK_OSCILLATION = "feedback_oscillation"
    GRADIENT_INSTABILITY = "gradient_instability"
    AUTONOMY_PRESSURE = "autonomy_pressure"
    ORGAN_SILENCE = "organ_silence"


class SignalLevel(StrEnum):
    """Severity level for anomaly signals."""
    NOMINAL = "NOMINAL"       # score < 0.30 — everything normal
    ELEVATED = "ELEVATED"     # score 0.30-0.55 — worth watching
    ANOMALOUS = "ANOMALOUS"   # score 0.55-0.80 — requires attention
    CRITICAL = "CRITICAL"     # score > 0.80 — requires immediate action


class Recommendation(StrEnum):
    """Action recommendation derived from anomaly score."""
    PROCEED = "PROCEED"         # full autonomy — no anomalies
    PROCEED_CAUTIOUS = "CAUTION"  # reduced autonomy — anomalies detected
    HOLD = "HOLD"               # governance hold — critical anomalies
    SABAR = "SABAR"             # escalate to principal (F13)


class GateVerdictEvent(BaseModel):
    """A single governance gate verdict from the NATS GOVERNANCE stream."""
    gate: str
    verdict: str  # PASS, HOLD, SABAR, PROCEED
    session_id: str = ""
    tool_name: str = ""
    action_class: str = "OBSERVE"
    autonomy_tier: str = ""
    reasons: list[str] = Field(default_factory=list)
    violated_laws: list[str] = Field(default_factory=list)
    timestamp: str = ""


class FeedbackSignalEvent(BaseModel):
    """A feedback loop signal from the NATS FEEDBACK stream."""
    signal: str  # PROCEED, REVISE_LOCAL, REVISE_GLOBAL, BRANCH, BACKTRACK, HOLD
    session_id: str = ""
    step_number: int = 0
    source_organ: str = "arifOS"
    target_organ: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = ""


class GradientSignalEvent(BaseModel):
    """A constitutional cost gradient signal from the NATS GRADIENT stream."""
    dimension: str  # constitution, physics, capital, substrate, continuity, dignity
    delta: float = 0.0
    session_id: str = ""
    source_organ: str = "arifOS"
    metadata: dict[str, Any] = Field(default_factory=dict)
    timestamp: str = ""


class E7AutonomyEvent(BaseModel):
    """An E7 Principal Paradox event from the NATS E7 stream."""
    event: str  # E7_AUTONOMY_CHANGE, E7_OVERRIDE, E7_ATTESTATION
    session_id: str = ""
    action_class: str = ""
    autonomy_tier: str = ""
    risk_tier: str = ""
    blast_radius: str = ""
    gate_verdict: str = ""
    reason: str = ""
    override_count: int = 0
    surge_active: bool = False
    timestamp: str = ""


class DimensionScore(BaseModel):
    """Score for a single anomaly dimension."""
    dimension: AnomalyDimension
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    level: SignalLevel = SignalLevel.NOMINAL
    trend: str = "stable"  # rising, falling, stable
    sample_count: int = 0
    last_signal: str = ""
    last_updated: str = ""

    @property
    def nominal(self) -> bool:
        return self.score < 0.30


class AnomalyScore(BaseModel):
    """Complete anomaly assessment — the primary output of the anomaly scorer.

    Published to arifos.anomaly.score subject for consumption by:
    - AAA cockpit (governance visibility)
    - 333-AGI (reasoning decisions)
    - 555-ASI (ethical critique)
    - A-AUDIT (compliance verification)
    - Autonomy calibration (E7 gate dynamic ceiling)
    """
    model_config = {"json_schema_extra": {
        "example": {
            "overall_score": 0.23,
            "overall_level": "NOMINAL",
            "recommendation": "PROCEED",
            "dimensions": {
                "governance_drift": {"dimension": "governance_drift", "score": 0.15, "level": "NOMINAL"},
                "feedback_oscillation": {"dimension": "feedback_oscillation", "score": 0.10, "level": "NOMINAL"},
                "gradient_instability": {"dimension": "gradient_instability", "score": 0.35, "level": "ELEVATED"},
                "autonomy_pressure": {"dimension": "autonomy_pressure", "score": 0.05, "level": "NOMINAL"},
                "organ_silence": {"dimension": "organ_silence", "score": 0.20, "level": "NOMINAL"},
            },
            "signals": [],
            "worst_dimension": "gradient_instability",
            "worst_dimension_score": 0.35,
            "federation_health": "NOMINAL",
        }
    }}

    overall_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_level: SignalLevel = SignalLevel.NOMINAL
    recommendation: Recommendation = Recommendation.PROCEED
    dimensions: dict[str, DimensionScore] = Field(default_factory=dict)
    signals: list[str] = Field(default_factory=list)
    signal_count_1h: int = 0
    worst_dimension: str = ""
    worst_dimension_score: float = 0.0
    federation_health: str = "NOMINAL"  # NOMINAL, DEGRADED, CRITICAL
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class DetectorState(BaseModel):
    """Internal state tracking for a single detector."""
    ema: float = 0.0           # exponential moving average
    ema_alpha: float = 0.15    # smoothing factor (higher = more responsive)
    spike_count: int = 0       # count of spikes in current window
    spike_threshold: float = 0.60  # score above this = spike
    last_n_scores: list[float] = Field(default_factory=list, max_length=50)
    samples_seen: int = 0
    last_updated: str = ""

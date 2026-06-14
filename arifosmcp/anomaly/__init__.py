"""
arifOS Anomaly Scorer — federation-wide anomaly detection via NATS streams.

Consumes: NATS GOVERNANCE, FEEDBACK, GRADIENT, E7_AUTONOMY, heartbeat
Produces: AnomalyScore (5 dimensions, 0.0-1.0) → cockpit, agents, autonomy calibration

Quick start:
    from arifosmcp.anomaly import get_scorer, AnomalyNATSSubscriber

    # Offline mode — feed events manually
    scorer = get_scorer()
    scorer.feed_gate_verdict(event)
    score = scorer.assess()

    # Live mode — subscribe to NATS
    sub = AnomalyNATSSubscriber()
    await sub.start()
    # ... events flow ...
    score = scorer.assess()

Architecture:
  schemas.py       — Pydantic models: AnomalyScore, DimensionScore, events
  detectors.py     — 5 detectors: governance_drift, feedback_oscillation,
                      gradient_instability, autonomy_pressure, organ_silence
  scorer.py        — AnomalyScorer: singleton, ingestion, assessment
  nats_subscriber.py — NATS bridge: subscribe to streams, feed scorer,
                        periodic score publishing

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from arifosmcp.anomaly.detectors import (
    AutonomyPressureDetector,
    FeedbackOscillationDetector,
    GovernanceDriftDetector,
    GradientInstabilityDetector,
    OrganSilenceDetector,
)
from arifosmcp.anomaly.nats_subscriber import (
    ANOMALY_SCORE_SUBJECT,
    ASSESS_INTERVAL_S,
    AnomalyNATSSubscriber,
)
from arifosmcp.anomaly.schemas import (
    AnomalyDimension,
    AnomalyScore,
    DetectorState,
    DimensionScore,
    E7AutonomyEvent,
    FeedbackSignalEvent,
    GateVerdictEvent,
    GradientSignalEvent,
    Recommendation,
    SignalLevel,
)
from arifosmcp.anomaly.scorer import AnomalyScorer, get_scorer, reset_scorer

__all__ = [
    # ── Scorer ──
    "AnomalyScorer",
    "get_scorer",
    "reset_scorer",
    # ── NATS bridge ──
    "AnomalyNATSSubscriber",
    "ANOMALY_SCORE_SUBJECT",
    "ASSESS_INTERVAL_S",
    # ── Schemas ──
    "AnomalyScore",
    "DimensionScore",
    "DetectorState",
    "AnomalyDimension",
    "SignalLevel",
    "Recommendation",
    "GateVerdictEvent",
    "FeedbackSignalEvent",
    "GradientSignalEvent",
    "E7AutonomyEvent",
    # ── Detectors ──
    "GovernanceDriftDetector",
    "FeedbackOscillationDetector",
    "GradientInstabilityDetector",
    "AutonomyPressureDetector",
    "OrganSilenceDetector",
]

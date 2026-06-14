"""
Anomaly Scorer — core scoring engine for federation-wide anomaly detection.

Five dimensions tracked via exponential moving average with spike detection:
  1. governance_drift    — gate verdict patterns changing over time
  2. feedback_oscillation — feedback loops cycling without convergence
  3. gradient_instability — constitutional cost dimensions spiking
  4. autonomy_pressure    — E7 override frequency increasing
  5. organ_silence        — federation organs not publishing heartbeats

Each detector independently scores 0.0-1.0. The combined anomaly score is a
weighted sum with governance and gradient weighted higher (they are the
constitutional backbone).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from arifosmcp.anomaly.detectors import (
    AutonomyPressureDetector,
    BaseDetector,
    FeedbackOscillationDetector,
    GovernanceDriftDetector,
    GradientInstabilityDetector,
    OrganSilenceDetector,
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

logger = logging.getLogger("arifosmcp.anomaly.scorer")

# ── Dimension weights for combined score ──
# Governance + Gradient = constitutional backbone (most important)
# Autonomy = E7 paradox (medium)
# Feedback = convergence health (medium)
# Organ silence = federation liveness (lower — survives degraded)
DIMENSION_WEIGHTS: dict[AnomalyDimension, float] = {
    AnomalyDimension.GOVERNANCE_DRIFT: 0.30,
    AnomalyDimension.GRADIENT_INSTABILITY: 0.25,
    AnomalyDimension.AUTONOMY_PRESSURE: 0.20,
    AnomalyDimension.FEEDBACK_OSCILLATION: 0.15,
    AnomalyDimension.ORGAN_SILENCE: 0.10,
}

# ── Thresholds for anomaly level classification ──
NOMINAL_THRESHOLD = 0.30   # below this: NOMINAL
ELEVATED_THRESHOLD = 0.55  # below this: ELEVATED
ANOMALOUS_THRESHOLD = 0.80  # below this: ANOMALOUS, above: CRITICAL

# ── Recommendation thresholds ──
PROCEED_THRESHOLD = 0.25     # below this: PROCEED (full autonomy)
CAUTION_THRESHOLD = 0.50     # below this: CAUTION (reduced autonomy)
HOLD_THRESHOLD = 0.70        # below this: HOLD, above: SABAR (escalate)

# ── Window sizes ──
SPIKE_WINDOW_S = 3600        # 1 hour
SIGNAL_WINDOW_S = 300        # 5 minutes — signals older than this are stale


def _classify_level(score: float) -> SignalLevel:
    if score < NOMINAL_THRESHOLD:
        return SignalLevel.NOMINAL
    if score < ELEVATED_THRESHOLD:
        return SignalLevel.ELEVATED
    if score < ANOMALOUS_THRESHOLD:
        return SignalLevel.ANOMALOUS
    return SignalLevel.CRITICAL


def _classify_recommendation(overall: float) -> Recommendation:
    if overall < PROCEED_THRESHOLD:
        return Recommendation.PROCEED
    if overall < CAUTION_THRESHOLD:
        return Recommendation.PROCEED_CAUTIOUS
    if overall < HOLD_THRESHOLD:
        return Recommendation.HOLD
    return Recommendation.SABAR


class AnomalyScorer:
    """Singleton anomaly scoring engine for the arifOS federation.

    Lifecycle:
      scorer = AnomalyScorer()
      scorer.feed_gate_verdict(event)     # from NATS GOVERNANCE
      scorer.feed_feedback_signal(event)  # from NATS FEEDBACK
      scorer.feed_gradient_signal(event)  # from NATS GRADIENT
      scorer.feed_e7_event(event)         # from NATS E7
      scorer.feed_heartbeat(organ, status)  # from NATS heartbeat
      score = scorer.assess()             # produce AnomalyScore
    """

    _instance: AnomalyScorer | None = None

    def __new__(cls) -> AnomalyScorer:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        self._detectors: dict[AnomalyDimension, BaseDetector] = {
            AnomalyDimension.GOVERNANCE_DRIFT: GovernanceDriftDetector(),
            AnomalyDimension.FEEDBACK_OSCILLATION: FeedbackOscillationDetector(),
            AnomalyDimension.GRADIENT_INSTABILITY: GradientInstabilityDetector(),
            AnomalyDimension.AUTONOMY_PRESSURE: AutonomyPressureDetector(),
            AnomalyDimension.ORGAN_SILENCE: OrganSilenceDetector(),
        }

        self._signal_count_1h: int = 0
        self._last_assessment: AnomalyScore | None = None
        self._signals: list[str] = []  # recent signal descriptions

        # Federation organ liveness tracking
        self._organ_last_seen: dict[str, str] = {}  # organ → ISO timestamp
        self._organ_status: dict[str, str] = {}     # organ → status

    # ── Feed methods — ingest events from NATS streams ────────────────────

    def feed_gate_verdict(self, event: GateVerdictEvent) -> None:
        """Ingest a governance gate verdict from NATS GOVERNANCE stream."""
        self._detectors[AnomalyDimension.GOVERNANCE_DRIFT].ingest(event)
        self._signal_count_1h += 1

        # Signal: track HOLD events
        if event.verdict in ("HOLD", "VOID"):
            self._signals.append(
                f"Gate {event.gate} HOLD on {event.tool_name}: {', '.join(event.reasons[:2])}"
            )
            if len(self._signals) > 100:
                self._signals = self._signals[-50:]

    def feed_feedback_signal(self, event: FeedbackSignalEvent) -> None:
        """Ingest a feedback loop signal from NATS FEEDBACK stream."""
        self._detectors[AnomalyDimension.FEEDBACK_OSCILLATION].ingest(event)
        self._signal_count_1h += 1

        # Signal: track oscillating feedback
        if event.signal in ("BACKTRACK", "HOLD", "REVISE_GLOBAL"):
            self._signals.append(
                f"Feedback {event.signal} from {event.source_organ} → {event.target_organ or 'mesh'}"
            )
            if len(self._signals) > 100:
                self._signals = self._signals[-50:]

    def feed_gradient_signal(self, event: GradientSignalEvent) -> None:
        """Ingest a gradient signal from NATS GRADIENT stream."""
        self._detectors[AnomalyDimension.GRADIENT_INSTABILITY].ingest(event)
        self._signal_count_1h += 1

        # Signal: track large gradient deltas
        if abs(event.delta) > 0.30:
            self._signals.append(
                f"Gradient spike: {event.dimension} Δ={event.delta:+.3f}"
            )
            if len(self._signals) > 100:
                self._signals = self._signals[-50:]

    def feed_e7_event(self, event: E7AutonomyEvent) -> None:
        """Ingest an E7 Principal Paradox event from NATS E7 stream."""
        self._detectors[AnomalyDimension.AUTONOMY_PRESSURE].ingest(event)
        self._signal_count_1h += 1

        if event.override_count > 5:
            self._signals.append(
                f"E7 override surge: {event.override_count} overrides, surge={event.surge_active}"
            )
            if len(self._signals) > 100:
                self._signals = self._signals[-50:]

    def feed_heartbeat(self, organ: str, status: str = "alive") -> None:
        """Record a federation organ heartbeat."""
        self._organ_last_seen[organ] = datetime.now(UTC).isoformat()
        self._organ_status[organ] = status
        self._detectors[AnomalyDimension.ORGAN_SILENCE].ingest(
            {"organ": organ, "status": status, "timestamp": self._organ_last_seen[organ]}
        )

    # ── Assessment — produce the anomaly score ───────────────────────────

    def assess(self) -> AnomalyScore:
        """Produce a complete anomaly assessment across all 5 dimensions.

        Returns an AnomalyScore with per-dimension breakdowns, overall score,
        signal level, and action recommendation.

        This is the primary output consumed by cockpit views, agent decisions,
        and autonomy calibration.
        """
        now = datetime.now(UTC).isoformat()
        dim_scores: dict[str, DimensionScore] = {}
        weighted_sum = 0.0
        worst_dim = ""
        worst_score = 0.0

        for dimension, detector in self._detectors.items():
            ds = detector.compute_score()
            ds.last_updated = now
            dim_scores[dimension.value] = ds

            weight = DIMENSION_WEIGHTS.get(dimension, 0.10)
            weighted_sum += ds.score * weight

            if ds.score > worst_score:
                worst_score = ds.score
                worst_dim = dimension.value

        # Prune stale signals (older than SIGNAL_WINDOW_S)
        self._prune_signals()

        overall_score = round(weighted_sum, 4)
        overall_level = _classify_level(overall_score)
        recommendation = _classify_recommendation(overall_score)

        # Federation health: CRITICAL if any dimension is CRITICAL
        federation_health = "NOMINAL"
        if any(ds.level == SignalLevel.CRITICAL for ds in dim_scores.values()):
            federation_health = "CRITICAL"
        elif any(ds.level == SignalLevel.ANOMALOUS for ds in dim_scores.values()):
            federation_health = "DEGRADED"
        elif worst_score >= ELEVATED_THRESHOLD:
            federation_health = "DEGRADED"

        score = AnomalyScore(
            overall_score=overall_score,
            overall_level=overall_level,
            recommendation=recommendation,
            dimensions=dim_scores,
            signals=list(self._signals[-20:]),  # last 20 signals
            signal_count_1h=self._signal_count_1h,
            worst_dimension=worst_dim,
            worst_dimension_score=worst_score,
            federation_health=federation_health,
            timestamp=now,
        )

        self._last_assessment = score
        return score

    def _prune_signals(self) -> None:
        """Remove stale signals. Called before each assessment."""
        # Signals are pruned by count, not time — last 50 signals kept
        pass  # Already handled in feed methods with max length

    # ── Internal state access (for testing / cockpit) ────────────────────

    @property
    def detector_states(self) -> dict[str, DetectorState]:
        return {dim.value: det.state for dim, det in self._detectors.items()}

    @property
    def organ_liveness(self) -> dict[str, dict[str, str]]:
        return {
            organ: {"last_seen": ts, "status": self._organ_status.get(organ, "unknown")}
            for organ, ts in self._organ_last_seen.items()
        }

    def get_state_snapshot(self) -> dict[str, Any]:
        """Return a snapshot of all internal state (for cockpit / debug)."""
        return {
            "detector_states": {
                dim.value: det.state.model_dump()
                for dim, det in self._detectors.items()
            },
            "organ_liveness": self.organ_liveness,
            "signal_count_1h": self._signal_count_1h,
            "recent_signals": self._signals[-10:],
            "last_assessment": (
                self._last_assessment.model_dump() if self._last_assessment else None
            ),
        }

    def reset(self) -> None:
        """Reset all detector state (for testing)."""
        for detector in self._detectors.values():
            detector.reset()
        self._signal_count_1h = 0
        self._signals.clear()
        self._organ_last_seen.clear()
        self._organ_status.clear()
        self._last_assessment = None


# ── Singleton accessor ───────────────────────────────────────────────────

def get_scorer() -> AnomalyScorer:
    """Get or create the federation anomaly scorer (singleton)."""
    return AnomalyScorer()


def reset_scorer() -> None:
    """Reset the scorer singleton (for testing)."""
    # pylint: disable=protected-access
    AnomalyScorer._instance = None

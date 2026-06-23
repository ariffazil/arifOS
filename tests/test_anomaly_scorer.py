"""
Tests for the Anomaly Scorer — all 5 detectors + integration.

Covers:
  - GovernanceDriftDetector: block ratio, novelty, pattern lock
  - FeedbackOscillationDetector: revision streak, oscillation, severity
  - GradientInstabilityDetector: magnitude, whipsaw, multidimensional shock
  - AutonomyPressureDetector: overrides, surge, tier downgrades
  - OrganSilenceDetector: freshness, silence, weighted scoring
  - AnomalyScorer: ingestion, assessment, recommendation levels
  - AnomalyNATSSubscriber: offline mode (no NATS required)

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime

import pytest

from arifosmcp.anomaly import (
    AnomalyDimension,
    AnomalyNATSSubscriber,
    AnomalyScore,
    AutonomyPressureDetector,
    DimensionScore,
    E7AutonomyEvent,
    FeedbackOscillationDetector,
    FeedbackSignalEvent,
    GateVerdictEvent,
    GovernanceDriftDetector,
    GradientInstabilityDetector,
    GradientSignalEvent,
    OrganSilenceDetector,
    Recommendation,
    SignalLevel,
    get_scorer,
    reset_scorer,
)


# ═══════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════


def _ts() -> str:
    return datetime.now(UTC).isoformat()


def _make_gate_event(
    verdict: str = "PASS",
    gate: str = "GATE_5_FLOORS",
    tool_name: str = "arif_sense_observe",
    violated_laws: list[str] | None = None,
) -> GateVerdictEvent:
    return GateVerdictEvent(
        gate=gate,
        verdict=verdict,
        tool_name=tool_name,
        violated_laws=violated_laws or [],
        timestamp=_ts(),
    )


def _make_feedback_event(
    signal: str = "PROCEED", step_number: int = 1, source: str = "arifOS"
) -> FeedbackSignalEvent:
    return FeedbackSignalEvent(
        signal=signal,
        step_number=step_number,
        source_organ=source,
        timestamp=_ts(),
    )


def _make_gradient_event(
    dimension: str = "constitution", delta: float = 0.05
) -> GradientSignalEvent:
    return GradientSignalEvent(
        dimension=dimension,
        delta=delta,
        timestamp=_ts(),
    )


def _make_e7_event(
    event_type: str = "E7_AUTONOMY_CHANGE",
    override_count: int = 0,
    surge_active: bool = False,
    autonomy_tier: str = "FULL_AUTO",
) -> E7AutonomyEvent:
    return E7AutonomyEvent(
        event=event_type,
        override_count=override_count,
        surge_active=surge_active,
        autonomy_tier=autonomy_tier,
        timestamp=_ts(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# DETECTOR UNIT TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestGovernanceDriftDetector:
    """Gate verdict pattern drift detection."""

    def test_nominal_when_all_pass(self) -> None:
        det = GovernanceDriftDetector()
        for _ in range(20):
            det.ingest(_make_gate_event("PASS"))
        score = det.compute_score()
        assert score.score < 0.30
        assert score.level == SignalLevel.NOMINAL

    def test_elevated_on_repeated_holds(self) -> None:
        det = GovernanceDriftDetector()
        # Feed 5 passes, 15 holds — block ratio must dominate
        for _ in range(5):
            det.ingest(_make_gate_event("PASS"))
        for _ in range(15):
            det.ingest(_make_gate_event("HOLD", violated_laws=["E7"]))
        score = det.compute_score()
        assert score.score > 0.25

    def test_novelty_amplifies_score(self) -> None:
        det = GovernanceDriftDetector()
        # Same violation repeated vs new violations
        det.ingest(_make_gate_event("HOLD", violated_laws=["E7"]))
        s1 = det.compute_score()
        det.ingest(_make_gate_event("HOLD", violated_laws=["F1", "F2", "F13"]))
        s2 = det.compute_score()
        # Second should be higher (more novel laws)
        assert s2.score > s1.score

    def test_pattern_lock_detected(self) -> None:
        det = GovernanceDriftDetector()
        # Same gate blocks 5 times
        for _ in range(5):
            det.ingest(_make_gate_event("HOLD", gate="GATE_2_BUDGET"))
        score = det.compute_score()
        assert score.score > 0.15

    def test_reset_clears_state(self) -> None:
        det = GovernanceDriftDetector()
        for _ in range(10):
            det.ingest(_make_gate_event("HOLD"))
        det.reset()
        score = det.compute_score()
        assert score.score == 0.0


class TestFeedbackOscillationDetector:
    """Feedback loop oscillation detection."""

    def test_nominal_on_proceed(self) -> None:
        det = FeedbackOscillationDetector()
        for _ in range(20):
            det.ingest(_make_feedback_event("PROCEED"))
        score = det.compute_score()
        assert score.score < 0.15

    def test_elevated_on_backtrack(self) -> None:
        det = FeedbackOscillationDetector()
        det.ingest(_make_feedback_event("BACKTRACK"))
        det.ingest(_make_feedback_event("BACKTRACK"))
        det.ingest(_make_feedback_event("BACKTRACK"))
        score = det.compute_score()
        assert score.score > 0.40

    def test_hold_is_critical(self) -> None:
        det = FeedbackOscillationDetector()
        for _ in range(5):
            det.ingest(_make_feedback_event("HOLD"))
        score = det.compute_score()
        # With streak boost, should be elevated or higher
        assert score.score > 0.50

    def test_revision_streak_amplifies(self) -> None:
        det = FeedbackOscillationDetector()
        # 10 REVISE_LOCAL in a row builds streak
        for _ in range(10):
            det.ingest(_make_feedback_event("REVISE_LOCAL"))
        score = det.compute_score()
        assert score.score > 0.30

    def test_oscillation_between_organs(self) -> None:
        det = FeedbackOscillationDetector()
        # Ping-pong: REVISE_LOCAL → REVISE_GLOBAL → REVISE_LOCAL → REVISE_GLOBAL
        for _ in range(5):
            det.ingest(_make_feedback_event("REVISE_LOCAL"))
            det.ingest(_make_feedback_event("REVISE_GLOBAL"))
        score = det.compute_score()
        # Oscillation + revision streak should push it up
        assert score.score > 0.25


class TestGradientInstabilityDetector:
    """Constitutional cost gradient instability detection."""

    def test_nominal_on_small_deltas(self) -> None:
        det = GradientInstabilityDetector()
        for _ in range(20):
            det.ingest(_make_gradient_event("constitution", delta=0.02))
        score = det.compute_score()
        assert score.score < 0.30

    def test_elevated_on_large_delta(self) -> None:
        det = GradientInstabilityDetector()
        for _ in range(4):
            det.ingest(_make_gradient_event("physics", delta=0.45))
            det.ingest(_make_gradient_event("physics", delta=0.50))
        score = det.compute_score()
        assert score.score > 0.30

    def test_whipsaw_detection(self) -> None:
        det = GradientInstabilityDetector()
        # Feed 3 whipsaw pairs — EMA needs to build up
        for _ in range(3):
            det.ingest(_make_gradient_event("capital", delta=0.40))
            det.ingest(_make_gradient_event("capital", delta=-0.40))
        score = det.compute_score()
        assert score.score > 0.30

    def test_multidimensional_shock(self) -> None:
        det = GradientInstabilityDetector()
        # 4 dimensions spike simultaneously
        det.ingest(_make_gradient_event("constitution", delta=0.30))
        det.ingest(_make_gradient_event("physics", delta=0.25))
        det.ingest(_make_gradient_event("capital", delta=0.35))
        det.ingest(_make_gradient_event("substrate", delta=0.20))
        score = det.compute_score()
        # The 4th should trigger multidimensional shock boost
        assert score.score > 0.10  # at minimum, should register something


class TestAutonomyPressureDetector:
    """E7 autonomy pressure detection."""

    def test_nominal_no_overrides(self) -> None:
        det = AutonomyPressureDetector()
        for _ in range(10):
            det.ingest(_make_e7_event("E7_AUTONOMY_CHANGE", autonomy_tier="FULL_AUTO"))
        score = det.compute_score()
        assert score.score < 0.10

    def test_elevated_on_overrides(self) -> None:
        det = AutonomyPressureDetector()
        for _ in range(3):
            det.ingest(_make_e7_event("E7_OVERRIDE", override_count=6, surge_active=True))
        score = det.compute_score()
        assert score.score > 0.45

    def test_surge_amplifies(self) -> None:
        det = AutonomyPressureDetector()
        det.ingest(_make_e7_event("E7_OVERRIDE", override_count=3, surge_active=False))
        s1 = det.compute_score()
        det.ingest(_make_e7_event("E7_OVERRIDE", override_count=3, surge_active=True))
        s2 = det.compute_score()
        # Surge should push score higher
        assert s2.score >= s1.score

    def test_tier_downgrades_accumulate(self) -> None:
        det = AutonomyPressureDetector()
        for _ in range(2):
            det.ingest(_make_e7_event("E7_AUTONOMY_CHANGE", autonomy_tier="PROPOSE_ONLY"))
            det.ingest(
                _make_e7_event("E7_AUTONOMY_CHANGE", autonomy_tier="PRINCIPAL_APPROVAL_REQUIRED")
            )
        score = det.compute_score()
        assert score.score > 0.08


class TestOrganSilenceDetector:
    """Federation organ silence detection."""

    def test_nominal_when_all_fresh(self) -> None:
        det = OrganSilenceDetector()
        det.ingest({"organ": "arifOS", "status": "alive", "timestamp": _ts()})
        det.ingest({"organ": "GEOX", "status": "alive", "timestamp": _ts()})
        det.ingest({"organ": "WEALTH", "status": "alive", "timestamp": _ts()})
        score = det.compute_score()
        assert score.score < 0.30

    def test_elevated_when_organ_stale(self) -> None:
        det = OrganSilenceDetector()
        # arifOS fresh, GEOX silent for 20 minutes
        for _ in range(3):
            det.ingest({"organ": "arifOS", "status": "alive", "timestamp": _ts()})
            stale_ts = datetime.fromtimestamp(time.time() - 1200, tz=UTC).isoformat()
            det.ingest({"organ": "GEOX", "status": "alive", "timestamp": stale_ts})
        score = det.compute_score()
        assert score.score > 0.20

    def test_core_organs_weighted_higher(self) -> None:
        det = OrganSilenceDetector()
        # arifOS silent for 1 hour
        stale_ts = datetime.fromtimestamp(time.time() - 3600, tz=UTC).isoformat()
        det.ingest({"organ": "arifOS", "status": "alive", "timestamp": stale_ts})
        det.ingest({"organ": "AAA", "status": "alive", "timestamp": _ts()})
        score = det.compute_score()
        # arifOS weighted 0.30, silence score should reflect this
        assert score.score > 0.10


# ═══════════════════════════════════════════════════════════════════════════
# ANOMALY SCORER INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAnomalyScorer:
    """Integration tests for the full anomaly scorer."""

    def setup_method(self) -> None:
        reset_scorer()

    def test_initial_state_is_nominal(self) -> None:
        scorer = get_scorer()
        score = scorer.assess()
        assert score.overall_score == 0.0
        assert score.overall_level == SignalLevel.NOMINAL
        assert score.recommendation == Recommendation.PROCEED
        assert score.federation_health == "NOMINAL"

    def test_all_dimensions_present(self) -> None:
        scorer = get_scorer()
        score = scorer.assess()
        expected_dims = {dim.value for dim in AnomalyDimension}
        assert set(score.dimensions.keys()) == expected_dims

    def test_proceed_recommendation_low_score(self) -> None:
        scorer = get_scorer()
        # Feed nominal events
        for _ in range(10):
            scorer.feed_gate_verdict(_make_gate_event("PASS"))
            scorer.feed_feedback_signal(_make_feedback_event("PROCEED"))
            scorer.feed_gradient_signal(_make_gradient_event("constitution", 0.01))
        score = scorer.assess()
        assert score.recommendation == Recommendation.PROCEED
        assert score.overall_score < 0.30

    def test_caution_recommendation_moderate_anomalies(self) -> None:
        scorer = get_scorer()
        # Feed events that raise the score moderately
        for _ in range(12):
            scorer.feed_gate_verdict(_make_gate_event("HOLD", violated_laws=["E7"]))
            scorer.feed_feedback_signal(_make_feedback_event("REVISE_GLOBAL"))
            scorer.feed_gradient_signal(_make_gradient_event("physics", delta=0.35))
            scorer.feed_e7_event(_make_e7_event("E7_OVERRIDE", override_count=4, surge_active=True))
        score = scorer.assess()
        assert score.recommendation in (Recommendation.PROCEED_CAUTIOUS, Recommendation.HOLD)
        assert score.overall_score > 0.25

    def test_hold_recommendation_severe_anomalies(self) -> None:
        scorer = get_scorer()
        # Heavy bombardment of critical events
        for _ in range(60):
            scorer.feed_gate_verdict(_make_gate_event("HOLD", violated_laws=["F1", "F13", "E7"]))
            scorer.feed_feedback_signal(_make_feedback_event("HOLD"))
            scorer.feed_gradient_signal(_make_gradient_event("dignity", delta=0.60))
            scorer.feed_e7_event(
                _make_e7_event("E7_OVERRIDE", override_count=15, surge_active=True)
            )
        score = scorer.assess()
        # Should be at CAUTION or above
        assert score.overall_level.value in ("ELEVATED", "ANOMALOUS", "CRITICAL")

    def test_signal_accumulation(self) -> None:
        scorer = get_scorer()
        for _ in range(5):
            scorer.feed_gate_verdict(_make_gate_event("HOLD", violated_laws=["F13"]))
        score = scorer.assess()
        assert score.signal_count_1h == 5
        assert len(score.signals) > 0

    def test_worst_dimension_tracked(self) -> None:
        scorer = get_scorer()
        # Push governance drift up hard
        for _ in range(30):
            scorer.feed_gate_verdict(_make_gate_event("HOLD", violated_laws=["F1", "F2", "F13"]))
        score = scorer.assess()
        assert score.worst_dimension == "governance_drift"
        assert score.worst_dimension_score > 0.10

    def test_federation_health_degraded(self) -> None:
        scorer = get_scorer()
        # Push a dimension into ANOMALOUS
        for _ in range(80):
            scorer.feed_gate_verdict(_make_gate_event("HOLD", violated_laws=["F1", "F13"]))
            scorer.feed_feedback_signal(_make_feedback_event("HOLD"))
            scorer.feed_gradient_signal(_make_gradient_event("constitution", delta=0.50))
        score = scorer.assess()
        assert score.federation_health in ("DEGRADED", "CRITICAL")

    def test_organ_liveness_tracking(self) -> None:
        scorer = get_scorer()
        scorer.feed_heartbeat("arifOS", "alive")
        scorer.feed_heartbeat("GEOX", "alive")
        scorer.feed_heartbeat("WEALTH", "degraded")

        liveness = scorer.organ_liveness
        assert "arifOS" in liveness
        assert "GEOX" in liveness
        assert liveness["WEALTH"]["status"] == "degraded"

    def test_reset_clears_all_state(self) -> None:
        scorer = get_scorer()
        for _ in range(20):
            scorer.feed_gate_verdict(_make_gate_event("HOLD"))
        scorer.reset()
        score = scorer.assess()
        assert score.overall_score == 0.0
        assert score.signal_count_1h == 0

    def test_singleton_returns_same_instance(self) -> None:
        s1 = get_scorer()
        s2 = get_scorer()
        assert s1 is s2


# ═══════════════════════════════════════════════════════════════════════════
# SCHEMA TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSchemas:
    """Pydantic model validation."""

    def test_anomaly_score_json_serializable(self) -> None:
        score = AnomalyScore(
            overall_score=0.45,
            overall_level=SignalLevel.ELEVATED,
            recommendation=Recommendation.PROCEED_CAUTIOUS,
            dimensions={
                "governance_drift": DimensionScore(
                    dimension=AnomalyDimension.GOVERNANCE_DRIFT,
                    score=0.30,
                    level=SignalLevel.ELEVATED,
                    trend="rising",
                    sample_count=10,
                ),
            },
            worst_dimension="governance_drift",
            worst_dimension_score=0.30,
        )
        data = score.model_dump()
        assert data["overall_score"] == 0.45
        assert data["overall_level"] == "ELEVATED"
        assert "dimensions" in data

    def test_dimension_score_bounds(self) -> None:
        # Score must be 0.0-1.0
        with pytest.raises(Exception):
            DimensionScore(dimension=AnomalyDimension.GOVERNANCE_DRIFT, score=1.5)

    def test_gate_verdict_event_parsing(self) -> None:
        event = GateVerdictEvent(
            gate="GATE_5_FLOORS",
            verdict="HOLD",
            violated_laws=["F1", "F13"],
        )
        assert event.gate == "GATE_5_FLOORS"
        assert event.verdict == "HOLD"
        assert "F1" in event.violated_laws


# ═══════════════════════════════════════════════════════════════════════════
# NATS SUBSCRIBER (OFFLINE MODE)
# ═══════════════════════════════════════════════════════════════════════════


class TestNATSSubscriberOffline:
    """Offline-mode tests (no NATS required)."""

    def test_creates_subscriber(self) -> None:
        sub = AnomalyNATSSubscriber()
        assert sub.connected is False
        assert sub.scorer is not None

    @pytest.mark.asyncio
    async def test_offline_status(self) -> None:
        sub = AnomalyNATSSubscriber()
        status = await sub.get_status()
        assert status["connected"] is False
        assert status["running"] is False

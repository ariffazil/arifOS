"""
Anomaly Detectors — five independent signal processors that score dimensions.

Each detector:
  - Ingests events from its NATS stream
  - Maintains an exponential moving average (EMA) of anomaly intensity
  - Detects spikes (sustained deviation above threshold)
  - Computes a 0.0-1.0 score with level classification

Detector contract:
  class MyDetector(BaseDetector):
      def ingest(self, event) -> None:   # process one event
      def compute_score(self) -> DimensionScore:  # produce current score

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections import deque
from datetime import UTC, datetime
from typing import Any

from arifosmcp.anomaly.schemas import (
    AnomalyDimension,
    DetectorState,
    DimensionScore,
    E7AutonomyEvent,
    FeedbackSignalEvent,
    GateVerdictEvent,
    GradientSignalEvent,
    SignalLevel,
)

# ── Base detector ────────────────────────────────────────────────────────


class BaseDetector(ABC):
    """Base class for all anomaly detectors.

    Provides EMA tracking, spike detection, and score computation from
    a sliding window of observations.
    """

    dimension: AnomalyDimension

    def __init__(self, ema_alpha: float = 0.15, spike_threshold: float = 0.60,
                 window_size: int = 50) -> None:
        self.state = DetectorState(
            ema_alpha=ema_alpha,
            spike_threshold=spike_threshold,
        )
        self._window_size = window_size
        self._observations: deque[dict[str, Any]] = deque(maxlen=window_size)
        self._raw_values: deque[float] = deque(maxlen=window_size)

    @abstractmethod
    def ingest(self, event: Any) -> None:
        """Process one event. Subclasses extract a raw anomaly intensity 0.0-1.0."""
        ...

    def _update_ema(self, raw: float) -> None:
        """Update exponential moving average and spike tracking."""
        # Clamp raw to [0.0, 1.0]
        raw = max(0.0, min(1.0, raw))

        self.state.ema = (
            self.state.ema_alpha * raw
            + (1.0 - self.state.ema_alpha) * self.state.ema
        )
        self.state.samples_seen += 1
        self.state.last_updated = datetime.now(UTC).isoformat()

        # Track recent scores for trend
        self.state.last_n_scores.append(self.state.ema)
        if len(self.state.last_n_scores) > self._window_size:
            self.state.last_n_scores = self.state.last_n_scores[-self._window_size:]

        # Spike detection: if EMA exceeds threshold, increment spike count
        if self.state.ema >= self.state.spike_threshold:
            self.state.spike_count += 1

        self._raw_values.append(raw)

    def _compute_trend(self) -> str:
        """Determine trend direction from recent EMA trajectory."""
        scores = self.state.last_n_scores
        if len(scores) < 5:
            return "stable"

        # Compare last 5 vs previous 5
        recent = scores[-5:]
        earlier = scores[-10:-5] if len(scores) >= 10 else scores[:5]
        recent_avg = sum(recent) / len(recent)
        earlier_avg = sum(earlier) / len(earlier)

        delta = recent_avg - earlier_avg
        if delta > 0.05:
            return "rising"
        if delta < -0.05:
            return "falling"
        return "stable"

    def compute_score(self) -> DimensionScore:
        """Produce the current dimension score from EMA and spike state."""
        # Base score is EMA, boosted by recent spikes
        score = self.state.ema

        # Spike boost: each recent spike adds 0.05, capped at 0.95
        spike_boost = min(0.15, self.state.spike_count * 0.03)
        score = min(0.95, score + spike_boost)

        # Decay spike count over time (not persisted here — reset on read)
        self.state.spike_count = max(0, self.state.spike_count - 1)

        level = self._classify_level(score)

        return DimensionScore(
            dimension=self.dimension,
            score=round(score, 4),
            level=level,
            trend=self._compute_trend(),
            sample_count=self.state.samples_seen,
            last_signal=self._last_signal_description(),
            last_updated=self.state.last_updated,
        )

    @staticmethod
    def _classify_level(score: float) -> SignalLevel:
        if score < 0.30:
            return SignalLevel.NOMINAL
        if score < 0.55:
            return SignalLevel.ELEVATED
        if score < 0.80:
            return SignalLevel.ANOMALOUS
        return SignalLevel.CRITICAL

    def _last_signal_description(self) -> str:
        if not self._observations:
            return ""
        obs = self._observations[-1]
        return str(obs.get("summary", ""))[:120]

    def reset(self) -> None:
        """Reset detector state (for testing)."""
        self.state = DetectorState(ema_alpha=self.state.ema_alpha,
                                   spike_threshold=self.state.spike_threshold)
        self._observations.clear()
        self._raw_values.clear()


# ═══════════════════════════════════════════════════════════════════════════
# DETECTOR 1: GOVERNANCE DRIFT
# ═══════════════════════════════════════════════════════════════════════════

class GovernanceDriftDetector(BaseDetector):
    """Detects drift in governance gate verdict patterns.

    Anomaly intensity rises when:
      - HOLD/VOID verdicts increase in frequency
      - Same gate blocks repeatedly (pattern lock)
      - Gate latency increases (pipeline degradation)
      - Violated laws appear that weren't seen before
    """

    dimension = AnomalyDimension.GOVERNANCE_DRIFT

    def __init__(self) -> None:
        super().__init__(ema_alpha=0.12, spike_threshold=0.55)
        self._hold_count: int = 0
        self._pass_count: int = 0
        self._gate_block_counts: dict[str, int] = {}  # gate → block count
        self._seen_violated_laws: set[str] = set()

    def ingest(self, event: GateVerdictEvent) -> None:
        """Process a governance gate verdict."""
        is_block = event.verdict in ("HOLD", "VOID")
        is_warn = event.verdict in ("WARN", "SABAR")

        if is_block:
            self._hold_count += 1
            self._gate_block_counts[event.gate] = (
                self._gate_block_counts.get(event.gate, 0) + 1
            )
        else:
            self._pass_count += 1

        # Raw anomaly intensity — composite of block ratio + novelty + pattern lock
        total_decisions = self._hold_count + self._pass_count
        block_ratio = self._hold_count / max(total_decisions, 1)

        # Novelty: how many new violated laws appeared?
        new_laws = [law for law in event.violated_laws if law not in self._seen_violated_laws]
        for law in new_laws:
            self._seen_violated_laws.add(law)
        novelty_score = min(0.5, len(new_laws) * 0.10)

        # Pattern lock: same gate blocking repeatedly
        pattern_score = 0.0
        if self._gate_block_counts:
            max_blocks = max(self._gate_block_counts.values())
            pattern_score = min(0.4, max_blocks * 0.08)

        # Composite: block ratio weighted highest, novelty second, pattern lock third
        raw = (block_ratio * 0.50) + (novelty_score * 0.25) + (pattern_score * 0.25)

        # WARN/SABAR adds moderate intensity
        if is_warn and not is_block:
            raw += 0.10

        self._observations.append({
            "summary": f"{event.gate} → {event.verdict}" + (
                f" [{', '.join(event.violated_laws)}]" if event.violated_laws else ""
            ),
            "raw": raw,
        })
        self._update_ema(min(1.0, raw))


# ═══════════════════════════════════════════════════════════════════════════
# DETECTOR 2: FEEDBACK OSCILLATION
# ═══════════════════════════════════════════════════════════════════════════

class FeedbackOscillationDetector(BaseDetector):
    """Detects oscillation in cross-organ feedback loops.

    Anomaly intensity rises when:
      - REVISE_GLOBAL / BACKTRACK signals are frequent (loop instability)
      - HOLD signals appear in feedback (governance intervention)
      - Signal sequence shows ping-pong pattern (A→B→A→B without PROCEED)
      - Step numbers are high without convergence (loop exhaustion)
    """

    dimension = AnomalyDimension.FEEDBACK_OSCILLATION

    def __init__(self) -> None:
        super().__init__(ema_alpha=0.18, spike_threshold=0.50)
        self._last_signal: str = ""
        self._oscillation_count: int = 0
        self._revision_streak: int = 0  # consecutive non-PROCEED signals

    def ingest(self, event: FeedbackSignalEvent) -> None:
        """Process a feedback loop signal."""
        signal = event.signal

        # Track oscillation: alternating between REVISE_LOCAL and REVISE_GLOBAL
        if self._last_signal.startswith("REVISE") and signal.startswith("REVISE"):
            if signal != self._last_signal:
                self._oscillation_count += 1

        # Track revision streak: consecutive non-PROCEED signals
        if signal == "PROCEED":
            self._revision_streak = 0
        else:
            self._revision_streak += 1

        self._last_signal = signal

        # Compute raw anomaly intensity:
        # - Backtrack/HOLD = high intensity
        # - Revision streak = medium intensity
        # - REVISE_GLOBAL = moderate
        # - REVISE_LOCAL = low
        severity_map = {
            "BACKTRACK": 0.80,
            "HOLD": 0.90,
            "REVISE_GLOBAL": 0.55,
            "REVISE_LOCAL": 0.30,
            "BRANCH": 0.40,
            "PROCEED": 0.05,
        }
        base_severity = severity_map.get(signal, 0.20)

        # Boost from revision streak (capped at 0.3 boost)
        streak_boost = min(0.30, self._revision_streak * 0.06)

        # Boost from oscillation (ping-pong between organs)
        oscillation_boost = min(0.20, self._oscillation_count * 0.04)

        raw = min(1.0, base_severity + streak_boost + oscillation_boost)

        # PROCEED rapidly reduces intensity
        if signal == "PROCEED":
            raw = max(0.01, raw * 0.50)

        self._observations.append({
            "summary": f"{signal} step={event.step_number} streak={self._revision_streak}",
            "raw": raw,
        })
        self._update_ema(raw)


# ═══════════════════════════════════════════════════════════════════════════
# DETECTOR 3: GRADIENT INSTABILITY
# ═══════════════════════════════════════════════════════════════════════════

class GradientInstabilityDetector(BaseDetector):
    """Detects instability in the constitutional cost function gradient.

    Anomaly intensity rises when:
      - Any dimension's delta is large (|Δ| > 0.30)
      - Multiple dimensions move simultaneously (correlated shock)
      - Any single dimension spikes repeatedly (sustained instability)
      - Delta signs oscillate (constitutional whipsaw)
    """

    dimension = AnomalyDimension.GRADIENT_INSTABILITY

    def __init__(self) -> None:
        super().__init__(ema_alpha=0.25, spike_threshold=0.45)
        self._dimension_last_delta: dict[str, float] = {}
        self._dimension_spike_count: dict[str, int] = {}
        self._multidimensional_shocks: int = 0

    def ingest(self, event: GradientSignalEvent) -> None:
        """Process a gradient signal."""
        dim = event.dimension
        delta = event.delta
        abs_delta = abs(delta)

        # Track per-dimension deltas for whip-saw detection
        prev_delta = self._dimension_last_delta.get(dim, 0.0)
        whipsaw = (prev_delta * delta < 0 and abs_delta > 0.15)  # sign flip with magnitude
        self._dimension_last_delta[dim] = delta

        # Track per-dimension spike count (|Δ| > 0.25 = spike)
        if abs_delta > 0.25:
            self._dimension_spike_count[dim] = (
                self._dimension_spike_count.get(dim, 0) + 1
            )

        # Detect multidimensional shock: >2 dimensions active in current window
        recently_active = sum(
            1 for d in self._dimension_last_delta
            if abs(self._dimension_last_delta.get(d, 0.0)) > 0.15
        )
        if recently_active >= 3:
            self._multidimensional_shocks += 1

        # Raw anomaly intensity:
        # - Large absolute delta = primary signal
        # - Whipsaw = amplification
        # - Multidimensional shock = systemic risk
        magnitude_score = min(1.0, abs_delta / 0.50)  # |Δ| of 0.50 → score 1.0
        whipsaw_boost = 0.20 if whipsaw else 0.0
        systemic_boost = 0.25 if recently_active >= 3 else 0.0

        raw = min(1.0, magnitude_score + whipsaw_boost + systemic_boost)

        self._observations.append({
            "summary": f"∇{dim} Δ={delta:+.4f}" + (" WHIPSAW" if whipsaw else "") + (
                f" multi_dim={recently_active}" if recently_active >= 3 else ""
            ),
            "raw": raw,
        })
        self._update_ema(raw)


# ═══════════════════════════════════════════════════════════════════════════
# DETECTOR 4: AUTONOMY PRESSURE
# ═══════════════════════════════════════════════════════════════════════════

class AutonomyPressureDetector(BaseDetector):
    """Detects pressure on the E7 autonomy ceiling.

    Anomaly intensity rises when:
      - E7 override count exceeds MAX_OVERRIDES_PER_HOUR (3)
      - Surge mode is active (principal repeatedly overriding)
      - Autonomy tier is being downgraded frequently
      - PROPOSE_ONLY or PRINCIPAL_APPROVAL_REQUIRED appear on low-risk actions
    """

    dimension = AnomalyDimension.AUTONOMY_PRESSURE

    def __init__(self) -> None:
        super().__init__(ema_alpha=0.25, spike_threshold=0.55)
        self._override_total: int = 0
        self._surge_active: bool = False
        self._tier_downgrades: int = 0
        self._last_tier: str = "FULL_AUTO"

    def ingest(self, event: E7AutonomyEvent) -> None:
        """Process an E7 Principal Paradox event."""
        # Track overrides
        if event.event == "E7_OVERRIDE":
            self._override_total += event.override_count
            self._surge_active = event.surge_active

        # Track tier downgrades
        if event.event == "E7_AUTONOMY_CHANGE":
            current_tier = event.autonomy_tier
            tier_order = {"FULL_AUTO": 0, "PROPOSE_ONLY": 1, "PRINCIPAL_APPROVAL_REQUIRED": 2}
            prev_order = tier_order.get(self._last_tier, 0)
            curr_order = tier_order.get(current_tier, 0)
            if curr_order > prev_order:
                self._tier_downgrades += 1
            self._last_tier = current_tier

        # Compute raw anomaly intensity:
        # - Override count (relative to max of 3/hour)
        # - Surge active = heavy pressure
        # - Tier downgrades accumulating = autonomy erosion
        override_score = min(1.0, self._override_total / 3.0)  # 3 overrides → 1.0
        surge_score = 0.40 if self._surge_active else 0.0
        downgrade_score = min(0.60, self._tier_downgrades * 0.15)

        raw = min(1.0, override_score + surge_score + downgrade_score)

        self._observations.append({
            "summary": f"E7 overrides={self._override_total} surge={self._surge_active} "
                       f"downgrades={self._tier_downgrades} tier={self._last_tier}",
            "raw": raw,
        })
        self._update_ema(raw)


# ═══════════════════════════════════════════════════════════════════════════
# DETECTOR 5: ORGAN SILENCE
# ═══════════════════════════════════════════════════════════════════════════

class OrganSilenceDetector(BaseDetector):
    """Detects when federation organs stop publishing.

    Anomaly intensity rises when:
      - An organ hasn't been seen for > 5 minutes
      - Multiple organs are silent simultaneously
      - An organ reports status != "alive"
      - Core organs (arifOS, GEOX) go silent (higher weight)

    This detector does NOT use EMA — it computes score directly from
    time-since-last-seen for each organ.
    """

    dimension = AnomalyDimension.ORGAN_SILENCE

    # Organ weights — core organs are heavier
    ORGAN_WEIGHTS: dict[str, float] = {
        "arifOS": 0.30,
        "GEOX": 0.20,
        "WEALTH": 0.15,
        "WELL": 0.15,
        "MIND": 0.10,
        "MEMORY": 0.05,
        "AAA": 0.05,
    }

    STALE_THRESHOLD_S = 300     # 5 minutes — organ is stale
    SILENT_THRESHOLD_S = 900    # 15 minutes — organ is silent
    DEAD_THRESHOLD_S = 3600     # 60 minutes — organ is presumed dead

    def __init__(self) -> None:
        super().__init__(ema_alpha=0.25, spike_threshold=0.40)
        self._organ_seen: dict[str, float] = {}  # organ → epoch seconds

    def ingest(self, event: dict[str, Any]) -> None:
        """Process a heartbeat event: {"organ": str, "status": str, "timestamp": str}."""
        organ = event.get("organ", "unknown")
        status = event.get("status", "alive")
        ts_str = event.get("timestamp", "")

        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
        except (ValueError, AttributeError):
            ts = time.time()

        self._organ_seen[organ] = ts

        # Compute raw anomaly intensity from silence of ALL known organs
        now = time.time()
        raw = self._compute_silence_score(now)

        self._observations.append({
            "summary": f"{organ}={status}" if status != "alive" else f"{organ}=alive",
            "raw": raw,
        })
        self._update_ema(raw)

    def _compute_silence_score(self, now: float) -> float:
        """Compute silence score from all tracked organs."""
        if not self._organ_seen:
            return 0.0

        total_weight = 0.0
        weighted_silence = 0.0

        for organ, last_seen in self._organ_seen.items():
            gap_s = now - last_seen
            weight = self.ORGAN_WEIGHTS.get(organ, 0.10)
            total_weight += weight

            if gap_s > self.DEAD_THRESHOLD_S:
                silence_factor = 1.0
            elif gap_s > self.SILENT_THRESHOLD_S:
                silence_factor = 0.75
            elif gap_s > self.STALE_THRESHOLD_S:
                silence_factor = 0.40
            else:
                # Fresh — linear decay from 0.30 at STALE_THRESHOLD to 0.0 now
                silence_factor = max(0.0, 0.30 * (gap_s / self.STALE_THRESHOLD_S))

            weighted_silence += silence_factor * weight

        if total_weight == 0:
            return 0.0

        return weighted_silence / total_weight

    def compute_score(self) -> DimensionScore:
        """Override: re-compute silence score from current organ timestamps."""
        raw = self._compute_silence_score(time.time())
        # Update EMA with current silence state
        self.state.ema = (
            self.state.ema_alpha * raw
            + (1.0 - self.state.ema_alpha) * self.state.ema
        )
        return super().compute_score()

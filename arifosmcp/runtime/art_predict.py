"""
ART 2.0 — Predictive Trust Module

Extends ART 1.0 (reactive lifecycle) with predictive capabilities:
  - Blast quantization: string enum → numerical weight
  - Trust decay curves: exponential decay forecasting
  - Tool Q-table: learned optimal tool selection per task class
  - Predictive demotion: forecast failure before it happens

Lineage:
  2026-06-21 — ART 1.0 forged (493 lines, reactive lifecycle)
  2026-06-21 — ART 2.0 predictive layer (this file)

Usage:
    from arifosmcp.runtime.art_predict import (
        quantize_blast,
        compute_trust_decay,
        predict_failure,
        ToolQTable,
    )

    # Quantize blast radius to numerical weight
    weight = quantize_blast("infrastructure")  # → 27

    # Compute trust decay over time
    trust = compute_trust_decay(initial_trust=1.0, days_elapsed=30, failure_rate=0.1)

    # Predict if tool will fail
    risk = predict_failure(failure_rate=0.25, drift_count=2, days_since_use=45)

Hermeneutic grounding:
  Ebbinghaus    → exponential forgetting curve → trust decay as memory decay
  Feynman       → "the first principle is you must not fool yourself" → trust is not optimism
  Shannon       → channel capacity + entropy → trust as signal-to-noise ratio
  Kahneman      → System 1/2 → fast reflex (ART 1.0) vs slow prediction (ART 2.0)

DITEMPA BUKAN DIBERI — Prediction is forged, not guessed.
"""

from __future__ import annotations
import math
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("arifosmcp.art_predict")

# ═══════════════════════════════════════════════════════════════════════
# BLAST QUANTIZATION — string enum → numerical weight
# ═══════════════════════════════════════════════════════════════════════
# The weights follow a geometric progression (×3 per tier):
#   LOW=1, MEDIUM=3, HIGH=9, INFRASTRUCTURE=27, CIVILIZATIONAL=81

BLAST_WEIGHTS: dict[str, float] = {
    "none": 0.0,
    "low": 1.0,
    "local": 1.0,
    "medium": 3.0,
    "system": 3.0,
    "high": 9.0,
    "infrastructure": 27.0,
    "civilizational": 81.0,
    "unknown": 3.0,  # default to medium as conservative
}

BLAST_LABELS: dict[str, str] = {
    "0.0": "none",
    "1.0": "low",
    "3.0": "medium",
    "9.0": "high",
    "27.0": "infrastructure",
    "81.0": "civilizational",
}


def quantize_blast(blast_str: str) -> float:
    """Convert blast radius string to numerical weight.

    Used by ART 2.0 to compute risk-adjusted trust thresholds.
    A tool with HIGH blast (weight=9) needs higher trust to proceed
    than a tool with LOW blast (weight=1).
    """
    return BLAST_WEIGHTS.get(blast_str.lower(), 3.0)


def dequantize_blast(weight: float) -> str:
    """Convert numerical weight back to label."""
    closest = min(BLAST_LABELS.keys(), key=lambda k: abs(float(k) - weight))
    return BLAST_LABELS[closest]


# ═══════════════════════════════════════════════════════════════════════
# TRUST BANDS — not binary, continuous
# ═══════════════════════════════════════════════════════════════════════


class TrustBand(str, Enum):
    """Continuous trust expressed as discrete bands for ACT pattern selection."""

    TRUST_HIGH = "trust_high"  # [0.80, 1.00] — full autonomy
    TRUST_MEDIUM = "trust_medium"  # [0.50, 0.80) — canary recommended
    TRUST_LOW = "trust_low"  # [0.20, 0.50) — strict gating required
    TRUST_CRITICAL = "trust_critical"  # [0.00, 0.20) — human required


def classify_trust_band(trust_score: float) -> TrustBand:
    """Map a continuous trust score to a band."""
    if trust_score >= 0.80:
        return TrustBand.TRUST_HIGH
    elif trust_score >= 0.50:
        return TrustBand.TRUST_MEDIUM
    elif trust_score >= 0.20:
        return TrustBand.TRUST_LOW
    else:
        return TrustBand.TRUST_CRITICAL


# ═══════════════════════════════════════════════════════════════════════
# TRUST DECAY CURVE — exponential forgetting
# ═══════════════════════════════════════════════════════════════════════
# trust(t) = trust_0 * e^(-λ * t)
# Where:
#   trust_0   = initial trust (1.0 for new tools, lower for observed)
#   λ         = decay constant = failure_rate * blast_weight * base_decay
#   t         = days since last successful use
#
# Ebbinghaus grounding: memory decays exponentially. So does tool trust.
# A tool not used for 90 days should have significantly lower trust.

BASE_DECAY_RATE: float = 0.01  # 1% per day baseline decay


def compute_trust_decay(
    initial_trust: float = 1.0,
    days_elapsed: int = 0,
    failure_rate: float = 0.0,
    blast_weight: float = 1.0,
) -> float:
    """Compute exponential trust decay.

    Args:
        initial_trust: Starting trust (1.0 = brand new tool)
        days_elapsed: Days since last successful use
        failure_rate: Historical failure rate [0.0, 1.0]
        blast_weight: Quantized blast weight (1, 3, 9, 27, 81)

    Returns:
        Current trust score [0.0, 1.0]
    """
    # Decay constant: higher failure rate + higher blast = faster decay
    decay_lambda = (
        BASE_DECAY_RATE * (1.0 + failure_rate * 10.0) * (1.0 + math.log2(blast_weight + 1) * 0.1)
    )

    # Exponential decay
    trust = initial_trust * math.exp(-decay_lambda * days_elapsed)

    # Clamp to [0.0, 1.0]
    return max(0.0, min(1.0, trust))


def compute_trust_from_signals(
    failure_rate: float,
    drift_count: int,
    days_since_use: int,
    blast_weight: float,
    recent_successes: int = 0,
    recent_failures: int = 0,
) -> tuple[float, TrustBand]:
    """Compute composite trust score from multiple signals.

    Combines:
      1. Failure rate penalty
      2. Drift penalty (schema/permission changes)
      3. Staleness penalty (Ebbinghaus decay)
      4. Blast-adjusted threshold
      5. Recent trajectory (successes vs failures in last 10 calls)

    Returns:
        (trust_score, trust_band)
    """
    # Base trust starts at 1.0
    trust = 1.0

    # 1. Failure rate penalty (exponential)
    if failure_rate > 0:
        trust *= math.exp(-failure_rate * 5.0)  # 50% failure → ~8% trust

    # 2. Drift penalty
    if drift_count > 0:
        trust *= math.exp(-drift_count * 0.5)  # each drift costs ~40%

    # 3. Staleness penalty (Ebbinghaus)
    if days_since_use > 0:
        decay_lambda = (
            BASE_DECAY_RATE
            * (1.0 + failure_rate * 10.0)
            * (1.0 + math.log2(blast_weight + 1) * 0.1)
        )
        trust *= math.exp(-decay_lambda * days_since_use)

    # 4. Recent trajectory boost/penalty
    total_recent = recent_successes + recent_failures
    if total_recent > 0:
        recent_ratio = recent_successes / total_recent
        trust *= 0.5 + recent_ratio * 0.5

    # Clamp
    trust = max(0.0, min(1.0, trust))

    return trust, classify_trust_band(trust)


# ═══════════════════════════════════════════════════════════════════════
# PREDICTIVE FAILURE — forecast before it happens
# ═══════════════════════════════════════════════════════════════════════


class FailureRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


def predict_failure(
    failure_rate: float,
    drift_count: int,
    days_since_use: int,
    blast_weight: float = 1.0,
    recent_failure_trend: float = 0.0,  # 0=stable, 1=increasing, -1=decreasing
) -> tuple[FailureRisk, float]:
    """Predict if a tool is likely to fail on next use.

    Returns:
        (risk_level, confidence) — confidence in [0.0, 1.0]
    """
    # Base risk from failure rate
    risk = failure_rate

    # Drift increases risk (each drift = schema changed = likely to fail)
    risk += drift_count * 0.1

    # Staleness increases risk (tool may have changed while unused)
    if days_since_use > 30:
        risk += 0.1
    if days_since_use > 90:
        risk += 0.2

    # Blast weight amplifies risk perception (not actual failure probability,
    # but the consequence-weighted risk)
    blast_factor = math.log2(blast_weight + 1) * 0.05

    # Recent trend: increasing failures → higher risk
    if recent_failure_trend > 0:
        risk += 0.1 * recent_failure_trend

    # Clamp
    risk = max(0.0, min(1.0, risk))

    # Classify
    if risk < 0.2:
        return FailureRisk.LOW, (1.0 - risk)
    elif risk < 0.4:
        return FailureRisk.MEDIUM, (1.0 - risk)
    elif risk < 0.7:
        return FailureRisk.HIGH, (1.0 - risk)
    else:
        return FailureRisk.CRITICAL, (1.0 - risk)


# ═══════════════════════════════════════════════════════════════════════
# TOOL Q-TABLE — learned optimal tool selection
# ═══════════════════════════════════════════════════════════════════════
# Q(tool, task_class) → expected_success_rate
#
# Updated by:
#   - Successful tool calls → Q increases
#   - Failed tool calls → Q decreases
#   - Human HOLD overrides → Q decreases (human distrust is a signal)
#   - Human SEAL overrides of ART HOLD → Q increases (tool was vindicated)


@dataclass
class QEntry:
    """One entry in the tool Q-table."""

    tool_name: str
    task_class: str
    expected_success_rate: float  # [0.0, 1.0]
    sample_count: int = 0  # how many observations
    last_updated: str = ""  # ISO timestamp


class ToolQTable:
    """Learned tool selection table.

    Q(tool, task_class) → expected_success_rate [0.0, 1.0]

    Usage:
        qtable = ToolQTable()
        qtable.update("mcp_github_search_repos", "search", success=True)
        q = qtable.query("mcp_github_search_repos", "search")
        # → 0.95 (if 19/20 succeeded)
    """

    def __init__(self) -> None:
        self._entries: dict[tuple[str, str], QEntry] = {}

    def query(self, tool_name: str, task_class: str = "default") -> float:
        """Get expected success rate for a tool+task combination.

        Returns 0.5 (unknown) if no data yet — conservative for new tools.
        """
        entry = self._entries.get((tool_name, task_class))
        if entry is None:
            return 0.5  # unknown tool → 50% (conservative)
        return entry.expected_success_rate

    def update(
        self,
        tool_name: str,
        task_class: str,
        success: bool,
        human_override: bool = False,
    ) -> None:
        """Update Q-value after a tool call outcome.

        Uses exponential moving average:
            Q_new = Q_old + α * (reward - Q_old)

        Where:
            α = learning rate (1/sample_count for first 20, then 0.05)
            reward = 1.0 for success, 0.0 for failure
            human_override = -0.2 if human rejected a successful call
        """
        from datetime import datetime, timezone

        key = (tool_name, task_class)
        entry = self._entries.get(key)

        if entry is None:
            # First observation
            self._entries[key] = QEntry(
                tool_name=tool_name,
                task_class=task_class,
                expected_success_rate=1.0 if success else 0.0,
                sample_count=1,
                last_updated=datetime.now(timezone.utc).isoformat(),
            )
            return

        # Learning rate: adaptive
        alpha = 1.0 / min(entry.sample_count + 1, 20) if entry.sample_count < 20 else 0.05

        # Reward
        reward = 1.0 if success else 0.0
        if human_override:
            reward -= 0.2  # human distrust is a negative signal

        # Update
        entry.expected_success_rate = entry.expected_success_rate + alpha * (
            reward - entry.expected_success_rate
        )
        entry.sample_count += 1
        entry.last_updated = datetime.now(timezone.utc).isoformat()

    def top_k(self, task_class: str, k: int = 3) -> list[tuple[str, float]]:
        """Get top-K tools for a task class by Q-value."""
        candidates = [
            (tool, entry.expected_success_rate)
            for (tool, tc), entry in self._entries.items()
            if tc == task_class
        ]
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[:k]

    def suggest_act_pattern(self, tool_name: str, task_class: str) -> str | None:
        """Suggest which ACT pattern to use based on Q-value.

        Returns:
            "default_deploy" if Q >= 0.8
            "dangerous_migration" if Q >= 0.5
            "human_in_loop" if Q < 0.5
            None if no data
        """
        q = self.query(tool_name, task_class)
        if q == 0.5:
            return None  # no data
        if q >= 0.8:
            return "default_deploy"
        elif q >= 0.5:
            return "dangerous_migration"
        else:
            return "human_in_loop_change"

    def count(self) -> int:
        return len(self._entries)

    def entries(self) -> list[QEntry]:
        return list(self._entries.values())


# ═══════════════════════════════════════════════════════════════════════
# INTEGRATION: update ART's _suggest_transition to use predictive signals
# ═══════════════════════════════════════════════════════════════════════
# Called from art.py after the reflex verdict.
# Returns recommended ACT pattern and predictive risk assessment.


@dataclass
class ArtPredictiveResult:
    """Predictive extension to ART's reflex verdict."""

    trust_score: float
    trust_band: TrustBand
    failure_risk: FailureRisk
    risk_confidence: float
    recommended_pattern: str | None
    blast_weight: float


def get_predictive_assessment(
    tool_name: str,
    action_class: str,
    failure_rate: float,
    drift_count: int,
    days_since_use: int,
    blast_str: str,
    recent_successes: int = 0,
    recent_failures: int = 0,
    qtable: ToolQTable | None = None,
) -> ArtPredictiveResult:
    """Compute the full ART 2.0 predictive assessment.

    Called after ART 1.0 reflex verdict. Provides:
      - Continuous trust score + band
      - Predicted failure risk
      - Recommended ACT pattern from Q-table
      - Quantized blast weight
    """
    blast_weight = quantize_blast(blast_str)

    # Compute trust from all signals
    trust_score, trust_band = compute_trust_from_signals(
        failure_rate=failure_rate,
        drift_count=drift_count,
        days_since_use=days_since_use,
        blast_weight=blast_weight,
        recent_successes=recent_successes,
        recent_failures=recent_failures,
    )

    # Predict failure risk
    risk, confidence = predict_failure(
        failure_rate=failure_rate,
        drift_count=drift_count,
        days_since_use=days_since_use,
        blast_weight=blast_weight,
    )

    # Query Q-table for pattern suggestion
    recommended = None
    if qtable is not None:
        recommended = qtable.suggest_act_pattern(tool_name, action_class)

    return ArtPredictiveResult(
        trust_score=trust_score,
        trust_band=trust_band,
        failure_risk=risk,
        risk_confidence=confidence,
        recommended_pattern=recommended,
        blast_weight=blast_weight,
    )

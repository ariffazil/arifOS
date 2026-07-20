"""
arifosmcp/runtime/qdf.py — Quantum Decision Field (Born-Rule QDF)

Forged: 2026-07-15
Purpose: QDF computation with Born-rule amplitudes for ATP gate.
Floor alignment: F2 TRUTH (epistemic labeling), F4 CLARITY (ΔS ≤ 0),
                 F7 HUMILITY (uncertainty acknowledged), F13 SOVEREIGN (collapse governed).

QDF = f(epistemic_label, confidence_band, witness_position, blast_radius)

Born-rule compliance:
  - Confidence in outcome X = |⟨X|ψ⟩|²
  - Amplitudes are signed (can be negative = interference)
  - Normalization: Σ|α|² = 1
  - Phase matters (constructive/destructive interference)

Target: QDF ≥ 0.83 per APEX solver spec.

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Any

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_QDF_THRESHOLD = 0.83  # APEX solver spec target
MIN_QDF_THRESHOLD = 0.60  # Phase 1 starting threshold
HOLD_QDF_THRESHOLD = 0.60  # Below this → HOLD
VOID_QDF_THRESHOLD = 0.30  # Below this → VOID


# ═══════════════════════════════════════════════════════════════════════════════
# EPISTEMIC LABELS (F2 TRUTH)
# ═══════════════════════════════════════════════════════════════════════════════


class EpistemicLabel(str, Enum):
    """Epistemic tier of evidence. F2 TRUTH: every claim must be labeled."""

    OBSERVED = "OBSERVED"  # direct measurement
    DERIVED = "DERIVED"  # computed from observations
    INTERPRETED = "INTERPRETED"  # inferred from patterns
    SPECULATED = "SPECULATED"  # hypothesis without strong evidence
    ASSUMED = "ASSUMED"  # taken as given, not verified
    UNKNOWN = "UNKNOWN"  # no information


# Amplitude for each epistemic label (Born-rule: |α|² = probability)
EPISTEMIC_AMPLITUDES: dict[EpistemicLabel, float] = {
    EpistemicLabel.OBSERVED: 1.0,
    EpistemicLabel.DERIVED: 0.9,
    EpistemicLabel.INTERPRETED: 0.7,
    EpistemicLabel.SPECULATED: 0.4,
    EpistemicLabel.ASSUMED: 0.2,
    EpistemicLabel.UNKNOWN: 0.1,
}


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIDENCE BAND (F2 TRUTH + F7 HUMILITY)
# ═══════════════════════════════════════════════════════════════════════════════


class ConfidenceBand(str, Enum):
    """Confidence level of evidence. F7 HUMILITY: acknowledge uncertainty."""

    VERIFIED = "VERIFIED"  # independently confirmed
    HIGH = "HIGH"  # strong evidence, minor gaps
    MODERATE = "MODERATE"  # reasonable evidence, some uncertainty
    LOW = "LOW"  # weak evidence, significant gaps
    UNKNOWN = "UNKNOWN"  # no confidence data


CONFIDENCE_AMPLITUDES: dict[ConfidenceBand, float] = {
    ConfidenceBand.VERIFIED: 1.0,
    ConfidenceBand.HIGH: 0.85,
    ConfidenceBand.MODERATE: 0.6,
    ConfidenceBand.LOW: 0.3,
    ConfidenceBand.UNKNOWN: 0.1,
}


# ═══════════════════════════════════════════════════════════════════════════════
# WITNESS POSITION (F3 WITNESS)
# ═══════════════════════════════════════════════════════════════════════════════


class WitnessPosition(str, Enum):
    """Positional witness taxonomy. F3 WITNESS: who is attesting."""

    HUMAN = "HUMAN"  # sovereign human attested
    EXTERNAL = "EXTERNAL"  # outside the federation
    INTERNAL = "INTERNAL"  # inside federation, different organ
    SELF = "SELF"  # same agent attesting to itself


# Penalty for witness position (self-attestation is least reliable)
WITNESS_PENALTIES: dict[WitnessPosition, float] = {
    WitnessPosition.HUMAN: 0.0,
    WitnessPosition.EXTERNAL: -0.05,
    WitnessPosition.INTERNAL: -0.10,
    WitnessPosition.SELF: -0.20,
}


# ═══════════════════════════════════════════════════════════════════════════════
# BLAST RADIUS (F1 AMANAH)
# ═══════════════════════════════════════════════════════════════════════════════


class BlastRadius(str, Enum):
    """Blast radius of the action. F1 AMANAH: reversible-first."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    IRREVERSIBLE = "irreversible"


BLAST_MODIFIERS: dict[BlastRadius, float] = {
    BlastRadius.LOW: 1.0,
    BlastRadius.MEDIUM: 0.9,
    BlastRadius.HIGH: 0.8,
    BlastRadius.IRREVERSIBLE: 0.7,
}


# ═══════════════════════════════════════════════════════════════════════════════
# BORN-RULE AMPLITUDE VECTOR
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class AmplitudeVector:
    """
    Born-rule compliant amplitude vector.
    |ψ⟩ = α_obs|O⟩ + α_der|D⟩ + α_int|I⟩ + α_spec|S⟩ + α_ass|A⟩ + α_unk|U⟩

    Normalization: Σ|α|² = 1
    Phase: each amplitude can be positive (constructive) or negative (destructive)
    """

    observed: float = 0.0
    derived: float = 0.0
    interpreted: float = 0.0
    speculated: float = 0.0
    assumed: float = 0.0
    unknown: float = 0.0

    def normalize(self) -> AmplitudeVector:
        """Normalize so Σ|α|² = 1. Born-rule compliance."""
        norm = math.sqrt(
            self.observed**2
            + self.derived**2
            + self.interpreted**2
            + self.speculated**2
            + self.assumed**2
            + self.unknown**2
        )
        if norm < 1e-10:
            # All zeros → equal superposition (maximum uncertainty)
            n = math.sqrt(1.0 / 6.0)
            return AmplitudeVector(n, n, n, n, n, n)
        return AmplitudeVector(
            self.observed / norm,
            self.derived / norm,
            self.interpreted / norm,
            self.speculated / norm,
            self.assumed / norm,
            self.unknown / norm,
        )

    def probability(self, label: EpistemicLabel) -> float:
        """Born rule: P(x) = |⟨x|ψ⟩|²"""
        amp = getattr(self, label.value.lower(), 0.0)
        return amp**2

    def total_probability(self) -> float:
        """Should be 1.0 after normalization."""
        return (
            self.observed**2
            + self.derived**2
            + self.interpreted**2
            + self.speculated**2
            + self.assumed**2
            + self.unknown**2
        )

    def dominant_label(self) -> EpistemicLabel:
        """Which epistemic label has the highest amplitude?"""
        amps = {
            EpistemicLabel.OBSERVED: abs(self.observed),
            EpistemicLabel.DERIVED: abs(self.derived),
            EpistemicLabel.INTERPRETED: abs(self.interpreted),
            EpistemicLabel.SPECULATED: abs(self.speculated),
            EpistemicLabel.ASSUMED: abs(self.assumed),
            EpistemicLabel.UNKNOWN: abs(self.unknown),
        }
        return max(amps, key=amps.get)  # type: ignore[arg-type]

    def interference_score(self) -> float:
        """
        Interference between epistemic labels.
        Positive = constructive (corroborating evidence).
        Negative = destructive (contradicting evidence).
        """
        # Sum of signed amplitudes (not squared)
        return (
            self.observed
            + self.derived
            + self.interpreted
            + self.speculated
            + self.assumed
            + self.unknown
        )


def build_amplitude_vector(
    epistemic_label: EpistemicLabel | str = EpistemicLabel.UNKNOWN,
    confidence_band: ConfidenceBand | str = ConfidenceBand.UNKNOWN,
) -> AmplitudeVector:
    """
    Build an amplitude vector from epistemic label and confidence band.

    The dominant amplitude is set by the epistemic label.
    Confidence modulates the spread across other labels.
    """
    if isinstance(epistemic_label, str):
        epistemic_label = EpistemicLabel(epistemic_label)
    if isinstance(confidence_band, str):
        confidence_band = ConfidenceBand(confidence_band)

    base_amp = EPISTEMIC_AMPLITUDES[epistemic_label]
    conf_amp = CONFIDENCE_AMPLITUDES[confidence_band]

    # Dominant label gets base_amp * conf_amp
    dominant = base_amp * conf_amp

    # Other labels get residual spread (lower = more uncertain)
    residual = (1.0 - dominant) / 5.0  # distribute among 5 other labels

    vec = AmplitudeVector(
        observed=dominant if epistemic_label == EpistemicLabel.OBSERVED else residual,
        derived=dominant if epistemic_label == EpistemicLabel.DERIVED else residual,
        interpreted=dominant if epistemic_label == EpistemicLabel.INTERPRETED else residual,
        speculated=dominant if epistemic_label == EpistemicLabel.SPECULATED else residual,
        assumed=dominant if epistemic_label == EpistemicLabel.ASSUMED else residual,
        unknown=dominant if epistemic_label == EpistemicLabel.UNKNOWN else residual,
    )

    return vec.normalize()


# ═══════════════════════════════════════════════════════════════════════════════
# QDF COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class QDFResult:
    """Result of QDF computation."""

    qdf: float  # final QDF score [0, 1]
    amplitude_vector: AmplitudeVector  # Born-rule amplitudes
    epistemic_contribution: float  # epistemic label factor
    confidence_contribution: float  # confidence band factor
    witness_contribution: float  # witness position factor
    blast_contribution: float  # blast radius factor
    interference: float  # constructive/destructive
    threshold_met: bool  # qdf >= threshold
    verdict: str  # PROCEED / HOLD / VOID

    def to_dict(self) -> dict[str, Any]:
        return {
            "qdf": round(self.qdf, 4),
            "amplitude_vector": {
                "observed": round(self.amplitude_vector.observed, 4),
                "derived": round(self.amplitude_vector.derived, 4),
                "interpreted": round(self.amplitude_vector.interpreted, 4),
                "speculated": round(self.amplitude_vector.speculated, 4),
                "assumed": round(self.amplitude_vector.assumed, 4),
                "unknown": round(self.amplitude_vector.unknown, 4),
                "normalization": round(self.amplitude_vector.total_probability(), 4),
                "dominant_label": self.amplitude_vector.dominant_label().value,
                "interference_score": round(self.amplitude_vector.interference_score(), 4),
            },
            "contributions": {
                "epistemic": round(self.epistemic_contribution, 4),
                "confidence": round(self.confidence_contribution, 4),
                "witness": round(self.witness_contribution, 4),
                "blast": round(self.blast_contribution, 4),
            },
            "interference": round(self.interference, 4),
            "threshold_met": self.threshold_met,
            "verdict": self.verdict,
        }


def compute_qdf(
    epistemic_label: EpistemicLabel | str = EpistemicLabel.UNKNOWN,
    confidence_band: ConfidenceBand | str = ConfidenceBand.UNKNOWN,
    witness_position: WitnessPosition | str = WitnessPosition.SELF,
    blast_radius: BlastRadius | str = BlastRadius.LOW,
    threshold: float = DEFAULT_QDF_THRESHOLD,
) -> QDFResult:
    """
    Compute QDF (Quantum Decision Field) score.

    QDF = epistemic × confidence × (1 + witness_penalty) × blast_modifier × interference_factor

    Born-rule compliance:
      - Amplitude vector built from epistemic + confidence
      - Interference score from signed amplitudes
      - Final QDF is |⟨PROCEED|ψ⟩|²

    Floor alignment:
      F2 TRUTH: epistemic labeling enforced
      F4 CLARITY: ΔS ≤ 0 (structured output)
      F7 HUMILITY: uncertainty acknowledged (UNKNOWN amplitude > 0)
      F13 SOVEREIGN: collapse governed (verdict returned, not executed)
    """
    # Normalize inputs
    if isinstance(epistemic_label, str):
        epistemic_label = EpistemicLabel(epistemic_label)
    if isinstance(confidence_band, str):
        confidence_band = ConfidenceBand(confidence_band)
    if isinstance(witness_position, str):
        witness_position = WitnessPosition(witness_position)
    if isinstance(blast_radius, str):
        blast_radius = BlastRadius(blast_radius)

    # Build amplitude vector (Born-rule)
    amp_vec = build_amplitude_vector(epistemic_label, confidence_band)

    # Individual contributions
    epistemic_contrib = EPISTEMIC_AMPLITUDES[epistemic_label]
    confidence_contrib = CONFIDENCE_AMPLITUDES[confidence_band]
    witness_contrib = 1.0 + WITNESS_PENALTIES[witness_position]  # [0.80, 1.0]
    blast_contrib = BLAST_MODIFIERS[blast_radius]  # [0.70, 1.0]

    # Interference factor from amplitude vector
    # Normalize to [0.5, 1.5] range (destructive → constructive)
    raw_interference = amp_vec.interference_score()
    interference_factor = 0.5 + max(0.0, min(raw_interference, 1.0))

    # QDF = product of all factors
    qdf = (
        epistemic_contrib
        * confidence_contrib
        * witness_contrib
        * blast_contrib
        * interference_factor
    )

    # Clamp to [0, 1]
    qdf = max(0.0, min(1.0, qdf))

    # Determine verdict
    if qdf >= threshold:
        verdict = "PROCEED"
    elif qdf >= HOLD_QDF_THRESHOLD:
        verdict = "HOLD"
    elif qdf >= VOID_QDF_THRESHOLD:
        verdict = "HOLD"
    else:
        verdict = "VOID"

    return QDFResult(
        qdf=qdf,
        amplitude_vector=amp_vec,
        epistemic_contribution=epistemic_contrib,
        confidence_contribution=confidence_contrib,
        witness_contribution=witness_contrib,
        blast_contribution=blast_contrib,
        interference=interference_factor,
        threshold_met=qdf >= threshold,
        verdict=verdict,
    )


def born_confidence(
    amplitude_vector: AmplitudeVector,
    target_label: EpistemicLabel | str = EpistemicLabel.OBSERVED,
) -> float:
    """
    Born-rule confidence: P(x) = |⟨x|ψ⟩|²

    ZEN-4: Replace scalar confidence with amplitude vector.
    Returns probability of target label given the amplitude vector.
    """
    if isinstance(target_label, str):
        target_label = EpistemicLabel(target_label)
    return amplitude_vector.probability(target_label)


def interference_check(
    vec_a: AmplitudeVector,
    vec_b: AmplitudeVector,
) -> float:
    """
    Check interference between two amplitude vectors.
    Positive = constructive (corroborating).
    Negative = destructive (contradicting).
    """
    return (
        vec_a.observed * vec_b.observed
        + vec_a.derived * vec_b.derived
        + vec_a.interpreted * vec_b.interpreted
        + vec_a.speculated * vec_b.speculated
        + vec_a.assumed * vec_b.assumed
        + vec_a.unknown * vec_b.unknown
    )

"""
arifosmcp/runtime/truth_kernel.py — Constitutional Truth Kernel
═══════════════════════════════════════════════════════════════════════════════
Forged 2026-07-14 · F13 SOVEREIGN RATIFIED

PURPOSE
-------
Compute epistemic warrant honestly without conflating it with truth, sealing,
authority, or physical entropy. The kernel can never possess truth; it can
only estimate how strongly the available evidence justifies believing a claim,
under declared assumptions.

CORE INVARIANTS (T1-T13 from the constitutional amendment)
---------------------------------------------------------
T1  Reality precedes language — no seal overrides direct reality.
T2  Confidence is not truth — every probability exposes its model + assumptions.
T3  Measurement requires uncertainty — instrument, units, time, uncertainty.
T4  Provenance is mandatory — no high epistemic state without retrievable lineage.
T5  Witnesses must be independent — source count ≠ witness diversity.
T6  Contradictions survive — minority evidence and unresolved conflict preserved.
T7  Falsifiers are declared — no CORROBORATED without a possible disconfirming
    observation.
T8  Time is explicit — dynamic claims decay unless refreshed.
T9  Normative claims expose their frame — "good", "fair", "safe" require
    declared values + affected humans.
T10 Seal preserves, never sanctifies — immutable falsehood remains falsehood.
T11 Truth does not self-authorize — W(C) ⊄ A(a). Evidence ≠ permission.
T12 Thermodynamics stays physical — Landauer checks only grounded physical
    erasure telemetry; semantic uncertainty ≠ physical bit erasure.
T13 Corrections append history — correction supersedes claim but never silently
    deletes the previous state.

FOUR QUANTITIES THE KERNEL NEVER COLLAPSES
------------------------------------------
  1. Ontic truth       T(C,R) ∈ {0, 1}   — correspondence with reality (kernel
                                              normally cannot observe directly).
  2. Epistemic warrant W(C|E,M,A,t) ∈ [0,1] — what the kernel CAN estimate.
  3. Meaning           M(C|S,V,H,K)       — why this truth matters, to whom,
                                              over what horizon.
  4. Authority         A(a|S,delegation,risk,reversibility) — whether action a
                                              is permitted (orthogonal to W).

THE PHYSICAL MEMBRANE
---------------------
  R (reality) → Y (observation) → E (structured evidence)
              → B (belief state) → M (meaning)   → a (action)

Every arrow can distort reality. Governance belongs at the arrows.

DITEMPA BUKAN DIBERI — Reality determines truth. The machine estimates warrant.
The human anchors meaning. Authority governs action. VAULT remembers what
happened.
"""

from __future__ import annotations

import logging
import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

logger = logging.getLogger("arifosmcp.truth_kernel")

__all__ = [
    "ClaimKind",
    "RecordState",
    "AuthorityState",
    "EpistemicState",
    "Claim",
    "Evidence",
    "Assessment",
    "ResourceTelemetry",
    "PhysicalErasureCheck",
    "TruthEngine",
    "check_physical_erasure_bound",
    "legacy_truth_vector",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Enumerations
# ═══════════════════════════════════════════════════════════════════════════════


class ClaimKind(str, Enum):
    """What KIND of claim is this? Math truth ≠ physical truth ≠ forecast."""

    FORMAL_AXIOMATIC = "formal_axiomatic"  # true relative to declared axioms + derivation
    DEFINITIONAL = "definitional"  # true under an explicit convention
    EMPIRICAL_STABLE = "empirical_stable"  # physically measured, slow-changing
    EMPIRICAL_DYNAMIC = "empirical_dynamic"  # current-state claim requiring fresh evidence
    CAUSAL_HYPOTHESIS = "causal_hypothesis"  # explanatory claim requiring causal design
    FORECAST = "forecast"  # probabilistic future claim
    NORMATIVE = "normative"  # evaluated under a moral/constitutional frame
    AMBIGUOUS = "ambiguous"  # not sufficiently defined


class RecordState(str, Enum):
    """Where is this record in its lifecycle?"""

    TRANSIENT = "transient"  # not yet recorded
    ATTESTED = "attested"  # evidence chain recorded
    RATIFIED = "ratified"  # constitutional review passed
    SEALED = "sealed"  # irreversible append to VAULT999


class AuthorityState(str, Enum):
    """What is the agent permitted to DO with this claim?

    Note: orthogonal to epistemic state. A high-warrant claim may still
    require F13 human authority. A low-warrant claim may still be
    observable.
    """

    OBSERVE = "observe"
    ADVISE = "advise"
    REVERSIBLE_EXECUTE = "reversible_execute"
    REQUIRE_F13 = "require_f13"
    FORBIDDEN = "forbidden"


class EpistemicState(str, Enum):
    """What does the evidence currently justify believing?

    Replaces one-dimensional "truth level". SEALS DO NOT PROMOTE THIS.
    """

    UNKNOWN = "unknown"
    HYPOTHESIS = "hypothesis"
    SUPPORTED = "supported"
    CORROBORATED = "corroborated"
    VERIFIED_MEASUREMENT = "verified_measurement"
    CONTESTED = "contested"
    FALSIFIED = "falsified"
    STALE = "stale"
    AMBIGUOUS = "ambiguous"  # T9 — claim kind or frame not well-defined


# ═══════════════════════════════════════════════════════════════════════════════
# Domain objects
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Claim:
    """A claim subject to epistemic assessment.

    Attributes:
        claim_id: Stable identifier (e.g. "petronas-dividend-constraint").
        text: Human-readable statement of the claim.
        kind: One of ClaimKind. Determines the path through the engine.
        prior_probability: P(H) in [0, 1]. Defaults to 0.5.
        falsifiers: Tuple of disconfirming observations that would count
            against the claim. T7 — no CORROBORATED without falsifiers.
        declared_frame: For NORMATIVE claims, the moral/constitutional
            frame used. T9 — required for normative claims.
        affected_humans: For NORMATIVE claims, who bears the consequence.
    """

    claim_id: str
    text: str
    kind: ClaimKind
    prior_probability: float = 0.5
    falsifiers: tuple[str, ...] = ()
    declared_frame: str | None = None
    affected_humans: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not (0.0 <= self.prior_probability <= 1.0):
            raise ValueError(f"prior_probability must be in [0, 1], got {self.prior_probability}")


@dataclass
class Evidence:
    """A single evidence item with discount coefficients and likelihoods.

    The likelihood_if_claim and likelihood_if_not_claim form the natural
    log likelihood ratio that drives Bayesian log-odds updating.
    """

    evidence_id: str
    description: str
    likelihood_if_claim: float  # P(E | H)
    likelihood_if_not_claim: float  # P(E | ¬H)
    source_quality: float = 1.0  # Q  ∈ [0, 1]
    independence: float = 1.0  # I  ∈ [0, 1]
    reproducibility: float = 1.0  # R  ∈ [0, 1]
    calibration: float = 1.0  # K  ∈ [0, 1]
    freshness: float = 1.0  # Z  ∈ [0, 1] (1 = fresh, 0 = totally stale)
    lineage_group: str | None = None  # for independence clustering
    provenance_uri: str | None = None  # for T4 auditability


@dataclass
class ResourceTelemetry:
    """Physical compute / erasure telemetry for the Landauer check.

    All fields optional. When missing, the physical check returns UNMEASURED —
    it never VOIDs a claim. T12 — thermodynamics stays physical.
    """

    actual_joules: float | None = None
    bits_erased: int | None = None
    temperature_kelvin: float | None = None
    hardware_source: str | None = None
    measurement_uncertainty: float | None = None


@dataclass
class PhysicalErasureCheck:
    """Result of a Landauer check.

    status ∈ {"WITHIN_BOUND", "ABOVE_BOUND", "UNMEASURED", "INSUFFICIENT_DATA"}.
    """

    status: str
    actual_joules: float | None = None
    minimum_joules: float | None = None
    temperature_kelvin: float | None = None
    bits_erased: int | None = None
    note: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# Assessment — what the kernel CAN estimate (epistemic warrant, not truth)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Assessment:
    """Constitutional assessment of a claim.

    Fields map 1-to-1 to the kernel's 10-vector:
      T = [p, H_epistemic, IG, C_conflict, N_eff, Q, R, K, F, P_v, Z]
    plus derived scalars (warrant, state, record_state, authority_state).
    """

    claim_id: str
    claim_kind: ClaimKind

    # Scalar — for routing decisions
    warrant: float  # W ∈ [0, 1]
    posterior_probability: float  # P(H | E)
    epistemic_state: EpistemicState  # discrete state

    # Vector — for truth-seeking and audit
    prior_probability: float  # p
    posterior_log_odds: float  # L
    epistemic_entropy_bits: float  # H_epistemic
    information_gain_bits: float  # IG
    contradiction_index: float  # C_conflict ∈ [0, 1]
    effective_witness_count: float  # N_eff
    source_quality_mean: float  # Q
    reproducibility_mean: float  # R
    calibration_mean: float  # K
    falsifiability: float  # F ∈ [0, 1]
    provenance_completeness: float  # P_v
    freshness_factor: float  # Z

    # Record & authority — orthogonal to epistemic state
    record_state: RecordState
    authority_state: AuthorityState

    # Constitutional assertions
    sealed_does_not_imply_true: bool = True  # T10 invariant
    truth_does_not_self_authorize: bool = True  # T11 invariant

    # Audit trail
    evidence_count: int = 0
    evidence_ids: list[str] = field(default_factory=list)
    lineage_groups: list[str] = field(default_factory=list)
    falsifiers: tuple[str, ...] = ()
    assessment_timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "claim_id": self.claim_id,
            "claim_kind": self.claim_kind.value,
            "warrant": self.warrant,
            "posterior_probability": self.posterior_probability,
            "epistemic_state": self.epistemic_state.value,
            "prior_probability": self.prior_probability,
            "posterior_log_odds": self.posterior_log_odds,
            "epistemic_entropy_bits": self.epistemic_entropy_bits,
            "information_gain_bits": self.information_gain_bits,
            "contradiction_index": self.contradiction_index,
            "effective_witness_count": self.effective_witness_count,
            "source_quality_mean": self.source_quality_mean,
            "reproducibility_mean": self.reproducibility_mean,
            "calibration_mean": self.calibration_mean,
            "falsifiability": self.falsifiability,
            "provenance_completeness": self.provenance_completeness,
            "freshness_factor": self.freshness_factor,
            "record_state": self.record_state.value,
            "authority_state": self.authority_state.value,
            "sealed_does_not_imply_true": self.sealed_does_not_imply_true,
            "truth_does_not_self_authorize": self.truth_does_not_self_authorize,
            "evidence_count": self.evidence_count,
            "evidence_ids": list(self.evidence_ids),
            "lineage_groups": list(self.lineage_groups),
            "falsifiers": list(self.falsifiers),
            "assessment_timestamp": self.assessment_timestamp,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Math utilities — pure, no I/O
# ═══════════════════════════════════════════════════════════════════════════════


def _safe_log(x: float) -> float:
    if x <= 0.0:
        return float("-inf")
    return math.log(x)


def _clip01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _entropy_bits(prob: float) -> float:
    """Binary entropy of a Bernoulli(prob)."""
    if prob <= 0.0 or prob >= 1.0:
        return 0.0
    return -(prob * math.log2(prob) + (1.0 - prob) * math.log2(1.0 - prob))


def _logistic(x: float) -> float:
    """Numerically stable sigmoid."""
    if x >= 0.0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


# ═══════════════════════════════════════════════════════════════════════════════
# Physical erasure check (Landauer) — T12
# ═══════════════════════════════════════════════════════════════════════════════

KB = 1.380649e-23  # Boltzmann constant (J/K)
LN2 = math.log(2.0)


def check_physical_erasure_bound(telemetry: ResourceTelemetry) -> dict[str, Any]:
    """Check whether observed physical erasure meets the Landauer bound.

    Domain: PHYSICAL erasure of physically represented information at a
    measured temperature. NOT semantic uncertainty reduction, NOT compute
    cost, NOT 'clarity gained'.

    Returns a dict with status ∈ {WITHIN_BOUND, ABOVE_BOUND, UNMEASURED,
    INSUFFICIENT_DATA}. Never VOID. The kernel must never claim
    'hallucination' from a missing physical measurement.
    """
    result: dict[str, Any] = {
        "status": "UNMEASURED",
        "actual_joules": telemetry.actual_joules,
        "minimum_joules": None,
        "temperature_kelvin": telemetry.temperature_kelvin,
        "bits_erased": telemetry.bits_erased,
        "hardware_source": telemetry.hardware_source,
        "note": "",
    }
    if (
        telemetry.actual_joules is None
        or telemetry.bits_erased is None
        or telemetry.temperature_kelvin is None
    ):
        result["status"] = "UNMEASURED"
        result["note"] = (
            "Physical erasure telemetry unavailable. T12: missing measurement "
            "is UNMEASURED, not VOID, not hallucination."
        )
        return result

    if telemetry.bits_erased <= 0 or telemetry.temperature_kelvin <= 0.0:
        result["status"] = "INSUFFICIENT_DATA"
        result["note"] = "bits_erased and temperature_kelvin must be positive."
        return result

    minimum_joules = telemetry.bits_erased * KB * telemetry.temperature_kelvin * LN2
    result["minimum_joules"] = minimum_joules

    if telemetry.actual_joules + 1e-30 < minimum_joules:
        result["status"] = "WITHIN_BOUND"
        result["note"] = (
            f"Observed {telemetry.actual_joules:.3e} J is at or below the "
            f"Landauer lower bound {minimum_joules:.3e} J — possible "
            f"sub-Landauer effect (check measurement noise)."
        )
    else:
        result["status"] = "ABOVE_BOUND"
        result["note"] = (
            f"Observed {telemetry.actual_joules:.3e} J is above the Landauer "
            f"lower bound {minimum_joules:.3e} J — consistent with the principle."
        )
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# TruthEngine — the assessment core
# ═══════════════════════════════════════════════════════════════════════════════


class TruthEngine:
    """Stateless assessor. Pure functions; safe to instantiate per call.

    Computes the 10-vector + scalar warrant for a (claim, evidence) pair.
    Does NOT decide authority. Does NOT sanctify sealed claims.
    """

    def assess(
        self,
        claim: Claim,
        evidence: Sequence[Evidence],
        record_state: RecordState = RecordState.TRANSIENT,
        freshness_override: float | None = None,
    ) -> Assessment:
        """Run the full assessment. Returns an Assessment with the 10-vector.

        Step order:
          1.  Validate inputs
          2.  Effective witness count N_eff (lineage-clustered)
          3.  Per-evidence discounted log-likelihood ratios
          4.  Posterior log-odds and posterior probability
          5.  Epistemic entropy + KL information gain
          6.  Contradiction index C_conflict
          7.  Quality means Q, R, K
          8.  Falsifiability F
          9.  Provenance completeness P_v
          10. Freshness Z
          11. Scalar warrant W = p · (Q·I·R·K·F·P_v·Z)^(1/7)
          12. Epistemic state from vector (with T6 contest priority)
          13. Authority state from record_state + kind
        """
        if not evidence:
            return self._assess_no_evidence(claim, record_state)

        # ── 1. Per-evidence discounted log-likelihood ratio ──────────────
        scores: list[float] = []
        weights: list[float] = []
        groups: list[str | None] = []

        for ev in evidence:
            # T5: discount by source quality, independence, reproducibility,
            # calibration, freshness (combined as α per §4 of the spec).
            # α = sqrt(Q * I * R * K * Z)  — geometric mean keeps the floor
            # high so a single zero in any dimension collapses the discount
            # honestly.
            alpha = math.sqrt(
                max(ev.source_quality, 0.0)
                * max(ev.independence, 0.0)
                * max(ev.reproducibility, 0.0)
                * max(ev.calibration, 0.0)
                * max(ev.freshness, 0.0)
            )
            alpha = _clip01(alpha)

            # Likelihood ratio
            if ev.likelihood_if_not_claim <= 0.0:
                # Evidence impossible under ¬H → strongly supports H
                ln_lambda = 10.0  # cap to avoid inf
            else:
                ln_lambda = _safe_log(ev.likelihood_if_claim) - _safe_log(
                    ev.likelihood_if_not_claim
                )

            s = alpha * ln_lambda
            scores.append(s)
            weights.append(alpha)
            groups.append(ev.lineage_group)

        # ── 2. Effective witness count N_eff (lineage-clustered) ───────
        n_eff = self._effective_witness_count(scores, groups)

        # ── 3. Posterior log-odds ───────────────────────────────────────
        prior = _clip01(claim.prior_probability)
        L_prior = math.log(prior / (1.0 - prior)) if 0.0 < prior < 1.0 else 0.0
        L_posterior = L_prior + sum(scores)
        posterior = _clip01(_logistic(L_posterior))

        # ── 4. Epistemic entropy + KL information gain ────────────────
        h_prior = _entropy_bits(prior)
        h_post = _entropy_bits(posterior)
        ig = max(0.0, h_prior - h_post)

        # ── 5. Contradiction index C_conflict ──────────────────────────
        abs_sum = sum(abs(s) for s in scores)
        if abs_sum == 0.0:
            c_conflict = 0.0
        else:
            c_conflict = _clip01(1.0 - abs(sum(scores)) / abs_sum)

        # ── 6. Quality means ───────────────────────────────────────────
        q_mean = sum(ev.source_quality for ev in evidence) / len(evidence)
        r_mean = sum(ev.reproducibility for ev in evidence) / len(evidence)
        k_mean = sum(ev.calibration for ev in evidence) / len(evidence)

        # ── 7. Falsifiability F ───────────────────────────────────────
        f = self._falsifiability(claim)

        # ── 8. Provenance completeness P_v ────────────────────────────
        p_v = self._provenance_completeness(evidence)

        # ── 9. Freshness Z ─────────────────────────────────────────────
        if freshness_override is not None:
            z = _clip01(freshness_override)
        else:
            z = min(ev.freshness for ev in evidence)

        # ── 10. Scalar warrant W = p · (Q·I·R·K·F·P_v·Z)^(1/7) ────────
        i_mean = sum(ev.independence for ev in evidence) / len(evidence)
        # Use the effective N_eff vs raw count to penalize duplicated witnesses
        independence_factor = min(1.0, n_eff / max(1.0, float(len(evidence))))
        i_eff = _clip01(i_mean * independence_factor)

        if any(x <= 0.0 for x in (q_mean, r_mean, k_mean, f, p_v, z, i_eff)):
            scalar_geo = 0.0
        else:
            scalar_geo = (q_mean * i_eff * r_mean * k_mean * f * p_v * z) ** (1.0 / 7.0)
        warrant = _clip01(prior * scalar_geo)

        # ── 11. Epistemic state from vector ────────────────────────────
        state = self._derive_state(
            claim=claim,
            warrant=warrant,
            posterior=posterior,
            c_conflict=c_conflict,
            f=f,
            p_v=p_v,
            z=z,
        )

        # ── 12. Authority state from record_state + kind ───────────────
        authority = self._derive_authority(claim.kind, record_state)

        return Assessment(
            claim_id=claim.claim_id,
            claim_kind=claim.kind,
            warrant=warrant,
            posterior_probability=posterior,
            epistemic_state=state,
            prior_probability=prior,
            posterior_log_odds=L_posterior,
            epistemic_entropy_bits=h_post,
            information_gain_bits=ig,
            contradiction_index=c_conflict,
            effective_witness_count=n_eff,
            source_quality_mean=q_mean,
            reproducibility_mean=r_mean,
            calibration_mean=k_mean,
            falsifiability=f,
            provenance_completeness=p_v,
            freshness_factor=z,
            record_state=record_state,
            authority_state=authority,
            evidence_count=len(evidence),
            evidence_ids=[ev.evidence_id for ev in evidence],
            lineage_groups=sorted({g for g in groups if g}),
            falsifiers=claim.falsifiers,
        )

    # ── internal helpers ─────────────────────────────────────────────

    def _assess_no_evidence(self, claim: Claim, record_state: RecordState) -> Assessment:
        """No evidence path. Prior only. State forced to HYPOTHESIS."""
        prior = _clip01(claim.prior_probability)
        return Assessment(
            claim_id=claim.claim_id,
            claim_kind=claim.kind,
            warrant=0.0,
            posterior_probability=prior,
            epistemic_state=EpistemicState.HYPOTHESIS,
            prior_probability=prior,
            posterior_log_odds=0.0,
            epistemic_entropy_bits=_entropy_bits(prior),
            information_gain_bits=0.0,
            contradiction_index=0.0,
            effective_witness_count=0.0,
            source_quality_mean=0.0,
            reproducibility_mean=0.0,
            calibration_mean=0.0,
            falsifiability=self._falsifiability(claim),
            provenance_completeness=0.0,
            freshness_factor=1.0,
            record_state=record_state,
            authority_state=self._derive_authority(claim.kind, record_state),
            evidence_count=0,
            evidence_ids=[],
            lineage_groups=[],
            falsifiers=claim.falsifiers,
        )

    @staticmethod
    def _effective_witness_count(scores: Sequence[float], groups: Sequence[str | None]) -> float:
        """T5: source count ≠ witness diversity. Cluster by lineage_group.

        N_eff = (sum w_i)^2 / sum w_i^2  (effective sample size).
        Within each lineage group, only the strongest evidence counts;
        other items in the same group contribute as correlated repeats.
        """
        if not scores:
            return 0.0
        # group weights
        per_group: dict[str, float] = {}
        for s, g in zip(scores, groups):
            w = abs(s)
            key = g or "_ungrouped_"
            if key in per_group:
                # correlated — keep the larger
                if w > per_group[key]:
                    per_group[key] = w
            else:
                per_group[key] = w
        weights = list(per_group.values())
        if not weights:
            return 0.0
        sum_w = sum(weights)
        sum_w2 = sum(w * w for w in weights)
        if sum_w2 == 0.0:
            return 0.0
        return (sum_w * sum_w) / sum_w2

    @staticmethod
    def _falsifiability(claim: Claim) -> float:
        """T7: no falsifiers → confidence cap.

        Returns F ∈ (0, 1]. If no falsifiers declared → F = 0.0 (cannot
        become CORROBORATED). If ≥ 1 falsifier → F = 1.0; if more, we
        scale gently above to recognise that richer disconfirmation
        structure is healthier.
        """
        n = len(claim.falsifiers)
        if n == 0:
            return 0.0
        # Saturating curve
        return _clip01(1.0 - math.exp(-float(n)))

    @staticmethod
    def _provenance_completeness(evidence: Sequence[Evidence]) -> float:
        """P_v = fraction of evidence items that declare a provenance_uri."""
        if not evidence:
            return 0.0
        with_prov = sum(1 for ev in evidence if ev.provenance_uri)
        return with_prov / float(len(evidence))

    @staticmethod
    def _derive_state(
        claim: Claim,
        warrant: float,
        posterior: float,
        c_conflict: float,
        f: float,
        p_v: float,
        z: float,
    ) -> EpistemicState:
        """Derive discrete epistemic state from the 10-vector.

        Priority rules (from §12 of the spec + invariants):
          T6  contradiction > 0.5  → CONTESTED (regardless of warrant)
          T8  freshness = 0         → STALE
          T7  falsifiability = 0    → cap at SUPPORTED (no CORROBORATED)
          T9  NORMATIVE + no frame  → AMBIGUOUS (cannot become VERIFIED)
          T3  no provenance (P_v=0) → cap at SUPPORTED
        """
        # T6: contradiction wins
        if c_conflict > 0.5:
            return EpistemicState.CONTESTED
        # T8: staleness
        if z <= 0.0:
            return EpistemicState.STALE
        # T7: no falsifiers → CAP at SUPPORTED (regardless of warrant value).
        # Without falsifiers the claim cannot be CORROBORATED, but the
        # evidence still exists, so we acknowledge it at SUPPORTED rather
        # than collapsing to UNKNOWN.
        if f <= 0.0:
            if posterior >= 0.5:
                return EpistemicState.SUPPORTED
            return EpistemicState.HYPOTHESIS
        # T9: normative without declared frame
        if claim.kind == ClaimKind.NORMATIVE and not claim.declared_frame:
            return EpistemicState.AMBIGUOUS
        # ambiguous claim kind
        if claim.kind == ClaimKind.AMBIGUOUS:
            return EpistemicState.AMBIGUOUS
        # T3 / T4: no provenance → cap at SUPPORTED
        if p_v <= 0.0 and posterior >= 0.5:
            return EpistemicState.SUPPORTED

        # Ladder from warrant + posterior
        if claim.kind == ClaimKind.FORMAL_AXIOMATIC and posterior >= 0.99:
            return EpistemicState.VERIFIED_MEASUREMENT  # truth relative to axioms
        if claim.kind == ClaimKind.EMPIRICAL_STABLE and warrant >= 0.9 and p_v >= 0.8:
            return EpistemicState.VERIFIED_MEASUREMENT
        if warrant >= 0.8 and f > 0.5 and c_conflict <= 0.2 and p_v >= 0.8:
            return EpistemicState.CORROBORATED
        if warrant >= 0.5:
            return EpistemicState.SUPPORTED
        if warrant >= 0.2:
            return EpistemicState.HYPOTHESIS
        return EpistemicState.UNKNOWN

    @staticmethod
    def _derive_authority(kind: ClaimKind, record_state: RecordState) -> AuthorityState:
        """Authority is orthogonal to warrant.

        Default: ADVISE (lowest non-trivial authorization). SEALed records
        can be ADVISE; they do not auto-grant execution. NORMATIVE claims
        REQUIRE_F13 by default because they touch the constitutional frame.
        FORECAST claims without RATIFIED record state are ADVISE only.
        """
        if kind == ClaimKind.NORMATIVE:
            return AuthorityState.REQUIRE_F13
        if record_state == RecordState.SEALED:
            return AuthorityState.ADVISE
        if record_state == RecordState.RATIFIED:
            return AuthorityState.REVERSIBLE_EXECUTE
        if record_state == RecordState.ATTESTED:
            return AuthorityState.ADVISE
        return AuthorityState.OBSERVE


# ═══════════════════════════════════════════════════════════════════════════════
# Legacy adapter — Phase 1 (transitional only)
# ═══════════════════════════════════════════════════════════════════════════════


def legacy_truth_vector(assessment: Assessment) -> dict[str, Any]:
    """Map a new Assessment back to the legacy TruthVector shape.

    Phase 1 contract: this adapter is the ONLY sanctioned path. Marked
    transitional. Do not extend the legacy fields — rename and migrate.
    """
    return {
        "grounding_g": assessment.provenance_completeness,
        "truth_tau": assessment.warrant,
        "uncertainty_sigma": assessment.epistemic_entropy_bits,
        "coherence_c": 1.0 - assessment.contradiction_index,
        "entropy_delta_s": 0.0,  # DEPRECATED — semantic/physical conflation
        "humility_omega0": 1.0 - assessment.warrant,
        # Extra fields for the new design (not in legacy vector)
        "_transitional": True,
        "_new_assessment": assessment.to_dict(),
    }

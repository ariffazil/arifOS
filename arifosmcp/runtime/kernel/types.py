"""
arifOS Kernel — Governance Physics Primitives

Δ (entropy/pressure), Ω (uncertainty/epistemic), Ψ (integrity/alignment),
metabolic phases 000-999, evidence items, verdicts, source weights,
tripwires, and the unified GovernanceState.

Collapse doctrine (F13 SOVEREIGN):
  - Branches may compute, propose, argue.
  - Only 888 may collapse. Only 999 may seal.
  - Tripwires between 777→888→999 are never bypassed.

Python is judge. TypeScript is hands. Quantum is calculator.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Literal

# ── 1. Uncertainty Tags ────────────────────────

UncertaintyTag = Literal["UNKNOWN", "ESTIMATE", "HYPOTHESIS", "PLAUSIBLE", "CLAIM"]

UNCERTAINTY_ORDER: dict[UncertaintyTag, int] = {
    "UNKNOWN": 0,
    "ESTIMATE": 1,
    "HYPOTHESIS": 2,
    "PLAUSIBLE": 3,
    "CLAIM": 4,
}


# ── 2. Verdicts ────────────────────────────────

# SEAL: canonical ratified
# SABAR: honest sub-threshold (declared without self-deception)
# HOLD: judgment suspended pending more evidence
# VOID: invalid mathematical/constitutional conclusion
# UNRESOLVED: computational limit (timeout, solver UNKNOWN, resource exhaustion) —
#             distinct a VOID. (EUREKA J-20, ratified 888-APEX 2026-09-07.)
#             Routes to FORMAL_STATUS_UNRESOLVED per truth ladder L0-L6.
Verdict = Literal["SEAL", "SABAR", "HOLD", "VOID", "UNRESOLVED"]


# ── 2b. Anomaly Status (EUREKA J-32, ratified 888-APEX 2026-09-07) ────────

# Track anomaly lifecycle in measurement envelopes.
# none:      no anomaly observed
# pending:   anomaly candidate detected, under investigation
# confirmed: anomaly verified, quarantine active
# resolved:  anomaly resolved, model updated or accepted as chronic
AnomalyStatus = Literal["none", "pending", "confirmed", "resolved"]


# ── 2c. Truth Level (EUREKA J-27, ratified 888-APEX 2026-09-07) ──────────

# Truth ladder (TRUTH-LADDER-L0-L6-2026-09-07.md).
# L0:    Syntax validity
# L1:    Type validity
# L2:    Formal/arithmetic validity (bounded computation)
# L3a:   Formal-model conformance (∂f/∂x correct on declared formula)
# L3b:   Semantic-model adequacy (formula matches stated objective) — NOT a math question
# L4:    Empirical correspondence (inputs reflect the world)
# L5:    Decision admissibility (governance + reversibility + cost)
# L6:    Human ratification (F13 SOVEREIGN)
#
# arif_seal MUST block if truth_level < L5.
TruthLevel = Literal["L0", "L1", "L2", "L3a", "L3b", "L4", "L5", "L6"]


# ── 2d. APEX Frame (EUREKA J-29, ratified 888-APEX 2026-09-07) ──────────

# Frame metadata for any APEX score record.
# A score without frame is an incomplete claim.
# See APEX_FRAME_ANOMALY_DOCTRINE-2026-09-07.md for full doctrine.
ApexFrameId = str  # e.g., "AAA-governance-v3"
ApexSubject = str  # agent / actor / system being measured
ApexWindow = str  # ISO-8601 observation window, e.g., "2026-09-07T08:00+08/2026-09-07T09:00+08"
ApexFormulaVersion = str  # e.g., "APEX-G-v3"
ApexPolicyVersion = str  # e.g., "arifos-policy-2026-09"
ApexDataProvenance = str  # URI / hash / reference to input sources


# ── 2e. Evidence Kind (EUREKA J-23, ratified 888-APEX 2026-09-07) ──────

# Replacement taxonomy for the legacy `evidence_class: observed | derived |
# reported | unknown` field. Future code paths should populate this instead.
# Legacy values remain accepted for backward compat.
EvidenceKind = Literal[
    "ExactRational",  # exact rational number
    "AlgebraicReal",  # exact algebraic with isolating interval
    "CertifiedInterval",  # interval with explicit lower/upper bounds
    "SymbolicExpression",  # symbolic (SymPy, etc.)
    "FloatingEstimate",  # IEEE float — approx, with known precision
    "MonteCarloEstimate",  # MC-derived estimate (stochastic)
    "EmpiricalMeasurement",  # from real-world observation
    "HeuristicScore",  # from heuristic / model output (no formal basis)
    "SolverUnknown",  # from solver UNKNOWN / timeout / resource exhaustion
    # legacy values (deprecated — emit new taxonomy, keep parseable):
    "observed",
    "derived",
    "reported",
    "unknown",
]


# ── 3. Phases ──────────────────────────────────

Phase = Literal[0, 111, 333, 555, 777, 888, 900, 999]

PHASES: list[Phase] = [0, 111, 333, 555, 777, 888, 900, 999]

PHASE_LABELS: dict[Phase, str] = {
    0: "INTENT",
    111: "OBSERVE",
    333: "REASON",
    555: "CRITIQUE",
    777: "FORGE",
    888: "JUDGE",
    900: "COOL",
    999: "SEAL",
}

PHASE_ORDER: dict[Phase, int] = {
    0: 0,
    111: 1,
    333: 2,
    555: 3,
    777: 4,
    888: 5,
    900: 6,
    999: 7,
}


# ── 4. Evidence ────────────────────────────────


@dataclass
class EvidenceItem:
    id: str
    source: str
    payload: dict | None = None
    uncertainty: UncertaintyTag = "UNKNOWN"
    lineage_id: str | None = None
    timestamp: str | None = None

    @classmethod
    def create(
        cls,
        source: str,
        payload: dict | None = None,
        uncertainty: UncertaintyTag = "UNKNOWN",
        lineage_id: str | None = None,
    ) -> EvidenceItem:
        return cls(
            id=uuid.uuid4().hex[:16],
            source=source.upper(),
            payload=payload,
            uncertainty=uncertainty,
            lineage_id=lineage_id,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )


# ── 5. Source Weights ─────────────────────────

SOURCE_WEIGHTS: dict[str, float] = {
    "GEOX": 1.0,
    "WEALTH": 0.85,
    "WELL": 0.7,
    "LLM": 0.4,
    "QUANTUM": 0.5,
    "HUMAN": 1.0,
}


# ── 6. Tripwires ──────────────────────────────

TripwireId = Literal[
    "AUTHORITY",
    "UNCERTAINTY",
    "INTEGRITY",
    "ENTROPY",
    "REVERSIBILITY",
    "RASA_DERITA",
    "FLOOR",
]

Severity = Literal["BLOCK", "DELAY", "WARN"]


@dataclass
class TripwireResult:
    id: TripwireId
    triggered: bool
    reason: str
    severity: Severity


# ── 7. Governance Scalars ─────────────────────


@dataclass
class GovernanceScalars:
    delta: float  # Δ — entropy/pressure
    omega: float  # Ω — uncertainty/epistemic
    psi: float  # Ψ — integrity/alignment
    omega_zero: float = 0.04  # Ω₀ — baseline confidence band [0.03, 0.05]


# ── 8. Collapse Result ────────────────────────

SourceConsensus = Literal["HIGH", "MODERATE", "LOW", "CONFLICT"]


@dataclass
class EvidenceFusion:
    total_items: int
    source_breakdown: dict[str, int]
    weighted_omega: float
    source_consensus: SourceConsensus


@dataclass
class CollapseResult:
    verdict: Verdict
    tripwires: list[TripwireResult]
    scalars: GovernanceScalars
    evidence_fusion: EvidenceFusion
    timestamp: str


# ── 9. Blast Radius ───────────────────────────

BlastRadius = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

BLAST_WEIGHTS: dict[BlastRadius, float] = {
    "LOW": 0.1,
    "MEDIUM": 0.3,
    "HIGH": 0.6,
    "CRITICAL": 0.9,
}


@dataclass
class RiskProfile:
    blast_radius: BlastRadius = "LOW"
    human_consequence: str = "NONE"
    capital_consequence: str = "NONE"


# ── 10. Governance State ──────────────────────


@dataclass
class GovernanceState:
    phase: Phase = 0
    evidence: list[EvidenceItem] = field(default_factory=list)
    scalars: GovernanceScalars = field(default_factory=lambda: GovernanceScalars(0.0, 1.0, 0.5))
    risk: RiskProfile = field(default_factory=RiskProfile)
    verdict: Verdict | None = None
    authority_present: bool = False
    reversible: bool = False
    timestamp: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )
    cc_id: str = field(default_factory=lambda: uuid.uuid4().hex[:24])
    session_id: str | None = None
    actor_id: str | None = None
    collapse: CollapseResult | None = None
    # RASA DERITA Phase 3 — optional mutation gate inputs (not public tools)
    causal_cascade: dict | None = None
    consent_lease: dict | None = None
    action_mode: str | None = None
    action_tier: str | None = None
    requires_consent: bool = False

    def clone(self, **overrides) -> GovernanceState:
        """Immutable-style update: returns new state with overridden fields."""
        data = {
            "phase": self.phase,
            "evidence": list(self.evidence),
            "scalars": self.scalars,
            "risk": self.risk,
            "verdict": self.verdict,
            "authority_present": self.authority_present,
            "reversible": self.reversible,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cc_id": self.cc_id,
            "session_id": self.session_id,
            "actor_id": self.actor_id,
            "collapse": self.collapse,
            "causal_cascade": self.causal_cascade,
            "consent_lease": self.consent_lease,
            "action_mode": self.action_mode,
            "action_tier": self.action_tier,
            "requires_consent": self.requires_consent,
        }
        data.update(overrides)
        return GovernanceState(**data)


# ── 11. Organ Interface ───────────────────────


class Organ:
    """All compute organs implement this interface.

    Kernel never lets an organ:
      - set verdict
      - change phase beyond its allowed band
      - bypass 888 or 999
    """

    name: str

    async def compute(self, input_data: dict) -> list[EvidenceItem]:
        raise NotImplementedError


# ── 12. Thresholds ────────────────────────────

OMEGA_MAX = 0.4
PSI_MIN = 0.7  # F2 base integrity floor — fallback when evidence class is ambiguous
DELTA_CRITICAL = 0.7
OMEGA_WARN = 0.3
OMEGA_HARD_LIMIT = 0.6
OMEGA_ZERO_MIN = 0.03  # F7 HUMILITY: Ω₀ floor — no fake certainty
OMEGA_ZERO_MAX = 0.05  # F7 HUMILITY: Ω₀ ceiling — no fake humility

# ── 12.5 — F2 Dual-Mode Thresholds (Compression-Kernel Doctrine, 2026-08-02) ──
# Per the compression-kernel doctrine: the kernel IS a compressor.
# LIT (direct observation, OBS) → F2 ≥ 0.99 — near-certain, range-encoded precision
# REF (derivation, DER/INT/SPEC) → F2 ≥ 0.85 — back-reference inherits + decays
# Demanding 0.99 for derivations makes the dictionary useless — every match
# gets demoted to LIT, FQ → 0, kernel over-verifies. See DOCTRINE.md §2.4, §6.
# Forged: 2026-08-02 by 333-AGI under F13 SOVEREIGN directive "execute now".
# Seal: RECEIPT.md §Bug 2 (F2 threshold too strict for REFs).
PSI_MIN_OBS = 0.99  # F2 TRUTH: direct observation threshold — near-certain
PSI_MIN_DER = 0.85  # F2 TRUTH: derivation/interpretation threshold — inherited confidence

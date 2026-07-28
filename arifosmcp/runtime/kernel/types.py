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

Verdict = Literal["SEAL", "SABAR", "HOLD", "VOID"]


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
PSI_MIN = 0.7
DELTA_CRITICAL = 0.7
OMEGA_WARN = 0.3
OMEGA_HARD_LIMIT = 0.6
OMEGA_ZERO_MIN = 0.03  # F7 HUMILITY: Ω₀ floor — no fake certainty
OMEGA_ZERO_MAX = 0.05  # F7 HUMILITY: Ω₀ ceiling — no fake humility

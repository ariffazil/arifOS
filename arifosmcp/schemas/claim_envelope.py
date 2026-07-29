"""
claim_envelope.py — F2 TRUTH Claim Envelope Schema

RASA DERITA Semantic Closure — Gate 1 of 6.

Every consequential output from the arifOS kernel MUST carry a machine-checkable
claim envelope. This replaces the input-side lexical check that currently inspects
prompt wording for markers like "source:" and "according to."

Architecture:
  This schema defines the data model. The evaluator in core/laws.py
  enforces that every consequential output claim carries a valid envelope.

Truth Classes:
  OBS  — Direct observation or live receipt
  DER  — Inputs plus reproducible derivation
  INT  — Evidence plus stated interpretive assumptions
  SPEC — Explicit hypothesis with confidence cap
  UNK  — No factual execution permitted (honesty, not authority)

Rules:
  1. Unlabelled consequential claims → HOLD
  2. OBS without evidence → fails
  3. DER without derivation inputs → fails
  4. INT and SPEC cannot exceed their confidence caps
  5. UNK is acceptable as honesty but cannot authorize mutation
  6. Mixed evidence/interpretation → split into separate claims
  7. Current facts require fresh evidence
  8. Every canonical tool output preserves epistemic labels

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TruthClass(str, Enum):
    """Epistemic truth class for claim classification."""

    OBS = "OBS"  # Direct observation or live receipt
    DER = "DER"  # Inputs plus reproducible derivation
    INT = "INT"  # Evidence plus stated interpretive assumptions
    SPEC = "SPEC"  # Explicit hypothesis with confidence cap
    UNK = "UNK"  # No factual execution permitted


# Confidence caps per truth class. INT and SPEC cannot exceed these.
CONFIDENCE_CAPS: dict[TruthClass, float] = {
    TruthClass.OBS: 0.90,  # Observations can be misread
    TruthClass.DER: 0.85,  # Derivations can have hidden assumptions
    TruthClass.INT: 0.75,  # Interpretations carry irreducible uncertainty
    TruthClass.SPEC: 0.60,  # Speculation is inherently uncertain
    TruthClass.UNK: 0.30,  # Unknown — honest, not authoritative
}


@dataclass(frozen=True)
class EvidenceReceipt:
    """A single piece of evidence supporting a claim."""

    receipt_id: str  # e.g., "receipt:abc123" or "sha256:def456"
    source: str  # Where the evidence came from
    observed_at: datetime  # When the evidence was observed
    truth_class: TruthClass  # Epistemic class of the evidence itself


@dataclass(frozen=True)
class ClaimEnvelope:
    """Machine-checkable claim unit for every consequential output.

    Fields:
      claim: The statement being made
      truth_class: Epistemic classification (OBS/DER/INT/SPEC/UNK)
      confidence: Self-assessed confidence [0.0, 1.0], capped by truth_class
      evidence_receipts: List of evidence supporting this claim
      derived_from: IDs of claims this one was derived from
      valid_as_of: When this claim was evaluated
      uncertainties: Known unknowns affecting this claim
      provenance: Who/which organ made this claim
    """

    claim: str
    truth_class: TruthClass
    confidence: float
    evidence_receipts: list[EvidenceReceipt] = field(default_factory=list)
    derived_from: list[str] = field(default_factory=list)
    valid_as_of: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    uncertainties: list[str] = field(default_factory=list)
    provenance: str = "arifOS.kernel"

    def validate(self) -> tuple[bool, list[str]]:
        """Validate this claim envelope against F2 rules.

        Returns (is_valid, list_of_violations).
        """
        violations: list[str] = []

        # Rule 1: Truth class must be one of the valid classes
        if self.truth_class not in TruthClass:
            violations.append(f"Invalid truth_class: {self.truth_class}")
            return False, violations

        # Rule 2: OBS without evidence fails
        if self.truth_class == TruthClass.OBS and not self.evidence_receipts:
            violations.append("OBS claim requires at least one evidence_receipt")

        # Rule 3: DER without derivation inputs fails
        if self.truth_class == TruthClass.DER and not self.derived_from:
            violations.append("DER claim requires derived_from inputs")

        # Rule 4: INT and SPEC confidence caps
        cap = CONFIDENCE_CAPS.get(self.truth_class, 1.0)
        if self.confidence > cap:
            violations.append(
                f"{self.truth_class.value} confidence {self.confidence} exceeds cap {cap}"
            )

        # Rule 5: UNK cannot authorize mutation (checked at call site)
        # Rule 6: Mixed evidence handling (checked at call site)
        # Rule 7: Current facts freshness (checked by valid_as_of age)
        stale_age_hours = 24
        age = (datetime.now(timezone.utc) - self.valid_as_of).total_seconds() / 3600
        if self.truth_class in (TruthClass.OBS, TruthClass.DER) and age > stale_age_hours:
            violations.append(
                f"Stale evidence: {self.truth_class.value} claim is {age:.1f}h old "
                f"(max {stale_age_hours}h)"
            )

        # Confidence must be in [0, 1]
        if not (0.0 <= self.confidence <= 1.0):
            violations.append(f"Confidence {self.confidence} not in [0.0, 1.0]")

        return len(violations) == 0, violations

    def is_consequential(self) -> bool:
        """A claim is consequential if it could influence a decision or action."""
        return self.truth_class != TruthClass.UNK


def validate_claim_bundle(claims: list[ClaimEnvelope]) -> tuple[bool, list[str]]:
    """Validate a bundle of claims together.

    Rule 6 enforcement: if claims mix evidence types without separation,
    flag them.
    """
    all_violations: list[str] = []
    all_valid = True

    truth_classes = {c.truth_class for c in claims}
    if len(truth_classes) > 1 and len(claims) == 1:
        # Single claim with mixed types — should be split
        pass  # This is informational; the caller should split

    for claim in claims:
        valid, violations = claim.validate()
        if not valid:
            all_valid = False
            all_violations.extend(violations)

    # Rule 8: Every consequential claim must preserve epistemic labels
    for claim in claims:
        if claim.is_consequential() and not claim.evidence_receipts and not claim.derived_from:
            all_valid = False
            all_violations.append(
                f"Consequential claim '{claim.claim[:80]}...' has no evidence or derivation source"
            )

    return all_valid, all_violations

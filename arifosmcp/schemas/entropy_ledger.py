"""
entropy_ledger.py — F4 CLARITY Entropy Ledger Schema

RASA DERITA Semantic Closure — Gate 4 of 6.

Replaces the query-length based F4 check with a before-and-after uncertainty
ledger that measures whether an output actually reduced entropy (ΔS ≤ 0).

Operational definition of entropy S:
  S = unresolved ambiguity
    + unsupported claims
    + unresolved contradictions
    + stale evidence
    + unbounded scope
    + missing authority

ΔS = S_after - S_before

Interpretation:
  ΔS < 0: clarity improved — PROCEED
  ΔS = 0: no improvement — acceptable only if agent explicitly bounded the unknown
  ΔS > 0: the answer created more confusion — HOLD

Naming an unresolved contradiction can reduce entropy even when the
contradiction itself remains unresolved. Pretending the contradiction
disappeared cannot.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EntropySource(str, Enum):
    """Sources of entropy in a decision space."""

    UNRESOLVED_AMBIGUITY = "unresolved_ambiguity"
    UNSUPPORTED_CLAIMS = "unsupported_claims"
    UNRESOLVED_CONTRADICTION = "unresolved_contradiction"
    STALE_EVIDENCE = "stale_evidence"
    UNBOUNDED_SCOPE = "unbounded_scope"
    MISSING_AUTHORITY = "missing_authority"


# Contribution of each entropy source to total S
ENTROPY_WEIGHTS: dict[EntropySource, float] = {
    EntropySource.UNRESOLVED_AMBIGUITY: 0.25,
    EntropySource.UNSUPPORTED_CLAIMS: 0.20,
    EntropySource.UNRESOLVED_CONTRADICTION: 0.20,
    EntropySource.STALE_EVIDENCE: 0.15,
    EntropySource.UNBOUNDED_SCOPE: 0.10,
    EntropySource.MISSING_AUTHORITY: 0.10,
}


@dataclass
class EntropyLedgerEntry:
    """A single entropy measurement point — before or after an output."""

    label: str  # "before" or "after"
    unresolved_ambiguity: int = 0  # Count of ambiguous items
    unsupported_claims: int = 0  # Count of claims without evidence
    unresolved_contradictions: int = 0  # Count of contradictions
    stale_evidence_count: int = 0  # Count of stale evidence items
    unbounded_scope: bool = False  # Is scope unbounded?
    missing_authority: bool = False  # Is authority missing?
    total_claims: int = 0  # Total claims in this state

    def compute_s(self) -> float:
        """Compute the entropy score S from this entry's counts.

        S is weighted sum of entropy sources, normalized to [0, 1].
        """
        max_claims = max(self.total_claims, 1)  # Avoid division by zero

        factors = {
            EntropySource.UNRESOLVED_AMBIGUITY: min(self.unresolved_ambiguity / max_claims, 1.0),
            EntropySource.UNSUPPORTED_CLAIMS: min(self.unsupported_claims / max_claims, 1.0),
            EntropySource.UNRESOLVED_CONTRADICTION: min(
                self.unresolved_contradictions / max_claims, 1.0
            ),
            EntropySource.STALE_EVIDENCE: min(self.stale_evidence_count / max_claims, 1.0),
            EntropySource.UNBOUNDED_SCOPE: 1.0 if self.unbounded_scope else 0.0,
            EntropySource.MISSING_AUTHORITY: 1.0 if self.missing_authority else 0.0,
        }

        s = sum(ENTROPY_WEIGHTS[source] * factors[source] for source in EntropySource)
        return min(s, 1.0)


@dataclass
class EntropyAssessment:
    """Before-and-after entropy assessment for a single output.

    Use:
      assessment = EntropyAssessment()
      assessment.before = EntropyLedgerEntry(label="before", ...)
      assessment.after = EntropyLedgerEntry(label="after", ...)

      delta_s = assessment.compute_delta_s()
      passed = assessment.evaluate_f4()
    """

    before: EntropyLedgerEntry | None = None
    after: EntropyLedgerEntry | None = None
    bounded_unknowns: list[str] = field(default_factory=list)
    contradictions_named: list[str] = field(default_factory=list)
    evidence_acquired: bool = False

    def compute_delta_s(self) -> float | None:
        """Compute ΔS = S_after - S_before.

        Returns None if either measurement is missing.
        """
        if self.before is None or self.after is None:
            return None
        return self.after.compute_s() - self.before.compute_s()

    def evaluate_f4(self) -> tuple[bool, float | None, list[str]]:
        """Evaluate F4 CLARITY — ΔS ≤ 0.

        Returns (passed, delta_s, reasons).
        """
        reasons: list[str] = []

        delta_s = self.compute_delta_s()
        if delta_s is None:
            return False, None, ["Missing before or after entropy measurement"]

        if delta_s < 0:
            reasons.append(f"ΔS = {delta_s:.3f}: clarity improved")
            return True, delta_s, reasons

        if delta_s == 0:
            if self.bounded_unknowns:
                reasons.append(f"ΔS = 0: no change, but unknowns bounded: {self.bounded_unknowns}")
                return True, delta_s, reasons
            if self.contradictions_named:
                reasons.append(
                    f"ΔS = 0: no change, but contradictions named: {self.contradictions_named}"
                )
                return True, delta_s, reasons
            reasons.append("ΔS = 0: no improvement and no bounded unknowns — SABAR")
            return False, delta_s, reasons

        # ΔS > 0
        reasons.append(f"ΔS = {delta_s:.3f}: output increased confusion — HOLD")

        # Check for specific failure modes
        if (
            self.after and self.after.unsupported_claims > self.before.unsupported_claims
            if self.before
            else 0
        ):
            reasons.append("Unsupported elaboration increased entropy")
        if self.after and not self.evidence_acquired:
            reasons.append("No new evidence acquired")

        return False, delta_s, reasons


def estimate_entropy_from_query(query: str) -> EntropyLedgerEntry:
    """Estimate baseline entropy from a query/input.

    This is a heuristic estimation, not a precise measurement.
    The actual entropy ledger should be populated by the agent
    based on claim analysis, not query length.
    """
    entry = EntropyLedgerEntry(label="before", total_claims=1)

    # Heuristics for ambiguity detection
    ambiguous_patterns = [
        "maybe",
        "possibly",
        "perhaps",
        "might",
        "could be",
        "either",
        "or",
        "unclear",
        "unknown",
        "?",
    ]
    entry.unresolved_ambiguity = sum(1 for p in ambiguous_patterns if p in query.lower())

    # Scope bounding check
    entry.unbounded_scope = len(query) < 20 and "?" in query

    return entry

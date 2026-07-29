"""
federated_evidence.py — Multi-Organ Federation Evidence Bundle Schema

RASA DERITA Semantic Closure — Gate 3 of 6.

When multiple organs (WELL, WEALTH, GEOX) contribute signals about a decision,
the federation MUST preserve provenance, expose contradictions, and refuse
silent averaging. This schema defines the evidence bundle structure.

Rules:
  1. Never erase organ identity
  2. Never average disagreement into false consensus
  3. Missing evidence remains missing
  4. Stale evidence is downgraded
  5. WELL cannot diagnose trauma
  6. A WELL signal cannot independently authorize action
  7. Fusion cannot become psychological profiling without explicit consent
  8. The kernel judges admissibility; organs do not judge each other

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from arifosmcp.schemas.claim_envelope import TruthClass


class Organ(str, Enum):
    """Federation organs that can contribute evidence signals."""

    GEOX = "GEOX"
    WEALTH = "WEALTH"
    WELL = "WELL"
    ARIFOS = "arifOS"
    AFORGE = "A-FORGE"


class FusionVerdict(str, Enum):
    """What the fusion layer can conclude."""

    CLEAR = "CLEAR"  # All signals align, no conflicts
    PARTIAL = "PARTIAL"  # Some organs missing or stale
    CONFLICT = "CONFLICT"  # Organs disagree — do not average
    INCONCLUSIVE = "INCONCLUSIVE"  # Not enough evidence
    BLOCKED = "BLOCKED"  # WELL diagnosis boundary violated


# Prohibited inference patterns — these must never appear in fusion output
PROHIBITED_INFERENCES: frozenset[str] = frozenset(
    [
        "clinical",
        "diagnosis",
        "psychological",
        "trauma",
        "mental health",
        "personality disorder",
        "cognitive impairment",
        "depression",
        "anxiety",
        "ptsd",
        "bipolar",
        "schizophrenia",
        "psychiatric",
        "therapeutic",
    ]
)

# Maximum age for evidence before it is considered stale (hours)
MAX_EVIDENCE_AGE_HOURS = 24

# WELL is REFLECT_ONLY — can never be the sole evidence for action
WELL_REFLECT_ONLY = True


@dataclass(frozen=True)
class OrganSignal:
    """A single signal from one organ."""

    organ: Organ
    truth_class: TruthClass
    finding: str
    provenance: list[str] = field(default_factory=list)  # receipt IDs
    authority: str = "ADVISORY"  # ADVISORY / REFLECT_ONLY / COMPUTE_ONLY
    valid_until: datetime | None = None
    confidence: float = 0.5

    def is_stale(self) -> bool:
        """Check if this signal's evidence is too old."""
        if self.valid_until is None:
            return False
        return datetime.now(timezone.utc) > self.valid_until

    def age_hours(self) -> float | None:
        if self.valid_until is None:
            return None
        return (datetime.now(timezone.utc) - self.valid_until).total_seconds() / 3600


@dataclass
class FederatedEvidenceBundle:
    """Multi-organ evidence bundle for a single decision scope.

    This bundle collects signals from all relevant organs, identifies
    conflicts, tracks missing evidence, and enforces consent boundaries.

    Fields:
      subject_scope: What decision this bundle covers
      consent_lease: Consent token for privacy-sensitive data use
      signals: Per-organ evidence signals
      conflicts: Identified contradictions between organ signals
      missing_organs: Organs that should contribute but haven't
      prohibited_inferences: Detected violations (e.g., WELL diagnosing)
      fusion_verdict: What the fusion layer can conclude
    """

    subject_scope: str
    consent_lease: str | None = None
    signals: list[OrganSignal] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    missing_organs: list[Organ] = field(default_factory=list)
    prohibited_inferences: list[str] = field(default_factory=list)
    fusion_verdict: FusionVerdict = FusionVerdict.INCONCLUSIVE

    def validate(self) -> tuple[bool, list[str]]:
        """Validate this evidence bundle against federation rules.

        Returns (is_valid, list_of_violations).
        """
        violations: list[str] = []

        # Rule 5: WELL cannot diagnose
        for signal in self.signals:
            if signal.organ == Organ.WELL:
                finding_lower = signal.finding.lower()
                for prohibited in PROHIBITED_INFERENCES:
                    if prohibited.replace("_", " ") in finding_lower:
                        violations.append(
                            f"WELL signal contains prohibited inference '{prohibited}': "
                            f"'{signal.finding[:80]}...'"
                        )
                        self.prohibited_inferences.append(prohibited)

        # Rule 6: WELL signal cannot independently authorize action
        well_signals = [s for s in self.signals if s.organ == Organ.WELL]
        non_well_signals = [s for s in self.signals if s.organ != Organ.WELL]
        if well_signals and not non_well_signals and self.fusion_verdict == FusionVerdict.CLEAR:
            violations.append(
                "WELL cannot independently authorize action (REFLECT_ONLY). "
                "At least one non-WELL organ must contribute."
            )

        # Rule 2: Never average disagreement into false consensus
        if self.conflicts and self.fusion_verdict == FusionVerdict.CLEAR:
            violations.append(
                f"Conflicts exist but fusion_verdict is CLEAR. Conflicts: {self.conflicts}"
            )

        # Rule 4: Stale evidence is downgraded
        for signal in self.signals:
            if signal.is_stale():
                age = signal.age_hours()
                violations.append(
                    f"Stale signal from {signal.organ.value}: "
                    f"'{signal.finding[:60]}...' is {age:.1f}h old"
                )

        # Rule 3: Missing evidence remains missing
        if self.missing_organs and self.fusion_verdict == FusionVerdict.CLEAR:
            violations.append(
                f"Missing organs {[o.value for o in self.missing_organs]} "
                f"but fusion_verdict is CLEAR"
            )

        # Rule 7: No psychological profiling without consent
        # Only flag WELL INT/SPEC signals — OBS and DER are measurement, not profiling
        has_well_inference = any(
            s.organ == Organ.WELL
            and s.truth_class in (TruthClass.INT, TruthClass.SPEC)
            and not s.finding.lower().startswith(
                ("reduced operational", "normal", "elevated fatigue")
            )
            for s in self.signals
        )
        has_well_behavioral = any(
            s.organ == Organ.WELL
            and s.truth_class in (TruthClass.INT, TruthClass.SPEC)
            and any(
                kw in s.finding.lower()
                for kw in (
                    "behavioral",
                    "pattern",
                    "personality",
                    "psychological",
                    "mental",
                    "cognitive",
                )
            )
            for s in self.signals
        )
        if has_well_behavioral and not self.consent_lease:
            violations.append(
                "WELL behavioral/psychological interpretation present but no consent_lease. "
                "Fusion cannot become psychological profiling without consent."
            )
        # Also flag any explicit diagnosis language
        for signal in self.signals:
            if signal.organ == Organ.WELL:
                finding_lower = signal.finding.lower()
                for prohibited in PROHIBITED_INFERENCES:
                    if prohibited in finding_lower:
                        if (
                            "reduced operational" not in finding_lower
                            and "elevated fatigue" not in finding_lower
                        ):
                            violations.append(
                                f"WELL signal contains prohibited term '{prohibited}': "
                                f"'{signal.finding[:80]}...'"
                            )
                            self.prohibited_inferences.append(prohibited)

        return len(violations) == 0, violations

    def compute_verdict(self) -> FusionVerdict:
        """Compute the fusion verdict from the evidence bundle.

        This is a deterministic function, not an AI judgment.
        """
        # Check for blocked state first
        _, violations = self.validate()
        if any("prohibited inference" in v for v in violations):
            return FusionVerdict.BLOCKED

        # Check for conflicts
        if self.conflicts:
            return FusionVerdict.CONFLICT

        # Check for missing/incomplete
        if self.missing_organs or not self.signals:
            return FusionVerdict.PARTIAL

        # Check for stale evidence
        if any(s.is_stale() for s in self.signals):
            return FusionVerdict.PARTIAL

        # Check that WELL isn't the only source for action
        well_only = len(self.signals) == 1 and self.signals[0].organ == Organ.WELL
        if well_only:
            return FusionVerdict.PARTIAL

        # All signals present, fresh, non-conflicting
        return FusionVerdict.CLEAR


def build_federation_bundle(
    *,
    subject_scope: str,
    organ_signals: list[OrganSignal],
    consent_lease: str | None = None,
) -> FederatedEvidenceBundle:
    """Build a federation evidence bundle from individual organ signals.

    This is the canonical constructor — it auto-detects conflicts,
    missing organs, and prohibited inferences.
    """
    signals_by_organ: dict[Organ, list[OrganSignal]] = {}
    for s in organ_signals:
        signals_by_organ.setdefault(s.organ, []).append(s)

    # Detect missing organs (those that should contribute)
    expected_organs = {Organ.GEOX, Organ.WEALTH, Organ.WELL}
    present_organs = set(signals_by_organ.keys())
    missing_organs = list(expected_organs - present_organs)

    # Detect conflicts between organs
    conflicts: list[str] = []
    organ_findings = [(s.organ, s.finding.lower()) for s in organ_signals]
    for i, (org_a, finding_a) in enumerate(organ_findings):
        for org_b, finding_b in organ_findings[i + 1 :]:
            if org_a != org_b:
                # Simple conflict detection: opposite keywords
                conflict_pairs = [
                    ("high", "low"),
                    ("positive", "negative"),
                    ("increase", "decrease"),
                    ("agree", "disagree"),
                    ("stable", "unstable"),
                    ("safe", "dangerous"),
                ]
                for pos, neg in conflict_pairs:
                    if (pos in finding_a and neg in finding_b) or (
                        neg in finding_a and pos in finding_b
                    ):
                        conflicts.append(
                            f"{org_a.value}:{finding_a[:40]} vs {org_b.value}:{finding_b[:40]}"
                        )
                        break

    bundle = FederatedEvidenceBundle(
        subject_scope=subject_scope,
        consent_lease=consent_lease,
        signals=organ_signals,
        conflicts=conflicts,
        missing_organs=missing_organs,
    )

    bundle.fusion_verdict = bundle.compute_verdict()
    return bundle

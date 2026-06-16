"""
Engineering Claim Validator — Typed validation for engineering claims.

F2 TRUTH: Every engineering claim must pass validation:
- Has epistemic label (OBS/DER/INT/SPEC)
- Has evidence chain
- Has witness attestation (F3 TRI-WITNESS)
- Confidence capped at 0.90 (F7)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ValidationVerdict(str, Enum):
    """Validation verdicts for engineering claims."""

    SEAL = "SEAL"
    SABAR = "SABAR"
    HOLD = "HOLD"
    VOID = "VOID"


@dataclass
class EngineeringClaim:
    """An engineering claim to validate."""

    claim: str
    epistemic_label: str  # OBS | DER | INT | SPEC
    confidence: float  # 0.0–0.90
    evidence: list[str] = field(default_factory=list)
    witness_type: Optional[str] = None  # human | ai | earth
    witness_id: Optional[str] = None
    floor_compliance: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.confidence > 0.90:
            raise ValueError("F7 HUMILITY: confidence cannot exceed 0.90")
        if self.epistemic_label not in ("OBS", "DER", "INT", "SPEC"):
            raise ValueError(f"Unknown epistemic label: {self.epistemic_label}")


class EngineeringClaimValidator:
    """Validate engineering claims against constitutional floors."""

    def validate(self, claim: EngineeringClaim) -> tuple[ValidationVerdict, list[str]]:
        """Return verdict + list of issues found."""
        issues = []

        # F2 TRUTH: epistemic label required
        if not claim.epistemic_label:
            issues.append("Missing epistemic label")

        # F2 TRUTH: evidence required
        if not claim.evidence:
            issues.append("Missing evidence chain")

        # F3 TRI-WITNESS: at least one witness
        if not claim.witness_type or not claim.witness_id:
            issues.append("Missing witness attestation (F3)")

        # F7 HUMILITY: confidence cap
        if claim.confidence > 0.90:
            issues.append(f"Confidence {claim.confidence} exceeds 0.90 cap (F7)")

        # F11 AUDIT: at least one floor compliance mentioned
        if not claim.floor_compliance:
            issues.append("Missing floor compliance reference (F11)")

        # Determine verdict
        if not issues:
            verdict = ValidationVerdict.SEAL
        elif len(issues) == 1 and "Missing floor compliance" in issues[0]:
            verdict = ValidationVerdict.SABAR
        else:
            verdict = ValidationVerdict.HOLD

        return verdict, issues

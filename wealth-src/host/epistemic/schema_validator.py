"""
Epistemic Input Schema Validator.

Validates that prospect inputs from GEOX carry probabilistic distributions,
not single scalars. Enforces integrity_score gating.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ValidationError:
    field: str
    message: str
    severity: str = "ERROR"


@dataclass
class SchemaValidationResult:
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    status: str = "VALID"
    hold: bool = False
    reason: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "valid": self.valid,
            "status": self.status,
        }
        if self.errors:
            result["errors"] = [
                {"field": e.field, "message": e.message, "severity": e.severity}
                for e in self.errors
            ]
        if self.warnings:
            result["warnings"] = [
                {"field": w.field, "message": w.message, "severity": w.severity}
                for w in self.warnings
            ]
        if self.hold:
            result["hold"] = True
        if self.reason:
            result["reason"] = self.reason
        return result


class ProspectInputSchema:
    """
    Required schema for prospect inputs from GEOX.
    REJECTS single scalars for volumetrics.
    """

    REQUIRED_FIELDS = ["prospect_id", "stoiip", "pos", "integrity_score"]
    INTEGRITY_THRESHOLD = 0.3
    INTEGRITY_WARNING_THRESHOLD = 0.6

    @staticmethod
    def validate_stoiip(stoiip: Any) -> List[ValidationError]:
        errors: List[ValidationError] = []

        if not isinstance(stoiip, dict):
            errors.append(
                ValidationError(
                    field="stoiip",
                    message="stoiip must be a dict with p10/p50/p90 values, not a scalar",
                    severity="ERROR",
                )
            )
            return errors

        required_keys = ["p10", "p50", "p90"]
        missing = [k for k in required_keys if k not in stoiip]
        if missing:
            errors.append(
                ValidationError(
                    field="stoiip",
                    message=f"stoiip missing required keys: {missing}. Single-value outputs are FORBIDDEN.",
                    severity="ERROR",
                )
            )
            return errors

        for key in required_keys:
            val = stoiip[key]
            if not isinstance(val, (int, float)):
                errors.append(
                    ValidationError(
                        field=f"stoiip.{key}",
                        message=f"{key} must be a number, got {type(val).__name__}",
                        severity="ERROR",
                    )
                )
            elif val < 0:
                errors.append(
                    ValidationError(
                        field=f"stoiip.{key}",
                        message=f"{key} must be non-negative, got {val}",
                        severity="ERROR",
                    )
                )

        if stoiip.get("p10", 0) > stoiip.get("p50", float("inf")):
            errors.append(
                ValidationError(
                    field="stoiip.p10",
                    message=f"p10 ({stoiip['p10']}) must be <= p50 ({stoiip['p50']})",
                    severity="ERROR",
                )
            )

        if stoiip.get("p50", float("inf")) > stoiip.get("p90", float("inf")):
            errors.append(
                ValidationError(
                    field="stoiip.p50",
                    message=f"p50 ({stoiip['p50']}) must be <= p90 ({stoiip['p90']})",
                    severity="ERROR",
                )
            )

        return errors

    @classmethod
    def validate(cls, data: Dict[str, Any]) -> SchemaValidationResult:
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        for field_name in cls.REQUIRED_FIELDS:
            if field_name not in data:
                errors.append(
                    ValidationError(
                        field=field_name,
                        message=f"Required field '{field_name}' is missing",
                        severity="ERROR",
                    )
                )

        if "stoiip" in data:
            errors.extend(cls.validate_stoiip(data["stoiip"]))

        if "pos" in data:
            pos = data["pos"]
            if not isinstance(pos, (int, float)):
                errors.append(
                    ValidationError(
                        field="pos",
                        message=f"pos must be a number, got {type(pos).__name__}",
                        severity="ERROR",
                    )
                )
            elif not 0 <= pos <= 1:
                errors.append(
                    ValidationError(
                        field="pos",
                        message=f"pos must be between 0 and 1, got {pos}",
                        severity="ERROR",
                    )
                )

        if "integrity_score" in data:
            score = data["integrity_score"]
            if not isinstance(score, (int, float)):
                errors.append(
                    ValidationError(
                        field="integrity_score",
                        message=f"integrity_score must be a number, got {type(score).__name__}",
                        severity="ERROR",
                    )
                )
            elif score < cls.INTEGRITY_THRESHOLD:
                errors.append(
                    ValidationError(
                        field="integrity_score",
                        message=f"integrity_score ({score}) < {cls.INTEGRITY_THRESHOLD} — below decision threshold",
                        severity="ERROR",
                    )
                )
            elif score < cls.INTEGRITY_WARNING_THRESHOLD:
                warnings.append(
                    ValidationError(
                        field="integrity_score",
                        message=f"integrity_score ({score}) is between {cls.INTEGRITY_THRESHOLD} and {cls.INTEGRITY_WARNING_THRESHOLD} — PLAUSIBLE, pass with warning",
                        severity="WARNING",
                    )
                )

        if "model_lineage_hash" not in data:
            warnings.append(
                ValidationError(
                    field="model_lineage_hash",
                    message="model_lineage_hash not provided — correlation tracking will be limited",
                    severity="WARNING",
                )
            )

        if "posterior_breadth" not in data:
            warnings.append(
                ValidationError(
                    field="posterior_breadth",
                    message="posterior_breadth not provided — breadth check skipped",
                    severity="WARNING",
                )
            )

        if errors:
            return SchemaValidationResult(
                valid=False,
                errors=errors,
                warnings=warnings,
                status="INVALID",
                hold=True,
                reason="Schema validation failed",
            )

        has_low_integrity = "integrity_score" in data and data["integrity_score"] < cls.INTEGRITY_THRESHOLD
        has_high_integrity = "integrity_score" in data and data["integrity_score"] >= cls.INTEGRITY_THRESHOLD

        if has_low_integrity:
            return SchemaValidationResult(
                valid=True,
                warnings=warnings,
                status="EPISTEMIC_HOLD",
                hold=True,
                reason="GEOX integrity below threshold",
            )

        if has_high_integrity and warnings:
            return SchemaValidationResult(
                valid=True,
                warnings=warnings,
                status="PASS_WITH_WARNING",
                hold=False,
            )

        return SchemaValidationResult(
            valid=True,
            warnings=warnings if warnings else [],
            status="PASS",
            hold=False,
        )


class EpistemicSchemaValidator:
    """
    Validates prospect inputs against epistemic requirements.
    REJECTS scalar volumetrics.
    REQUIRES integrity_score >= 0.3 for capital allocation.
    """

    def __init__(self, min_integrity_score: float = 0.3) -> None:
        self.min_integrity_score = min_integrity_score

    def validate_prospect(self, prospect: Dict[str, Any]) -> SchemaValidationResult:
        return ProspectInputSchema.validate(prospect)

    def validate_portfolio(self, prospects: List[Dict[str, Any]]) -> Dict[str, Any]:
        results: List[Dict[str, Any]] = []
        all_errors: List[Dict[str, Any]] = []
        all_warnings: List[Dict[str, Any]] = []
        held_prospects: List[str] = []

        for prospect in prospects:
            prospect_id = prospect.get("prospect_id", "UNKNOWN")
            validation = self.validate_prospect(prospect)
            results.append({
                "prospect_id": prospect_id,
                **validation.to_dict(),
            })

            if not validation.valid or validation.hold:
                held_prospects.append(prospect_id)
                all_errors.extend(validation.errors)

            all_warnings.extend(validation.warnings)

        portfolio_valid = len(held_prospects) == 0 and len(all_errors) == 0

        return {
            "portfolio_valid": portfolio_valid,
            "total_prospects": len(prospects),
            "held_prospects": held_prospects,
            "prospect_results": results,
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "status": "EPISTEMIC_HOLD" if held_prospects else "PASS",
        }

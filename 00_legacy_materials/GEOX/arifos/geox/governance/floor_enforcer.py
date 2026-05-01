"""
FloorEnforcer — Verify Constitutional Floor Compliance
DITEMPA BUKAN DIBERI

Enforces arifOS Constitutional Floors relevant to GEOX:
  - F1 Amanah (Reversibility): Operations must be undoable
  - F4 Clarity (Unit Integrity): All values have explicit units
  - F7 Humility (Uncertainty): Confidence in [0.03, 0.15] range required
  - F9 Anti-Hantu (No Phantom Data): No hallucinated or unverified data
  - F13 Sovereign (Human Override): Human can override any decision
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass
class FloorCheckResult:
    """Result of checking a constitutional floor."""
    floor: str  # F1, F4, F7, F9, F13
    passed: bool
    violations: list[str] = field(default_factory=list)
    recommendation: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "floor": self.floor,
            "passed": self.passed,
            "violation_count": len(self.violations),
            "violations": self.violations,
            "recommendation": self.recommendation,
        }


class FloorEnforcer:
    """
    Enforces arifOS constitutional floors for GEOX operations.
    
    Each floor check returns a FloorCheckResult with detailed
    information about any violations.
    """
    
    # F7 Humility bounds (must acknowledge 3-15% uncertainty)
    F7_MIN_CONFIDENCE = 0.03
    F7_MAX_CONFIDENCE = 0.15
    
    def __init__(self):
        self._check_count = 0
    
    def check_f1_amanah(
        self,
        operation: Any,
        can_undo: bool | None = None,
        undo_method: str | None = None,
    ) -> FloorCheckResult:
        """
        Check F1 Amanah (Reversibility).
        
        Operations must be reversible or have compensating controls.
        """
        violations = []
        
        if can_undo is False:
            violations.append(
                "Operation cannot be undone (F1 Amanah violation)"
            )
        
        if not undo_method and can_undo is not True:
            violations.append(
                "No undo method specified for potentially destructive operation"
            )
        
        return FloorCheckResult(
            floor="F1",
            passed=len(violations) == 0,
            violations=violations,
            recommendation="Implement undo mechanism or compensating controls",
        )
    
    def check_f4_clarity(
        self,
        data: Any,
        required_units: list[str] | None = None,
    ) -> FloorCheckResult:
        """
        Check F4 Clarity (Unit Integrity).
        
        All numerical values must have explicit units.
        """
        violations = []
        
        # Check for unit metadata
        if hasattr(data, "units"):
            units = data.units
            if not units or units == "unknown":
                violations.append("Units specified but empty or 'unknown'")
        elif isinstance(data, dict):
            # Check dict values for units
            for key, value in data.items():
                if isinstance(value, (int, float, np.number)):
                    # Numeric values should have unit info
                    violations.append(
                        f"Numeric value '{key}' has no unit information"
                    )
        elif isinstance(data, np.ndarray):
            # Arrays should have unit metadata
            if not hasattr(data, "units"):
                violations.append("NumPy array has no unit metadata")
        
        # Check required units are present
        if required_units:
            data_keys = set(data.keys()) if isinstance(data, dict) else set()
            for unit in required_units:
                if unit not in data_keys:
                    violations.append(f"Required unit '{unit}' not found")
        
        return FloorCheckResult(
            floor="F4",
            passed=len(violations) == 0,
            violations=violations,
            recommendation="Add explicit units to all numerical values",
        )
    
    def check_f7_humility(
        self,
        confidence: float | None,
        uncertainty_quantified: bool = False,
    ) -> FloorCheckResult:
        """
        Check F7 Humility (Uncertainty Acknowledgment).
        
        Confidence must be in [0.03, 0.15] range (3-15%).
        Outside this range is either overconfident or uselessly uncertain.
        """
        violations = []
        
        if confidence is None:
            violations.append("No confidence value provided (F7 violation)")
        elif confidence < self.F7_MIN_CONFIDENCE:
            violations.append(
                f"Confidence {confidence:.3f} below F7 minimum ({self.F7_MIN_CONFIDENCE})"
            )
        elif confidence > self.F7_MAX_CONFIDENCE:
            violations.append(
                f"Confidence {confidence:.3f} exceeds F7 maximum ({self.F7_MAX_CONFIDENCE}) — overconfidence detected"
            )
        
        if not uncertainty_quantified:
            violations.append("Uncertainty not explicitly quantified")
        
        return FloorCheckResult(
            floor="F7",
            passed=len(violations) == 0,
            violations=violations,
            recommendation=f"Set confidence in [{self.F7_MIN_CONFIDENCE}, {self.F7_MAX_CONFIDENCE}] range and document uncertainty sources",
        )
    
    def check_f9_anti_hantu(
        self,
        data: Any,
        provenance: dict[str, Any] | None = None,
    ) -> FloorCheckResult:
        """
        Check F9 Anti-Hantu (No Phantom Data).
        
        No hallucinated, generated, or unverified data allowed.
        """
        violations = []
        
        # Check for provenance
        if not provenance:
            violations.append("No data provenance provided (F9 violation)")
        else:
            # Check source
            source = provenance.get("source")
            if not source:
                violations.append("Provenance missing 'source' field")
            elif source in ("generated", "hallucinated", "synthetic_unverified"):
                violations.append(f"Unverified data source: {source}")
            
            # Check verification
            if not provenance.get("verified", False):
                violations.append("Data not marked as verified")
        
        # Check for AI-generated indicators
        if hasattr(data, "metadata"):
            meta = data.metadata
            if meta.get("ai_generated"):
                violations.append("Data flagged as AI-generated without verification")
            if meta.get("hallucination_risk") == "high":
                violations.append("High hallucination risk detected in metadata")
        
        return FloorCheckResult(
            floor="F9",
            passed=len(violations) == 0,
            violations=violations,
            recommendation="Provide verified provenance for all data",
        )
    
    def check_f13_sovereign(
        self,
        has_override: bool = True,
        override_documented: bool = False,
    ) -> FloorCheckResult:
        """
        Check F13 Sovereign (Human Override).
        
        Human must be able to override any decision.
        """
        violations = []
        
        if not has_override:
            violations.append("No human override mechanism provided (F13 violation)")
        
        if has_override and not override_documented:
            violations.append("Override mechanism exists but not documented")
        
        return FloorCheckResult(
            floor="F13",
            passed=len(violations) == 0,
            violations=violations,
            recommendation="Document human override mechanism and ensure it's accessible",
        )
    
    def check_all(
        self,
        data: Any,
        confidence: float | None = None,
        provenance: dict[str, Any] | None = None,
        can_undo: bool | None = None,
    ) -> dict[str, FloorCheckResult]:
        """
        Check all relevant floors.
        
        Returns dict of floor -> FloorCheckResult.
        """
        self._check_count += 1
        
        return {
            "F1": self.check_f1_amanah(data, can_undo),
            "F4": self.check_f4_clarity(data),
            "F7": self.check_f7_humility(confidence),
            "F9": self.check_f9_anti_hantu(data, provenance),
            "F13": self.check_f13_sovereign(),
        }
    
    def get_summary(
        self,
        results: dict[str, FloorCheckResult],
    ) -> dict[str, Any]:
        """Get summary of floor check results."""
        passed = sum(1 for r in results.values() if r.passed)
        total = len(results)
        
        all_violations = []
        for floor, result in results.items():
            all_violations.extend(result.violations)
        
        return {
            "floors_checked": total,
            "floors_passed": passed,
            "compliance_rate": passed / total if total > 0 else 0,
            "all_passed": passed == total,
            "total_violations": len(all_violations),
            "violations": all_violations,
        }

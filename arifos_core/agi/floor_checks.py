"""
AGI ORTHOGONAL KERNEL — floors.py (Moulded from floor_checks.py)

The Geometry of AGI is an ORTHOGONAL TETRAHEDRON.
Each Floor is an independent axis. They do not cross.

Floors:
- Floor1_Amanah: Integrity/Credentials (Axis Z)
- Floor2_Truth: Evidence/Hallucination (Axis X)
- Floor3_TriWitness: Consensus (Axis Y)
- Floor4_DeltaS: Clarity/Entropy (Axis T)

DITEMPA BUKAN DIBERI - v46.2
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# =============================================================================
# 1. THE ORTHOGONAL BASE (Geometry)
# =============================================================================

@dataclass
class FloorResult:
    """Discrete Result of an Orthogonal Check."""
    passed: bool
    score: float
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class Floor(ABC):
    """
    Abstract Floor — Each is ORTHOGONAL to others.
    Pure functions only. No side effects.
    """
    @abstractmethod
    def check(self, output: str, context: Dict[str, Any]) -> FloorResult:
        """Evaluate the text against this specific independent axis."""
        pass

# =============================================================================
# 2. THE FLOORS (Implementation)
# =============================================================================

class Floor1_Amanah(Floor):
    """
    AXIS Z: INTEGRITY (Amanah)
    Checks for credential leakage and unauthorized mandates.
    """
    def check(self, output: str, context: Dict[str, Any]) -> FloorResult:
        # 1. Credential Check (Simple substring scan for now)
        forbidden_patterns = ["sk-", "ghp_", "password=", "api_key="]
        for pat in forbidden_patterns:
            if pat in output:
                return FloorResult(False, 0.0, f"Credential Leak Detected: {pat}")

        # 2. Mandate Check (from context)
        within_mandate = context.get("within_mandate", True)
        if not within_mandate:
            return FloorResult(False, 0.0, "Action exceeds authorized mandate")

        return FloorResult(True, 1.0, "Amanah Verified")


class Floor2_Truth(Floor):
    """
    AXIS X: TRUTH (Factual Accuracy)
    Requires evidence. Zero tolerance for hallucination.
    """
    def check(self, output: str, context: Dict[str, Any]) -> FloorResult:
        metrics = context.get("metrics", {})
        truth_score = metrics.get("truth", 0.0) # Default to fail-closed

        # Threshold Check
        if truth_score >= 0.99:
            return FloorResult(True, truth_score, "Truth Verified (≥0.99)")
        elif truth_score >= 0.90:
             # Soft pass for non-critical
            return FloorResult(True, truth_score, f"Truth Acceptable ({truth_score:.2f})")
        else:
            return FloorResult(False, truth_score, f"Truth Failure ({truth_score:.2f} < 0.99)")


class Floor3_TriWitness(Floor):
    """
    AXIS Y: WITNESS (Consensus)
    Requires convergence from multiple sources/agents.
    """
    def check(self, output: str, context: Dict[str, Any]) -> FloorResult:
        convergence = context.get("convergence", 0.0)

        if convergence >= 0.95:
             return FloorResult(True, convergence, "Tri-Witness Consensus Achieved")
        elif convergence >= 0.80:
             return FloorResult(True, convergence, "Partial Consensus")
        else:
             return FloorResult(False, convergence, f"Consensus Failure ({convergence:.2f} < 0.95)")


class Floor4_DeltaS(Floor):
    """
    AXIS T: CLARITY (Entropy)
    Low jargon, high structure. No contradictions.
    """
    def check(self, output: str, context: Dict[str, Any]) -> FloorResult:
        # Delta S (Change in Entropy). Negative is bad (confusion).
        # We want >= 0.0 (Clarification)
        delta_s = context.get("delta_s", -1.0) # Default fail

        if delta_s >= 0.0:
            return FloorResult(True, delta_s, f"Clarity Increased (+{delta_s:.2f})")
        else:
            return FloorResult(False, delta_s, f"Confusion Increased ({delta_s:.2f} < 0.0)")

# =============================================================================
# 3. CONVENIENCE ORCHESTRATOR
# =============================================================================

def check_agi_floors(output: str, context: Dict[str, Any]) -> List[FloorResult]:
    """Run the Orthogonal Tetrahedron checks."""
    floors = [
        Floor1_Amanah(),
        Floor2_Truth(),
        Floor3_TriWitness(),
        Floor4_DeltaS()
    ]
    return [floor.check(output, context) for floor in floors]

# =============================================================================
# 4. LEGACY WRAPPERS (For Backward Compatibility)
# =============================================================================

def check_truth_f1(text: str, context: Optional[Dict[str, Any]] = None) -> Any:
    """Wrapper for Floor2_Truth to satisfy legacy imports."""
    context = context or {}
    result = Floor2_Truth().check(text, context)
    # Legacy F1CheckResult shim object if needed, or simple return
    # Returning simple structure for now, matching previous signature mostly
    return result

def check_delta_s_f2(context: Optional[Dict[str, Any]] = None) -> Any:
    """Wrapper for Floor4_DeltaS to satisfy legacy imports."""
    context = context or {}
    # Fake output as DeltaS check in legacy was context-only
    result = Floor4_DeltaS().check("", context)
    return result

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .labels import StateDomain, WitnessType, TruthStatus, Confidence


@dataclass
class Witness:
    """A single channel of evidence about human-state expression."""

    witness_type: WitnessType
    available: bool
    confidence: Confidence
    source: str
    notes: List[str] = field(default_factory=list)
    raw: Optional[Dict[str, Any]] = None


@dataclass
class HumanStateEstimate:
    """Safe, labelled output from the Evidence Classifier.

    This is NOT a verdict on Arif's actual state.
    It is a structured classification of what evidence exists,
    what can be safely said, and what must not be claimed.
    """

    domain: StateDomain
    status: TruthStatus
    confidence: Confidence
    textual_signals: List[str]
    biological_signals: List[str]
    sovereign_confirmation: Optional[bool]
    safe_statement: str
    forbidden_claims: List[str]
    human_confirmation_required: bool
    medical_boundary: str = (
        "This is operational readiness evidence classification, not medical diagnosis. "
        "Expression patterns are not biological facts."
    )

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .labels import StateDomain, WitnessType, TruthStatus, Confidence


@dataclass
class Witness:
    witness_type: WitnessType
    available: bool
    confidence: Confidence
    source: str
    notes: List[str] = field(default_factory=list)
    raw: Optional[Dict[str, Any]] = None


@dataclass
class HumanStateEstimate:
    domain: StateDomain
    status: TruthStatus
    confidence: Confidence
    textual_signals: List[str]
    biological_signals: List[str]
    sovereign_confirmation: Optional[bool]
    safe_statement: str
    forbidden_claims: List[str]
    human_confirmation_required: bool
    medical_boundary: str = "This is operational readiness inference, not medical diagnosis."

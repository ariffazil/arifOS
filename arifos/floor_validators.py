"""
arifOS Floor Validators Shim
Redirects root-level imports to arifos.core.floor_validators
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class FloorType(Enum):
    HARD = "hard"
    SOFT = "soft"
    DERIVED = "derived"

@dataclass
class FloorValidationResult:
    """Result of a single floor validation."""
    floor_id: str
    is_valid: bool
    score: Optional[float]
    reason: str
    floor_type: str  # String for simplicity in shim

from .core.enforcement.floor_validators import validate_f1_amanah as _v1
from .core.enforcement.floor_validators import validate_f2_truth as _v2
from .core.enforcement.floor_validators import validate_f3_tri_witness as _v3
from .core.enforcement.floor_validators import validate_f4_clarity as _v4
from .core.enforcement.floor_validators import validate_f5_peace as _v5
from .core.enforcement.floor_validators import validate_f6_empathy as _v6
from .core.enforcement.floor_validators import validate_f7_humility as _v7
from .core.enforcement.floor_validators import validate_f8_genius as _v8
from .core.enforcement.floor_validators import validate_f9_cdark as _v9
from .core.enforcement.floor_validators import validate_f10_ontology as _v10
from .core.enforcement.floor_validators import validate_f11_command_auth as _v11
from .core.enforcement.floor_validators import validate_f12_injection_defense as _v12
from .core.enforcement.floor_validators import validate_f13_curiosity as _v13


def validate_f1_amanah(action: str, is_reversible: bool, has_mandate: bool, requires_approval: bool = False):
    action_dict = {"type": action}
    context = {"human_authorized": has_mandate, "requires_approval": requires_approval}
    res = _v1(action_dict, context)
    return FloorValidationResult(
        floor_id="F1_Amanah",
        is_valid=res.get("pass", False),
        score=1.0 if res.get("pass") else 0.0,
        reason=res.get("reason", ""),
        floor_type="hard"
    )

def validate_f2_truth(statement: str, evidence: List[str], confidence: float, is_estimate: bool = False):
    context = {"response": statement, "canonical_sources": evidence, "confidence": confidence, "is_estimate": is_estimate}
    res = _v2(statement, context)
    return FloorValidationResult(
        floor_id="F2_Truth",
        is_valid=res.get("pass", False),
        score=res.get("score", 0.0),
        reason=res.get("reason", ""),
        floor_type="hard"
    )

def validate_f3_tri_witness(human_vote: float, ai_vote: float, earth_vote: float):
    agi_output = {"reasoning": {"consistent": ai_vote > 0.5}}
    context = {"human_intent_clear": human_vote > 0.5}
    res = _v3("", agi_output, context)
    return FloorValidationResult(
        floor_id="F3_TriWitness",
        is_valid=res.get("pass", False),
        score=res.get("score", 0.0),
        reason=f"Human={human_vote}, AI={ai_vote}, Earth={earth_vote}",
        floor_type="hard"
    )

def validate_f6_empathy(stakeholder_impacts: Dict[str, float]):
    context = {"vulnerability": max(stakeholder_impacts.values()) if stakeholder_impacts else 0.5}
    res = _v6("", context)
    return FloorValidationResult(
        floor_id="F6_Empathy",
        is_valid=res.get("pass", False),
        score=res.get("score", 0.0),
        reason=res.get("reason", ""),
        floor_type="soft"
    )

def validate_f10_ontology(response: str):
    res = _v10(response)
    return FloorValidationResult(
        floor_id="F10_Ontology",
        is_valid=res.get("pass", False),
        score=1.0 if res.get("pass") else 0.0,
        reason=res.get("reason", ""),
        floor_type="hard"
    )

def validate_f11_command_auth(operator_id: str, operator_nonce: str, authorized_operators: set, requires_nonce: bool = True):
    context = {"user_id": operator_id, "human_authorized": operator_id in authorized_operators}
    res = _v11(context)
    return FloorValidationResult(
        floor_id="F11_CommandAuth",
        is_valid=res.get("pass", False),
        score=1.0 if res.get("pass") else 0.0,
        reason=res.get("reason", ""),
        floor_type="hard"
    )

def validate_f12_injection_defense(user_input: str):
    res = _v12(user_input)
    return FloorValidationResult(
        floor_id="F12_InjectionDefense",
        is_valid=res.get("pass", False),
        score=res.get("score", 0.0),
        reason=res.get("reason", ""),
        floor_type="hard"
    )

def validate_f13_curiosity(question_count: int, alternative_count: int, novelty_score: float):
    query = "?" * question_count + " alternative " * alternative_count
    res = _v13(query, {})
    return FloorValidationResult(
        floor_id="F13_Curiosity",
        is_valid=res.get("pass", False),
        score=res.get("score", 0.0),
        reason=res.get("reason", ""),
        floor_type="soft"
    )

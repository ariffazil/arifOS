"""
arifosmcp/schemas/claim.py — Shared Claim Protocol (SCP v1.0)
════════════════════════════════════════════════════════════

Canonical data structure for domain witnesses (GEOX, WEALTH, WELL).
DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations
from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field

class UncertaintyClass(str, Enum):
    FACT = "FACT"
    ESTIMATE = "ESTIMATE"
    SPECULATION = "SPECULATION"

class RiskPotential(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class DomainWitness(str, Enum):
    GEOX = "GEOX"
    WEALTH = "WEALTH"
    WELL = "WELL"
    ARIFOS = "arifOS"

class Uncertainty(BaseModel):
    uncertainty_class: UncertaintyClass = Field(..., alias="class")
    confidence: float = Field(..., ge=0.0, le=1.0)

class Risk(BaseModel):
    reversible: bool
    harm_potential: RiskPotential
    human_decision_required: bool

class Authority(BaseModel):
    ai_decides: bool
    final_authority: str = "ARIF"

class GovernedClaim(BaseModel):
    claim: str
    domain: DomainWitness
    evidence: List[str] = []
    uncertainty: Uncertainty
    risk: Risk
    authority: Authority
    next_safe_action: str

    class Config:
        populate_by_name = True

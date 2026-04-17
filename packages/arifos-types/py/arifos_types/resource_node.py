"""
ResourceNode — 4-layer decision kernel
Geology → Engineering → Economics → Governance
DITEMPA BUKAN DIBERI
"""

from typing import Optional, List, Tuple
from pydantic import BaseModel
from arifos_types.epistemic import EpistemicTag


class DecisionContext(BaseModel):
    jurisdiction: str
    analysis_date: str
    market_regime: str
    model_version: str


class PetrophysSource(BaseModel):
    well_id: str
    depth_interval: Tuple[float, float]
    n_net_pay_samples: int
    epistemic: EpistemicTag
    model: str


class GeologyNode(BaseModel):
    volume_p10: Optional[float] = None
    volume_p50: float
    volume_p90: Optional[float] = None
    quality_index: float
    depth_m: float
    structure_complexity: float
    seal_confidence: Optional[float] = None
    charge_confidence: Optional[float] = None
    recoverability_confidence: Optional[float] = None
    risk_geo: float
    epistemic_geo: Optional[EpistemicTag] = None
    petrophys_source: Optional[PetrophysSource] = None


class EngineeringNode(BaseModel):
    recovery_factor: float
    capex_usd: float
    opex_usd_per_unit: float
    uptime: Optional[float] = None
    cycle_time_months: float
    infrastructure_distance_km: Optional[float] = None


class EconomicsNode(BaseModel):
    price_model: str
    discount_rate: float
    fiscal_terms: str
    npv_usd: Optional[float] = None
    irr: Optional[float] = None
    breakeven_usd_per_unit: Optional[float] = None
    sigma_market: Optional[float] = None


class GovernanceNode(BaseModel):
    policy_state: str
    admissibility_status: str
    carbon_cost_usd_per_tco2e: Optional[float] = None
    compliance_cost_usd: Optional[float] = None
    delay_risk: Optional[float] = None
    required_modifications: Optional[List[str]] = None
    sigma_policy: Optional[float] = None
    penalty_infinite: Optional[bool] = None
    peace2: Optional[float] = None
    maruah_score: Optional[float] = None


class ResourceNode(BaseModel):
    id: str
    decision_context: DecisionContext
    geology: GeologyNode
    engineering: EngineeringNode
    economics: EconomicsNode
    governance: GovernanceNode


def createEmptyResourceNode(id: str) -> ResourceNode:
    return ResourceNode(
        id=id,
        decision_context=DecisionContext(
            jurisdiction="",
            analysis_date="2026-04-18",
            market_regime="",
            model_version="v0.1",
        ),
        geology=GeologyNode(
            volume_p50=0,
            quality_index=0,
            depth_m=0,
            structure_complexity=0,
            risk_geo=1,
        ),
        engineering=EngineeringNode(
            recovery_factor=0,
            capex_usd=0,
            opex_usd_per_unit=0,
            cycle_time_months=0,
        ),
        economics=EconomicsNode(
            price_model="",
            discount_rate=0.1,
            fiscal_terms="",
        ),
        governance=GovernanceNode(
            policy_state="",
            admissibility_status="deferred",
        ),
    )
"""
arifOS v2.0 — Canonical Verdict Enumerations
═══════════════════════════════════════════════════════════════════════════
Defines the three primary seals (SEAL, HOLD, VOID, SABAR), the 13 canonical 
constitutional floors, and the metabolic telemetry schemas.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class SealType(str, Enum):
    """
    The four canonical seals of arifOS v2.0.
    Only SEAL allows progression to Tier 05 (Execution).
    """
    SEAL    = "SEAL"     # W³ ≥ 0.95, all Floors pass — proceed
    HOLD    = "HOLD"     # 888_HOLD — human veto/review required
    SABAR   = "SABAR"    # Wait — more evidence needed (Temporal Sabar)
    VOID    = "VOID"     # Hard Floor violation — blocked permanently


class VerdictState(str, Enum):
    """
    Detailed verdict states within the canonical seals.
    """
    # SEAL substates
    SEAL_CANONICAL = "SEAL_CANONICAL"      # High confidence, full compliance
    SEAL_QUALIFIED = "SEAL_QUALIFIED"      # Compliant with noted assumptions
    
    # HOLD substates
    HOLD_888 = "HOLD_888"                  # Human Architect intervention required
    HOLD_UNCERTAINTY = "HOLD_UNCERTAINTY"  # Ωₒᵣₜₕₒ < 0.95 or Peace² < 0.70
    HOLD_TEMPORAL = "HOLD_TEMPORAL"        # Waiting for data vintage refresh
    
    # VOID substates
    VOID_BREACH = "VOID_BREACH"            # Constitutional Floor violation
    VOID_HANTU = "VOID_HANTU"              # Shadow arifOS / Narrative Laundering
    VOID_IRREVERSIBLE = "VOID_IRREVERSIBLE" # Irreversible action without W³
    
    # SABAR substates
    SABAR_EPISTEMIC = "SABAR_EPISTEMIC"    # Waiting for grounded truth
    SABAR_GEOPOLITICAL = "SABAR_GEOPOLITICAL" # Waiting for external stability


class FloorState(str, Enum):
    """
    Metabolic states for each of the 13 floors.
    """
    INACTIVE = "INACTIVE"
    ACTIVE   = "ACTIVE"
    COMPLETE = "COMPLETE"
    HOLD     = "HOLD"
    VOID     = "VOID"


class FloorName(str, Enum):
    """
    The 13 canonical floors of arifOS v2.0.
    Ordered by the Gödel-Locked Cognitive Stack.
    """
    F1_REVERSIBILITY = "F1_REVERSIBILITY"   # κᵣ — Can we undo this?
    F2_TRUTH         = "F2_TRUTH"           # Λ2 — Physical grounding
    F3_TRI_WITNESS   = "F3_TRI_WITNESS"     # W³ — H·A·E alignment
    F4_CLARITY       = "F4_CLARITY"         # ΔS — Entropy reduction
    F5_ORTHOGONALITY = "F5_ORTHOGONALITY"   # Ω — Lane independence
    F6_MARUAH        = "F6_MARUAH"          # Peace² — Human dignity
    F7_HUMILITY      = "F7_HUMILITY"        # κ_H — Uncertainty declared
    F8_LOGIC         = "F8_LOGIC"           # Internal consistency
    F9_ANTI_HANTU    = "F9_ANTI_HANTU"      # Shadow detection
    F10_AMANAH       = "F10_AMANAH"         # Fiduciary duty
    F11_IDENTITY     = "F11_IDENTITY"       # Session anchoring
    F12_CONTINUITY   = "F12_CONTINUITY"     # Passive monitoring
    F13_SOVEREIGNTY  = "F13_SOVEREIGNTY"    # Human Architect Veto


class PipelineStage(int, Enum):
    """
    The 000→999 metabolic stages of arifOS v2.0.
    """
    S000_INIT   = 0
    S111_SENSE  = 111
    S333_MIND   = 333
    S444_KERNEL = 444
    S666_HEART  = 666
    S777_FORGE  = 777
    S888_JUDGE  = 888
    S999_VAULT  = 999


class ConstitutionalThresholds(BaseModel):
    """
    Numerical thresholds for v2.0 metabolic gates.
    """
    omega_min: float         = 0.95   # Ω Orthogonality
    peace2_floor: float      = 0.70   # Ethical Stability
    w3_min: float            = 0.95   # Tri-Witness Consensus
    delta_s_ceiling: float   = 0.20   # Entropy Limit
    kappa_r_phys_floor: float = 0.40  # Reversibility Floor
    kappa_h_low: float       = 0.03   # Humility Band Min
    kappa_h_high: float      = 0.15   # Humility Band Max


class FloorMetrics(BaseModel):
    """
    Metrics for a single floor execution.
    """
    floor_number: int = Field(..., ge=1, le=13)
    floor_name: FloorName = Field(...)
    state: FloorState = Field(default=FloorState.INACTIVE)
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    violation: Optional[str] = None
    
    @field_validator('floor_number')
    @classmethod
    def validate_floor(cls, v: int) -> int:
        if not 1 <= v <= 13:
            raise ValueError(f"Floor must be 1-13, got {v}")
        return v


class KernelMetrics(BaseModel):
    """
    Unified Telemetry from 13-floor kernel execution.
    """
    omega_ortho: float = Field(default=1.0, ge=0.0, le=1.0)
    delta_s: float = Field(default=0.0)
    peace2: float = Field(default=1.0)
    kappa_r: float = Field(default=1.0)
    w3: float = Field(default=1.0, ge=0.0, le=1.0)
    shadow_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    witness_vector: Dict[str, float] = Field(
        default_factory=lambda: {"human": 1.0, "ai": 1.0, "earth": 1.0}
    )
    
    floors_passed: List[FloorName] = Field(default_factory=list)
    floors_violated: List[FloorName] = Field(default_factory=list)
    
    overall_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class VerdictResult(BaseModel):
    """
    Complete arifOS v2.0 verdict result.
    """
    epoch: str = "2026.4.16-CANONICAL"
    session_id: str
    verdict: SealType = Field(default=SealType.HOLD)
    state: VerdictState = Field(default=VerdictState.HOLD_888)
    metrics: KernelMetrics = Field(default_factory=KernelMetrics)
    explanation: str = Field(default="")
    recommendations: List[str] = Field(default_factory=list)
    
    def is_sealed(self) -> bool:
        """Check if execution is authorized."""
        return self.verdict == SealType.SEAL
    
    def is_void(self) -> bool:
        """Check if constitution is breached."""
        return self.verdict == SealType.VOID

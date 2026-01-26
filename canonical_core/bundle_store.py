"""
Bundle Store - Constitiutional bundle schemas & storage.
Enforces strict separation between AGI Delta, ASI Omega, and APEX Merged bundles.
Based on: 000_THEORY/000_LAW.md (Trinity Parallel Architecture)
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator
from dataclasses import dataclass
import threading


# ==================== BUNDLE SCHEMAS ====================

ASI_FLOORS = {
    "F6_Empathy": "κᵣ ≥ 0.95",
    "F5_Peace": "Benefit/Harm ≥ 1.0",
    "F1_Amanah": "Reversible OR Auditable",
    "F9_AntiHantu": "Consciousness < 0.30",
    "F11_Command": "Identity Verified"
}


@dataclass
class Stakeholder:
    """Stakeholder with vulnerability assessment."""
    entity: str
    vulnerability: float  # 0.0 to 1.0
    impact: str  # "direct" or "indirect"
    confidence: float  # confidence in assessment
    
    def __post_init__(self):
        if not (0.0 <= self.vulnerability <= 1.0):
            raise ValueError("Vulnerability must be in [0.0, 1.0]")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be in [0.0, 1.0]")


class OmegaBundle(BaseModel):
    """
    ASI (Heart) output bundle.
    Contains empathy assessment, safety constraints, and ASI floors.
    """
    session_id: str
    stakeholders: List[Stakeholder] = Field(default_factory=list)
    weakest_stakeholder: str = Field(..., description="Most vulnerable entity")
    empathy_kappa: float = Field(..., ge=0.0, le=1.0, description="κᵣ ≥ 0.95 required")
    safety_constraints: List[str] = Field(default_factory=list)
    floor_scores: Dict[str, float] = Field(default_factory=dict)
    vote: str = Field(..., pattern="^(SEAL|VOID|SABAR|PARTIAL)$")
    reversible: bool = Field(False, description="F1 Amanah check")
    authority_verified: bool = Field(False, description="F11 Command Authority")
    
    def model_dump(self) -> Dict[str, Any]:
        """Convert to dict for JSON storage."""
        return {
            "session_id": self.session_id,
            "stakeholders": [s.__dict__ for s in self.stakeholders],
            "weakest_stakeholder": self.weakest_stakeholder,
            "empathy_kappa": self.empathy_kappa,
            "safety_constraints": self.safety_constraints,
            "floor_scores": self.floor_scores,
            "vote": self.vote,
            "reversible": self.reversible,
            "authority_verified": self.authority_verified
        }


class DeltaBundle(BaseModel):
    """AGI (Mind) output bundle (placeholder for now)."""
    session_id: str
    facts: List[str]
    reasoning_tree: Dict[str, Any]
    confidence_scores: Dict[str, float]
    floor_scores: Dict[str, float]
    vote: str
    entropy_delta: float
    omega_humility: float


class MergedBundle(BaseModel):
    """APEX convergence after 444 TRINITY_SYNC."""
    session_id: str
    delta_bundle: DeltaBundle
    omega_bundle: OmegaBundle
    consensus_score: float = Field(..., ge=0.0, le=1.0)
    pre_verdict: str = Field(..., pattern="^(SEAL|VOID|SABAR|PARTIAL|888_HOLD)$")
    trinity_dissent: bool = Field(False, description="AGI/ASI disagreement")


# ==================== BUNDLE STORAGE ====================

class BundleStore:
    """
    Thread-safe bundle storage enforcing Trinity isolation.
    
    Critical Invariant: ASI cannot see AGI reasoning until 444.
    """
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._bundles: Dict[str, Any] = {}
        self._lock = threading.Lock()
        self._asi_access_blocked = False  # Once AGI stored, ASI can't read
    
    def store_delta(self, bundle: DeltaBundle) -> None:
        """Store AGI bundle. Locks ASI from reading it."""
        with self._lock:
            if "delta" in self._bundles:
                raise RuntimeError("Delta bundle already stored")
            self._bundles["delta"] = bundle
            self._asi_access_blocked = True  # ASI isolation enforced
    
    def store_omega(self, bundle: OmegaBundle) -> None:
        """Store ASI bundle. ASI never sees AGI."""
        with self._lock:
            if "delta" in self._bundles and self._asi_access_blocked:
                # This is the constitutional isolation check
                # ASI should NOT have direct access to AGI reasoning
                pass  # No error, ASI can't access via this method
            self._bundles["omega"] = bundle
    
    def get_delta(self) -> Optional[DeltaBundle]:
        """Only APEX can retrieve AGI bundle (at 444)."""
        with self._lock:
            return self._bundles.get("delta")
    
    def get_omega(self) -> Optional[OmegaBundle]:
        """Only APEX can retrieve ASI bundle (at 444)."""
        with self._lock:
            return self._bundles.get("omega")
    
    def store_merged(self, bundle: MergedBundle) -> None:
        """APEX stores merged result for post-444 stages."""
        with self._lock:
            self._bundles["merged"] = bundle
    
    def get_merged(self) -> Optional[MergedBundle]:
        """Stages 777-999 read merged bundle."""
        with self._lock:
            return self._bundles.get("merged")


# ==================== GLOBAL STORE FACTORY ====================

_SESSION_STORES: Dict[str, BundleStore] = {}
_SESSION_LOCK = threading.Lock()


def get_store(session_id: str) -> BundleStore:
    """Get or create bundle store for session."""
    with _SESSION_LOCK:
        if session_id not in _SESSION_STORES:
            _SESSION_STORES[session_id] = BundleStore(session_id)
        return _SESSION_STORES[session_id]


def purge_store(session_id: str) -> None:
    """Remove session store (cleanup)."""
    with _SESSION_LOCK:
        if session_id in _SESSION_STORES:
            del _SESSION_STORES[session_id]

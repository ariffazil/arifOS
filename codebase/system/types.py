"""
arifOS Constitutional Types (v53.0.0)
Shared types to prevent circular dependencies.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

class Verdict(Enum):
    """
    The Trinity of Constitutional Verdicts.
    Simplified v53.0 Architecture.
    """
    SEAL = "SEAL"      # Approved / Proceed (includes conditional pass)
    SABAR = "SABAR"    # Paused / Wait / Blocked (includes holds & hypervisor)
    VOID = "VOID"      # Rejected / Stop (hard constitutional failure)

    def __str__(self) -> str:
        return self.value

@dataclass
class Metrics:
    """Constitutional Metrics."""
    truth: float = 1.0
    delta_s: float = 0.0
    peace_squared: float = 1.0
    kappa_r: float = 0.95
    omega_0: float = 0.04
    amanah: bool = True
    tri_witness: float = 0.95
    rasa: bool = True
    anti_hantu: bool = True
    psi: Optional[float] = 1.0

@dataclass
class FloorCheckResult:
    """Result from a single floor check."""
    floor_id: str
    floor_name: str
    threshold: float
    value: float
    passed: bool
    is_hard: bool = True
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ApexVerdict:
    """Result from APEX judgment."""
    verdict: Verdict
    pulse: float = 1.0
    reason: str = ""
    violated_floors: List[str] = field(default_factory=list)
    compass_alignment: Dict[str, bool] = field(default_factory=dict)
    genius_stats: Dict[str, float] = field(default_factory=dict)
    proof_hash: Optional[str] = None
    cooling_metadata: Optional[Dict[str, Any]] = None
    sub_verdict: Optional[str] = None  # Nuance (e.g. "CONDITIONAL", "PHOENIX_HOLD")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "verdict": self.verdict.value,
            "sub_verdict": self.sub_verdict,
            "pulse": self.pulse,
            "reason": self.reason,
            "violated_floors": self.violated_floors,
            "compass_alignment": self.compass_alignment,
            "genius_stats": self.genius_stats,
            "proof_hash": self.proof_hash,
            "cooling_metadata": self.cooling_metadata
        }

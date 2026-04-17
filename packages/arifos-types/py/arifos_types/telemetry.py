"""
TelemetryPayload — Structured telemetry for VAULT999 sealing
DITEMPA BUKAN DIBERI
"""

import hashlib
from typing import Optional, List
from pydantic import BaseModel
from arifos_types.epistemic import EpistemicTag
from arifos_types.verdict import Verdict


class Witness(BaseModel):
    human: str
    ai: str
    earth: str


class TelemetryPayload(BaseModel):
    epoch: float
    session_id: str
    pipeline_stage: str
    dS: float
    peace2: float
    kappa_r: float
    shadow: float
    confidence: float
    psi_le: float
    verdict: Verdict
    witness: Witness
    qdf: float
    floor_violations: List[str]
    epistemic: Optional[EpistemicTag] = None
    hash: str


DEFAULT_TELEMETRY = {
    "dS": 0.1,
    "peace2": 1.0,
    "kappa_r": 0.8,
    "shadow": 0.1,
    "confidence": 0.8,
    "psi_le": 0.8,
    "qdf": 0.8,
    "floor_violations": [],
}


def createTelemetryHash(
    epoch: float,
    session_id: str,
    pipeline_stage: str,
    verdict: str,
    qdf: float,
    peace2: float,
) -> str:
    input_str = f"{epoch}{session_id}{pipeline_stage}{verdict}{qdf}{peace2}"
    return hashlib.sha256(input_str.encode()).hexdigest()[:16]
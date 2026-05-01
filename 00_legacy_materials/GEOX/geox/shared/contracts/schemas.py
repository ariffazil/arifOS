from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, List, Any
from pydantic import BaseModel

class UnitRef(BaseModel):
    name: str
    symbol: str
    quantity: str

class XYPoint(BaseModel):
    x: float
    y: float

class XYZPoint(BaseModel):
    x: float
    y: float
    z: float

class BoundingBox(BaseModel):
    min: XYZPoint
    max: XYZPoint
    crs: Optional[str] = None

class VerticalDomain(str, Enum):
    twt_ms = "twt_ms"
    tvdss_m = "tvdss_m"
    md_m = "md_m"
    tvd_m = "tvd_m"

class GeoContext(BaseModel):
    crsName: str
    crsEpsg: int
    verticalDomain: VerticalDomain
    isTimeDomain: bool
    units: Dict[str, UnitRef]

class EvidenceKind(str, Enum):
    well = "well"
    seismic = "seismic"
    map = "map"
    log = "log"
    top = "top"
    verdict = "verdict"

class EvidenceRef(BaseModel):
    id: str
    kind: EvidenceKind
    sourceUri: str
    timestamp: datetime
    version: Optional[str] = None

class EvidenceObject(BaseModel):
    ref: EvidenceRef
    context: GeoContext
    payload: Any
    metadata: Optional[Dict[str, Any]] = None

class TransformStatus(str, Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"

class TransformRequest(BaseModel):
    requestId: str
    sourceContext: GeoContext
    targetContext: GeoContext
    dataToTransform: List[XYZPoint]
    method: str = "bilinear"

class TransformResult(BaseModel):
    requestId: str
    transformedData: List[XYZPoint]
    errorRms: Optional[float] = None
    status: TransformStatus

class VerdictStatus(str, Enum):
    SEAL = "SEAL"
    PARTIAL = "PARTIAL"
    SABAR = "SABAR"
    VOID = "VOID"
    HOLD_888 = "888_HOLD"

class RiskFactor(BaseModel):
    key: str
    impact: float
    reason: str

class RiskAssessment(BaseModel):
    score: float # 0 to 1
    factors: List[RiskFactor]

class Verdict(BaseModel):
    verdictId: str
    intentId: str
    status: VerdictStatus
    confidence: float
    author: str
    rationale: str
    risk: RiskAssessment
    auditTraceId: str
    timestamp: datetime

class AuditEvent(BaseModel):
    eventId: str
    actor: str
    tool: str
    evidenceRefs: List[str]
    verdictId: Optional[str] = None
    inputSnapshot: Any
    outputSnapshot: Any
    timestamp: datetime

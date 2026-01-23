from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class GovernRequest(BaseModel):
    """
    Request payload for the /govern endpoint.
    Represents an input to be metabolized by the 000-999 loop.
    """
    input: str = Field(..., description="The raw input text or data to be processed")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context metadata")
    stakeholders: Optional[List[str]] = Field(default_factory=list, description="Explicit stakeholders for Empathy checks")
    authority_token: Optional[str] = Field(None, description="JWT or nonce for F11 Command Authority")

class VerdictFloors(BaseModel):
    """
    Constitutional floor scores returned in the verdict.
    """
    F1_Amanah: bool
    F2_Truth: float
    F3_Peace2: float
    F4_Clarity: float
    F5_Peace: float = Field(..., alias="F5_Peace2") # Alias for compatibility
    F6_Empathy: float
    F7_Humility: float
    F8_Genius: Optional[float] = None
    F9_AntiHantu: float
    F10_Ontology: bool
    F11_Authority: bool
    F12_Injection: float
    F13_Curiosity: float

class GovernResponse(BaseModel):
    """
    Response payload from the /govern endpoint.
    Contains the sealed verdict and cryptographic proof.
    """
    verdict: str = Field(..., description="SEAL, PARTIAL, SABAR, or VOID")
    response: Optional[str] = Field(None, description="The generated response/action")
    floors: Dict[str, Any] = Field(..., description="Scores for all constitutional floors")
    cooling_tier: str = Field(..., description="assigned cooling tier (e.g. 0h, 72h)")
    zkpc_receipt: Optional[str] = Field(None, description="Merkle root hash or zk proof")
    session_id: str = Field(..., description="Unique ID for this governance session")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class HealthStatus(BaseModel):
    status: str
    version: str
    trinity_coherence: float
    floors_active: int

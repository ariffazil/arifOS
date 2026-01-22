from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolAttribute(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

class ToolListResponse(BaseModel):
    tools: List[ToolAttribute]

class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    approval_token: Optional[str] = None

class FloorScore(BaseModel):
    floor: str
    score: float
    reason: str

class GovernanceVerdict(BaseModel):
    verdict: str  # SEAL, PARTIAL, VOID, SABAR, 888_HOLD
    floor_scores: List[FloorScore]
    requires_approval: bool = False
    consequences: Optional[str] = None
    approval_nonce: Optional[str] = None

class ToolCallResponse(BaseModel):
    tool_name: str
    status: str  # success, error, governed_halt
    output: Optional[Any] = None
    governance: GovernanceVerdict
    error: Optional[str] = None

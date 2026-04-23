"""
AgentMessage — A2A communication envelope
DITEMPA BUKAN DIBERI
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, field_validator
from arifos_types.epistemic import EpistemicTag


class MessageType(str):
    TASK = "task"
    RESULT = "result"
    QUERY = "query"
    ACK = "ack"
    HOLD = "hold"
    ABORT = "abort"
    STATUS = "status"


class AgentMessage(BaseModel):
    message_id: str
    sender_id: str
    receiver_id: str
    session_id: str
    task_id: str
    subtask_id: Optional[str] = None
    parent_message_id: Optional[str] = None
    message_type: str
    payload: Dict[str, Any]
    schema_ref: Optional[str] = None
    maruah_score: float
    epistemic: EpistemicTag
    floor_violations: List[str] = []
    irreversible: bool = False
    timestamp: str
    ttl_seconds: int = 300
    expires_at: str
    ack_required: bool = False
    ack_received: bool = False
    ack_timestamp: Optional[str] = None


class SendAgentMessageInput(BaseModel):
    sender_id: str
    receiver_id: str
    task_id: str
    session_id: str
    message_type: str
    payload: Dict[str, Any]
    maruah_score: float
    epistemic: Optional[EpistemicTag] = None
    irreversible: bool = False
    ttl_seconds: int = 300


class SendAgentMessageOutput(BaseModel):
    message_id: str
    status: str
    rejection_reason: Optional[str] = None
    hold_triggered: bool = False
    expires_at: str
    vault_record_id: str


def validateAgentMessage(msg: AgentMessage) -> List[str]:
    errors = []

    if msg.maruah_score < 0.5:
        errors.append("MARUAH_FAIL: maruah_score must be >= 0.5")

    if msg.ttl_seconds > 3600:
        errors.append("TTL_EXCEEDED: ttl_seconds max is 3600")

    if msg.irreversible and not msg.ack_required:
        errors.append("IRREVERSIBLE_REQUIRES_ACK: irreversible messages must set ack_required=true")

    return errors
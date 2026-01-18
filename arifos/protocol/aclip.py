"""
arifOS aCLIP (arifOS Command Line Interface Protocol)
Canonical Schema - Component 1
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Literal, Optional

from .codes import Role, StageCode, Verdict


@dataclass
class ACLIPMessage:
    """
    Canonical 000-999 Metabolic Message Schema
    Source of Truth: REPO_STRUCTURE_v49.md
    """
    aclip_version: str = "v49"
    id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:8]}")
    stage: StageCode = StageCode.INIT_000
    source: str = "mcp_gateway"
    target: str = "vault_server"

    payload: Dict[str, Any] = field(default_factory=dict)

    metadata: Dict[str, Any] = field(default_factory=lambda: {
        "timestamp": datetime.utcnow().isoformat(),
        "trace_id": f"trace_{uuid.uuid4().hex[:8]}",
        "priority": "normal"
    })

    def validate(self) -> bool:
        """Basic schema validation"""
        if self.aclip_version != "v49":
            raise ValueError(f"Invalid protocol version: {self.aclip_version}")
        return True

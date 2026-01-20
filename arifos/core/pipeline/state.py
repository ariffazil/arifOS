"""
arifos.core/pipeline/state.py

The Vector State.
Carries the 3-Axis Truth across the 9 Stages.

Axis 1: AGI Verdict (Mind)
Axis 2: ASI Verdict (Heart)
Axis 3: APEX Verdict (Soul)

DITEMPA BUKAN DIBERI - Forged v46.2
"""

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class PipelineStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    SEALED = "SEALED"
    FAILED = "FAILED"

@dataclass
class PipelineState:
    """
    The Sovereign State Object.
    Passed through 000-999.
    """
    # Identity
    job_id: str
    session_id: str

    # Input/Output
    query: str
    parsed_query: str = ""
    draft_reasoning: str = ""
    empathetic_draft: str = ""
    aligned_content: str = ""
    final_response: str = ""

    # Metabolic State
    current_stage: str = "000"
    status: PipelineStatus = PipelineStatus.INITIALIZED
    stage_trace: List[str] = field(default_factory=list)
    stage_times: Dict[str, float] = field(default_factory=dict)

    # Entropy (Thermodynamics)
    s_input: float = 0.0
    s_output: float = 0.0
    delta_s: float = 0.0

    # The 3-Axis Vector (The Soul of the State)
    # Axis 1: Mind
    agi_verdict: Dict[str, Any] = field(default_factory=dict)

    # Axis 2: Heart
    asi_verdict: Dict[str, Any] = field(default_factory=dict)

    # Axis 3: Soul (The Constraint)
    apex_verdict: Dict[str, Any] = field(default_factory=dict)

    # Context & Memory
    context_blocks: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)

    # Telemetry
    start_time: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "stage": self.current_stage,
            "trace": self.stage_trace,
            "vector": {
                "agi": self.agi_verdict,
                "asi": self.asi_verdict,
                "apex": self.apex_verdict
            },
            "warnings": self.warnings
        }

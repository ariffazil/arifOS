from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class ContinuityRecord(BaseModel):
    """
    Hardened continuity guarantee — every tool output carries this.

    This record allows for the full reconstruction of the inference chain,
    ensuring that no 'hallucinated' shortcuts are taken between tools.
    """

    chain_id: str = Field(default_factory=lambda: f"geox-chain-{uuid.uuid4().hex[:8]}")
    previous_tool: str | None = None
    previous_output_id: str | None = None
    artifact_continuity: bool = True  # True if all image paths exist and are readable
    governance_version: str = "0.4.0-identity-forge"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    floors_enforced: list[str] = Field(
        default_factory=lambda: [
            "F1_amanah",
            "F4_clarity",
            "F7_humility",
            "F9_anti_hantu",
            "F13_sovereign",
        ]
    )


class HardenedToolOutput(BaseModel):
    """
    Every GEOX tool now returns this wrapper for continuity.

    This ensures that the 'Earth Witness' output is always structured,
    audit-ready, and verifiable by the arifOS kernel.
    """

    result: Any  # The tool-specific result (usually a BaseModel)
    artifacts: dict[str, str] = Field(default_factory=dict)  # image paths / base64 strings
    continuity: ContinuityRecord
    contrast_metadata: dict | None = None
    verdict: Literal["SEAL", "QUALIFY", "HOLD", "GEOX_BLOCK"] = "QUALIFY"
    telemetry: dict = Field(
        default_factory=lambda: {
            "seal": "DITEMPA BUKAN DIBERI",
            "organ": "GEOX",
            "role": "Earth Witness",
        }
    )

    model_config = {"arbitrary_types_allowed": True}

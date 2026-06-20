"""
Cedar Bridge — Phase 2 stub.

Cedar (AWS-style authorization language) is recommended for Phase 2.
This stub is a placeholder that always returns ALLOW with override=True,
preserving constitutional chain (arifOS still decides).
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class CedarBridge:
    """Phase 2 placeholder. Will integrate with Rust Cedar engine via PyO3."""

    enabled: bool = False

    async def evaluate(
        self, principal: str, action: str, resource: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        return {
            "decision": "ALLOW",
            "override": True,  # arifOS always has override
            "phase": 2,
            "note": "Cedar bridge is Phase 2; using OPA today",
        }

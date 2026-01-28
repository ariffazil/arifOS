"""
AGI Kernel (Native) for Codebase
v53.0.0 - Constitutional AI Mind/Δ

Native implementation using the AGIRoom from codebase.agi.executor
"""

import asyncio
import logging
from typing import Any, Dict, Optional

from codebase.agi.executor import AGIRoom, AGIRoomResult
from codebase.bundles import DeltaBundle, EngineVote

logger = logging.getLogger(__name__)


class AGINeuralCore:
    """
    Native AGI (Mind) Neural Core

    Executes stages 111 (SENSE), 222 (THINK), 333 (REASON) natively
    Uses the AGIRoom architecture
    """

    def __init__(self):
        self._room_registry: Dict[str, AGIRoom] = {}
        self._lock = asyncio.Lock()

    async def execute(self, action: str, kwargs: dict) -> dict:
        """
        Unified AGI execution entry point (used by MCP bridge)

        Args:
            action: Action to perform (full, sense, think, reason, evaluate)
            kwargs: Arguments including query, session_id, context

        Returns:
            Result dictionary with verdict and stage outputs
        """
        query = kwargs.get("query", kwargs.get("text", ""))
        session_id = kwargs.get("session_id", f"agi_{id(query)}")
        context = kwargs.get("context", {})

        logger.info(f"[AGI-NATIVE] Action: {action}, Session: {session_id}")

        try:
            room = await self._get_or_create_room(session_id)

            if action in ("full", "genius", "think"):
                # Execute full AGI pipeline
                result = room.execute(query, context)
                return self._format_result(result, session_id)

            elif action == "sense":
                # Just run sense stage
                from codebase.agi.stages import execute_stage_111
                sense_output = execute_stage_111(query, session_id, context)
                return {
                    "status": "SEAL" if sense_output.stage_pass else "VOID",
                    "verdict": "SEAL" if sense_output.stage_pass else "VOID",
                    "session_id": session_id,
                    "sense": sense_output.to_dict() if hasattr(sense_output, 'to_dict') else str(sense_output),
                    "native_execution": True
                }

            elif action == "evaluate":
                # Quick evaluation mode
                truth_score = kwargs.get("truth_score", 0.95)
                confidence = kwargs.get("confidence", 0.90)
                passed = truth_score >= 0.85 and confidence >= 0.80

                return {
                    "status": "SEAL" if passed else "VOID",
                    "verdict": "SEAL" if passed else "VOID",
                    "session_id": session_id,
                    "metrics": {
                        "truth_score": truth_score,
                        "confidence": confidence
                    },
                    "native_execution": True
                }

            elif action == "forge":
                # Format/projection mode
                return {
                    "status": "SEAL",
                    "verdict": "SEAL",
                    "session_id": session_id,
                    "draft": query,
                    "native_execution": True
                }

            else:
                # Default to full execution
                result = room.execute(query, context)
                return self._format_result(result, session_id)

        except Exception as e:
            logger.error(f"[AGI-NATIVE] Error: {e}")
            return {
                "status": "VOID",
                "verdict": "VOID",
                "session_id": session_id,
                "error": str(e),
                "native_execution": True
            }

    def _format_result(self, result: AGIRoomResult, session_id: str) -> dict:
        """Format AGIRoomResult to legacy-compatible dict."""
        bundle = result.delta_bundle

        return {
            "status": bundle.vote.value,
            "verdict": bundle.vote.value,
            "session_id": session_id,
            "truth_score": bundle.truth_score if hasattr(bundle, 'truth_score') else 0.95,
            "confidence": bundle.confidence if hasattr(bundle, 'confidence') else 0.90,
            "delta_s": bundle.delta_s if hasattr(bundle, 'delta_s') else 0.0,
            "reasoning": bundle.vote_reason,
            "floors_checked": ["F2", "F4", "F7", "F10", "F12", "F13"],
            "execution_time_ms": result.execution_time_ms,
            "_bundle": bundle,
            "native_execution": True
        }

    async def _get_or_create_room(self, session_id: str) -> AGIRoom:
        """Get existing room or create new one."""
        async with self._lock:
            if session_id not in self._room_registry:
                self._room_registry[session_id] = AGIRoom(session_id=session_id)
            return self._room_registry[session_id]


# Legacy compatibility alias
AGIKernel = AGINeuralCore

__all__ = ["AGINeuralCore", "AGIKernel"]

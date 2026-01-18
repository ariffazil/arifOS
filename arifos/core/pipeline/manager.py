"""
arifos_core/pipeline/manager.py

The Pipeline Orchestrator.
Drivers the Sovereign Cleanse (000 -> 999).

Features:
    - 9-Stage Non-Linear Execution
    - Stage Module Loading
    - Vector State Management

DITEMPA BUKAN DIBERI - Forged v46.2
"""

import importlib
import logging
from typing import Any, Dict, Optional

from arifos.core.pipeline.state import PipelineState, PipelineStatus

# Correct stage mapping
STAGE_MODULES = {
    "000": "arifos_core.000_void.stage",
    "111": "arifos_core.111_sense.stage",
    "222": "arifos_core.222_reflect.stage",
    "333": "arifos_core.333_reason.stage",
    "444": "arifos_core.444_evidence.stage",
    "555": "arifos_core.555_empathize.stage",
    "666": "arifos_core.666_align.stage",
    "777": "arifos_core.777_forge.stage",
    "888": "arifos_core.888_judge.stage",
    "999": "arifos_core.999_seal.stage",
}

class PipelineManager:
    def __init__(self):
        self.logger = logging.getLogger("arifos.pipeline")

    def execute(self, query: str, job_id: str = "unsigned") -> Dict[str, Any]:
        """
        Execute the full Sovereign Pipeline.
        """
        # Initialize State
        state = PipelineState(
            job_id=job_id,
            session_id="session_v46", # In real impl this comes from env
            query=query
        )

        # Convert state to dict for stage processing (Stage modules expect dict context for now)
        # TODO: Refactor stages to accept PipelineState object directly for type safety.
        # For Phase 2 compatibility with just-written stages, we use dict.
        context = state.to_dict()
        context["user_input"] = query # Map input for 111
        # Re-attach the state object reference if stages need methods (not needed yet)

        # The Sovereign Loop
        pipeline_sequence = ["000", "111", "222", "333", "444", "555", "666", "777", "888", "999"]

        try:
            for stage_id in pipeline_sequence:
                # Early Exit / Branching Check
                # If a previous stage set a "jump" or "block" status, handle it.
                if context.get("status", "").startswith("BLOCKED"):
                    self.logger.warning(f"Pipeline BLOCKED at {state.current_stage}")
                    break

                # 888_HOLD logic from 111 crisis detection
                if context.get("verdict") == "888_HOLD":
                     if stage_id not in ["888", "999"]:
                         continue # Skip to Judge

                module_name = STAGE_MODULES.get(stage_id)
                if not module_name:
                    continue

                # Dynamically impoprt and run
                mod = importlib.import_module(module_name)
                execute_func = getattr(mod, "execute_stage", None)

                if execute_func:
                    # Execute Stage
                    self.logger.info(f"Executing {stage_id}...")
                    context = execute_func(context)
                else:
                    self.logger.error(f"Stage {stage_id} missing execute_stage function")

        except Exception as e:
            self.logger.error(f"Pipeline CRITICAL FAIL: {e}", exc_info=True)
            context["status"] = "FAILED"
            context["error"] = str(e)

        return context

# Singleton Entry Point
_MANAGER = PipelineManager()

def execute_pipeline_v46(query: str, job_id: str = "unsigned") -> Dict[str, Any]:
    return _MANAGER.execute(query, job_id)

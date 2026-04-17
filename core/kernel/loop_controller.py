"""
core/kernel/loop_controller.py — The SabarLoop (Safe Autonomy Throttle).

This module implements the execution loop that drives the Planner's DAG,
governed by the Constitutional Floors and the Sabar Protocol.

Author: Muhammad Arif bin Fazil
Status: Implementation (v2026.04.16-IGNITION)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from core.kernel.planner import Plan, Planner, Task

# We assume the organs expose async interfaces as described in _0_init.py etc.
from core.organs import _0_init, _1_agi, _2_asi, _3_apex, _4_vault

# arifOS Core Imports
from core.shared.types import Verdict

logger = logging.getLogger("arifOS.SabarLoop")

@dataclass
class LoopStepResult:
    task_id: str
    verdict: Verdict
    receipt: dict[str, Any] | None = None
    entropy_delta: float = 0.0
    message: str = ""
    timestamp: float = field(default_factory=time.time)

@dataclass
class LoopRunResult:
    plan_id: str
    status: str  # COMPLETED, HALTED, SABAR_WAIT, FAILED, RUNNING
    iterations: int
    final_entropy: float
    history: list[LoopStepResult] = field(default_factory=list)

class SabarLoopController:
    """
    The 'Metabolic Pump' of arifOS. 
    Drives autonomous execution while enforcing entropy and budget floors.
    
    Philosophy: Governed Power. 
    The loop does not decide law; it cycles through the law's checkpoints.
    """

    def __init__(
        self, 
        max_iterations: int = 3, 
        entropy_threshold: float = 0.05,
        budget: float = 100.0,
        sabar_retry_limit: int = 1
    ):
        self.max_iterations = max_iterations
        self.entropy_threshold = entropy_threshold
        self.budget_remaining = budget
        self.sabar_retry_limit = sabar_retry_limit
        
        self.entropy_window: list[float] = []
        self.current_iteration = 0
        self.task_retries: dict[str, int] = {}

    async def run(self, plan: Plan, planner: Planner) -> LoopRunResult:
        """
        Executes the plan DAG until completion, exhaustion, or HOLD.
        """
        history = []
        status = "RUNNING"
        self.current_iteration = 0

        logger.info(f"Starting SabarLoop for Plan {plan.id} (Goal: {plan.goal})")

        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            
            # 1. Pull next executable tasks from Planner (Nodes with dependencies met)
            ready_tasks = planner.get_current_tasks(plan.id)
            if not ready_tasks:
                logger.info(f"Plan {plan.id} COMPLETED: No more executable tasks.")
                status = "COMPLETED"
                break

            # v1: Sequential execution of ready tasks for maximum governance control
            task = ready_tasks[0]
            logger.info(f"Iteration {self.current_iteration}: Executing Task {task.id} - {task.description}")
            
            # 2. Execute the Metabolic Cycle (000 -> 999)
            step_result = await self.step(task, plan)
            history.append(step_result)

            # 3. Handle Verdicts & State Transitions
            if step_result.verdict == Verdict.HOLD:
                logger.warning(f"888 HOLD triggered on Task {task.id}. Halting loop.")
                status = "HALTED"
                planner.update_task_status(plan.id, task.id, "FAILED", step_result.message)
                break
            
            if step_result.verdict == Verdict.VOID:
                logger.error(f"Security VOID on Task {task.id}. Emergency shutdown.")
                status = "FAILED"
                planner.update_task_status(plan.id, task.id, "FAILED", "VOID Verdict")
                break
            
            if step_result.verdict == Verdict.SABAR:
                retries = self.task_retries.get(task.id, 0)
                if retries < self.sabar_retry_limit:
                    logger.info(f"SABAR verdict on Task {task.id}. Initiating repair cycle {retries+1}/{self.sabar_retry_limit}")
                    self.task_retries[task.id] = retries + 1
                    # Repair: Update task description with feedback for next iteration
                    task.description = f"RETRY (Feedback: {step_result.message}): {task.description}"
                    self.current_iteration -= 1 # Repair cycles don't consume iteration budget in v1
                    continue
                else:
                    logger.warning(f"SABAR retry limit reached for Task {task.id}. Waiting for human.")
                    status = "SABAR_WAIT"
                    planner.update_task_status(plan.id, task.id, "PENDING", "SABAR Retry Limit Reached")
                    break

            # 4. Success: Update Planner and Metrics
            if step_result.verdict == Verdict.SEAL:
                planner.update_task_status(plan.id, task.id, "COMPLETED", step_result.receipt)
                self.budget_remaining -= 1.0 # Simple cost model
                
                # Check Entropy Trend (Sliding Window of 3)
                if self._is_entropy_runaway(step_result.entropy_delta):
                    logger.warning("Entropy runaway detected. Cooling required.")
                    status = "HALTED"
                    break

            if self.budget_remaining <= 0:
                logger.warning("Compute budget exhausted.")
                status = "HALTED"
                break

        return LoopRunResult(
            plan_id=plan.id,
            status=status,
            iterations=self.current_iteration,
            final_entropy=self._calculate_mean_entropy(),
            history=history
        )

    async def step(self, task: Task, plan: Plan) -> LoopStepResult:
        """
        The 000 -> 999 Metabolic Cycle for a single task.
        Connects the static Judge to the dynamic Execution Forge.
        """
        session_id = plan.id # Use plan ID as the metabolic session anchor
        
        try:
            # 000: INIT (Airlock & Authority)
            init_out = await _0_init.init(
                query=task.description,
                session_id=session_id,
                actor_id="arif", # Default to Sovereign for loop execution in v1
                auth_token="IM ARIF"
            )
            
            if init_out.verdict != Verdict.SEAL:
                return LoopStepResult(
                    task_id=task.id,
                    verdict=init_out.verdict,
                    message=f"000_INIT_FAIL: {init_out.error_message}"
                )

            # 111-333: MIND (AGI Reasoning & Truth)
            agi_out = await _1_agi.agi(
                query=task.description,
                session_id=session_id,
                constitutional_context=plan.goal
            )
            
            # 444-666: HEART (ASI Alignment & Empathy)
            asi_out = await _2_asi.asi(
                thought_content=agi_out.final_answer,
                session_id=session_id
            )

            # 777-888: APEX (Final Constitutional Judge)
            # We map the multi-stage outputs to the Apex Judge
            apex_out = await _3_apex.apex(
                query=task.description,
                reason_summary=agi_out.final_answer,
                session_id=session_id,
                # Additional context for the judge
                agi_metrics=agi_out.metrics,
                asi_verdict=asi_out.verdict
            )

            # Extract entropy delta from AGI metrics (Shannon Entropy)
            entropy_delta = agi_out.metrics.delta_s if hasattr(agi_out.metrics, 'delta_s') else 0.01

            # 999: VAULT (Immutable Audit)
            await _4_vault.vault(
                session_id=session_id,
                verdict=apex_out.verdict,
                evidence=f"Loop Iteration {self.current_iteration} for Task {task.id}",
                payload={
                    "task": task.description,
                    "agi": agi_out.model_dump() if hasattr(agi_out, 'model_dump') else str(agi_out),
                    "asi": asi_out.model_dump() if hasattr(asi_out, 'model_dump') else str(asi_out),
                    "apex": apex_out.model_dump() if hasattr(apex_out, 'model_dump') else str(apex_out)
                }
            )

            return LoopStepResult(
                task_id=task.id,
                verdict=normalize_verdict(apex_out.verdict),
                entropy_delta=entropy_delta,
                message=apex_out.reasoning or "Task processed through apex."
            )

        except Exception as e:
            logger.exception(f"Critical metabolic collapse in SabarLoop step: {e}")
            return LoopStepResult(
                task_id=task.id,
                verdict=Verdict.VOID,
                message=f"METABOLIC_COLLAPSE: {str(e)}"
            )

    def _is_entropy_runaway(self, latest_delta: float) -> bool:
        self.entropy_window.append(latest_delta)
        if len(self.entropy_window) > 3:
            self.entropy_window.pop(0)
        
        if len(self.entropy_window) == 3:
            # Monotonic increase and above total threshold
            increasing = self.entropy_window[2] > self.entropy_window[1] > self.entropy_window[0]
            high_entropy = sum(self.entropy_window) > self.entropy_threshold
            return increasing and high_entropy
        return False

    def _calculate_mean_entropy(self) -> float:
        if not self.entropy_window:
            return 0.0
        return sum(self.entropy_window) / len(self.entropy_window)

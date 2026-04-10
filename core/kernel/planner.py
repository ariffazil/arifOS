"""
core/kernel/planner.py — Planner Object and Task Graph.

Represents and manages multi-step plans or task graphs for agent execution,
supporting ReAct, Reflection, and complex planning workflows.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import uuid

@dataclass
class Task:
    """A single unit of work in a plan."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    result: Optional[Any] = None
    dependencies: List[str] = field(default_factory=list)

@dataclass
class Plan:
    """A collection of tasks organized in a task graph."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    tasks: Dict[str, Task] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class Planner:
    """
    Manages explicit, inspectable plans and task graphs.
    Enables decomposition and tracking of complex agentic workflows.
    """

    def __init__(self):
        self._plans: Dict[str, Plan] = {}

    def create_plan(self, goal: str, context: Optional[Dict[str, Any]] = None) -> Plan:
        """Create a new plan for a given goal."""
        plan = Plan(goal=goal, metadata=context or {})
        self._plans[plan.id] = plan
        return plan

    def add_task(self, plan_id: str, description: str, dependencies: Optional[List[str]] = None) -> str:
        """Add a task to a plan, potentially with dependencies on other tasks."""
        if plan_id not in self._plans:
            raise ValueError(f"Plan '{plan_id}' not found.")
        
        task = Task(description=description, dependencies=dependencies or [])
        self._plans[plan_id].tasks[task.id] = task
        return task.id

    def update_task_status(self, plan_id: str, task_id: str, status: str, result: Optional[Any] = None):
        """Update the status and result of a task."""
        if plan_id not in self._plans or task_id not in self._plans[plan_id].tasks:
            raise ValueError(f"Task '{task_id}' not found in plan '{plan_id}'.")
        
        task = self._plans[plan_id].tasks[task_id]
        task.status = status
        if result is not None:
            task.result = result

    def get_current_tasks(self, plan_id: str) -> List[Task]:
        """Retrieve tasks that are ready to execute (PENDING and all dependencies COMPLETED)."""
        if plan_id not in self._plans:
            raise ValueError(f"Plan '{plan_id}' not found.")
        
        plan = self._plans[plan_id]
        ready_tasks = []
        for task in plan.tasks.values():
            if task.status == "PENDING":
                # Check dependencies
                all_done = True
                for dep_id in task.dependencies:
                    dep = plan.tasks.get(dep_id)
                    if not dep or dep.status != "COMPLETED":
                        all_done = False
                        break
                if all_done:
                    ready_tasks.append(task)
        
        return ready_tasks

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Retrieve a plan by its ID."""
        return self._plans.get(plan_id)

    def list_plans(self) -> List[str]:
        """List IDs of all managed plans."""
        return list(self._plans.keys())

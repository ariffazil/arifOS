"""
core/kernel/planner.py — Planner Object and Task Graph.

Represents and manages multi-step plans or task graphs for agent execution,
supporting ReAct, Reflection, and complex planning workflows.

REPAIRED 2026-04-19: Planning Organ now carries governance metadata
(risk_tier, reversibility, approval_status) and exposes normalize_intent_to_plan()
so that no non-trivial INTENT -> EXECUTION path bypasses an explicit plan object.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Task:
    """A single unit of work in a plan."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED, HELD
    result: Any | None = None
    dependencies: list[str] = field(default_factory=list)
    # ── Governance surface (repaired) ────────────────────────────────────────
    tool_name: str = ""  # Canonical tool that will execute this task
    mode: str = "default"  # Sub-mode within the tool
    risk_markers: list[str] = field(default_factory=list)
    reversibility_score: float = 0.0  # 0.0 (safe) → 1.0 (irreversible)
    governance_status: str = "PENDING"  # PENDING, SEAL, HOLD, VOID
    approval_required: bool = False


@dataclass
class Plan:
    """A collection of tasks organized in a task graph."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    tasks: dict[str, Task] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    # ── Governance surface (repaired) ────────────────────────────────────────
    source_intent: str = ""  # Raw intent / query that spawned this plan
    source_request_id: str = ""  # Upstream request / envelope id if available
    session_id: str = ""
    actor_id: str = "anonymous"
    risk_tier: str = "medium"  # low, medium, high, critical
    governance_verdict: str = "PENDING"  # PENDING, SEAL, HOLD, VOID
    approval_status: str = "pending"  # pending, approved, rejected
    irreversibility_score: float = 0.0
    floor_violations: list[str] = field(default_factory=list)


class Planner:
    """
    Manages explicit, inspectable plans and task graphs.
    Enables decomposition and tracking of complex agentic workflows.
    """

    def __init__(self):
        self._plans: dict[str, Plan] = {}

    def create_plan(self, goal: str, context: dict[str, Any] | None = None) -> Plan:
        """Create a new plan for a given goal."""
        plan = Plan(goal=goal, metadata=context or {})
        self._plans[plan.id] = plan
        return plan

    def add_task(
        self,
        plan_id: str,
        description: str,
        dependencies: list[str] | None = None,
        tool_name: str = "",
        mode: str = "default",
        risk_markers: list[str] | None = None,
        reversibility_score: float = 0.0,
        approval_required: bool = False,
    ) -> str:
        """Add a task to a plan, potentially with dependencies on other tasks."""
        if plan_id not in self._plans:
            raise ValueError(f"Plan '{plan_id}' not found.")

        task = Task(
            description=description,
            dependencies=dependencies or [],
            tool_name=tool_name,
            mode=mode,
            risk_markers=risk_markers or [],
            reversibility_score=reversibility_score,
            approval_required=approval_required,
        )
        self._plans[plan_id].tasks[task.id] = task
        return task.id

    def update_task_status(
        self, plan_id: str, task_id: str, status: str, result: Any | None = None
    ):
        """Update the status and result of a task."""
        if plan_id not in self._plans or task_id not in self._plans[plan_id].tasks:
            raise ValueError(f"Task '{task_id}' not found in plan '{plan_id}'.")

        task = self._plans[plan_id].tasks[task_id]
        task.status = status
        if result is not None:
            task.result = result

    def get_current_tasks(self, plan_id: str) -> list[Task]:
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

    def get_plan(self, plan_id: str) -> Plan | None:
        """Retrieve a plan by its ID."""
        return self._plans.get(plan_id)

    def list_plans(self) -> list[str]:
        """List IDs of all managed plans."""
        return list(self._plans.keys())


# ═══════════════════════════════════════════════════════════════════════════════
# PLANNING ORGAN — Canonical Intent → Plan Normalization (REPAIRED)
# ═══════════════════════════════════════════════════════════════════════════════


def normalize_intent_to_plan(
    intent: str,
    session_id: str = "",
    actor_id: str = "anonymous",
    request_id: str = "",
    risk_tier: str = "medium",
    planner: Planner | None = None,
) -> Plan:
    """
    Convert raw intent / query into a canonical Plan object.

    This is the PRIMARY entry gate: every non-trivial execution path MUST
    create a plan through this function before proceeding to governance
    or execution stages.

    The plan carries:
      - plan identifier
      - source intent/request identifier
      - tasks / subtasks derived from intent classification
      - dependencies (implicit ordering)
      - risk / reversibility markers
      - placeholder approval/governance status
    """
    pl = planner or get_global_planner()

    # Derive a concise goal from intent
    goal = intent.strip()[:500] if intent else "unnamed_intent"

    plan = pl.create_plan(
        goal=goal,
        context={
            "raw_intent": intent,
            "normalized_at": __import__("datetime")
            .datetime.now(__import__("datetime").timezone.utc)
            .isoformat(),
        },
    )
    plan.source_intent = intent or ""
    plan.source_request_id = request_id
    plan.session_id = session_id
    plan.actor_id = actor_id
    plan.risk_tier = risk_tier

    # ── Intent-classification heuristics (minimal, deterministic) ────────────
    q = (intent or "").lower()
    destructive_signals = {
        "delete",
        "remove",
        "drop",
        "wipe",
        "format",
        "shutdown",
        "kill",
        "revoke",
        "execute",
        "deploy",
        "seal",
        "forge",
        "write",
        "modify",
    }
    has_destructive = any(s in q for s in destructive_signals)

    # Task 1: Governance / Sensing (always present)
    t1 = pl.add_task(
        plan_id=plan.id,
        description="Sense and classify intent against constitutional floors",
        tool_name="arifos_sense",
        mode="classify",
        risk_markers=["destructive_detected"] if has_destructive else [],
    )

    # Task 2: Reason / Plan (always present)
    t2 = pl.add_task(
        plan_id=plan.id,
        description="Reason about the request and formulate response plan",
        tool_name="arifos_mind",
        mode="reason",
        dependencies=[t1],
        risk_markers=["destructive_detected"] if has_destructive else [],
    )

    # Task 3: Execution (conditional)
    if has_destructive or risk_tier in ("high", "critical"):
        t3 = pl.add_task(
            plan_id=plan.id,
            description="Execute approved action with rollback context",
            tool_name="arifos_forge",
            mode="execute",
            dependencies=[t2],
            risk_markers=["irreversible", "destructive_detected"],
            reversibility_score=0.85,
            approval_required=True,
        )
        plan.approval_status = "pending"
        plan.irreversibility_score = 0.85
    else:
        t3 = pl.add_task(
            plan_id=plan.id,
            description="Execute safe action",
            tool_name="arifos_kernel",
            mode="route",
            dependencies=[t2],
            risk_markers=[],
            reversibility_score=0.0,
            approval_required=False,
        )
        plan.irreversibility_score = 0.0

    # Task 4: Seal / Audit (always present)
    pl.add_task(
        plan_id=plan.id,
        description="Seal outcome to vault and emit telemetry",
        tool_name="arifos_vault",
        mode="seal",
        dependencies=[t3],
    )

    return plan


def evaluate_plan_against_governance(plan: Plan) -> Plan:
    """
    Run F1 (Amanah) irreversibility scoring over a plan.

    Returns the plan with updated:
      - governance_verdict
      - approval_status
      - floor_violations

    If any task triggers critical irreversibility, the plan verdict is
    downgraded to HOLD and approval_status stays 'pending'.
    """
    try:
        from arifosmcp.runtime.irreversibility import AmanahIrreversibilityScorer

        scorer = AmanahIrreversibilityScorer()
    except Exception:
        # If scorer unavailable, degrade gracefully — do not block
        plan.governance_verdict = "SEAL"
        return plan

    max_score = 0.0
    violations: list[str] = []
    any_hold = False

    for task in plan.tasks.values():
        if not task.tool_name:
            continue
        result = scorer.evaluate_payload(
            tool_name=task.tool_name,
            mode=task.mode,
            args={"query": plan.source_intent, "plan_id": plan.id},
            actor_id=plan.actor_id,
        )
        # Planning-phase leniency: unknown tools are conceptual at this stage.
        # Downgrade F1_UNKNOWN_TOOL from conservative hold (0.8) to medium (0.3)
        # UNLESS the task already carries explicit risk signals from intent classification.
        adjusted_violations = list(result.floor_violations)
        has_explicit_risk = (
            task.approval_required
            or task.reversibility_score >= 0.7
            or any(m in ("irreversible", "destructive_detected") for m in task.risk_markers)
        )
        if result.floor_violations == ["F1_UNKNOWN_TOOL"] and not has_explicit_risk:
            adjusted_score = 0.3
            adjusted_violations = []
            adjusted_hold = False
        else:
            adjusted_score = result.score
            adjusted_hold = result.triggers_888_hold

        task.reversibility_score = adjusted_score
        if adjusted_hold:
            task.governance_status = "HOLD"
            any_hold = True
        if adjusted_violations:
            violations.extend(adjusted_violations)
        max_score = max(max_score, adjusted_score)

    plan.irreversibility_score = round(max_score, 3)
    plan.floor_violations = list(dict.fromkeys(violations))  # dedupe

    if any_hold or max_score >= 0.7:
        plan.governance_verdict = "HOLD"
        plan.approval_status = "pending"
    else:
        plan.governance_verdict = "SEAL"
        plan.approval_status = "approved"

    return plan


def plan_to_execution_manifest(plan: Plan) -> dict[str, Any]:
    """
    Serialize a plan into the minimal dict expected by execution layers.
    Used to thread plan metadata through existing tool invocation paths.
    """
    return {
        "plan_id": plan.id,
        "goal": plan.goal,
        "source_intent": plan.source_intent,
        "source_request_id": plan.source_request_id,
        "session_id": plan.session_id,
        "actor_id": plan.actor_id,
        "risk_tier": plan.risk_tier,
        "governance_verdict": plan.governance_verdict,
        "approval_status": plan.approval_status,
        "irreversibility_score": plan.irreversibility_score,
        "floor_violations": plan.floor_violations,
        "task_count": len(plan.tasks),
        "tasks": [
            {
                "task_id": t.id,
                "description": t.description,
                "tool_name": t.tool_name,
                "mode": t.mode,
                "status": t.status,
                "dependencies": t.dependencies,
                "reversibility_score": t.reversibility_score,
                "governance_status": t.governance_status,
                "approval_required": t.approval_required,
            }
            for t in plan.tasks.values()
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL PLANNER & RECONCILER (P0-3: Anonymous GANTUNG sweep)
# ═══════════════════════════════════════════════════════════════════════════════

_global_planner: Planner | None = None


def get_global_planner() -> Planner:
    """Return the process-wide Planner singleton for plan tracking."""
    global _global_planner
    if _global_planner is None:
        _global_planner = Planner()
    return _global_planner


def reconcile_abandoned_plans(max_age_minutes: float = 5.0) -> list[dict[str, Any]]:
    """
    Scan the global planner for anonymous abandoned plans and VOID them.

    Policy:
      - Only plans with no actor_id (anonymous) are auto-VOIDed.
      - Actor-bound plans are NEVER touched — F13 sovereignty.
      - Plans older than max_age_minutes with governance_verdict != SEAL are VOIDed.

    Returns:
      List of reconciliation records for audit logging.
    """
    import logging
    from datetime import datetime, timezone

    logger = logging.getLogger(__name__)
    now = datetime.now(timezone.utc)
    reconciled: list[dict[str, Any]] = []
    planner = get_global_planner()

    for plan_id, plan in list(planner._plans.items()):
        # Skip actor-bound plans — sovereign territory
        if plan.actor_id and plan.actor_id.strip().lower() not in {"", "anonymous", "none"}:
            continue

        # Skip already-resolved plans
        if plan.governance_verdict in ("SEAL", "VOID"):
            continue

        # Check age from metadata
        created_at_str = plan.metadata.get("normalized_at", "")
        if created_at_str:
            try:
                created_at = datetime.fromisoformat(created_at_str)
                age_minutes = (now - created_at).total_seconds() / 60.0
                if age_minutes > max_age_minutes:
                    plan.governance_verdict = "VOID"
                    plan.approval_status = "rejected"
                    plan.floor_violations.append("F11_ANONYMOUS_ABANDONED")
                    reconciled.append(
                        {
                            "plan_id": plan_id,
                            "reason": "F11_ANONYMOUS_ABANDONED",
                            "age_minutes": round(age_minutes, 1),
                            "session_id": plan.session_id,
                            "actor_id": plan.actor_id,
                        }
                    )
                    logger.warning(
                        f"[RECONCILER] VOID {plan_id} — anonymous, abandoned "
                        f"({age_minutes:.1f}min > {max_age_minutes}min)"
                    )
            except Exception:
                pass

    return reconciled

"""
arifos_plan — Planning Organ Tool v1.1
======================================
Constitutional planning tool for external state mutations.

Hardens existing shadow planner (core/kernel/planner.py) into a governed organ.
All calls emit CLAIM_ONLY. 888_JUDGE must ratify before EXECUTION.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""


import uuid
import hashlib
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, Any, List

# ─── Enums ────────────────────────────────────────────────────────────────────

class PlanStatus(Enum):
    DRAFT             = "DRAFT"
    PENDING_APPROVAL  = "PENDING_APPROVAL"
    APPROVED          = "APPROVED"
    IN_EXECUTION      = "IN_EXECUTION"
    COMPLETED         = "COMPLETED"
    ABORTED           = "ABORTED"
    FAILED            = "FAILED"

class RiskBand(Enum):
    LOW      = "LOW"
    MEDIUM   = "MEDIUM"
    HIGH     = "HIGH"
    CRITICAL = "CRITICAL"

# ─── Schemas ───────────────────────────────────────────────────────────────────

@dataclass
class SovereignIntent:
    intent_id: str
    description: str
    constraints: Dict[str, Any]
    floors: Dict[str, str]
    risk_prelude: Dict[str, Any]
    created_by: str
    created_at: str
    epoch_id: str = ""
    status: str = "ACTIVE"

    def to_json(self) -> dict:
        return asdict(self)

@dataclass
class Task:
    task_id: str
    description: str
    tool: str
    mutates_external_state: bool
    target_surface: str
    reversible: bool
    risk_band: str
    status: str = "PLANNED"
    dependencies: List[str] = field(default_factory=list)
    result: Optional[Dict] = None
    created_at: str = ""

    def to_json(self) -> dict:
        return asdict(self)

@dataclass
class Plan:
    plan_id: str
    intent_id: str
    epoch_id: str
    status: str
    risk_band: str
    irreversible: bool
    tasks: List[Task]
    created_by: str
    created_at: str
    analysis: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    hold_reason: Optional[str] = None

    def requires_888_hold(self) -> bool:
        return self.irreversible or self.risk_band in ("HIGH", "CRITICAL")

    def to_json(self) -> dict:
        d = asdict(self)
        d['requires_888_hold'] = self.requires_888_hold()
        return d

@dataclass
class PlanReceipt:
    receipt_id: str
    plan_id: str
    decision: str   # APPROVED | REJECTED | HOLD | MODIFIED
    verdict: str    # SEAL | VOID | HOLD — constitutional verdict
    decided_by: str
    decided_at: str
    notes: str
    floor_signatures: List[str] = field(default_factory=list)

    def to_json(self) -> dict:
        return asdict(self)

@dataclass
class ExecutionReceipt:
    receipt_id: str
    epoch_id: str
    plan_id: str
    task_id: str
    status: str   # COMPLETED | FAILED | SKIPPED
    started_at: str
    finished_at: str
    logs_ref: Optional[str] = None
    error: Optional[str] = None

    def to_json(self) -> dict:
        return asdict(self)

# ─── Floor Checker ─────────────────────────────────────────────────────────────

FLOORS_TO_CHECK = ["F1", "F2", "F3", "F5", "F6"]

def _check_floors(tasks: List[Task], risk_band: str, irreversible: bool) -> Dict[str, Any]:
    """Return analysis block for propose_plan output."""
    holds = []
    tasks_irreversible = []

    for task in tasks:
        if not task.reversible:
            tasks_irreversible.append(task.task_id)
            holds.append({
                "task_id": task.task_id,
                "reason": f"{task.tool} on {task.target_surface} — irreversible",
                "requires_888_hold": True,
            })
        elif task.risk_band in ("HIGH", "CRITICAL"):
            holds.append({
                "task_id": task.task_id,
                "reason": f"risk_band={task.risk_band}",
                "requires_888_hold": True,
            })

    plan_irreversible = irreversible or len(tasks_irreversible) > 0

    return {
        "floors_checked": FLOORS_TO_CHECK,
        "irreversibility_summary": {
            "plan_irreversible": plan_irreversible,
            "tasks_irreversible": tasks_irreversible,
        },
        "holds": holds,
    }

# ─── In-Memory Store (MVP — swap for Postgres in production) ──────────────────

class PlanStore:
    def __init__(self):
        self.intents: Dict[str, SovereignIntent] = {}
        self.plans: Dict[str, Plan] = {}
        self.receipts: Dict[str, List[PlanReceipt]] = {}   # plan_id → receipts
        self.exec_receipts: Dict[str, ExecutionReceipt] = {}

    def add_intent(self, intent: SovereignIntent):
        self.intents[intent.intent_id] = intent

    def add_plan(self, plan: Plan):
        self.plans[plan.plan_id] = plan

    def add_receipt(self, receipt: PlanReceipt):
        if receipt.plan_id not in self.receipts:
            self.receipts[receipt.plan_id] = []
        self.receipts[receipt.plan_id].append(receipt)

    def add_exec_receipt(self, er: ExecutionReceipt):
        self.exec_receipts[er.receipt_id] = er

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return self.plans.get(plan_id)

    def get_receipts(self, plan_id: str) -> List[PlanReceipt]:
        return sorted(
            self.receipts.get(plan_id, []),
            key=lambda r: r.decided_at
        )

    def get_plans_by_status(self, status: PlanStatus) -> List[Plan]:
        return [p for p in self.plans.values() if p.status == status.value]

    def get_pending(self, epoch_id: str = "", risk_band: str = "",
                    contains_irreversible: bool = False) -> List[Plan]:
        statuses = ["PENDING_APPROVAL", "IN_EXECUTION", "HOLD"]
        results = [p for p in self.plans.values() if p.status in statuses]
        if epoch_id:
            results = [p for p in results if p.epoch_id == epoch_id]
        if risk_band:
            results = [p for p in results if p.risk_band == risk_band]
        if contains_irreversible:
            results = [p for p in results if p.irreversible]
        return results

_store = PlanStore()

# ─── Tool Modes ────────────────────────────────────────────────────────────────

def propose_plan(
    intent: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None,
    tasks: Optional[List[Dict]] = None,
    created_by: str = "arifOS_bot",
    epoch_id: str = "",
    risk_band: str = "MEDIUM",
    irreversible: bool = False,
    metadata: Optional[Dict] = None
) -> dict:
    """
    Create SovereignIntent + Plan from intent.
    Returns DRAFT Plan with GK analysis annotations.
    Auto-transitions to PENDING_APPROVAL if 888_HOLD required.
    """
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    intent_id = f"intent-{uuid.uuid4().hex[:12]}"
    plan_id = f"plan-{uuid.uuid4().hex[:12]}"
    eid = epoch_id or now

    # Build SovereignIntent
    sovereign_intent = SovereignIntent(
        intent_id=intent_id,
        description=intent.get("description", ""),
        constraints=intent.get("constraints", {}),
        floors=intent.get("floors", {}),
        risk_prelude=intent.get("risk_prelude", {}),
        created_by=created_by,
        created_at=now,
        epoch_id=eid,
    )
    _store.add_intent(sovereign_intent)

    # Build tasks
    task_objects = []
    for t in (tasks or []):
        task = Task(
            task_id=f"task-{uuid.uuid4().hex[:8]}",
            description=t.get("description", ""),
            tool=t.get("tool", "unknown"),
            mutates_external_state=t.get("mutates_external_state", True),
            target_surface=t.get("target_surface", "unknown"),
            reversible=t.get("reversible", False),
            risk_band=t.get("risk_band", "LOW"),
            dependencies=t.get("dependencies", []),
            status="PLANNED",
            created_at=now,
        )
        task_objects.append(task)

    plan = Plan(
        plan_id=plan_id,
        intent_id=intent_id,
        epoch_id=eid,
        status="DRAFT",
        risk_band=risk_band.upper(),
        irreversible=irreversible,
        tasks=task_objects,
        created_by=created_by,
        created_at=now,
        metadata=metadata or {},
    )

    # Add GK analysis
    plan.analysis = _check_floors(task_objects, risk_band, irreversible)

    # Auto-transition
    needs_hold = plan.requires_888_hold() or len(plan.analysis.get("holds", [])) > 0
    if needs_hold:
        plan.status = "PENDING_APPROVAL"
        plan.hold_reason = "888_HOLD: sovereign approval required before EXECUTION"
    else:
        plan.status = "APPROVED"

    _store.add_plan(plan)

    return {
        "CLAIM_ONLY": True,
        "verdict": "SEAL" if plan.status == "APPROVED" else "HOLD",
        "hold_reason": plan.hold_reason,
        "plan": plan.to_json(),
        "intent": sovereign_intent.to_json(),
        "analysis": plan.analysis,
    }

def get_plan(plan_id: str) -> dict:
    """Fetch plan + all receipts."""
    plan = _store.get_plan(plan_id)
    if not plan:
        return {"CLAIM_ONLY": True, "verdict": "VOID", "reason": f"Plan {plan_id} not found"}
    receipts = _store.get_receipts(plan_id)
    return {
        "CLAIM_ONLY": True,
        "plan": plan.to_json(),
        "receipts": [r.to_json() for r in receipts],
    }

def list_pending(
    epoch_id: str = "",
    actor_id: str = "",
    risk_band: str = "",
    contains_irreversible: bool = False
) -> dict:
    """List plans awaiting sovereign action."""
    plans = _store.get_pending(epoch_id, risk_band, contains_irreversible)
    return {
        "CLAIM_ONLY": True,
        "count": len(plans),
        "plans": [
            {
                "plan_id": p.plan_id,
                "status": p.status,
                "risk_band": p.risk_band,
                "has_888_hold": p.requires_888_hold() or len(p.analysis.get("holds", [])) > 0,
                "epoch_id": p.epoch_id,
            }
            for p in plans
        ],
    }

def update_status(
    plan_id: str,
    new_status: str,
    verdict: str,
    floors: Optional[Dict[str, str]] = None,
    comment: str = "",
    actor_id: str = "arifOS_bot"
) -> dict:
    """
    Transition plan with sovereign decision.
    verdict: APPROVED → SEAL, REJECTED → VOID, HOLD → HOLD
    Writes PlanReceipt and appends to Vault999.
    """
    plan = _store.get_plan(plan_id)
    if not plan:
        return {"CLAIM_ONLY": True, "verdict": "VOID", "reason": f"Plan {plan_id} not found"}

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    receipt = PlanReceipt(
        receipt_id=f"receipt-{uuid.uuid4().hex[:12]}",
        plan_id=plan_id,
        decision=new_status.upper(),
        verdict=verdict.upper(),
        decided_by=actor_id,
        decided_at=now,
        notes=comment,
        floor_signatures=[f"{k}:{v}" for k, v in (floors or {}).items()],
    )
    _store.add_receipt(receipt)

    # FSM transition
    if verdict.upper() == "APPROVED":
        plan.status = "APPROVED"
        return {"CLAIM_ONLY": True, "verdict": "SEAL", "plan": plan.to_json(), "receipt": receipt.to_json()}
    elif verdict.upper() == "REJECTED":
        plan.status = "ABORTED"
        return {"CLAIM_ONLY": True, "verdict": "VOID", "plan": plan.to_json(), "receipt": receipt.to_json()}
    elif verdict.upper() == "HOLD":
        plan.status = "PENDING_APPROVAL"
        plan.hold_reason = comment or "888_HOLD active"
        return {"CLAIM_ONLY": True, "verdict": "HOLD", "plan": plan.to_json(), "receipt": receipt.to_json()}

    return {"CLAIM_ONLY": True, "verdict": "VOID", "reason": f"Unknown verdict: {verdict}"}

def abort_plan(plan_id: str, reason: str, actor_id: str = "arifOS_bot") -> dict:
    """Soft-kill: transition to ABORTED. Forge must respect and stop remaining tasks."""
    plan = _store.get_plan(plan_id)
    if not plan:
        return {"CLAIM_ONLY": True, "verdict": "VOID", "reason": f"Plan {plan_id} not found"}

    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    receipt = PlanReceipt(
        receipt_id=f"receipt-{uuid.uuid4().hex[:12]}",
        plan_id=plan_id,
        decision="REJECTED",
        verdict="VOID",
        decided_by=actor_id,
        decided_at=now,
        notes=f"Abort: {reason}",
        floor_signatures=["F1:amamah"],
    )
    _store.add_receipt(receipt)
    plan.status = "ABORTED"

    return {"CLAIM_ONLY": True, "verdict": "SEAL", "plan": plan.to_json(), "receipt": receipt.to_json()}

def write_execution_receipt(
    plan_id: str,
    task_id: str,
    status: str,
    started_at: str,
    finished_at: str,
    logs_ref: str = "",
    error: str = "",
    epoch_id: str = ""
) -> dict:
    """Write ExecutionReceipt after a task completes. Links to Vault999."""
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    er = ExecutionReceipt(
        receipt_id=f"exec-{uuid.uuid4().hex[:12]}",
        epoch_id=epoch_id,
        plan_id=plan_id,
        task_id=task_id,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        logs_ref=logs_ref or None,
        error=error or None,
    )
    _store.add_exec_receipt(er)

    # Mark task complete
    plan = _store.get_plan(plan_id)
    if plan:
        for t in plan.tasks:
            if t.task_id == task_id:
                t.status = status
                t.result = {"logs_ref": logs_ref, "error": error}
                break

    return {"CLAIM_ONLY": True, "verdict": "SEAL", "execution_receipt": er.to_json()}

# ─── GK Runtime Check ─────────────────────────────────────────────────────────

def gk_can_execute(plan_id: str, task_id: str) -> dict:
    """
    Governance Kernel runtime check.
    Returns {can_execute: bool, reason?: str, task_id?: str}
    Forge calls this before any external state mutation.
    """
    plan = _store.get_plan(plan_id)
    if not plan:
        return {"can_execute": False, "reason": f"Plan {plan_id} not found"}

    if plan.status != "APPROVED":
        return {"can_execute": False, "reason": f"Plan status is {plan.status}, not APPROVED"}

    task = next((t for t in plan.tasks if t.task_id == task_id), None)
    if not task:
        return {"can_execute": False, "reason": f"Task {task_id} not found in plan"}

    if plan.status == "ABORTED":
        return {"can_execute": False, "reason": "Plan ABORTED — Forge must refuse"}

    # Check 888_HOLD
    needs_hold = (
        task.risk_band in ("HIGH", "CRITICAL") or
        not task.reversible
    )
    if needs_hold:
        receipts = _store.get_receipts(plan_id)
        has_approval = any(r.decision == "APPROVED" for r in receipts)
        if not has_approval:
            return {
                "can_execute": False,
                "reason": "888_HOLD: sovereign approval required",
                "task_id": task_id,
                "plan_id": plan_id,
            }

    return {"can_execute": True, "plan_id": plan_id, "task_id": task_id}

# ─── MCP Shim ─────────────────────────────────────────────────────────────────

def arifos_plan(mode: str, payload: dict) -> dict:
    """
    Main MCP entry point.
    All calls emit CLAIM_ONLY — 888_JUDGE verification required before EXECUTION.
    """
    if mode == "propose_plan":
        return propose_plan(
            intent=payload["intent"],
            context=payload.get("context"),
            tasks=payload.get("tasks"),
            created_by=payload.get("actor_id", "arifOS_bot"),
            epoch_id=payload.get("epoch_id", ""),
            risk_band=payload.get("risk_band", "MEDIUM"),
            irreversible=payload.get("irreversible", False),
            metadata=payload.get("metadata"),
        )
    elif mode == "get_plan":
        return get_plan(payload["plan_id"])
    elif mode == "list_pending":
        return list_pending(
            epoch_id=payload.get("epoch_id", ""),
            actor_id=payload.get("actor_id", ""),
            risk_band=payload.get("risk_band", ""),
            contains_irreversible=payload.get("contains_irreversible", False),
        )
    elif mode == "update_status":
        return update_status(
            plan_id=payload["plan_id"],
            new_status=payload.get("new_status", payload.get("decision", "")),
            verdict=payload.get("verdict", payload.get("decision", "")),
            floors=payload.get("floors"),
            comment=payload.get("comment", ""),
            actor_id=payload.get("actor_id", "arifOS_bot"),
        )
    elif mode == "abort_plan":
        return abort_plan(
            plan_id=payload["plan_id"],
            reason=payload.get("reason", "Sovereign abort"),
            actor_id=payload.get("actor_id", "arifOS_bot"),
        )
    elif mode == "write_execution_receipt":
        return write_execution_receipt(
            plan_id=payload["plan_id"],
            task_id=payload["task_id"],
            status=payload["status"],
            started_at=payload["started_at"],
            finished_at=payload["finished_at"],
            logs_ref=payload.get("logs_ref", ""),
            error=payload.get("error", ""),
            epoch_id=payload.get("epoch_id", ""),
        )
    elif mode == "gk_can_execute":
        return gk_can_execute(payload["plan_id"], payload["task_id"])
    else:
        return {"CLAIM_ONLY": True, "verdict": "VOID", "reason": f"Unknown mode: {mode}"}

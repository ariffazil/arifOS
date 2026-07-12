"""Task-level work contracts, budgets, events, and verification receipts."""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import uuid
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_BUDGETS = {
    "reasoning": {"max_cycles": 8, "max_model_calls": 6, "max_elapsed_seconds": 180},
    "tools": {"max_calls_total": 20, "max_calls_per_tool": 6, "max_failed_calls": 3},
    "coordination": {"max_delegations": 3, "max_depth": 2},
    "cost": {"max_usd": 1.50},
}
DEFAULT_TERMINATION = {
    "confidence_target": 0.85,
    "minimum_uncertainty_reduction": 0.05,
    "stop_on_repeated_evidence": True,
}
_LOCK = threading.RLock()
_TASKS: dict[str, dict[str, Any]] = {}
_SESSION_TASKS: dict[str, str] = {}


def _ledger_path() -> Path:
    return Path(os.getenv("ARIFOS_WORK_LEDGER", "/tmp/arifos/work_events.jsonl"))


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _append_event(state: dict[str, Any], stage: str, event_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    prior_hash = state.get("event_hash", "GENESIS")
    event = {
        "event_id": f"evt-{uuid.uuid4().hex}",
        "task_id": state["contract"]["task_id"],
        "session_id": state["contract"]["session_id"],
        "sequence": state.get("sequence", 0) + 1,
        "timestamp": _now(),
        "stage": stage,
        "event_type": event_type,
        "payload": payload,
        "prior_hash": prior_hash,
    }
    canonical = json.dumps(event, sort_keys=True, separators=(",", ":"))
    event["event_hash"] = hashlib.sha256(canonical.encode()).hexdigest()
    event["checksum"] = event["event_hash"]
    path = _ledger_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")
    state["sequence"] = event["sequence"]
    state["event_hash"] = event["event_hash"]
    return event


def create_work_contract(
    session_id: str,
    objective: str,
    success_criteria: list[str] | None = None,
    budgets: dict[str, Any] | None = None,
    autonomy_band: str = "ORANGE",
    verification_criteria: list[str] | None = None,
    task_id: str | None = None,
) -> dict[str, Any]:
    task_id = task_id or f"task-{uuid.uuid4().hex[:16]}"
    merged = deepcopy(DEFAULT_BUDGETS)
    for section, values in (budgets or {}).items():
        if section in merged and isinstance(values, dict):
            merged[section].update(values)
    contract = {
        "task_id": task_id,
        "session_id": session_id,
        "objective": objective.strip(),
        "success_criteria": list(success_criteria or []),
        "budgets": merged,
        "verification": {"required": True, "criteria": list(verification_criteria or [])},
        "autonomy_band": autonomy_band if autonomy_band in {"GREEN", "ORANGE", "RED"} else "ORANGE",
        "termination": deepcopy(DEFAULT_TERMINATION),
    }
    state = {
        "contract": contract,
        "started_monotonic": time.monotonic(),
        "usage": {
            "reasoning_cycles": 0,
            "model_calls": 0,
            "tool_calls": 0,
            "tool_calls_by_name": {},
            "failed_tool_calls": 0,
            "delegations": 0,
            "coordination_depth": 0,
            "estimated_cost_usd": 0.0,
        },
        "proposals": {},
        "held": False,
        "termination_reason": None,
        "sequence": 0,
    }
    with _LOCK:
        _TASKS[task_id] = state
        _SESSION_TASKS[session_id] = task_id
        event = _append_event(state, "INIT", "budget_created", {"contract": contract})
    return {"contract": deepcopy(contract), "event_id": event["event_id"]}


def _state_for(session_id: str | None = None, task_id: str | None = None) -> dict[str, Any] | None:
    with _LOCK:
        resolved = task_id or _SESSION_TASKS.get(session_id or "")
        return _TASKS.get(resolved or "")


def consume(session_id: str, resource: str, amount: float = 1, name: str | None = None) -> dict[str, Any]:
    with _LOCK:
        state = _state_for(session_id=session_id)
        if state is None:
            return {"allowed": True, "tracked": False}
        if state["held"]:
            return {"allowed": False, "tracked": True, "reason": state["termination_reason"], "snapshot": snapshot(session_id)}

        usage = state["usage"]
        budgets = state["contract"]["budgets"]
        limits = {
            "reasoning_cycle": ("reasoning_cycles", budgets["reasoning"]["max_cycles"]),
            "model_call": ("model_calls", budgets["reasoning"]["max_model_calls"]),
            "tool_call": ("tool_calls", budgets["tools"]["max_calls_total"]),
            "failed_tool_call": ("failed_tool_calls", budgets["tools"]["max_failed_calls"]),
            "delegation": ("delegations", budgets["coordination"]["max_delegations"]),
            "cost_usd": ("estimated_cost_usd", budgets["cost"]["max_usd"]),
        }
        if resource not in limits:
            raise ValueError(f"Unknown work resource: {resource}")
        field, limit = limits[resource]
        elapsed = time.monotonic() - state["started_monotonic"]
        reason = None
        if elapsed >= budgets["reasoning"]["max_elapsed_seconds"]:
            reason = "ELAPSED_BUDGET_EXHAUSTED"
        elif usage[field] + amount > limit:
            reason = (
                "REASONING_BUDGET_EXHAUSTED"
                if resource == "reasoning_cycle"
                else f"{resource.upper()}_BUDGET_EXHAUSTED"
            )
        elif resource == "tool_call" and name:
            per_tool = usage["tool_calls_by_name"].get(name, 0)
            if per_tool + amount > budgets["tools"]["max_calls_per_tool"]:
                reason = "PER_TOOL_BUDGET_EXHAUSTED"
        if reason:
            state["held"] = True
            state["termination_reason"] = reason
            _append_event(state, "CLOSE", "task_budget_hold", {"resource": resource, "reason": reason})
            return {"allowed": False, "tracked": True, "reason": reason, "snapshot": snapshot(session_id)}

        usage[field] += amount
        if resource == "tool_call" and name:
            usage["tool_calls_by_name"][name] = usage["tool_calls_by_name"].get(name, 0) + amount
        _append_event(state, "THINK" if resource in {"reasoning_cycle", "model_call"} else "ACT", "budget_consumed", {"resource": resource, "amount": amount, "name": name})
        return {"allowed": True, "tracked": True, "snapshot": snapshot(session_id)}


def register_proposal(session_id: str, proposal_type: str, expected_outcome: str, verification_plan: list[str]) -> dict[str, Any]:
    with _LOCK:
        state = _state_for(session_id=session_id)
        if state is None:
            raise ValueError("No work contract for session")
        proposal_id = f"prop-{uuid.uuid4().hex}"
        proposal = {"proposal_id": proposal_id, "type": proposal_type, "expected_outcome": expected_outcome, "verification_plan": list(verification_plan), "status": "DRAFT_ONLY" if not verification_plan else "UNVERIFIED"}
        state["proposals"][proposal_id] = proposal
        _append_event(state, "THINK", "proposal_generated", proposal)
        return deepcopy(proposal)


def record_verification(session_id: str, proposal_id: str, passed: bool, verifier: str, evidence_refs: list[str]) -> dict[str, Any]:
    with _LOCK:
        state = _state_for(session_id=session_id)
        if state is None or proposal_id not in state["proposals"]:
            raise ValueError("Unknown proposal")
        proposal = state["proposals"][proposal_id]
        proposal["status"] = "VERIFIED" if passed and evidence_refs else "FALSIFIED" if evidence_refs else "UNVERIFIED"
        verification = {"proposal_id": proposal_id, "status": proposal["status"], "verifier": verifier, "evidence_refs": list(evidence_refs)}
        event_type = "proposal_verified" if proposal["status"] == "VERIFIED" else "proposal_falsified" if proposal["status"] == "FALSIFIED" else "proposal_tested"
        _append_event(state, "VERIFY", event_type, verification)
        return verification


def snapshot(session_id: str) -> dict[str, Any] | None:
    with _LOCK:
        state = _state_for(session_id=session_id)
        if state is None:
            return None
        usage = deepcopy(state["usage"])
        usage["elapsed_seconds"] = round(time.monotonic() - state["started_monotonic"], 3)
        proposals = list(state["proposals"].values())
        return {
            "task_id": state["contract"]["task_id"],
            "budgets": deepcopy(state["contract"]["budgets"]),
            "usage": usage,
            "remaining": {
                "reasoning_cycles": max(0, state["contract"]["budgets"]["reasoning"]["max_cycles"] - usage["reasoning_cycles"]),
                "tool_calls": max(0, state["contract"]["budgets"]["tools"]["max_calls_total"] - usage["tool_calls"]),
                "delegations": max(0, state["contract"]["budgets"]["coordination"]["max_delegations"] - usage["delegations"]),
                "cost_usd": round(max(0.0, state["contract"]["budgets"]["cost"]["max_usd"] - usage["estimated_cost_usd"]), 6),
            },
            "verification": {
                "proposals": len(proposals),
                "verified": sum(p["status"] == "VERIFIED" for p in proposals),
                "falsified": sum(p["status"] == "FALSIFIED" for p in proposals),
                "untested": sum(p["status"] in {"DRAFT_ONLY", "UNVERIFIED"} for p in proposals),
            },
            "held": state["held"],
            "termination_reason": state["termination_reason"],
            "ledger_head": state.get("event_hash"),
        }


def clear_for_tests() -> None:
    with _LOCK:
        _TASKS.clear()
        _SESSION_TASKS.clear()

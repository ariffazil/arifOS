"""
Task Registry — TASK_LEDGER (Redis L1)

DITEMPA BUKAN DIBERI — Forged, Not Given.

Read/write unresolved swarm tasks.
Tasks are advisory until matched with lease + capability + policy.
New agents see open tasks at boot for continuity.

Key: swarm:tasks → JSON blob of task dicts
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

TASKS_KEY = "swarm:tasks"


# ── Public API ────────────────────────────────────────────────────


def read_unresolved_tasks() -> list[dict[str, Any]]:
    """
    Read TASK_LEDGER. Returns unresolved (PENDING/IN_PROGRESS) tasks.

    Only returns tasks visible to new agents — not private scratchpad.
    """
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = r.get(TASKS_KEY)
        if raw:
            all_tasks = json.loads(raw)
            return [
                t
                for t in all_tasks
                if t.get("status") in ("PENDING", "IN_PROGRESS")
                and t.get("visible_to_new_agents", True)
            ]
    except Exception as exc:
        logger.warning(f"Redis task read failed: {exc}")

    return []


def register_task(
    *,
    task_id: str,
    description: str = "",
    status: str = "PENDING",
    holder: str | None = None,
    last_seal_hash: str | None = None,
    visible_to_new_agents: bool = True,
) -> dict[str, Any]:
    """
    Register a new task in the swarm.

    Returns the task dict.
    """
    task = {
        "task_id": task_id,
        "description": description,
        "status": status,
        "holder": holder,
        "last_seal_hash": last_seal_hash,
        "visible_to_new_agents": visible_to_new_agents,
    }
    _store_task(task)
    return task


def update_task_status(
    task_id: str,
    status: str,
    holder: str | None = None,
) -> bool:
    """
    Update a task's status and holder.
    Returns True if updated.
    """
    tasks = _read_all_tasks()
    for task in tasks:
        if task.get("task_id") == task_id:
            task["status"] = status
            if holder is not None:
                task["holder"] = holder
            _write_all_tasks(tasks)
            return True
    return False


def abandon_holder_tasks(agent_id: str) -> int:
    """
    When an agent leaves/crashes, return all its tasks to PENDING.
    Returns count of tasks returned to pool.
    """
    tasks = _read_all_tasks()
    count = 0
    for task in tasks:
        if task.get("holder") == agent_id and task.get("status") == "IN_PROGRESS":
            task["status"] = "PENDING"
            task["holder"] = None
            count += 1
    if count:
        _write_all_tasks(tasks)
    return count


# ── Internal helpers ──────────────────────────────────────────────


def _read_all_tasks() -> list[dict[str, Any]]:
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = r.get(TASKS_KEY)
        if raw:
            return json.loads(raw)
    except Exception as exc:
        logger.warning(f"Redis task read failed: {exc}")
    return []


def _write_all_tasks(tasks: list[dict[str, Any]]) -> bool:
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = json.dumps(tasks, default=str)
        r.set(TASKS_KEY, raw)
        return True
    except Exception as exc:
        logger.warning(f"Redis task write failed: {exc}")
        return False


def _store_task(task: dict[str, Any]) -> bool:
    tasks = _read_all_tasks()
    tasks.append(task)
    return _write_all_tasks(tasks)

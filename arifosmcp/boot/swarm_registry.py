"""
Swarm Registry — SWARM_STATE_LEDGER (Redis L1)

DITEMPA BUKAN DIBERI — Forged, Not Given.

Read/write visible swarm state to Redis.
This is L1 ephemeral — swarm state is live, not archived.
VAULT999 is the canonical record; Redis is the working copy.

Key: swarm:state → JSON blob of active agents, organs, tasks
"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

SWARM_STATE_KEY = "swarm:state"


def read_swarm_state(*, session_id: str = "") -> dict[str, Any]:
    """
    Read SWARM_STATE_LEDGER from Redis.

    Must be read-only. If Redis unavailable, return degraded state, not exception.

    Returns:
      swarm_id: federation identifier
      status: WARM | COLD | DEGRADED | QUARANTINED
      active_agents: list of agent_ids
      active_organs: list of organ names
      open_tasks: list of task_ids
      blocked_tasks: list of blocked task_ids
      source: "redis" | "stub" | "unavailable"
      degraded: True if source not authoritative
    """
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = r.get(SWARM_STATE_KEY)
        if raw:
            state = json.loads(raw)
            state["source"] = "redis"
            state["degraded"] = False
            return state
    except Exception as exc:
        logger.warning(f"Redis swarm state read failed: {exc}")

    # Degraded stub — no swarm state available
    return {
        "swarm_id": "AAA-FEDERATION-PRIMARY",
        "status": "DEGRADED_EMPTY",
        "active_agents": [],
        "active_organs": [],
        "open_tasks": [],
        "blocked_tasks": [],
        "last_known_good_state": None,
        "source": "stub",
        "degraded": True,
        "session_id": session_id,
    }


def update_swarm_state(state: dict[str, Any]) -> bool:
    """
    Write swarm state to Redis.

    Returns True if write succeeded, False if degraded.
    """
    try:
        import redis

        r = redis.Redis(host="127.0.0.1", port=6379, socket_timeout=2.0)
        raw = json.dumps(state, default=str)
        r.set(SWARM_STATE_KEY, raw)
        logger.info("Swarm state written to Redis")
        return True
    except Exception as exc:
        logger.warning(f"Redis swarm state write failed: {exc}")
        return False


def announce_boot(agent_id: str, session_id: str) -> dict[str, Any]:
    """
    Announce a new agent boot to the swarm state.

    Adds agent to active_agents, updates status to WARM.
    Returns the updated swarm state.
    """
    state = read_swarm_state(session_id=session_id)

    active = state.get("active_agents", [])
    if agent_id not in active:
        active.append(agent_id)

    state["active_agents"] = active
    state["status"] = "WARM" if active else "COLD"
    state["last_boot"] = {
        "agent_id": agent_id,
        "session_id": session_id,
    }

    update_swarm_state(state)
    return state


def announce_offline(agent_id: str) -> dict[str, Any]:
    """
    Announce an agent leaving the swarm.
    Removes agent from active_agents.
    """
    state = read_swarm_state()

    active = state.get("active_agents", [])
    if agent_id in active:
        active.remove(agent_id)

    state["active_agents"] = active
    state["status"] = "WARM" if active else "COLD"

    update_swarm_state(state)
    return state

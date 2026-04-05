"""
arifosmcp/memory/shared_memory_mcp.py
======================================

Multi-agent shared memory bridge — Redis-backed hot scratchpad.
Provides cross-session state for Trinity swarm agents.

Stage: 555_MEMORY | Trinity: OMEGA Ω
Floors: F1 (Amanah/reversibility), F13 (Sovereign gate)
Modes: get, set, list, clear, expire

Constitutional rules:
- F1 AMANAH: all 'set' writes require ttl_seconds > 0 (reversibility mandate)
- F13 SOVEREIGN: operations are namespaced per agent_id + session_id
- Redis unavailable → degrade gracefully with SABAR verdict (no hard crash)
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from arifosmcp.runtime.memory_policy import enforce_memory_policy

logger = logging.getLogger(__name__)

_REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
_redis_client = None


def _redis():
    global _redis_client
    if _redis_client is None:
        import redis as _redis_lib

        _redis_client = _redis_lib.Redis.from_url(_REDIS_URL, decode_responses=True)
    return _redis_client


def _ns(agent_id: str, session_id: str) -> str:
    return f"shared_mem:{agent_id or 'global'}:{session_id or 'anon'}"


async def shared_memory_tool(
    action: str = "get",
    key: str = "",
    value: Any = None,
    agent_id: str = "",
    session_id: str = "",
    ttl_seconds: int = 86400,
    role: str = "",
) -> dict:
    """
    Redis-backed shared memory tool — multi-agent hot scratchpad.

    Modes:
    - get:    Retrieve shared memory by key.
    - set:    Store value with mandatory TTL (F1 reversibility).
    - list:   List all keys in the agent/session namespace.
    - clear:  Remove a single shared memory entry.
    - expire: Reset TTL on an existing key (0 = persist indefinitely).
    """
    payload = {
        "key": key,
        "value": value,
        "agent_id": agent_id,
        "session_id": session_id,
        "ttl_seconds": ttl_seconds,
        "role": role,
    }

    allowed, policy_result = enforce_memory_policy(
        tool_name="shared_memory_tool",
        action=action,
        agent_id=agent_id,
        payload=payload,
    )
    if not allowed:
        return policy_result

    # F1 AMANAH: writes without a TTL are irreversible → reject
    if action == "set" and ttl_seconds <= 0:
        return {
            "ok": False,
            "error": "F1 AMANAH: 'set' requires ttl_seconds > 0 (reversibility mandate).",
            "policy_violation": True,
        }

    try:
        r = _redis()
    except Exception as exc:
        logger.warning("Redis shared_memory unavailable: %s", exc)
        return {
            "ok": False,
            "action": action,
            "error": f"Redis connection failed: {exc}",
            "verdict": "SABAR",
        }

    namespace = _ns(agent_id, session_id)
    full_key = f"{namespace}:{key}"

    if action == "get":
        data = r.get(full_key)
        return {
            "ok": True,
            "action": action,
            "key": key,
            "value": json.loads(data) if data else None,
            "agent_id": agent_id,
            "session_id": session_id,
        }

    if action == "set":
        payload_json = json.dumps(value, default=str)
        r.setex(full_key, ttl_seconds, payload_json)
        return {
            "ok": True,
            "action": action,
            "key": key,
            "bytes_written": len(payload_json.encode()),
            "ttl_seconds": ttl_seconds,
            "agent_id": agent_id,
            "session_id": session_id,
        }

    if action == "list":
        keys = r.keys(f"{namespace}:*")
        return {
            "ok": True,
            "action": action,
            "keys": [k.replace(f"{namespace}:", "") for k in keys],
            "count": len(keys),
            "agent_id": agent_id,
            "session_id": session_id,
        }

    if action == "clear":
        deleted = r.delete(full_key)
        return {
            "ok": True,
            "action": action,
            "key": key,
            "deleted": bool(deleted),
            "agent_id": agent_id,
            "session_id": session_id,
        }

    if action == "expire":
        if ttl_seconds > 0:
            r.expire(full_key, ttl_seconds)
        else:
            r.persist(full_key)
        return {
            "ok": True,
            "action": action,
            "key": key,
            "ttl_seconds": ttl_seconds,
            "agent_id": agent_id,
            "session_id": session_id,
        }

    return {
        "ok": False,
        "action": action,
        "error": f"Unknown action: '{action}'. Supported: get, set, list, clear, expire.",
    }

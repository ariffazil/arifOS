"""
arifos_mcp/memory/shared_memory_mcp.py
======================================

Multi-agent shared memory bridge — Redis-backed.
Provides cross-session hot scratchpad for Trinity swarm agents.

Authority: A-ENGINEER | Floors: F1 (reversible), F13 (sovereign)
Modes: get, set, list, clear, expire
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from arifos_mcp.runtime.memory_policy import enforce_memory_policy

logger = logging.getLogger(__name__)

_REDIS_URL = os.getenv("REDIS_URL", "redis://127.0.0.1:6379")
_ = None


def _redis():
    global _
    if _ is None:
        import redis as _redis_lib  # noqa: I001
        _ = _redis_lib.Redis.from_url(_REDIS_URL, decode_responses=True)
    return _


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
    Redis-backed shared memory tool for multi-agent hot scratchpad.

    Modes:
    - get: Retrieve shared memory by key.
    - set: Store value in shared memory with optional TTL.
    - list: List keys for namespace.
    - clear: Remove shared memory entry.
    - expire: Reset TTL on existing key.
    """
    payload = {
        "key": key,
        "value": value,
        "agent_id": agent_id,
        "session_id": session_id,
        "ttl_seconds": ttl_seconds,
        "role": role,
    }

    # Runtime policy enforcement
    allowed, result = enforce_memory_policy(
        tool_name="shared_memory_tool",
        action=action,
        agent_id=agent_id,
        payload=payload,
    )
    if not allowed:
        return result

    # F1 AMANAH: set operations must have a TTL (reversibility)
    if action == "set" and ttl_seconds <= 0:
        return {
            "ok": False,
            "error": "F1 AMANAH: shared_memory_tool 'set' requires ttl_seconds > 0.",
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
            "agent_id": agent_id,
            "session_id": session_id,
            "count": len(keys),
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
        "error": f"Unknown action: {action}. Supported: get, set, list, clear, expire.",
    }

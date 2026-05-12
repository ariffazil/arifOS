from __future__ import annotations

import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

AZ_URL = os.environ.get("AGENT_ZERO_URL", "http://agent-zero:80")
AZ_API_KEY = os.environ.get("AGENT_ZERO_API_KEY", "")


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat()


def _nine_signal(status: str) -> dict:
    if status == "OK":
        return {
            "delta": {"plane": "machine_physical_state", "state": "KUKUH", "en": "SOLID"},
            "psi": {"plane": "governance_integrity", "state": "AMANAH", "en": "TRUSTED"},
            "omega": {"plane": "intelligence_discipline", "state": "BIJAKSANA", "en": "WISE"},
            "overall": {"state": "SELAMAT", "en": "SAFE"},
        }
    return {
        "delta": {"plane": "machine_physical_state", "state": "ROSAK", "en": "BROKEN"},
        "psi": {"plane": "governance_integrity", "state": "KHIANAT", "en": "BETRAYED"},
        "omega": {"plane": "intelligence_discipline", "state": "BANGANG", "en": "FOOLISH"},
        "overall": {"state": "RETAK", "en": "FAILED"},
    }


def delegate_to_agent_zero(
    task: str,
    project: str | None = None,
    lifetime_hours: int = 1,
) -> dict[str, Any]:
    try:
        headers = {"Content-Type": "application/json"}
        if AZ_API_KEY:
            headers["X-API-KEY"] = AZ_API_KEY

        with httpx.Client(timeout=120) as client:
            resp = client.post(
                f"{AZ_URL}/api_message",
                json={
                    "message": task,
                    "lifetime_hours": lifetime_hours,
                    **(project and {"project_name": project} or {}),
                },
                headers=headers,
            )
            if resp.status_code >= 400:
                raise OSError(f"HTTP {resp.status_code}: {resp.text[:200]}")
            result = resp.json()

        return {
            "status": "OK",
            "tool": "agent_zero_delegate",
            "result": {
                "response": result.get("response", result),
                "context_id": result.get("context_id"),
            },
            "meta": {"reason": "Task delegated to Agent Zero"},
            "output_policy": "DOMAIN_SEAL",
            "timestamp": _now(),
            "nine_signal": _nine_signal("OK"),
            "reasons": ["Agent Zero task completed successfully"],
        }

    except (OSError, httpx.HTTPError, httpx.ConnectError, httpx.TimeoutException) as e:
        return {
            "status": "HOLD",
            "tool": "agent_zero_delegate",
            "result": {"error": str(e)},
            "meta": {"reason": f"Agent Zero unreachable: {e}"},
            "output_policy": "DOMAIN_HOLD",
            "timestamp": _now(),
            "nine_signal": _nine_signal("HOLD"),
            "reasons": [f"Agent Zero unreachable: {e}"],
        }


async def agent_zero_delegate_tool(
    task: str,
    project: str | None = None,
    lifetime_hours: int = 1,
    session_id: str = "global",
    actor_id: str = "arif",
    ctx=None,
) -> dict[str, Any]:
    """Delegate a task to Agent Zero (browser, document, terminal, research)."""
    return delegate_to_agent_zero(task, project, lifetime_hours)

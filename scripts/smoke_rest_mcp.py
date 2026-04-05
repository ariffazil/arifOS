from __future__ import annotations

import os
import sys
from typing import Any

import httpx


def _auth_headers() -> dict[str, str]:
    token = os.getenv("ARIFOS_API_KEY") or os.getenv("ARIFOS_API_TOKEN")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def _call(base_url: str, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/mcp"
    payload = {"tool": tool, "arguments": arguments}
    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            url, json=payload, headers={"Content-Type": "application/json", **_auth_headers()}
        )
        r.raise_for_status()
        return r.json()


def main(argv: list[str]) -> int:
    base_url = os.getenv("arifosmcp_BASE_URL", "http://localhost:8080")
    actor_id = os.getenv("ARIFOS_ACTOR_ID", "smoke")
    query = "Smoke test: full tool surface"

    init = _call(
        base_url,
        "init_session",
        {"query": query, "actor_id": actor_id, "debug": True},
    )
    session_id: str | None = None
    if isinstance(init, dict):
        session_id = (init.get("result") or {}).get("session_id")

    if not session_id:
        print("init_session failed to return session_id:", init, file=sys.stderr)
        return 2

    _call(base_url, "agi_cognition", {"query": query, "session_id": session_id, "debug": True})
    _call(
        base_url,
        "asi_empathy",
        {"query": query, "session_id": session_id, "stakeholders": ["all"], "debug": True},
    )
    _call(
        base_url,
        "apex_verdict",
        {
            "session_id": session_id,
            "query": query,
            "proposed_verdict": "SEAL",
            "human_approve": True,
            "debug": True,
        },
    )
    _call(
        base_url,
        "vault_seal",
        {"session_id": session_id, "summary": "Smoke test seal", "verdict": "SEAL"},
    )

    # Resources + prompts visibility checks (non-fatal)
    try:
        with httpx.Client(timeout=10.0) as client:
            client.get(f"{base_url.rstrip('/')}/tools", headers=_auth_headers())
    except Exception:
        pass

    print(f"OK: session_id={session_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

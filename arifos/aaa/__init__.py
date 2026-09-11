"""arifos.aaa — thin A2A client for the AAA gateway.

CLIENT ONLY. Speaks LF A2A v1.0 JSON-RPC to http://localhost:3001/a2a
(override via ``AAA_A2A_URL``). Auth token read from ``A2A_KEY`` or
``ARIFOS_TOKEN`` env vars when the gateway requires it.

Card discovery works without auth:
- HTTP: GET /.well-known/agent-card.json (gateway card)
- Local: /root/AAA/a2a/registry/agents.yaml (canonical registry, YAML)

Usage::

    from arifos.aaa import A2AClient, cards
    print(len(cards()))                # >= 17 distinct identities on-host
    c = A2AClient()
    c.call("agent/list")               # requires token

CLI::

    python -m arifos.aaa cards
"""

from __future__ import annotations

import itertools
import json
import os
from typing import Any

import httpx

DEFAULT_URL = os.environ.get("AAA_A2A_URL", "http://localhost:3001/a2a")
DEFAULT_BASE = DEFAULT_URL.rsplit("/a2a", 1)[0]
A2A_VERSION = "1.0"
# AGENT_INDEX.json tombstoned 2026-09-08 — superseded by a2a/registry/agents.yaml (YAML).
# cards() now reads the gateway card only; canonical roster resolution is
# paths_resolver.CANON_AGENT_CARD_PATHS (planned).

__all__ = ["A2AClient", "cards", "gateway_card", "DEFAULT_URL"]


class A2AClient:
    """Minimal LF A2A v1.0 JSON-RPC client."""

    def __init__(
        self, url: str = DEFAULT_URL, token: str | None = None, timeout: float = 30.0
    ) -> None:
        self.url = url
        self._ids = itertools.count(1)
        headers = {"Content-Type": "application/json", "A2A-Version": A2A_VERSION}
        token = token or os.environ.get("A2A_KEY") or os.environ.get("ARIFOS_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._http = httpx.Client(timeout=timeout, headers=headers)

    def call(self, method: str, params: dict | None = None) -> Any:
        resp = self._http.post(
            self.url,
            json={
                "jsonrpc": "2.0",
                "id": next(self._ids),
                "method": method,
                "params": params or {},
            },
        )
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(f"A2A error from {method}: {data['error']}")
        return data.get("result")

    def close(self) -> None:
        self._http.close()


def gateway_card(base_url: str = DEFAULT_BASE) -> dict:
    """Fetch the AAA gateway agent card (no auth required)."""
    resp = httpx.get(f"{base_url}/.well-known/agent-card.json", timeout=15.0)
    resp.raise_for_status()
    return resp.json()


def cards() -> list[dict]:
    """Return distinct agent identities via the gateway card.

    AGENT_INDEX.json tombstoned 2026-09-08 (superseded by
    a2a/registry/agents.yaml — YAML, not JSON, so not parsed here).
    Canonical roster resolution: paths_resolver.CANON_AGENT_CARD_PATHS (planned).
    """
    return [gateway_card()]

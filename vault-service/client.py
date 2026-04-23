"""
VAULT999 Client — GEOX/WEALTH use this to seal entries
WELD-003: Unified Merkle-chained vault ledger
DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Optional

import httpx


VAULT_URL = os.environ.get("VAULT_URL", "http://localhost:8100")


class VaultClient:
    """Client for VAULT999 unified service."""

    def __init__(self, base_url: str = VAULT_URL):
        self.base_url = base_url.rstrip("/")
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, *args):
        if self._client:
            await self._client.aclose()

    async def seal(
        self,
        session_id: str,
        domain: str,
        tool: str,
        verdict: str,
        ac_risk: float,
        claim_tag: str,
        floor_violations: list[str] = None,
        epistemic: str = "ESTIMATE",
        witness_human: str = "ARIF",
        witness_ai: str = "AAA-AGENT",
        witness_earth: str = "SEISMIC",
    ) -> dict:
        """
        Write a governed action to the unified ledger.

        Only PROCEED and SEAL are sealed. HOLD and VOID are NOT sealed.
        """
        if verdict not in ("PROCEED", "SEAL"):
            raise ValueError(f"Only PROCEED or SEAL may be sealed. Got: {verdict}")

        payload = {
            "session_id": session_id,
            "domain": domain,
            "tool": tool,
            "verdict": verdict,
            "ac_risk": ac_risk,
            "claim_tag": claim_tag,
            "floor_violations": floor_violations or [],
            "epistemic": epistemic,
            "witness": {
                "human": witness_human,
                "ai": witness_ai,
                "earth": witness_earth,
            },
        }

        payload_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()

        body = {
            "session_id": session_id,
            "domain": domain,
            "tool": tool,
            "verdict": verdict,
            "ac_risk": ac_risk,
            "claim_tag": claim_tag,
            "payload_hash": payload_hash,
            "prev_hash": "",  # filled by server
            "floor_violations": floor_violations or [],
            "epistemic": epistemic,
            "witness_human": witness_human,
            "witness_ai": witness_ai,
            "witness_earth": witness_earth,
        }

        resp = await self._client.post(f"{self.base_url}/vault/seal", json=body)
        resp.raise_for_status()
        return resp.json()

    async def get_session(self, session_id: str) -> dict:
        """Get full chain for a session."""
        resp = await self._client.get(f"{self.base_url}/vault/session/{session_id}")
        resp.raise_for_status()
        return resp.json()

    async def health(self) -> dict:
        """Check service health."""
        resp = await self._client.get(f"{self.base_url}/health")
        resp.raise_for_status()
        return resp.json()


async def seal_vault_entry(
    session_id: str,
    domain: str,
    tool: str,
    verdict: str,
    ac_risk: float,
    claim_tag: str,
    floor_violations: list[str] = None,
) -> Optional[dict]:
    """
    Convenience function: seal a vault entry.

    Returns the ChainedEntry dict, or None if verdict is not PROCEED/SEAL.
    """
    if verdict not in ("PROCEED", "SEAL"):
        return None

    async with VaultClient() as client:
        return await client.seal(
            session_id=session_id,
            domain=domain,
            tool=tool,
            verdict=verdict,
            ac_risk=ac_risk,
            claim_tag=claim_tag,
            floor_violations=floor_violations,
        )
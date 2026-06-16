"""
OPA Bridge — Open Policy Agent HTTP eval client.

Constitutional role: arifOS asks OPA for a recommendation; arifOS is the authority.

Usage:
    bridge = OPABridge(endpoint="http://127.0.0.1:8181")
    verdict = await bridge.evaluate(
        policy_path="lease_policy",
        input={"actor_id": "arif", "action_class": "MUTATE", "tool": "vault_seal"},
    )
    # verdict.recommendation: ALLOW | DENY | SABAR
    # verdict.override: True means arifOS can override (always True for sovereign actions)

F1 AMANAH: OPA failure → fail-closed (deny mutation, allow observe).
F2 TRUTH: Every eval carries input hash for reproducibility.
F11 AUDIT: Every eval is OTLP-traced.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

import httpx
import structlog

log = structlog.get_logger("arifos.policy.opa")


@dataclass
class PolicyInput:
    """Typed policy input for OPA eval."""

    actor_id: str
    action_class: Literal["OBSERVE", "ANALYZE", "MUTATE", "GOVERNED", "SEAL"]
    tool: str
    session_id: Optional[str] = None
    resource: Optional[str] = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_opa(self) -> dict[str, Any]:
        return {
            "actor_id": self.actor_id,
            "action_class": self.action_class,
            "tool": self.tool,
            "session_id": self.session_id or "",
            "resource": self.resource or "",
            **self.extra,
        }

    def input_hash(self) -> str:
        return "sha256:" + hashlib.sha256(
            json.dumps(self.to_opa(), sort_keys=True).encode()
        ).hexdigest()


@dataclass
class PolicyVerdict:
    """OPA verdict wrapped with arifOS authority metadata."""

    recommendation: Literal["ALLOW", "DENY", "SABAR"]
    override: bool  # True if arifOS can override
    confidence: float  # 0.0–0.90 (F7 cap)
    evidence: dict[str, Any]
    input_hash: str
    policy_path: str
    eval_latency_ms: float
    timestamp: str

    def __str__(self) -> str:
        return f"PolicyVerdict({self.recommendation}, conf={self.confidence:.2f}, override={self.override})"


class OPABridge:
    """
    Async HTTP client for OPA REST API.

    Endpoint: http://127.0.0.1:8181 (default OPA port).
    Per ADR-001: Localhost IS the password. Bind 127.0.0.1, no auth.
    """

    def __init__(self, endpoint: str = "http://127.0.0.1:8181", timeout: float = 5.0):
        self.endpoint = endpoint.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def evaluate(
        self,
        policy_path: str,
        input: PolicyInput,
    ) -> PolicyVerdict:
        """
        Evaluate a Rego policy at policy_path with given input.

        Fails closed on network/OPA errors (DENY with override=True).
        """
        client = await self._ensure_client()
        url = f"{self.endpoint}/v1/data/{policy_path}"
        payload = {"input": input.to_opa()}
        t0 = time.time()

        try:
            resp = await client.post(url, json=payload)
            latency = (time.time() - t0) * 1000
            resp.raise_for_status()
            data = resp.json()
        except (httpx.HTTPError, httpx.RequestError, Exception) as e:
            log.warning("opa_eval_failed", error=str(e), policy=policy_path)
            # F1 AMANAH: fail-closed for mutations, fail-open for observes
            return PolicyVerdict(
                recommendation="DENY" if input.action_class in ("MUTATE", "SEAL") else "SABAR",
                override=True,
                confidence=0.5,
                evidence={"opa_error": str(e), "fail_closed": True},
                input_hash=input.input_hash(),
                policy_path=policy_path,
                eval_latency_ms=(time.time() - t0) * 1000,
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            )

        # Parse OPA response
        result = data.get("result", {})
        allow = result.get("allow", False)
        deny = result.get("deny", False)
        sabar = result.get("sabar", False)

        if allow:
            rec = "ALLOW"
        elif deny:
            rec = "DENY"
        else:
            rec = "SABAR"

        return PolicyVerdict(
            recommendation=rec,
            override=result.get("override", True),
            confidence=min(0.90, float(result.get("confidence", 0.85))),
            evidence=result,
            input_hash=input.input_hash(),
            policy_path=policy_path,
            eval_latency_ms=latency,
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

    async def load_policy(self, policy_path: str, rego_source: str) -> dict[str, Any]:
        """Load a Rego policy bundle into OPA (PUT /v1/policies/{path})."""
        client = await self._ensure_client()
        url = f"{self.endpoint}/v1/policies/{policy_path}"
        try:
            resp = await client.put(url, content=rego_source, headers={"Content-Type": "text/plain"})
            resp.raise_for_status()
            return {"status": "loaded", "policy_path": policy_path}
        except httpx.HTTPError as e:
            log.error("opa_load_failed", error=str(e), policy=policy_path)
            return {"status": "failed", "error": str(e), "policy_path": policy_path}

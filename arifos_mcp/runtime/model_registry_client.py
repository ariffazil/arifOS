"""
arifos_mcp/runtime/model_registry_client.py
==========================================

Lightweight async client for arifOS Model Registry.
Provides constitutional identity verification and model metadata lookup.

Wired to:
- architect_registry tool (model discovery modes)
- init_anchor (identity verification)
- A-ARCHITECT (model governance)

Environment:
- MODEL_REGISTRY_URL: http://model_registry:18792 (docker internal)
- Fallback: http://host.docker.internal:18792 (host access)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_REGISTRY_URL = os.getenv("MODEL_REGISTRY_URL", "http://model_registry:18792")


@dataclass
class ModelProfile:
    """Canonical model profile from registry."""
    provider: str
    family: str
    variant: str
    model_key: str
    capabilities: list[str]
    context_window: int
    constitutional_notes: str


@dataclass
class ProviderSoul:
    """Provider soul (governance archetype) from registry."""
    soul_key: str
    provider_name: str
    archetype: str
    constitutional_alignment: dict[str, Any]
    default_behavior: dict[str, Any]


@dataclass
class IdentityVerification:
    """Result of identity claim verification."""
    verified: bool
    declared: str
    matched_key: str | None
    model: dict | None
    mismatch_detected: bool
    drift_risk: str


class ModelRegistryClient:
    """
    Async client for arifOS Model Registry.
    
    Provides:
    - Model profile lookup (provider/family/variant)
    - Provider soul retrieval
    - Runtime profile lookup
    - Identity claim verification (F11 grounding)
    - Session anchor v2 creation
    """
    
    def __init__(self, base_url: str = DEFAULT_REGISTRY_URL):
        self.base_url = base_url.rstrip("/")
        self._client: Any = None
    
    async def _get_client(self):
        """Lazy httpx client initialization."""
        if self._client is None:
            import httpx
            self._client = httpx.AsyncClient(timeout=10.0)
        return self._client
    
    async def health(self) -> dict:
        """Check registry health."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning(f"Model registry health check failed: {exc}")
            return {"status": "unavailable", "error": str(exc)}
    
    async def get_model_profile(self, model_key: str) -> ModelProfile | None:
        """
        Get full model profile.
        
        model_key format: "provider/family/variant" (e.g., "anthropic/claude/claude-3-7-sonnet")
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/model/{model_key}")
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            return ModelProfile(
                provider=result.get("provider", ""),
                family=result.get("family", ""),
                variant=result.get("variant", ""),
                model_key=model_key,
                capabilities=result.get("capabilities", []),
                context_window=result.get("context_window", 0),
                constitutional_notes=result.get("constitutional_notes", ""),
            )
        except Exception as exc:
            logger.warning(f"Failed to get model profile for {model_key}: {exc}")
            return None
    
    async def get_provider_soul(self, soul_key: str) -> ProviderSoul | None:
        """
        Get provider soul (governance archetype).
        
        soul_key format: e.g., "anthropic_claude", "openai_gpt"
        """
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/soul/{soul_key}")
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            return ProviderSoul(
                soul_key=soul_key,
                provider_name=result.get("provider_name", ""),
                archetype=result.get("archetype", ""),
                constitutional_alignment=result.get("constitutional_alignment", {}),
                default_behavior=result.get("default_behavior", {}),
            )
        except Exception as exc:
            logger.warning(f"Failed to get provider soul for {soul_key}: {exc}")
            return None
    
    async def verify_identity(self, claimed_identity: str, claimed_provider: str | None = None) -> IdentityVerification:
        """
        Verify a model's claimed identity against the canonical registry.
        
        This is F11 (Identity) grounding - ensures the model is who it claims to be.
        """
        try:
            client = await self._get_client()
            payload = {"claimed_identity": claimed_identity}
            if claimed_provider:
                payload["claimed_provider"] = claimed_provider
            response = await client.post(f"{self.base_url}/verify/identity", json=payload)
            response.raise_for_status()
            data = response.json()
            result = data.get("result", {})
            return IdentityVerification(
                verified=result.get("verification_status") == "confirmed",
                declared=result.get("declared", claimed_identity),
                matched_key=result.get("verified"),
                model=result.get("model"),
                mismatch_detected=result.get("mismatch_detected", False),
                drift_risk=result.get("drift_risk", "unknown"),
            )
        except Exception as exc:
            logger.warning(f"Identity verification failed for {claimed_identity}: {exc}")
            return IdentityVerification(
                verified=False,
                declared=claimed_identity,
                matched_key=None,
                model=None,
                mismatch_detected=True,
                drift_risk="high",
            )
    
    async def list_models(self) -> list[str]:
        """List all registered model keys."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except Exception as exc:
            logger.warning(f"Failed to list models: {exc}")
            return []
    
    async def list_providers(self) -> list[str]:
        """List all registered provider soul keys."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/providers")
            response.raise_for_status()
            data = response.json()
            return data.get("providers", [])
        except Exception as exc:
            logger.warning(f"Failed to list providers: {exc}")
            return []
    
    async def init_anchor_v2(
        self,
        actor_id: str,
        declared_model_key: str,
        declared_role: str | None = None,
        requested_scope: list[str] | None = None,
    ) -> dict:
        """
        Create a MODEL_SOUL-bound session anchor.
        
        This is the v2 init_anchor that binds sessions to canonical model identities.
        """
        try:
            client = await self._get_client()
            payload = {
                "actor_id": actor_id,
                "declared_model_key": declared_model_key,
                "declared_role": declared_role,
                "requested_scope": requested_scope or ["read", "query"],
            }
            response = await client.post(f"{self.base_url}/init_anchor_v2", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning(f"Init anchor v2 failed for {actor_id}: {exc}")
            return {
                "ok": False,
                "tool": "init_anchor_v2",
                "status": "FAIL",
                "errors": [str(exc)],
            }
    
    async def get_catalog(self) -> dict:
        """Get the full registry catalog."""
        try:
            client = await self._get_client()
            response = await client.get(f"{self.base_url}/catalog")
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            logger.warning(f"Failed to get catalog: {exc}")
            return {}


# Singleton instance for reuse
_registry_client: ModelRegistryClient | None = None


def get_model_registry_client() -> ModelRegistryClient:
    """Get or create the singleton model registry client."""
    global _registry_client
    if _registry_client is None:
        _registry_client = ModelRegistryClient()
    return _registry_client


async def verify_model_identity(
    claimed_identity: str,
    claimed_provider: str | None = None,
) -> IdentityVerification:
    """
    Convenience function for F11 identity verification.
    
    Usage:
        result = await verify_model_identity("claude-3-7-sonnet", "anthropic")
        if result.verified:
            print(f"Identity confirmed: {result.matched_key}")
        else:
            print(f"DRIFT DETECTED: {result.drift_risk}")
    """
    client = get_model_registry_client()
    return await client.verify_identity(claimed_identity, claimed_provider)

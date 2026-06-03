"""
Capability Gateway — Secret Gateway Reconstruction A Foundation
═══════════════════════════════════════════════════════════════════════════════

Agents request capabilities, never raw secrets.
This gateway maps capability → provider → secret → execution.

Hard rules:
  - No tool calls os.getenv("API_KEY") directly.
  - All secret access routes through this gateway.
  - agent_visible_secret is always FALSE.
  - Capability grants expire and must be renewed.

DITEMPA BUKAN DIBERI — Jurisdiction before intelligence.
"""

from __future__ import annotations

import logging
import os
from datetime import UTC, datetime
from typing import Any

from arifosmcp.schemas.capability_grant import (
    CapabilityGrant,
    CapabilityProvider,
    CapabilityRequest,
)

logger = logging.getLogger(__name__)


class CapabilityResolutionError(Exception):
    """Raised when a capability cannot be resolved."""

    pass


class CapabilityGateway:
    """
    Central gateway for capability-based secret access.

    Holds a registry of capability → provider mappings.
    Secrets are resolved at gateway level, never returned to agents.
    """

    def __init__(self) -> None:
        self._grants: dict[str, CapabilityGrant] = {}  # key: "actor_id:capability"
        self._provider_config: dict[CapabilityProvider, dict[str, Any]] = {}
        self._resolve_log: list[dict[str, Any]] = []

    # ═══════════════════════════════════════════════════════════════════════════
    # REGISTRATION
    # ═══════════════════════════════════════════════════════════════════════════

    def register_provider(
        self,
        provider: CapabilityProvider,
        config: dict[str, Any],
    ) -> None:
        """Register a provider configuration."""
        self._provider_config[provider] = config
        logger.info(f"Registered provider {provider.value}")

    def grant(
        self,
        actor_id: str,
        capability: str,
        provider: CapabilityProvider,
        scope: list[str],
        secret_location: str,
        expires_at: datetime | None = None,
        session_id: str | None = None,
    ) -> CapabilityGrant:
        """
        Grant a capability to an actor.

        The agent never sees the secret_location in its view.
        """
        grant = CapabilityGrant(
            capability=capability,
            provider=provider,
            scope=scope,
            secret_location=secret_location,
            actor_id=actor_id,
            session_id=session_id,
            expires_at=expires_at,
        )
        key = f"{actor_id}:{capability}"
        self._grants[key] = grant
        logger.info(f"Granted {capability} to {actor_id}")
        return grant

    def revoke(self, actor_id: str, capability: str) -> None:
        """Revoke a capability grant."""
        key = f"{actor_id}:{capability}"
        if key in self._grants:
            del self._grants[key]
            logger.info(f"Revoked {capability} from {actor_id}")

    # ═══════════════════════════════════════════════════════════════════════════
    # RESOLUTION
    # ═══════════════════════════════════════════════════════════════════════════

    def resolve(
        self,
        request: CapabilityRequest,
        require_verified: bool = True,
    ) -> tuple[bool, str | None, CapabilityGrant | None]:
        """
        Resolve a capability request.

        Returns (ok, resolved_secret_or_reason, grant).

        If ok is True, the caller may proceed with the resolved secret.
        If ok is False, the reason string explains the denial.
        """
        actor_id = request.actor_id
        capability = request.capability
        requested_scope = request.scope

        key = f"{actor_id}:{capability}"
        grant = self._grants.get(key)

        if not grant:
            msg = f"Capability '{capability}' not granted to {actor_id}"
            self._log_resolve(actor_id, capability, False, msg)
            return False, msg, None

        if grant.is_expired():
            msg = f"Capability '{capability}' expired for {actor_id}"
            self._log_resolve(actor_id, capability, False, msg)
            return False, msg, None

        # Scope check
        if requested_scope and not any(grant.allows_scope(s) for s in requested_scope):
            msg = f"Capability '{capability}' scope mismatch for {actor_id}"
            self._log_resolve(actor_id, capability, False, msg)
            return False, msg, None

        # Resolve secret
        secret = self._resolve_secret(grant)
        if secret is None:
            msg = f"Secret for '{capability}' could not be resolved"
            self._log_resolve(actor_id, capability, False, msg)
            return False, msg, grant

        self._log_resolve(actor_id, capability, True, "resolved")
        return True, secret, grant

    def _resolve_secret(self, grant: CapabilityGrant) -> str | None:
        """
        Resolve the secret for a grant.

        This is the ONLY place in the federation where raw secrets are accessed.
        The agent never sees this path.
        """
        loc = grant.secret_location

        # Gateway-internal path format: gateway://<provider>/<service>/<account>
        if loc.startswith("gateway://"):
            parts = loc.replace("gateway://", "").split("/")
            if len(parts) >= 2:
                provider = parts[0]
                # Map to provider config
                provider_enum = None
                try:
                    provider_enum = CapabilityProvider(provider)
                except ValueError:
                    pass

                if provider_enum and provider_enum in self._provider_config:
                    config = self._provider_config[provider_enum]
                    # Composio bridge pattern
                    if provider == "composio":
                        # Return the API key from config
                        return config.get("api_key")
                    # Generic env-based resolution
                    env_key = config.get("env_key")
                    if env_key:
                        val = os.environ.get(env_key)
                        if val:
                            return val

        # Direct env fallback (legacy migration)
        if loc.startswith("env://"):
            env_var = loc.replace("env://", "")
            val = os.environ.get(env_var)
            if val:
                return val
            # Try secrets directory
            secret_file = f"/root/.secrets/env/{env_var}.txt"
            if os.path.exists(secret_file):
                try:
                    with open(secret_file) as f:
                        return f.read().strip()
                except Exception:
                    pass

        return None

    def _log_resolve(
        self,
        actor_id: str,
        capability: str,
        success: bool,
        detail: str,
    ) -> None:
        """Log resolution attempts (no secrets, ever)."""
        self._resolve_log.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "actor_id": actor_id,
            "capability": capability,
            "success": success,
            "detail": detail,
        })

    # ═══════════════════════════════════════════════════════════════════════════
    # QUERIES
    # ═══════════════════════════════════════════════════════════════════════════

    def list_grants(self, actor_id: str) -> list[dict[str, Any]]:
        """List all active grants for an actor (agent view, no secrets)."""
        result = []
        for key, grant in self._grants.items():
            if key.startswith(f"{actor_id}:"):
                result.append(grant.to_agent_view())
        return result

    def get_grant(self, actor_id: str, capability: str) -> CapabilityGrant | None:
        """Get a raw grant (gateway internal use only)."""
        key = f"{actor_id}:{capability}"
        return self._grants.get(key)

    def audit_log(self) -> list[dict[str, Any]]:
        """Return resolution audit log (no secrets)."""
        return self._resolve_log.copy()


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════

_gateway: CapabilityGateway | None = None


def get_gateway() -> CapabilityGateway:
    """Return the singleton gateway instance."""
    global _gateway
    if _gateway is None:
        _gateway = CapabilityGateway()
    return _gateway

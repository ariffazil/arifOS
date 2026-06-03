"""
Test Capability Gateway — Reconstruction A Foundation
══════════════════════════════════════════════════════
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from arifosmcp.core.gateway.capability_gateway import (
    CapabilityGateway,
    get_gateway,
)
from arifosmcp.schemas.capability_grant import (
    CapabilityGrant,
    CapabilityProvider,
    CapabilityRequest,
)


class TestCapabilityGrant:
    def test_agent_visible_secret_forbidden(self):
        with pytest.raises(ValueError, match="agent_visible_secret"):
            CapabilityGrant(
                capability="gmail.read",
                provider=CapabilityProvider.COMPOSIO,
                scope=["read"],
                secret_location="gateway://composio/gmail/arif",
                actor_id="arif",
                agent_visible_secret=True,
            )

    def test_default_invisible(self):
        grant = CapabilityGrant(
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
            actor_id="arif",
        )
        assert grant.agent_visible_secret is False

    def test_expired(self):
        grant = CapabilityGrant(
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
            actor_id="arif",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        assert grant.is_expired() is True

    def test_not_expired(self):
        grant = CapabilityGrant(
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
            actor_id="arif",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
        assert grant.is_expired() is False

    def test_allows_scope(self):
        grant = CapabilityGrant(
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read", "write"],
            secret_location="gateway://composio/gmail/arif",
            actor_id="arif",
        )
        assert grant.allows_scope("read") is True
        assert grant.allows_scope("delete") is False

    def test_admin_scope_allows_all(self):
        grant = CapabilityGrant(
            capability="gmail.admin",
            provider=CapabilityProvider.COMPOSIO,
            scope=["admin"],
            secret_location="gateway://composio/gmail/arif",
            actor_id="arif",
        )
        assert grant.allows_scope("read") is True
        assert grant.allows_scope("write") is True
        assert grant.allows_scope("delete") is True

    def test_to_agent_view_hides_secret(self):
        grant = CapabilityGrant(
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
            actor_id="arif",
        )
        view = grant.to_agent_view()
        assert "capability" in view
        assert "secret_location" not in view
        assert "provider" in view


class TestCapabilityGateway:
    def test_grant_and_resolve(self):
        gw = CapabilityGateway()
        gw.register_provider(CapabilityProvider.COMPOSIO, {"api_key": "test-key-123"})
        gw.grant(
            actor_id="arif",
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
        )

        req = CapabilityRequest(
            capability="gmail.read",
            scope=["read"],
            actor_id="arif",
        )
        ok, secret, grant = gw.resolve(req)
        assert ok is True
        assert secret == "test-key-123"
        assert grant is not None

    def test_resolve_ungranted(self):
        gw = CapabilityGateway()
        req = CapabilityRequest(
            capability="gmail.read",
            actor_id="arif",
        )
        ok, reason, grant = gw.resolve(req)
        assert ok is False
        assert "not granted" in reason
        assert grant is None

    def test_resolve_expired(self):
        gw = CapabilityGateway()
        gw.register_provider(CapabilityProvider.COMPOSIO, {"api_key": "test-key"})
        gw.grant(
            actor_id="arif",
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
            expires_at=datetime.now(UTC) - timedelta(hours=1),
        )
        req = CapabilityRequest(capability="gmail.read", actor_id="arif")
        ok, reason, grant = gw.resolve(req)
        assert ok is False
        assert "expired" in reason

    def test_resolve_scope_mismatch(self):
        gw = CapabilityGateway()
        gw.register_provider(CapabilityProvider.COMPOSIO, {"api_key": "test-key"})
        gw.grant(
            actor_id="arif",
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
        )
        req = CapabilityRequest(capability="gmail.read", scope=["delete"], actor_id="arif")
        ok, reason, grant = gw.resolve(req)
        assert ok is False
        assert "scope mismatch" in reason

    def test_revoke(self):
        gw = CapabilityGateway()
        gw.register_provider(CapabilityProvider.COMPOSIO, {"api_key": "test-key"})
        gw.grant(
            actor_id="arif",
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
        )
        gw.revoke("arif", "gmail.read")
        req = CapabilityRequest(capability="gmail.read", actor_id="arif")
        ok, reason, grant = gw.resolve(req)
        assert ok is False
        assert "not granted" in reason

    def test_list_grants(self):
        gw = CapabilityGateway()
        gw.grant(
            actor_id="arif",
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
        )
        grants = gw.list_grants("arif")
        assert len(grants) == 1
        assert grants[0]["capability"] == "gmail.read"
        assert "secret_location" not in grants[0]

    def test_audit_log_no_secrets(self):
        gw = CapabilityGateway()
        gw.register_provider(CapabilityProvider.COMPOSIO, {"api_key": "test-key"})
        gw.grant(
            actor_id="arif",
            capability="gmail.read",
            provider=CapabilityProvider.COMPOSIO,
            scope=["read"],
            secret_location="gateway://composio/gmail/arif",
        )
        req = CapabilityRequest(capability="gmail.read", actor_id="arif")
        gw.resolve(req)
        log = gw.audit_log()
        assert len(log) == 1
        assert log[0]["success"] is True
        # No secrets in log
        assert "test-key" not in str(log)

    def test_env_fallback_resolution(self, monkeypatch):
        monkeypatch.setenv("TEST_API_KEY", "env-secret-123")
        gw = CapabilityGateway()
        gw.grant(
            actor_id="arif",
            capability="test.read",
            provider=CapabilityProvider.CUSTOM,
            scope=["read"],
            secret_location="env://TEST_API_KEY",
        )
        req = CapabilityRequest(capability="test.read", actor_id="arif")
        ok, secret, grant = gw.resolve(req)
        assert ok is True
        assert secret == "env-secret-123"


class TestSingleton:
    def test_get_gateway_singleton(self):
        g1 = get_gateway()
        g2 = get_gateway()
        assert g1 is g2

"""
tests/test_session_preflight.py
═══════════════════════════════════════════════════════════════════
Tests for the pre-session / preflight lanes added to arif_session_init
and arif_kernel_route, plus the actor-propagation fix in the ingress
middleware.

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import pytest

from arifosmcp.runtime.ingress_middleware import _try_promote_local_service
from arifosmcp.schemas.federation_envelope import (
    AuthorityEnvelope,
    FederationEnvelope,
    FederationOrgan,
    RiskPassport,
)
from arifosmcp.tools.kernel import arif_kernel_route
from arifosmcp.tools.session import arif_session_init


@pytest.mark.asyncio
def test_session_init_ping_no_actor():
    """ping mode must work without actor_id and return kernel status."""
    result = arif_session_init(mode="ping")

    assert result.status == "OK"
    assert result.mode == "ping"
    assert result.result["kernel"] == "alive"
    assert result.result["observe_only"] is True
    assert result.result["mutation_allowed"] is False
    assert "required_for_init" in result.result
    assert "canonical_tools" in result.result


@pytest.mark.asyncio
def test_session_init_light_creates_session_birth():
    """light/full/init must return session_birth summary."""
    result = arif_session_init(
        mode="light",
        actor_id="arifbfazil",
        declared_model_key="minimax-m3",
    )

    assert result.status == "OK"
    assert "session_birth" in result.result
    birth = result.result["session_birth"]
    assert birth["actor_id"] == "arifbfazil"
    assert birth["actor_verified"] is False
    assert birth["authority_mode"] == "OPERATOR"
    assert birth["mutation_allowed"] is False
    assert birth["stage"] == "000"
    assert birth["session_id"].startswith("SEAL-")


def test_kernel_route_preflight_no_session():
    """preflight must work without session_id and return observe-only status."""
    result = arif_kernel_route(mode="preflight")

    assert result["status"] == "OK"
    assert result["result"]["kernel"] == "alive"
    assert result["result"]["observe_only"] is True
    assert result["result"]["session_required"] is True
    assert result["result"]["session_id_present"] is False
    assert "arif_session_init" in result["result"]["next_safe_action"]


def test_ingress_middleware_actor_recovery():
    """When Hermes sends itself as actor_id, middleware must recover the human caller."""
    envelope = FederationEnvelope(
        trace_id="trace-test-001",
        actor_id="Hermes@af-forge",
        caller_actor="arifbfazil",
        sovereign="arifbfazil",
        session_id="SEAL-TEST12345678",
        organ=FederationOrgan.ARIFOS,
        authority=AuthorityEnvelope(),
        risk=RiskPassport(),
        legacy_wrap=True,
    )

    promoted = _try_promote_local_service(envelope, {}, "arif_session_init")

    assert promoted is True
    assert envelope.actor_id == "arifbfazil"
    assert envelope.caller_actor == "arifbfazil"
    assert envelope.sovereign == "arifbfazil"
    assert envelope.executor_actor == "Hermes@af-forge"
    assert envelope.actor_verification == "delegated"


def test_ingress_middleware_human_actor_preserved():
    """When the original actor_id is already human, it must be preserved."""
    envelope = FederationEnvelope(
        trace_id="trace-test-002",
        actor_id="arifbfazil",
        session_id="SEAL-TEST12345678",
        organ=FederationOrgan.ARIFOS,
        authority=AuthorityEnvelope(),
        risk=RiskPassport(),
        legacy_wrap=True,
    )

    promoted = _try_promote_local_service(envelope, {}, "arif_kernel_route")

    assert promoted is True
    assert envelope.actor_id == "arifbfazil"
    assert envelope.caller_actor == "arifbfazil"
    assert envelope.sovereign == "arifbfazil"
    assert envelope.executor_actor == "Hermes@af-forge"

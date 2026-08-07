"""Focused B2 constitutional chokepoint regression tests."""

from __future__ import annotations

import builtins
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from starlette.applications import Starlette

from arifosmcp.runtime import ingress_middleware as ingress
from arifosmcp.runtime import act_token as sct
from arifosmcp.runtime.forge_preflight import g4_validate_sealed_forge_plan
from arifosmcp.schemas.federation_envelope import (
    AuthorityEnvelope,
    FederationEnvelope,
    FederationOrgan,
    RiskPassport,
)


def _legacy_envelope() -> FederationEnvelope:
    return FederationEnvelope(
        trace_id="b2-trace",
        actor_id="Hermes@af-forge",
        caller_actor="arifbfazil",
        sovereign="arifbfazil",
        session_id="SEAL-B2-TEST",
        organ=FederationOrgan.ARIFOS,
        authority=AuthorityEnvelope(),
        risk=RiskPassport(),
        legacy_wrap=True,
    )


def test_hermes_promotion_requires_localhost_and_constant_time_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    token = "t" * 32
    monkeypatch.setattr(ingress, "_load_service_token", lambda: token)

    monkeypatch.setattr(ingress, "_is_localhost_caller", lambda: True)
    envelope = _legacy_envelope()
    assert (
        ingress._try_promote_local_service(envelope, {"service_token": token}, "arif_forge") is True
    )
    assert envelope.legacy_wrap is False
    assert envelope.actor_verification == "delegated"

    monkeypatch.setattr(ingress, "_is_localhost_caller", lambda: False)
    envelope = _legacy_envelope()
    assert (
        ingress._try_promote_local_service(envelope, {"service_token": token}, "arif_forge")
        is False
    )
    assert envelope.legacy_wrap is True
    assert envelope.actor_id == "Hermes@af-forge"

    monkeypatch.setattr(ingress, "_is_localhost_caller", lambda: True)
    envelope = _legacy_envelope()
    assert (
        ingress._try_promote_local_service(envelope, {"service_token": "x" * 32}, "arif_forge")
        is False
    )
    assert envelope.legacy_wrap is True
    assert envelope.actor_verification != "delegated"


@pytest.mark.asyncio
async def test_rest_gate_import_failure_returns_structured_hold_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from arifosmcp.runtime.rest_routes import rest_routes as routes

    called = False

    async def tool(**_: Any) -> dict[str, str]:
        nonlocal called
        called = True
        return {"status": "OK"}

    app = Starlette()
    routes.register_rest_routes(app, {"arif_observe": tool})
    real_import = builtins.__import__

    def fail_gate(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "arifosmcp.runtime.pre_execution_gate":
            raise ImportError("test gate import failure")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_gate)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/tools/arif_observe", json={})

    payload = response.json()
    assert response.status_code == 503
    assert payload["verdict"] == "HOLD"
    assert payload["error"] == "GATE_UNAVAILABLE"
    assert payload["tool"] == "arif_observe"
    assert called is False


@pytest.mark.asyncio
async def test_rest_gate_available_allows_dispatch_after_gate_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from arifosmcp.runtime.rest_routes import rest_routes as routes

    async def tool(**_: Any) -> dict[str, str]:
        return {"status": "OK"}

    class _PassGate:
        is_blocked = False
        verdict = SimpleNamespace(value="SEAL")
        reasons: list[str] = []
        violations: list[str] = []

    monkeypatch.setattr(routes, "_rest_action_class", lambda *_: SimpleNamespace(value="OBSERVE"))
    monkeypatch.setattr(routes, "_is_actor_verified", lambda *_: True, raising=False)

    import arifosmcp.runtime.pre_execution_gate as gate

    monkeypatch.setattr(gate, "quick_gate", lambda **_: _PassGate())
    app = Starlette()
    routes.register_rest_routes(app, {"arif_observe": tool})
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        response = await client.post("/tools/arif_observe", json={})

    assert response.status_code == 200
    assert response.json()["result"] == {"status": "OK"}


def test_g4_dispatch_validation_passes_with_available_dependencies() -> None:
    valid, reasons = g4_validate_sealed_forge_plan(
        judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        plan_id="plan-b2",
    )

    assert valid is True
    assert reasons == []


@pytest.mark.parametrize("failure", [ImportError("missing"), AttributeError("missing")])
def test_g4_dispatch_import_or_attribute_failure_holds(
    monkeypatch: pytest.MonkeyPatch, failure: Exception
) -> None:
    real_import = builtins.__import__

    def fail_dispatch(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "arifosmcp.runtime.forge_dispatch":
            raise failure
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fail_dispatch)
    valid, reasons = g4_validate_sealed_forge_plan(
        judge_verdict="JUDGE_SEAL_AUTHORIZATION",
        plan_id="plan-b2",
    )

    assert valid is False
    assert any("E_PREFLIGHT_G4_DISPATCH_UNAVAILABLE" in reason for reason in reasons)


def test_sct_fallback_is_process_local_random_and_strict_production_holds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ARIFOS_SESSION_SECRET", raising=False)
    monkeypatch.delenv("ARIFOS_SESSION_SECRET_FILE", raising=False)
    monkeypatch.setattr(sct, "_PROD_SIGNING_KEY_PATHS", ())
    monkeypatch.setenv("ARIFOS_ENV", "development")
    monkeypatch.setenv("ARIFOS_STRICT_MODE", "0")

    first = sct._get_signing_secret()
    second = sct._get_signing_secret()
    assert len(first) == 32
    assert first == second
    assert first != b"fallback-ephemeral-secret"

    monkeypatch.setenv("ARIFOS_ENV", "production")
    with pytest.raises(RuntimeError, match="strict production"):
        sct._get_signing_secret()
    assert sct.verify_sct("act_v1.invalid.invalid") is None

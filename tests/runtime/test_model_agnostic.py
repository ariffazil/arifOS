"""Model-agnostic constitutional role gate (2026-10-17).

The frozen AGENT_MODEL_MAP is marked SUPERSEDED_BY_FEDERATION_MODELS_JSON.
These tests pin the fallback order:
  1. explicit AGENT_MODEL_MAP role set (when present)
  2. ARIFOS_CONSTITUTIONAL_MODELS env override
  3. live federation registry (model_routes[].constitutional == true)
  4. fail-closed when nothing is available
"""

from __future__ import annotations

import json

import pytest

from arifosmcp.runtime.llm_client import (
    LLMUnavailableError,
    select_model_for_role,
)


@pytest.fixture(autouse=True)
def isolated_outputs(tmp_path, monkeypatch):
    monkeypatch.setenv("ARIFOS_VAULT_OUTCOMES_PATH", str(tmp_path / "outcomes.jsonl"))
    monkeypatch.setenv("ARIFOS_AGENT_MODEL_MAP_PATH", str(tmp_path / "missing-map.json"))
    monkeypatch.delenv("ARIFOS_CONSTITUTIONAL_MODELS", raising=False)
    monkeypatch.delenv("ARIFOS_FEDERATION_MODELS", raising=False)
    yield


def test_env_override_allows_model(monkeypatch):
    monkeypatch.setenv("ARIFOS_CONSTITUTIONAL_MODELS", "vendor-x/model-y")
    assert (
        select_model_for_role("666_JUDGE", "vendor-x/model-y") == "vendor-x/model-y"
    )
    assert select_model_for_role("999_SEAL", "model-y") == "model-y"


def test_env_override_rejects_unknown_model(monkeypatch):
    monkeypatch.setenv("ARIFOS_CONSTITUTIONAL_MODELS", "vendor-x/model-y")
    with pytest.raises(LLMUnavailableError) as exc:
        select_model_for_role("666_JUDGE", "other/model")
    assert "FORBIDDEN_MODEL_FOR_ROLE" in str(exc.value)


def test_federation_registry_constitutional_flag(tmp_path, monkeypatch):
    registry = tmp_path / "federation-models.json"
    registry.write_text(
        json.dumps(
            {
                "model_routes": {
                    "alpha/beta": [{"provider": "alpha", "constitutional": True}],
                    "gamma/delta": [{"provider": "gamma", "constitutional": False}],
                }
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARIFOS_FEDERATION_MODELS", str(registry))

    assert select_model_for_role("666_JUDGE", "alpha/beta") == "alpha/beta"
    assert select_model_for_role("666_JUDGE", "beta") == "beta"
    with pytest.raises(LLMUnavailableError):
        select_model_for_role("666_JUDGE", "gamma/delta")


def test_non_constitutional_role_is_passthrough():
    assert select_model_for_role("333_REASON", "anything/at-all") == "anything/at-all"
    assert select_model_for_role(None, "whatever") == "whatever"


def test_no_source_stays_fail_closed(monkeypatch, tmp_path):
    monkeypatch.setenv("ARIFOS_FEDERATION_MODELS", str(tmp_path / "missing-fed.json"))
    monkeypatch.delenv("ARIFOS_CONSTITUTIONAL_MODELS", raising=False)
    with pytest.raises(LLMUnavailableError):
        select_model_for_role("666_JUDGE", "deepseek-v4-pro")

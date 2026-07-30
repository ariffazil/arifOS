"""
F13 Constitutional Model-Role Enforcement — 666_JUDGE / 999_SEAL gate.

Sovereign directive 2026-07-24: the AGENT_MODEL_MAP law must be executable
at call_llm() time, not just declarative. select_model_for_role() reads
the canonical map and fail-closes with a FORBIDDEN_MODEL_FOR_ROLE event
when a constitutional role (666_JUDGE, 999_SEAL) is served by a model
the map forbids for that role.

These tests are hermetic: they use tmp AGENT_MODEL_MAP fixtures and a
tmp VAULT999 outcomes path, and never touch the live /root/AAA registry
or the real VAULT999 ledger.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest

from arifosmcp.runtime import llm_client
from arifosmcp.runtime.llm_client import LLMUnavailableError, select_model_for_role


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
def agent_model_map_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Write a minimal AGENT_MODEL_MAP.json to tmp and point the gate at it."""
    map_path = tmp_path / "AGENT_MODEL_MAP.json"
    map_data: dict[str, Any] = {
        "models": [
            {
                "model_key": "deepseek/deepseek-v4-pro",
                "constitutional_roles": [
                    "333_THINK",
                    "444_ROUTE",
                    "555_MEMORY",
                    "666_JUDGE",
                    "777_FORGE",
                    "999_SEAL",
                ],
                "constitutional_roles_forbidden": [],
            },
            {
                "model_key": "deepseek/deepseek-v4-flash",
                "constitutional_roles": ["333_THINK", "444_ROUTE", "555_MEMORY"],
                "constitutional_roles_forbidden": [
                    "666_JUDGE",
                    "999_SEAL",
                ],
            },
            {
                "model_key": "minimax/MiniMax-M3",
                "constitutional_roles": ["777_FORGE"],
                "constitutional_roles_forbidden": [
                    "666_JUDGE",
                    "999_SEAL",
                ],
            },
        ]
    }
    map_path.write_text(json.dumps(map_data), encoding="utf-8")
    monkeypatch.setenv("ARIFOS_AGENT_MODEL_MAP_PATH", str(map_path))
    # Clear the module-level mtime cache so each test re-reads.
    llm_client._agent_model_map_cache["mtime"] = None
    llm_client._agent_model_map_cache["data"] = None
    return map_path


@pytest.fixture
def vault_outcomes_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    """Redirect VAULT999 operational ledger to a tmp file."""
    vault = tmp_path / "VAULT999"
    vault.mkdir()
    out = vault / "outcomes.jsonl"
    monkeypatch.setattr(llm_client, "_VAULT_OUTCOMES_PATH", out)
    return out


@pytest.fixture
def clear_tokenrouter_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default TOKENROUTER_MODEL to 'deepseek-v4-flash' for explicit-fallback tests."""
    monkeypatch.setenv("TOKENROUTER_MODEL", "deepseek-v4-flash")


# ── Sync tests: select_model_for_role ────────────────────────────────────────


def test_judge_role_with_v4_pro_allowed(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """666_JUDGE + deepseek-v4-pro → allowed, no event emitted, no raise."""
    result = select_model_for_role(
        "666_JUDGE", "deepseek-v4-pro", agent_id="arif_judge"
    )
    assert result == "deepseek-v4-pro"
    assert not vault_outcomes_path.exists(), "No FORBIDDEN event expected"


def test_judge_role_with_v4_flash_fails_closed(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """666_JUDGE + deepseek-v4-flash → fail-closed + FORBIDDEN event emitted."""
    with pytest.raises(LLMUnavailableError) as exc_info:
        select_model_for_role(
            "666_JUDGE", "deepseek-v4-flash", agent_id="arif_judge"
        )
    msg = str(exc_info.value)
    assert "FORBIDDEN_MODEL_FOR_ROLE" in msg
    assert "666_JUDGE" in msg
    assert "deepseek-v4-flash" in msg
    # VAULT999 event must be appended.
    assert vault_outcomes_path.exists()
    lines = vault_outcomes_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["event"] == "FORBIDDEN_MODEL_FOR_ROLE"
    assert event["role"] == "666_JUDGE"
    assert event["decision"] == "888_HOLD"
    assert event["effective_model"] == "deepseek-v4-flash"
    assert "deepseek/deepseek-v4-pro" in event["allowed_models"]
    assert event["agent_id"] == "arif_judge"
    assert "timestamp" in event


def test_seal_role_with_wrong_model_fails_closed(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """999_SEAL + MiniMax-M3 → fail-closed (v4-pro is sole allowed signer)."""
    with pytest.raises(LLMUnavailableError) as exc_info:
        select_model_for_role(
            "999_SEAL", "minimax/MiniMax-M3", agent_id="arif_seal"
        )
    assert "FORBIDDEN_MODEL_FOR_ROLE" in str(exc_info.value)
    assert "999_SEAL" in str(exc_info.value)
    event = json.loads(vault_outcomes_path.read_text(encoding="utf-8").strip())
    assert event["role"] == "999_SEAL"
    assert event["effective_model"] == "minimax/MiniMax-M3"


def test_seal_role_with_v4_pro_allowed(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """999_SEAL + deepseek/deepseek-v4-pro (full key) → allowed."""
    result = select_model_for_role(
        "999_SEAL", "deepseek/deepseek-v4-pro", agent_id="arif_seal"
    )
    assert result == "deepseek/deepseek-v4-pro"
    assert not vault_outcomes_path.exists()


def test_non_constitutional_role_passes_through(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """333_THINK with any model → passthrough, no enforcement."""
    # Flash is fine for 333_THINK (not gated).
    result = select_model_for_role(
        "333_THINK", "deepseek-v4-flash", agent_id="arif_think"
    )
    assert result == "deepseek-v4-flash"
    # Even forbidden-for-judge models pass when role is not gated.
    result = select_model_for_role(
        "444_ROUTE", "minimax/MiniMax-M3", agent_id="arif_route"
    )
    assert result == "minimax/MiniMax-M3"
    assert not vault_outcomes_path.exists()


def test_missing_registry_file_fails_closed_for_judge(
    tmp_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clear_tokenrouter_model: None,
) -> None:
    """Registry missing → fail-closed for 666_JUDGE (never silently allow)."""
    nonexistent = tmp_path / "does_not_exist.json"
    monkeypatch.setenv("ARIFOS_AGENT_MODEL_MAP_PATH", str(nonexistent))
    llm_client._agent_model_map_cache["mtime"] = None
    llm_client._agent_model_map_cache["data"] = None

    with pytest.raises(LLMUnavailableError) as exc_info:
        select_model_for_role("666_JUDGE", "deepseek-v4-pro", agent_id="arif_judge")
    assert "FORBIDDEN_MODEL_FOR_ROLE" in str(exc_info.value)
    assert "AGENT_MODEL_MAP unavailable" in str(exc_info.value)
    event = json.loads(vault_outcomes_path.read_text(encoding="utf-8").strip())
    assert event["reason"].startswith("AGENT_MODEL_MAP unavailable")
    assert event["allowed_models"] == []


def test_env_var_path_override_works(
    tmp_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    clear_tokenrouter_model: None,
) -> None:
    """ARIFOS_AGENT_MODEL_MAP_PATH env override resolves correctly."""
    custom_map = tmp_path / "custom_map.json"
    custom_map.write_text(
        json.dumps(
            {
                "models": [
                    {
                        "model_key": "anthropic/claude-opus-4",
                        "constitutional_roles": ["666_JUDGE", "999_SEAL"],
                        "constitutional_roles_forbidden": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ARIFOS_AGENT_MODEL_MAP_PATH", str(custom_map))
    llm_client._agent_model_map_cache["mtime"] = None
    llm_client._agent_model_map_cache["data"] = None

    # claude-opus-4 is allowed per the custom map.
    result = select_model_for_role("666_JUDGE", "claude-opus-4", agent_id="test")
    assert result == "claude-opus-4"
    # v4-pro is NOT in the custom map → must fail.
    with pytest.raises(LLMUnavailableError):
        select_model_for_role("666_JUDGE", "deepseek-v4-pro", agent_id="test")


def test_full_key_and_short_key_normalization(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """Both 'deepseek-v4-pro' (short) and 'deepseek/deepseek-v4-pro' (full) match."""
    # Short form (cascade style).
    assert select_model_for_role("666_JUDGE", "deepseek-v4-pro") == "deepseek-v4-pro"
    # Full form (map style).
    assert (
        select_model_for_role("666_JUDGE", "deepseek/deepseek-v4-pro")
        == "deepseek/deepseek-v4-pro"
    )
    assert not vault_outcomes_path.exists()


def test_tokenrouter_model_fallback_used_when_preferred_absent(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If requested_model is None, gate checks TOKENROUTER_MODEL env (Option B)."""
    # TOKENROUTER_MODEL = flash (not allowed for judge) → fail.
    monkeypatch.setenv("TOKENROUTER_MODEL", "deepseek-v4-flash")
    with pytest.raises(LLMUnavailableError) as exc_info:
        select_model_for_role("666_JUDGE", None, agent_id="arif_judge")
    assert "FORBIDDEN_MODEL_FOR_ROLE" in str(exc_info.value)
    assert "deepseek-v4-flash" in str(exc_info.value)

    # TOKENROUTER_MODEL = v4-pro → allowed.
    monkeypatch.setenv("TOKENROUTER_MODEL", "deepseek-v4-pro")
    result = select_model_for_role("666_JUDGE", None, agent_id="arif_judge")
    assert result == "deepseek-v4-pro"


def test_no_role_passes_through_with_empty_model(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    clear_tokenrouter_model: None,
) -> None:
    """role=None → passthrough; returns the empty string for no model."""
    assert select_model_for_role(None, None) == ""
    assert select_model_for_role("", "deepseek-v4-flash") == "deepseek-v4-flash"
    assert not vault_outcomes_path.exists()


# ── Async test: call_llm gate (integration at the choke point) ──────────────


@pytest.mark.asyncio
async def test_call_llm_judge_gate_fails_before_cascade(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """call_llm() with constitutional_role='666_JUDGE' + flash → raises
    LLMUnavailableError immediately, cascade never runs (no network call)."""
    # Even if the cascade had network/keys, the gate fires first.
    from arifosmcp.runtime.llm_client import call_llm

    monkeypatch.setenv("TOKENROUTER_MODEL", "deepseek-v4-flash")
    with pytest.raises(LLMUnavailableError) as exc_info:
        await call_llm(
            system="judge this",
            user="candidate",
            tool_origin="666_JUDGE",
            constitutional_role="666_JUDGE",
            preferred_model="deepseek-v4-flash",  # forbidden
            mode="infer",
        )
    assert "FORBIDDEN_MODEL_FOR_ROLE" in str(exc_info.value)
    # Event emitted to outcomes.jsonl.
    assert vault_outcomes_path.exists()
    event = json.loads(vault_outcomes_path.read_text(encoding="utf-8").strip())
    assert event["role"] == "666_JUDGE"
    assert event["effective_model"] == "deepseek-v4-flash"


@pytest.mark.asyncio
async def test_allowed_judge_model_failure_never_enters_generic_cascade(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Allowed model (v4-pro for judge) but TokenRouter unreachable →
    ConstitutionalSeatUnavailable raised — generic cascade NEVER entered.
    This proves the fail-closed gate at lines 1695-1706 works."""
    from arifosmcp.runtime.llm_client import (
        ConstitutionalSeatUnavailable,
        LLMUnavailableError,
        call_llm,
    )

    # Patch module-level TOKENROUTER constant to dead key
    # (env var is read at import time, so module attribute must be patched)
    import arifosmcp.runtime.llm_client as llm_mod

    monkeypatch.setattr(llm_mod, "TOKENROUTER_API_KEY", "dead-key")
    # Kill constitutional DeepSeek direct channel too — all map seats must fail
    # without entering MiniMax/MiMo/Groq generic cascade.
    monkeypatch.setattr(llm_mod, "DEEPSEEK_API_KEY", "")

    # Mock fallback engines that MUST NOT be called
    original_minimax = llm_mod._call_minimax
    original_mimo = llm_mod._call_mimo
    original_groq = llm_mod._call_groq

    call_tracker: list[str] = []

    async def track_minimax(*a, **kw) -> tuple[str, dict]:
        call_tracker.append("minimax")
        return await original_minimax(*a, **kw)

    async def track_mimo(*a, **kw) -> tuple[str, dict]:
        call_tracker.append("mimo")
        return await original_mimo(*a, **kw)

    async def track_groq(*a, **kw) -> tuple[str, dict]:
        call_tracker.append("groq")
        return await original_groq(*a, **kw)

    monkeypatch.setattr(llm_mod, "_call_minimax", track_minimax)
    monkeypatch.setattr(llm_mod, "_call_mimo", track_mimo)
    monkeypatch.setattr(llm_mod, "_call_groq", track_groq)

    with pytest.raises(ConstitutionalSeatUnavailable) as exc_info:
        await call_llm(
            system="judge this",
            user="candidate",
            constitutional_role="666_JUDGE",
            preferred_model="deepseek-v4-pro",  # allowed for judge!
            mode="infer",
            tool_origin="arif_judge",
        )

    msg = str(exc_info.value)
    assert "Constitutional seat unavailable" in msg
    assert "666_JUDGE" in msg
    assert "deepseek-v4-pro" in msg
    # Generic cascade was NEVER entered
    assert call_tracker == [], (
        f"Generic cascade WAS entered! Called: {call_tracker}"
    )
    # VAULT999 event must exist (last line may be multi-event JSONL)
    assert vault_outcomes_path.exists()
    lines = [
        json.loads(line)
        for line in vault_outcomes_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    event = next(e for e in lines if e.get("event") == "JUDGE_SEAT_UNAVAILABLE")
    assert event["decision"] == "HOLD"


@pytest.mark.asyncio
async def test_call_llm_smoke_mode_bypasses_gate(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke/diagnostic modes bypass the constitutional gate (test path)."""
    from arifosmcp.runtime.llm_client import call_llm

    monkeypatch.setenv("TOKENROUTER_MODEL", "deepseek-v4-flash")
    # Smoke mode: should NOT raise even with a forbidden model + role.
    envelope = await call_llm(
        system="smoke test",
        user="ping",
        tool_origin="666_JUDGE",
        constitutional_role="666_JUDGE",
        preferred_model="deepseek-v4-flash",  # would be forbidden in real call
        mode="smoke",
    )
    # Smoke returns deterministic HOLD envelope.
    assert envelope is not None
    assert envelope.provider == "deterministic_fallback"


@pytest.mark.asyncio
async def test_deepseek_direct_channel_serves_judge_when_tokenrouter_dead(
    agent_model_map_path: Path,
    vault_outcomes_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TR dead + DeepSeek direct OK → seat served without generic cascade.

    AMEND-20260730-SEAT-DEPUTY: map-allowed DeepSeek seat may use official
    DeepSeek API when TokenRouter is quota/channel-dead. MiniMax must not run.
    """
    import arifosmcp.runtime.llm_client as llm_mod
    from arifosmcp.runtime.llm_client import call_llm

    monkeypatch.setattr(llm_mod, "TOKENROUTER_API_KEY", "dead-key")

    async def fake_deepseek(*a, **kw):
        return (
            json.dumps({"verdict": "HOLD", "reason": "direct-ok"}),
            {"verdict": "HOLD", "reason": "direct-ok"},
        )

    call_tracker: list[str] = []

    async def track_minimax(*a, **kw):
        call_tracker.append("minimax")
        raise llm_mod.LLMUnavailableError("should not run")

    monkeypatch.setattr(llm_mod, "_call_deepseek_direct", fake_deepseek)
    monkeypatch.setattr(llm_mod, "_call_minimax", track_minimax)

    envelope = await call_llm(
        system="judge",
        user="candidate",
        constitutional_role="666_JUDGE",
        preferred_model="deepseek-v4-pro",
        mode="infer",
        tool_origin="arif_judge",
    )
    assert envelope is not None
    assert call_tracker == []
    # Deputy/channel event recorded
    lines = [
        json.loads(line)
        for line in vault_outcomes_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert any(e.get("event") == "JUDGE_SEAT_DEPUTY_ACTIVATED" for e in lines)
